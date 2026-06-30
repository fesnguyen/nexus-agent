from app.memory.base import BaseMemoryStore
from app.memory.memory_faiss_store import MemoryFaissStore
from app.ranking.reranker import MemoryReranker


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
        memory_store: BaseMemoryStore,
        faiss_store: MemoryFaissStore,
        reranker: MemoryReranker
    ) -> None:

        self.memory_store = memory_store
        self.faiss_store = faiss_store
        self.reranker = reranker

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
        lexical_memories = self.memory_store.search(
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
            self.memory_store.get_memory_ids_from_faiss(
                faiss_ids
            )
        )
        semantic_memories = (
            self.memory_store.get_many(
                memory_ids
            )
        )

        # Combine lexical and semantic memories, remove duplicates
        combined = {}

        for memory in lexical_memories:
            combined[memory.id] = memory

        for memory in semantic_memories:
            combined[memory.id] = memory

        if not combined:
            return ""
        
        # Reanking
        reranked = (
            self.reranker.rerank(
                query=query,
                memories=list(
                    combined.values()
                ),
                top_k=5,
            )
        )
        
        lines = [
            "Relevant Memory:"
        ]

        for memory in reranked:
            lines.append(
                f"- {memory.content}"
            )

        return "\n".join(lines)