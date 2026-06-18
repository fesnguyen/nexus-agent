import json

from app.agent.agent_action import AgentAction
from app.llm.base import BaseModel
from app.llm.prompts import REACT_PROMPT

from app.tools.registry import ToolRegistry


class ReActPlanner:

    def __init__(
        self,
        model: BaseModel,
        registry: ToolRegistry,
    ) -> None:

        self.model = model
        self.registry = registry

    def plan(
        self,
        user_input: str,
        observations: list[str],
    ) -> AgentAction:

        prompt = REACT_PROMPT.format(
            user_input=user_input,
            observations="\n".join(observations),
            tools=self._build_tool_descriptions(),
        )

        response = self.model.generate(
            prompt
        )

        payload = json.loads(
            response.strip()
        )

        return AgentAction.model_validate(
            payload
        )

    def _build_tool_descriptions(
        self,
    ) -> str:

        descriptions = []

        for tool_name in self.registry.list_tools():

            tool = self.registry.get(
                tool_name
            )

            descriptions.append(
                f"- {tool.name}: {tool.description}"
            )

        return "\n".join(
            descriptions
        )