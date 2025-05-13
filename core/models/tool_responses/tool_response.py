from pydantic import BaseModel
from typing import Optional, Union, Any, Literal

class ToolCallResult(BaseModel):
    tool_name: str
    result: Any
    
class ToolCallInput(BaseModel):
    role: Literal["tool"] = "tool"
    tool_call_id: str
    content: Any
    
class ToolCallFunction(BaseModel):
    name: str
    arguments: Union[str, dict]
    
class ToolCallResponse(BaseModel):
    id: str
    type: str
    function: ToolCallFunction
    
class ToolResponse(BaseModel):
    tool_args: Optional[list[dict]] = None
    tool_calls: Optional[list[dict]] = None
    tool_results: Optional[list[ToolCallResult]] = None
    tool_messages: Optional[list[ToolCallInput]] = None
    tool_notifications: Optional[list[Union[str, None]]] = None
    