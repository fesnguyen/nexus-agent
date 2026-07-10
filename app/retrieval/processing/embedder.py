"""
Document embedder.

Responsibilities
----------------
- Lazily load the embedding model.
- Convert chunks into embeddings.
"""

from __future__ import annotations

import numpy as np

from app.models.base_embedding import BaseEmbedding
from app.models.embedding_manager import EmbeddingManager
from app.retrieval.schema import Chunk
from configs.model_settings import RETRIEVAL_EMBEDDING_MODEL


class Embedder(BaseEmbedding):
    """
    Generate dense embeddings using Sentence Transformers.
    """

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
    ) -> None:
        super().__init__(
            embedding_manager,
            RETRIEVAL_EMBEDDING_MODEL,
        )

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

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = self.encode(
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

        embedding = self.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.astype(
            np.float32
        ).reshape(1, -1)