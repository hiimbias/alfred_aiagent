from typing import List, Optional, Callable, Any, Literal
from loguru import logger
from openai._types import NOT_GIVEN
import json
from core.models.responses import OpenAgentResponse
from core.models.tool_responses import ToolResponse, ToolCallResult
from core.interfaces.base_tool_handler import BaseToolHandler
from mcp import ClientSession 

class ToolHandler(BaseToolHandler):
    """
    A class to handle tool calls.
    
    ## Methods:
        `parse_tool_args()`: A method to parse the tool calls from the response.

        `handle_notification()`: A method to handle the notification from the tool call chunk.

        `handle_tool_request()`: A method to handle the tool request and get the final response with tool results.

    ## Properties:
        `tools`: A property to get and set the tools.

        `tools_map`: A property to get the tools map.
    """
    def __init__(self,
                 tools: Optional[List[Callable[..., Any]]] = NOT_GIVEN,
                 mcp_sessions: Optional[dict[str, ClientSession]] = None,
                 mcp_tools: Optional[dict[str, list[str]]] = None,
                 llm_provider: Literal["openai"] = None,
                 schema_type: Literal["OpenAI", "OpenAIRealtime"] = None,
                 *args,
                 **kwargs):
        
        self._tools = NOT_GIVEN
        self.tools_map = NOT_GIVEN
        self.llm_provider = llm_provider

        if llm_provider is None:
            raise ValueError("llm_provider must be provided")

        if tools is not NOT_GIVEN:
            self._tools = []
            for tool in tools:
                if not hasattr(tool, "schema"):
                    raise ValueError(f"Function '{tool.__name__}' does not have a `schema` attribute. Please wrap the function with `@tool` decorator from `openagentkit.core.utils.tool_wrapper`.")
                self._tools.append(tool.schema)

            match schema_type:
                case "OpenAI":
                    self.tools_map = {
                        tool.schema["function"]["name"]: tool for tool in tools
                    }
                case "OpenAIRealtime":
                    self.tools_map = {
                        tool.schema["name"]: tool for tool in tools
                    }
                case None:
                    raise ValueError("schema_type must be provided")
                case _:
                    raise ValueError(f"Unsupported schema type: {schema_type}")

        self.sessions_map = mcp_sessions
        self.mcp_tools_map = mcp_tools


        
    @property
    def tools(self):
        return self._tools
    
    @tools.setter
    def tools(self, tools):
        self._tools = [tool.schema for tool in tools] if tools else NOT_GIVEN
        self.tools_map = {
            tool.schema["function"]["name"]: tool for tool in tools
        } if tools is not NOT_GIVEN else NOT_GIVEN
        return f"Binded {len(self._tools)} tools."
    
        
    def _handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        """
        Handle the tool call and return the tool result.

        Args:
            tool_name (str): The name of the tool to handle.
            **kwargs: The keyword arguments to pass to the tool
        
        Returns:
            Any: The result of the tool call.
        """
        if self.tools_map is not NOT_GIVEN:
            tool = self.tools_map.get(tool_name, None)
            if not tool:
                return None
            elif callable(tool):
                return tool(**kwargs)
        else:
            logger.error("No tools provided")
            return None
    
    def parse_tool_args(self, response: dict) -> list[dict[str, Any]]:
        """
        Parse the tool calls from the response.

        Args:
            response (dict): The response from the OpenAI model.

        Returns:
            list[dict[str, Any]]: The tool calls.
        """
        tool_calls = None
        if hasattr(response, "tool_calls") and response.tool_calls is not None:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "arguments": tc.function.arguments,
                        "name": tc.function.name,
                    },
                }
                for tc in response.tool_calls
            ]

        return tool_calls
    
    
    def handle_tool_request(self, response: OpenAgentResponse) -> ToolResponse:
        """
        Handle tool requests and get the final response with tool results

        Args:
            response (OpenAgentResponse or OpenAgentStreamingResponse): The response from the OpenAI model.

        Returns:
            ToolResponse: The final response with tool results.
        """
        if type(response) != OpenAgentResponse:
            raise AttributeError("Response must be an OpenAgentResponse or OpenAgentStreamingResponse object")
        
        tool_args_list = []
        tool_results_list = []
        tool_messages_list = []
        notifications_list = []
        
        # Check if the response contains tool calls
        if response.tool_calls is None:
            #logger.debug("No tool calls found in the response. Skipping tool call handling.")
            return ToolResponse(
                tool_args=[],
                tool_calls=[],
                tool_results=[],
                tool_messages=[],
                tool_notifications=[]
            )

        # Handle tool calls 
        for tool_call in response.tool_calls:
            tool_call_id = tool_call.get("id")
            tool_name = tool_call.get("function").get("name")
            tool_args: dict = eval(tool_call.get("function").get("arguments"))
            # Save notification value and remove _notification key from tool args if present
            notification = tool_args.get("_notification", None)
            notifications_list.append(notification)
            tool_args.pop("_notification", None)
            
            # Handle the tool call (execute the tool)
            tool_result = self._handle_tool_call(tool_name, **tool_args)
            
            # Store the tool args
            tool_args_list.append(tool_args)

            # Store tool call and result
            tool_results_list.append(
                ToolCallResult(
                    tool_name=tool_name,
                    result=tool_result
                )
            )
            
            #logger.info(f"Tool Result: {tool_result}")
            
            # Convert tool result to string if it's not already a string
            tool_result_str = str(tool_result)
            
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result_str,  # Use string representation
            }

            tool_messages_list.append(tool_message)  
        
        return ToolResponse(
            tool_args=tool_args_list,
            tool_calls=response.tool_calls,
            tool_results=tool_results_list,
            tool_messages=tool_messages_list,
            tool_notifications=notifications_list
        )