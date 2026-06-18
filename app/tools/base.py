from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseTool(ABC):
    """
    Base interface for all Nexus tools.
    """

    name: str
    description: str

    input_schema: type[BaseModel]

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """
        Execute the tool.
        """
        raise NotImplementedError