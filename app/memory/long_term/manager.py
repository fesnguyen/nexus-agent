from app.memory.long_term.base import BaseMemoryStore
from app.memory.long_term.memory_faiss_store import MemoryFaissStore
from app.memory.long_term.models import Memory, MemoryExtractionResult
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

    
    def save(
        self,
        extracted_memories: list[Memory],
    ) -> None:
        """
        Persist memories into long-term storage and
        update the semantic index.
        """

        if not extracted_memories:
            return

        self.memory_store.save(extracted_memories)

        faiss_items = []

        for memory in extracted_memories:

            faiss_id = self.memory_store.get_next_faiss_id()

            self.memory_store.save_faiss_mapping(
                faiss_id=faiss_id,
                memory_id=memory.id,
            )

            faiss_items.append(
                (
                    faiss_id,
                    memory.content,
                )
            )

        self.faiss_store.add_many(
            faiss_items,
        )

        self.faiss_store.save()

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