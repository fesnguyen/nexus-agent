from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from app.contracts.tool_call import ToolCall


class AgentDecision(BaseModel):
    """
    Structured output produced by an LLM.

    Graph routing is based entirely on action.
    """

    thought: str = Field(
        description="Reasoning summary."
    )

    action: Literal[
        "respond",
        "tool",
        "retrieve",
        "memory",
        "plan",
        "finish",
    ]

    response: str | None = None

    tool_call: ToolCall | None = None