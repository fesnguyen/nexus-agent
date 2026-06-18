from typing import Literal

from pydantic import BaseModel

from app.agent.tool_call import ToolCall


class AgentDecision(BaseModel):
    """
    Decision produced by the planner.
    """

    action: Literal[
        "tool",
        "final_answer",
    ]

    tool_call: ToolCall | None = None

    answer: str | None = None