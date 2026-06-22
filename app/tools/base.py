from abc import ABC
from abc import abstractmethod
from typing import Any
from pydantic import BaseModel


class BaseTool(ABC):
    """
    Base class for all tools.
    """

    name: str
    description: str
    input_schema: BaseModel

    @abstractmethod
    def run(
        self,
        **kwargs: Any,
    ) -> Any:
        pass