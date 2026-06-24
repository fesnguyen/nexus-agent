from abc import ABC
from abc import abstractmethod
from typing import Type

from pydantic import BaseModel

from app.contracts.agent_decision import AgentDecision
from app.tools.registry import ToolRegistry


class BaseLLM(ABC):
    """
    Base interface for all LLM backends.
    """

    @abstractmethod
    def invoke(self, messages, tool: ToolRegistry, response_model: Type[BaseModel]) -> BaseModel:
        pass