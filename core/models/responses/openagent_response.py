from pydantic import BaseModel, Field
from core.models.responses.usage_response import UsageResponse
from typing import Optional, Dict, Any, List, Any, Union


class OpenAgentResponse(BaseModel):
    """
    A response model for the OpenAgent, containing various attributes
    to represent the response details.
    
    Schema:
        ```python
        class OpenAgentResponse(BaseModel):
            role: str
            content: Optional[Union[str, BaseModel, dict]] = None
            tool_calls: Optional[List[Union[Dict[str, Any], BaseModel]]] = None
            tool_results: Optional[List[Union[Dict[str, Any], BaseModel]]] = None
            refusal: Optional[str] = None
            audio: Optional[Union[str, bytes]] = None
            usage: Optional[UsageResponse] = None
        ```
    Where:
        - `role`: The role of the response (e.g., "assistant", "user").
        - `content`: The content of the response, which can be a string,
          BaseModel, dictionary, or any other type.
        - `tool_calls`: A list of tool calls made during the response.
        - `tool_results`: A list of results from the tool calls.
        - `refusal`: A string indicating a refusal to answer.
        - `audio`: Optional audio data associated with the response.
        - `usage`: An instance of UsageResponse containing usage details.
    """
    role: str
    content: Optional[Union[str, BaseModel, dict, Any]] = None
    tool_calls: Optional[List[Union[Dict[str, Any], BaseModel, Any]]] = None
    tool_results: Optional[List[Union[Dict[str, Any], BaseModel, Any]]] = None
    refusal: Optional[str] = None
    audio: Optional[bytes] = None
    usage: Optional[UsageResponse] = None
    
    
    