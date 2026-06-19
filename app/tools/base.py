from abc import ABC
from abc import abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Base class for all tools.
    """

    name: str
    description: str

    @abstractmethod
    def run(
        self,
        **kwargs: Any,
    ) -> Any:
        pass