from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel


class Attachment(BaseModel):
    """
    Persisted attachment.
    """

    id: int | None = None

    message_id: int | None = None

    type: str

    storage_path: str

    mime_type: str

    extracted_content: str

    created_at: datetime