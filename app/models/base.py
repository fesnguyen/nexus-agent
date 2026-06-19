from abc import ABC
from abc import abstractmethod

from app.contracts.agent_decision import AgentDecision


class BaseLLM(ABC):
    """
    Base interface for all LLM backends.
    """

    @abstractmethod
    def invoke(self, messages) -> AgentDecision:
        pass