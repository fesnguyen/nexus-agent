
from datetime import datetime
from typing import Literal

from typing import Optional

from app.api.schemas.base import BaseSchema
from app.memory.conversation.conversation_schemas import Attachment


class Message(BaseSchema):
    id: int
    role: Literal["system", "user", "assistant"]
    type: str
    content: str | None
    created_at: datetime
    attachments: Optional[list[Attachment]] = None