from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    # camelCase fields mapped to match your JavaScript keys exactly
    conversation_id: str = Field(..., alias="conversationId")
    message: str
    toggles: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        # Pydantic: Allow this model to be created using either 
        # the JavaScript camelCase alias OR the native Python snake_case variable name.
        populate_by_name = True


class ChatResponse(BaseModel):
    content: str