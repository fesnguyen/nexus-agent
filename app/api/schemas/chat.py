from typing import Any, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.base import BaseSchema


class ChatRequest(BaseSchema):
    # camelCase fields mapped to match your JavaScript keys exactly
    conversation_id: str = Field(..., alias="conversationId")
    message: str
    toggles: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseSchema):
    content: str
