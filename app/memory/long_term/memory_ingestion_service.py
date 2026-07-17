from __future__ import annotations

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)

from app.memory.long_term.extractor import MemoryExtractor
from app.memory.long_term.manager import MemoryManager


class MemoryIngestionService:
    """
    Extract and persist long-term memories from the latest chat exchange.
    """

    def __init__(
        self,
        extractor: MemoryExtractor,
        memory_manager: MemoryManager,
    ) -> None:
        self._extractor = extractor
        self._memory_manager = memory_manager

    def ingest(
        self,
        messages: list[BaseMessage],
    ) -> None:
        """
        Extract memories from the latest completed chat exchange.
        """

        exchange = self._get_latest_chat_exchange(
            messages,
        )

        if not exchange:
            return

        memories = self._extractor.extract(
            exchange,
        )

        if not memories:
            return

        self._memory_manager.save(
            memories,
        )

    def _get_latest_chat_exchange(
        self,
        messages: list[BaseMessage],
    ) -> list[BaseMessage]:
        """
        Return the latest completed chat exchange.

        The returned exchange begins with the latest HumanMessage
        and includes every subsequent message (AI/Tool) until the
        end of the conversation.
        """

        exchange: list[BaseMessage] = []

        for message in reversed(messages):

            exchange.append(message)

            if isinstance(message, HumanMessage):
                break

        exchange.reverse()

        return exchange