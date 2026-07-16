from pydantic import BaseModel
from pydantic import Field
from typing import Optional

from app.contracts.tool_call import ToolCall


class AgentDecision(BaseModel):
    """
    Structured output produced by an LLM.

    Graph routing is based entirely on action.
    """

    # Strictly forbid any unexpected fields
    model_config = {
        "extra": "forbid"
    }

    thought: str

    response: str

    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Tools to execute before generating a final answer."
    )