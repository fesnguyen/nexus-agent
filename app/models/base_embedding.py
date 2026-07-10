from abc import ABC

from sentence_transformers import SentenceTransformer

from app.models.embedding_manager import EmbeddingManager
from app.models.embedding_manager import EmbeddingManager


class BaseEmbedding(ABC):

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        model_name: str,
    ) -> None:
        self._embedding_manager = embedding_manager
        self._model_name = model_name

        self._embedding_manager.register(
            model_name,
        )

    def get_model(self) -> SentenceTransformer:
        return self._embedding_manager.get_model(self._model_name)

    def encode(
        self,
        *args,
        **kwargs,
    ):
        return self.get_model().encode(
            *args,
            **kwargs,
        )