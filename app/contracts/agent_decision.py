from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from app.contracts.tool_call import ToolCall


class AgentDecision(BaseModel):
    """
    Structured output produced by an LLM.

    Graph routing is based entirely on action.
    """

    thought: str | None = Field(
        default=None,
        description="Reasoning summary.",
    )

    response: str | None = Field(
        default=None,
        description="Final answer or response to the user query.",
    )

    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Tools to execute before generating a final answer."
    )