from app.agent.agent_decision import (
    AgentDecision,
)

from app.agent.agent_state import (
    AgentState,
)

from app.llm.base import BaseModel


PLANNER_PROMPT = """
You are an AI agent.

Decide exactly one action:

1. tool
   - More information is needed.
   - A tool should be used.

2. final_answer
   - The request can be answered.
   - Enough information has been gathered.

Respond with only one word:

tool

or

final_answer
"""


class Planner:
    """
    Decide whether the agent should:

        - call a tool
        - return a final answer
    """

    def __init__(
        self,
        model: BaseModel,
    ) -> None:

        self.model = model

    def plan(
        self,
        state: AgentState,
    ) -> AgentDecision:

        planner_state = state.model_copy(
            deep=True
        )

        planner_state.system_prompt = (
            PLANNER_PROMPT
        )

        response = (
            self.model.generate_text(
                planner_state,
            )
            .strip()
            .lower()
        )

        if "final_answer" in response:

            return AgentDecision(
                action="final_answer",
            )

        return AgentDecision(
            action="tool",
        )