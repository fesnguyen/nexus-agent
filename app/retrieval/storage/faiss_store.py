"""
FAISS vector store.

Responsibilities
----------------
- Build FAISS index.
- Add vectors.
- Perform similarity search.
- Save/load FAISS index.

This class intentionally knows nothing about:

- Chunk
- Document
- Metadata
- SQLite
"""

from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np


class FaissStore:
    """
    FAISS vector store.
    """

    def __init__(
        self,
        index_path: Path,
    ) -> None:
        self._index_path = index_path
        self._index: faiss.Index | None = None

    @property
    def size(self) -> int:
        """
        Number of indexed vectors.
        """

        if self._index is None:
            return 0

        return self._index.ntotal

    @property
    def dimension(self) -> int:
        """
        Embedding dimension.
        """

        if self._index is None:
            raise RuntimeError(
                "FAISS index has not been built."
            )

        return self._index.d

    def build(
        self,
        embeddings: np.ndarray,
    ) -> None:
        """
        Build a new FAISS index.
        """

        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D array."
            )

        dimension = embeddings.shape[1]

        self._index = faiss.IndexFlatIP(
            dimension
        )

        self._index.add(
            embeddings
        )

    def search(
        self,
        query_embedding: np.ndarray,
        k: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Search the index.

        Returns
        -------
        scores
        indices
        """

        if self._index is None:
            raise RuntimeError(
                "FAISS index has not been built."
            )

        return self._index.search(
            query_embedding,
            k,
        )

    def save(
        self,
    ) -> None:
        """
        Save the index.
        """

        if self._index is None:
            raise RuntimeError(
                "Nothing to save."
            )

        faiss.write_index(
            self._index,
            str(self._index_path),
        )

    def load(
        self,
    ) -> None:
        """
        Load an existing FAISS index.
        """

        self._index = faiss.read_index(
            str(self._index_path),
        )

    def exists(self) -> bool:
        return self._index_path.exists()