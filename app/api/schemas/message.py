
from datetime import datetime
from typing import Literal

from app.api.schemas.base import BaseSchema


class Message(BaseSchema):
    id: int
    role: Literal["system", "user", "assistant"]
    type: str
    content: str | None
    created_at: datetime