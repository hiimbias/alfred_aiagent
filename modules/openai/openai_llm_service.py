import os
from loguru import logger
from typing import Any, Callable, Dict, List, Optional, Literal, Generator
from openai import OpenAI
from openai._types import NOT_GIVEN, NotGiven
from pydantic import BaseModel
from core.handlers import ToolHandler
from core.interfaces import BaseLLMModel
from core.models.responses import (
    OpenAgentResponse,
    UsageResponse,
    PromptTokensDetails,
    CompletionTokensDetails,
)

class OpenAILLMService(BaseLLMModel):
    def __init__(self, 
                 client: OpenAI = None,
                 model: str = "gpt-4o-mini",
                 system_message: Optional[str] = None,
                 tools: Optional[List[Callable[..., Any]]] = NOT_GIVEN,
                 api_key: Optional[str] = os.getenv("OPENAI_API_KEY"),
                 temperature: Optional[float] = 0.3,
                 max_tokens: Optional[int] = None,
                 top_p: Optional[float] = None,
                *args,
                **kwargs
                 ) -> None:
        super().__init__(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            *args,
            **kwargs,
        )

        self._tool_handler = ToolHandler(
            tools=tools, llm_provider="openai", schema_type="OpenAI"
        )
        
        self._client = client
        if client is None:
            if api_key is None:
                raise ValueError("No API key provided. Please set the OPENAI_API_KEY environment variable or pass it as an argument.")
            self._client = OpenAI(
                api_key=api_key,
            )

        self._model = model
        self._api_key = api_key
        self._system_message = system_message
        self._context_history = [
            {
                "role": "system",
                "content": self._system_message,
            }
        ]

    @property
    def model(self) -> str:
        """
        Get the model name.

        Returns:
            The model name.
        """
        return self._model
    
    @property
    def history(self) -> List[Dict[str, Any]]:
        """
        Get the history of the conversation.

        Returns:
            The history of the conversation.
        """
        
        return self._context_history
    
    # Property to access tools from the tool handler
    @property
    def tools(self):
        """
        Get the tools from the tool handler.

        Returns:
            The tools from the tool handler.
        """
        return self._tool_handler.tools
    
    def clone(self) -> 'OpenAILLMService':
        """
        Clone the LLM model instance.

        Returns:
            A clone of the LLM model instance.
        """
        return OpenAILLMService(
            client=self._client,
            model=self._model,
            tools=self.tools,
            api_key=self._api_key,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            top_p=self._top_p,
        )
    
    def _handle_client_request(self,
                              messages: List[Dict[str, str]],
                              tools: Optional[List[Dict[str, Any]]],
                              response_schema: Optional[BaseModel] = NOT_GIVEN,
                              temperature: Optional[float] = None,
                              max_tokens: Optional[int] = None,
                              top_p: Optional[float] = None,
                              audio: Optional[bool] = False,
                              audio_format: Optional[str] = "pcm16",
                              audio_voice: Optional[Literal["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]] = "alloy",
                              **kwargs) -> OpenAgentResponse:
        """
        Handle the client request.

        Args:
            messages: The messages to send to the model.
            tools: The tools to use in the response.
            response_schema: The schema to use in the response.
            temperature: The temperature to use in the response.
            max_tokens: The max tokens to use in the response.
            top_p: The top p to use in the response.

        Returns:
            An OpenAgentResponse object.
        """

        temperature = kwargs.get("temperature", temperature)
        if temperature is None:
            temperature = self._temperature

        max_tokens = kwargs.get("max_tokens", max_tokens)
        if max_tokens is None:
            max_tokens = self._max_tokens

        top_p = kwargs.get("top_p", top_p)
        if top_p is None:
            top_p = self._top_p

        if tools is None:
            tools = self.tools

        if response_schema is NOT_GIVEN or isinstance(response_schema, NotGiven):
            # Handle the client request without response schema
            client_response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=tools,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    top_p=self._top_p,
                    modalities=["text", "audio"] if audio else ["text"],
                    audio={
                        "format": audio_format,
                        "voice": audio_voice,
                    } if audio else None,
            )
            
            response_message = client_response.choices[0].message

            # Create the response object
            response = OpenAgentResponse(
                role=response_message.role,
                content=response_message.content,
                tool_calls=response_message.tool_calls,
                refusal=response_message.refusal,
                audio=response_message.audio,
            )
        else:
            # Handle the client request with response schema
            client_response = self._client.beta.chat.completions.parse(
                model=self._model,
                messages=messages,
                tools=tools,
                response_format=response_schema,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                top_p=self._top_p,
            )

            response_message = client_response.choices[0].message

            # Create the response object
            response = OpenAgentResponse(
                role=response_message.role,
                content=response_message.parsed,
                tool_calls=response_message.tool_calls,
                refusal=response_message.refusal,
                audio=response_message.audio,
            )
        
        response.usage = UsageResponse(
            prompt_tokens=client_response.usage.prompt_tokens,
            completion_tokens=client_response.usage.completion_tokens,
            total_tokens=client_response.usage.total_tokens,
            prompt_tokens_details=PromptTokensDetails(
                cached_tokens=client_response.usage.prompt_tokens_details.cached_tokens,
                audio_tokens=client_response.usage.prompt_tokens_details.audio_tokens,
            ),
            completion_tokens_details=CompletionTokensDetails(
                reasoning_tokens=client_response.usage.completion_tokens_details.reasoning_tokens,
                audio_tokens=client_response.usage.completion_tokens_details.audio_tokens,
                accepted_prediction_tokens=client_response.usage.completion_tokens_details.accepted_prediction_tokens,
                rejected_prediction_tokens=client_response.usage.completion_tokens_details.rejected_prediction_tokens,
            ),
        )
        
        return response
          
    def model_generate(self, 
                       messages: List[Dict[str, str]],
                       tools: Optional[List[Dict[str, Any]]] = None,
                       response_schema: Optional[BaseModel] = NOT_GIVEN,
                       temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None,
                       top_p: Optional[float] = None,
                       audio: Optional[bool] = False,
                       audio_format: Optional[str] = "pcm16",
                       audio_voice: Optional[Literal["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]] = "alloy",
                       **kwargs) -> OpenAgentResponse:
        """
        Generate a response from the model.
        
        Args:
            messages: The messages to send to the model.
            tools: The tools to use in the response.
            response_schema: The schema to use in the response.
            temperature: The temperature to use in the response.
            max_tokens: The maximum number of tokens to use in the response.
            top_p: The top p to use in the response.
            audio: Whether to include audio in the response.
            audio_format: The format of the audio.
            audio_voice: The voice to use for the audio.
        
        Returns:
            An OpenAgentResponse object.

        Example:
        ```python
        from openagentkit.tools import duckduckgo_search_tool
        from openagentkit.modules.openai import OpenAILLMService

        llm_service = OpenAILLMService(client, tools=[duckduckgo_search_tool])
        response = llm_service.model_generate(messages=[{"role": "user", "content": "What is TECHVIFY?"}])
        ```
        """

        temperature = kwargs.get("temperature", temperature)
        if temperature is None:
            temperature = self._temperature

        max_tokens = kwargs.get("max_tokens", max_tokens)
        if max_tokens is None:
            max_tokens = self._max_tokens

        top_p = kwargs.get("top_p", top_p)
        if top_p is None:
            top_p = self._top_p

        if tools is None:
            tools = self.tools
            
        #logger.info(f"Tools: {tools}")

        # Handle the client request
        response = self._handle_client_request(
            messages=messages, 
            tools=tools,
            response_schema=response_schema,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            audio=audio,
            audio_format=audio_format,
            audio_voice=audio_voice,
        )
        
        if response.tool_calls:
            # Extract tool_calls arguments using the tool handler
            tool_calls = self._tool_handler.parse_tool_args(response)
            
            # Update the response with the parsed tool calls
            response.tool_calls = tool_calls
        
        return response
    
    def add_context(self, content: dict[str, str]):
        """
        Add context to the model.

        Args:
            content: The content to add to the context.

        Returns:
            The context history.
        """
        if not content:
            return self._context_history
        
        self._context_history.append(content)
        return self._context_history
        
    def extend_context(self, content: List[dict[str, str]]):
        """
        Extend the context of the model.

        Args:
            content: The content to extend the context with.

        Returns:
            The context history.
        """
        if not content:
            return self._context_history
        
        self._context_history.extend(content)
        return self._context_history
    
    def clear_context(self):
        """
        Clear the context of the model leaving only the system message.

        Returns:
            The cleared context history.
        """
        self._context_history = [
            {
                "role": "system",
                "content": self._system_message,
            }
        ]
        return self._context_history