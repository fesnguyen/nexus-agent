from app.memory.base import BaseMemoryStore
from app.memory.faiss_store import FaissStore


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
        faiss_store: FaissStore,
    ) -> None:

        self.store = store
        self.faiss_store = faiss_store

    def retrieve_context(
        self,
        query: str,
        limit: int = 10,
    ) -> str:
        """
        Retrieve relevant memories and
        convert them into prompt context.
        """

        # Lexical search
        lexical_memories = self.store.search(
            query=query,
            limit=limit,
        )

        # Semantic search
        faiss_ids = self.faiss_store.search(
            query=query,
            k=limit,
        )

        # Load semantic memories
        memory_ids = (
            self.store.get_memory_ids_from_faiss(
                faiss_ids
            )
        )
        semantic_memories = (
            self.store.get_many(
                memory_ids
            )
        )

        combined = {}

        for memory in lexical_memories:
            combined[memory.id] = memory

        for memory in semantic_memories:
            combined[memory.id] = memory

        if not combined:
            return ""
        
        lines = [
            "Relevant Memory:"
        ]

        for memory in combined.values():
            lines.append(
                f"- {memory.content}"
            )

        return "\n".join(lines)