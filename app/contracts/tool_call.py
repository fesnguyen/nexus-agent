from typing import Any
import uuid

from pydantic import BaseModel
from pydantic import Field


class ToolCall(BaseModel):
    """
    Request to execute a tool.
    """

    name: str = Field(
        description="Tool name registered in tool registry."
    )

    args: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments."
    )

    id: str = Field(default_factory=lambda: f"call_{uuid.uuid4().hex[:12]}")