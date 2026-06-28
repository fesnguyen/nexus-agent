"""
Document embedder.

Responsibilities
----------------
- Lazily load the embedding model.
- Convert chunks into embeddings.
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from app.retrieval.schema import Chunk


class Embedder:
    """
    Generate dense embeddings using Sentence Transformers.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ) -> None:

        self._model_name = model_name

        self._model: SentenceTransformer | None = None

    @property
    def dimension(self) -> int:
        """
        Embedding dimension.
        """

        return self._get_model().get_sentence_embedding_dimension()

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

        model = self._get_model()

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = model.encode(
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

        model = self._get_model()

        embedding = model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.astype(
            np.float32
        ).reshape(1, -1)

    def _get_model(
        self,
    ) -> SentenceTransformer:
        """
        Lazily load the embedding model.
        """

        if self._model is None:

            print(
                f"[RAG] Loading embedding model: {self._model_name}"
            )

            self._model = SentenceTransformer(
                self._model_name
            )

        return self._model