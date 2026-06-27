from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class FaissStore:
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
        index_path: str,
        model_name: str = "intfloat/multilingual-e5-base", # Support multiple languages
    ) -> None:

        self.index_path = Path(index_path)

        self.encoder = SentenceTransformer(
            model_name
        )

        self.dimension = (
            self.encoder
            .get_embedding_dimension()
        )

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

    def embed(
        self,
        text: str,
    ) -> np.ndarray:

        embedding = self.encoder.encode(
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

        self.index.add_with_ids(
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

        if self.index.ntotal == 0:
            return []

        query_vector = self.embed(
            query
        )

        scores, ids = self.index.search(
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
            self.index,
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
                self.encoder.encode(
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

        self.index.add_with_ids(
            vectors,
            ids,
        )