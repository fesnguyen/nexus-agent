from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.api.schemas.base import BaseSchema
from app.api.schemas.message import Message


class ConversationSummary(BaseSchema):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class Conversation(ConversationSummary):
    messages: list[Message] = Field(default_factory=list)


class ConversationsResponse(BaseSchema):
    items: list[Conversation]


class ConversationResponse(BaseSchema):
    data: Conversation