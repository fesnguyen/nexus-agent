from typing import Any

from pydantic import BaseModel
from pydantic import Field


class ToolCall(BaseModel):
    """
    Request to execute a tool.
    """

    name: str = Field(
        description="Tool name registered in tool registry."
    )

    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments."
    )