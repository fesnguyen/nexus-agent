from threading import Lock

import numpy as np
from sentence_transformers import SentenceTransformer

from app.retrieval.schema import Chunk


class EmbeddingManager:
    """
    Owns the application's embedding model.

    Responsibilities
    ----------------
    - Load the embedding model.
    - Generate embeddings.

    Future:
    - Model switching.
    - Model unloading.
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:
        self._model_name = model_name

        self._model: SentenceTransformer | None = None
        self._lock = Lock()

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def initialize(self) -> None:
        if self._model is not None:
            return

        with self._lock:
            if self._model is not None:
                return

            print(f"Loading embedding model '{self._model_name}'...")

            self._model = SentenceTransformer(
                self._model_name,
            )

            print(f"Embedding model '{self._model_name}' loaded.")

    def embed(
        self,
        chunks: list[Chunk],
    ) -> np.ndarray:
        """
        Generate embeddings for chunks.
        """

        if not chunks:
            raise RuntimeError(
                "No chunks to embed."
            )
        
        if self._model is None:
            self.initialize()

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.astype(
            np.float32
        )

    def embed_query(
        self,
        query: str,
    ) -> np.ndarray:
        """
        Generate an embedding for a search query.
        """

        if self._model is None:
            self.initialize()

        embedding = self._model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.astype(
            np.float32
        ).reshape(1, -1)