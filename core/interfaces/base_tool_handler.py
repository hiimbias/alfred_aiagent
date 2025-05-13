from abc import ABC, abstractmethod
from core.models.responses import OpenAgentResponse
from core.models.tool_responses import ToolResponse
from typing import Union, Any

class BaseToolHandler(ABC):
    @abstractmethod
    def parse_tool_args(self, response: dict) -> list[dict[str, Any]]:
        """
        An abstract method to parse the tool response.
        
        Args:
            response (dict): The tool response to be parsed.
            
        Returns:
            list[dict[str, Any]]: The tools calls.
        """
        raise NotImplementedError("Parse tool response method not implemented.")
    
    
    @abstractmethod
    def handle_tool_request(self, response: OpenAgentResponse) -> ToolResponse:
        """
        Handle tool requests and get the final response with tool results

        Args:
            response (OpenAgentResponse or OpenAgentStreamingResponse): The response from the OpenAI model.

        Returns:
            ToolResponse: The final response with tool results.
        """
        raise NotImplementedError 