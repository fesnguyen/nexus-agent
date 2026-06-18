from app.agent.agent_decision import (
    AgentDecision,
)

from app.llm.base import BaseModel


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
        user_input: str,
        observations: list[str],
    ) -> AgentDecision:

        observations_text = "\n".join(
            observations
        )

        prompt = f"""
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

User Request:
{user_input}

Observations:
{observations_text}
"""

        response = self.model.generate_text(
            prompt=prompt,
        )

        response = (
            response
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