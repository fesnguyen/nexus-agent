from sentence_transformers import CrossEncoder

from app.memory.long_term.models import Memory
from app.models.base_cross_encoder import BaseCrossEncoder
from app.models.cross_encoder_manager import CrossEncoderManager
from configs.model_settings import CROSS_ENCODER_MODEL


class MemoryReranker(BaseCrossEncoder):

    def __init__(
        self,
        cross_encoder_manager: CrossEncoderManager,
    ) -> None:
        super().__init__(
            cross_encoder_manager,
            CROSS_ENCODER_MODEL,
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

        scores = self.predict(
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