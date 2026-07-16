from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Literal
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.base import BaseDTO


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    toggles: Dict[str, Any] = Field(default_factory=dict)
    attachments: List[UploadFile] = Field(default_factory=list)

    @classmethod
    def as_form(
        cls,
        conversationId: str = Form(...),          # Maps camelCase from UI
        message: str = Form(""),
        toggles: str = Form("{}"),                 # Transmitted as a stringified JSON object
        attachments: List[UploadFile] = File([]),  # Captures multi-part file stream arrays
    ):
        # Parse the stringified toggles dictionary safely
        try:
            toggles_dict = json.loads(toggles)
        except (json.JSONDecodeError, TypeError):
            toggles_dict = {}

        return cls(
            conversation_id=conversationId,
            message=message,
            toggles=toggles_dict,
            attachments=attachments
        )


class ChatResponse(BaseDTO):
    content: str