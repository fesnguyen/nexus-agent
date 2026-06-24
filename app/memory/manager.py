from app.memory.base import BaseMemoryStore


class MemoryManager:
    """
    High-level memory interface used by agents.

    Responsibilities:

    - Retrieve relevant memories
    - Format memory context
    - Hide storage implementation details

    Does NOT:

    - Know about SQLite
    - Know about FAISS
    - Know about Qdrant
    """

    def __init__(
        self,
        store: BaseMemoryStore,
    ) -> None:

        self.store = store

    def retrieve_context(
        self,
        query: str,
        limit: int = 10,
    ) -> str:
        """
        Retrieve relevant memories and
        convert them into prompt context.
        """

        memories = self.store.search(
            query=query,
            limit=limit,
        )

        if not memories:
            return ""

        lines = [
            "Relevant Memory:"
        ]

        for memory in memories:

            lines.append(
                f"- {memory.content}"
            )

        return "\n".join(lines)