"""
Index manager.

Responsibilities
----------------
Coordinate the entire indexing pipeline.

Current implementation
----------------------
- Full rebuild

Future implementation
---------------------
- Incremental indexing
- Detect modified files
- Remove deleted files
- Re-embed changed files
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.models.embedding_manager import EmbeddingManager
from app.retrieval.ingestion.loader import Loader
from app.retrieval.processing.chunker import Chunker
from app.retrieval.processing.embedder import Embedder
from app.retrieval.schema import Chunk, Document
from app.retrieval.storage.chunk_store import ChunkStore
from app.retrieval.storage.faiss_store import FaissStore
from app.retrieval.storage.file_index_store import (
    FileIndexStore,
    IndexedFile,
)
from app.retrieval.storage.mapping_store import (
    MappingStore,
    VectorMapping,
)


@dataclass(slots=True)
class IndexResult:
    """
    Result of a complete indexing run.
    """

    documents: list[Document]

    chunks: list[Chunk]

    embeddings: np.ndarray


class IndexManager:
    """
    Coordinate the indexing pipeline.
    """

    def __init__(
        self,
        loader: Loader,
        chunker: Chunker,
        embedding_manager: Embedder,
        chunk_store: ChunkStore,
        file_index_store: FileIndexStore,
        mapping_store: MappingStore,
        vector_store: FaissStore,
    ) -> None:

        self._loader = loader
        self._chunker = chunker
        self._embedding_manager = embedding_manager

        self._chunk_store = chunk_store
        self._file_index_store = file_index_store
        self._mapping_store = mapping_store
        self._vector_store = vector_store

    def build(self) -> IndexResult:
        """
        Perform a complete rebuild.

        Future versions will replace this with
        incremental indexing without changing
        the public API.
        """

        #
        # Load documents
        #
        documents = self._loader.load()

        #
        # Chunk documents
        #
        chunks = self._chunker.chunk_documents(
            documents
        )

        #
        # Generate embeddings
        #
        embeddings = self._embedding_manager.embed(
            chunks
        )

        #
        # Build FAISS
        #
        self._vector_store.build(
            embeddings
        )

        self._vector_store.save()

        #
        # Store chunks
        #
        self._chunk_store.clear()

        self._chunk_store.add_many(
            chunks
        )

        #
        # Store file index
        #
        self._file_index_store.clear()

        for document in documents:

            chunk_count = sum(
                chunk.source == document.source
                for chunk in chunks
            )

            self._file_index_store.add(
                IndexedFile(
                    source=document.source,
                    content_hash=FileIndexStore.compute_hash(
                        document.source
                    ),
                    embedding_model=self._embedding_manager._model_name,
                    chunk_count=chunk_count,
                )
            )

        #
        # Store vector mapping
        #
        self._mapping_store.clear()

        for vector_id, chunk in enumerate(chunks):

            self._mapping_store.add(
                VectorMapping(
                    chunk_id=chunk.id,
                    vector_store="faiss",
                    embedding_model=self._embedding_manager._model_name,
                    vector_id=vector_id,
                )
            )

        return IndexResult(
            documents=documents,
            chunks=chunks,
            embeddings=embeddings,
        )
    
    def load(self) -> IndexResult:
        """
        Load an existing retrieval index.
        """

        #
        # Load FAISS
        #
        self._vector_store.load()

        #
        # Load chunks
        #
        chunks = self._chunk_store.list()

        #
        # Load documents
        #
        documents = self._loader.load()

        return IndexResult(
            documents=documents,
            chunks=chunks,
            embeddings=None,
        )
    
        
    def exists(self) -> bool:
        """
        Temporary check if the faiss store exist
        """
        return self._vector_store.exists()