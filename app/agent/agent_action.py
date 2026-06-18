# app/agent/agent_action.py

from typing import Any

from pydantic import BaseModel


class AgentAction(BaseModel):
    """
    Decision produced by the agent planner.
    """

    action: str
    content: Any