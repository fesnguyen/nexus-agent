from abc import ABC, abstractmethod


class BaseModel(ABC):
    """
    Base interface for all Nexus models.
    """

    @abstractmethod
    def generate(
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