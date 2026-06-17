import json

from app.agent.tool_call import ToolCall

from app.llm.base import BaseModel
from app.llm.prompts import TOOL_CALL_PROMPT

from app.tools.registry import ToolRegistry


class ToolCaller:
    """
    Uses the model to generate a structured tool call.

    Responsibilities:
        - Describe available tools
        - Ask the model to select a tool
        - Extract tool arguments
        - Return a validated ToolCall object
    """

    def __init__(
        self,
        model: BaseModel,
        registry: ToolRegistry,
    ) -> None:

        self.model = model
        self.registry = registry

    def generate_tool_call(
        self,
        user_input: str,
    ) -> ToolCall:
        """
        Generate a structured tool call from a user request.

        Args:
            user_input:
                Original user request.

        Returns:
            ToolCall object.
        """

        prompt = TOOL_CALL_PROMPT.format(
            tools=self._build_tool_descriptions()
        )

        prompt += (
            f"\n\nUser Request:\n{user_input}"
        )

        response = self.model.generate(
            prompt
        )

        try:
            payload = json.loads(
                response.strip()
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                f"Model returned invalid JSON:\n{response}"
            ) from exc

        return ToolCall.model_validate(
            payload
        )

    def _build_tool_descriptions(
        self,
    ) -> str:
        """
        Build tool descriptions for prompting.

        Returns:
            Formatted tool list.
        """

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