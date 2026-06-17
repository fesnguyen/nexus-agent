from app.llm.base import BaseModel
from app.tools.registry import ToolRegistry

from app.llm.prompts import TOOL_SELECTION_PROMPT


class ToolRouter:
    """
    Uses the model to select the best tool.
    """

    def __init__(
        self,
        model: BaseModel,
        registry: ToolRegistry,
    ) -> None:
        self.model = model
        self.registry = registry

    def route(
        self,
        user_input: str,
    ) -> str:
        """
        Return the selected tool name.
        """

        tool_descriptions = []

        for tool_name in self.registry.list_tools():

            tool = self.registry.get(tool_name)

            tool_descriptions.append(
                f"- {tool.name}: {tool.description}"
            )

        prompt = TOOL_SELECTION_PROMPT.format(
            tool_descriptions="\n".join(
                tool_descriptions
            )
        )

        prompt += f"\n\nUser Request:\n{user_input}"

        response = self.model.generate(
            prompt
        )

        return response.strip()