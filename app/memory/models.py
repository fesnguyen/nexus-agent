from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field


class MemoryType(str, Enum):
    """
    Categories of long-term memory.
    """

    PREFERENCE = "preference"

    FACT = "fact"

    PROJECT = "project"

    EPISODE = "episode"

    CONTEXT = "context"


class Memory(BaseModel):
    """
    Canonical memory entity used throughout Nexus.

    This model is storage-agnostic.
    SQLite, FAISS, Qdrant, Chroma, etc.
    should all use this same object.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    type: MemoryType

    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

class MemoryExtractionResult(BaseModel):
    """
    Structured output returned by the memory extractor.
    """

    memories: list[Memory] = Field(
        default_factory=list
    )