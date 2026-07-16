from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from app.api.schemas.base import BaseDTO


class ConversationSummaryDTO(BaseDTO):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDTO(ConversationSummaryDTO):
    messages: list[MessageDTO] = Field(default_factory=list)


class MessageDTO(BaseDTO):
    id: int
    role: Literal["system", "user", "assistant"]
    type: str
    content: str | None
    created_at: datetime
    attachments: Optional[list[AttachmentDTO]] = None


class AttachmentDTO(BaseDTO):
    id: int
    message_id: int
    type: str
    storage_path: str


class ConversationsResponseDTO(BaseDTO):
    items: list[ConversationDTO]


class ConversationResponseDTO(BaseDTO):
    data: ConversationDTO