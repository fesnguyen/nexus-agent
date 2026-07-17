from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.models.base_embedding import BaseEmbedding
from app.models.embedding_manager import EmbeddingManager
from configs.model_settings import MEMORY_EMBEDDING_MODEL


class MemoryFaissStore(BaseEmbedding):
    """
    Semantic memory index.

    Stores:
    - embeddings
    - faiss ids

    Does NOT store:
    - memory content
    - metadata
    """

    def __init__(
        self,
        index_path: Path,
        embedding_manager: EmbeddingManager,
    ) -> None:
        super().__init__(
            embedding_manager,
            MEMORY_EMBEDDING_MODEL,
        )

        self.index_path = index_path
        self.index = None
        self.dimension = None

    def get_index(self):
        """
        Get faiss index, if model is not loaded, this wait for loading before return
        """

        # Return cached index immediately if it's already in memory
        if self.index is not None:
            return self.index

        # Get model dimension for faiss initialization
        if self.dimension is None:
            self.dimension = self.embedding_model.get_embedding_dimension()

        if self.index_path.exists():
            self.index = faiss.read_index(
                str(self.index_path)
            )
        else:
            self.index = faiss.IndexIDMap(
                faiss.IndexFlatIP(
                    self.dimension
                )
            )

        return self.index

    def embed(
        self,
        text: str,
    ) -> np.ndarray:

        embedding = self.encode(
            text,
            normalize_embeddings=True,
        )

        return np.array(
            [embedding],
            dtype=np.float32,
        )

    def add(
        self,
        faiss_id: int,
        content: str,
    ) -> None:

        vector = self.embed(
            content
        )

        self.get_index().add_with_ids(
            vector,
            np.array(
                [faiss_id],
                dtype=np.int64,
            ),
        )

    def search(
        self,
        query: str,
        k: int = 10,
    ) -> list[int]:

        if self.get_index().ntotal == 0:
            return []

        query_vector = self.embed(
            query
        )

        scores, ids = self.get_index().search(
            query_vector,
            k,
        )

        return [
            int(faiss_id)
            for faiss_id in ids[0]
            if faiss_id != -1
        ]

    def save(
        self,
    ) -> None:

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.get_index(),
            str(self.index_path),
        )

    
    def add_many(
        self,
        items: list[tuple[int, str]],
    ) -> None:
        """Add multiple items to faiss index.

        Encode the content and add to index with their respective IDs.

        Args:
        items: list of tuple contain faiss id and pure memory content.
        """
        if not items:
            return

        vectors = []
        ids = []

        for faiss_id, content in items:

            vectors.append(
                self.encode(
                    content,
                    normalize_embeddings=True,
                )
            )

            ids.append(
                faiss_id
            )

        vectors = np.array(
            vectors,
            dtype=np.float32,
        )

        ids = np.array(
            ids,
            dtype=np.int64,
        )

        self.get_index().add_with_ids(
            vectors,
            ids,
        )