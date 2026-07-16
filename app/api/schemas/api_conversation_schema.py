from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from app.api.schemas.base import BaseSchema


class ConversationSummary(BaseSchema):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class Conversation(ConversationSummary):
    messages: list[Message] = Field(default_factory=list)

class Message(BaseSchema):
    id: int
    role: Literal["system", "user", "assistant"]
    type: str
    content: str | None
    created_at: datetime
    attachments: Optional[list[Attachment]] = None


class Attachment(BaseSchema):
    id: int
    message_id: int
    type: str
    url: str


class ConversationsResponse(BaseSchema):
    items: list[Conversation]


class ConversationResponse(BaseSchema):
    data: Conversation