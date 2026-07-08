
from datetime import datetime
from typing import Literal

from app.api.schemas.base import BaseSchema


class Message(BaseSchema):
    id: str
    role: Literal["system", "user", "assistant"]
    type: str
    content: str
    created_at: datetime