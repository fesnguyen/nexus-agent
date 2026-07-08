# memory/base.py

from abc import ABC
from abc import abstractmethod

from app.memory.long_term.models import Memory


class BaseMemoryStore(ABC):

    @abstractmethod
    def save(
        self,
        memories: list[Memory],
    ) -> None:
        ...

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Memory]:
        ...

    @abstractmethod
    def delete(
        self,
        memory_id: str,
    ) -> None:
        ...