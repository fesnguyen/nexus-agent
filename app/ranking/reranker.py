from sentence_transformers import CrossEncoder

from app.memory.long_term.models import Memory


class MemoryReranker:

    def __init__(
        self,
        model_name: str = (
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        ),
    ) -> None:

        self.model = CrossEncoder(
            model_name
        )

    def rerank(
        self,
        query: str,
        memories: list[Memory],
        top_k: int = 5,
    ) -> list[Memory]:

        if not memories:
            return []

        pairs = [
            (
                query,
                memory.content,
            )
            for memory in memories
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = sorted(
            zip(
                memories,
                scores,
                strict=False,
            ),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            memory
            for memory, _ in ranked[:top_k]
        ]