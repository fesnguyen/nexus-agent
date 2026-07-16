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

    thought: Optional[str] = Field(
        default=None,
        description="The internal reasoning or chain of thought before taking an action.",
    )

    response: Optional[str] = Field(
        default=None,
        description="Final answer or response to the user query.",
    )

    tool_calls: Optional[list[ToolCall]] = Field(
        default_factory=[],
        description="Tools to execute before generating a final answer."
    )