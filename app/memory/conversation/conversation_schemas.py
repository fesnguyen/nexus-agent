from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Message:
    id: str
    conversation_id: str
    role: str
    type: str
    content: str
    created_at: datetime

@dataclass(slots=True)
class Conversation:
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[Message]