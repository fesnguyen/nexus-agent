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
class Attachment():
    """
    Persisted attachment.
    """

    id: int

    message_id: int

    type: str

    storage_path: str

    mime_type: str

    extracted_content: str

    created_at: datetime

@dataclass(slots=True)
class Conversation:
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[Message]