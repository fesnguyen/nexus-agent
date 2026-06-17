from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Base interface for all Nexus tools.
    """

    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """
        Execute the tool.
        """
        raise NotImplementedError