from abc import ABC, abstractmethod

from app.agent.tool_call import ToolCall


class BaseModel(ABC):
    """
    Base interface for all Nexus models.
    """

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        image_path: str | None = None,
    ) -> str:
        """
        Generate a response.

        Args:
            prompt:
                User instruction.

            image_path:
                Optional image input.

        Returns:
            Model response.
        """
        pass

    @abstractmethod
    def generate_tool_call(
        self,
        user_input: str,
        tools: list[dict],
        image_path: str | None = None,
    ) -> ToolCall | None:
        """
        Generate a tool call using the model's native
        tool-calling capabilities.

        Args:
            user_input:
                User request.

            tools:
                Tool schemas exposed to the model.

            image_path:
                Optional image for multimodal models.

        Returns:
            ToolCall if the model decides a tool is required.

            None if the model can answer directly
            without using a tool.
        """
        pass