"""
Retrieval service.

Public entry point for the RAG subsystem.

Responsibilities
----------------
- Initialize the retrieval pipeline.
- Retrieve relevant chunks.

This class intentionally hides the implementation details of:

- Loader
- Parser
- Chunker
- Embedder
- FAISS
- SQLite
"""

from __future__ import annotations

from pathlib import Path

from app.retrieval.index_manager import IndexManager
from app.retrieval.ingestion.loader import Loader
from app.retrieval.ingestion.parser import Parser
from app.retrieval.processing.base_query_rewriter import BaseQueryRewriter
from app.retrieval.processing.chunker import Chunker
from app.retrieval.processing.embedder import Embedder
from app.retrieval.schema import Chunk, Document, SearchResult
from app.retrieval.storage.chunk_store import ChunkStore
from app.retrieval.storage.faiss_store import FaissStore
from app.retrieval.storage.file_index_store import FileIndexStore
from app.retrieval.storage.mapping_store import MappingStore


class RAGService:
    """
    Retrieval service.
    """

    def __init__(
        self,
        knowledge_dir: Path,
        database: Path,
        query_rewriter: BaseQueryRewriter,
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        chunk_size: int = 1500,
        chunk_overlap: int = 300,
    ) -> None:

        #
        # Processing
        #

        self._loader = Loader(
            knowledge_dir=knowledge_dir,
            parser=Parser(),
        )

        self._chunker = Chunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self._embedder = Embedder(
            model_name=embedding_model,
        )

        #
        # Storage
        #

        self._chunk_store = ChunkStore(database)

        self._file_index_store = FileIndexStore(database)

        self._mapping_store = MappingStore(database)

        self._vector_store = FaissStore()

        #
        # Index manager
        #

        self._index_manager = IndexManager(
            loader=self._loader,
            chunker=self._chunker,
            embedder=self._embedder,
            chunk_store=self._chunk_store,
            file_index_store=self._file_index_store,
            mapping_store=self._mapping_store,
            vector_store=self._vector_store,
        )

        self.query_rewriter = query_rewriter

        #
        # Runtime cache
        #

        self._documents: list[Document] = []

        self._chunks: list[Chunk] = []

        self._embeddings = None

    def initialize(self) -> None:
        """
        Build the retrieval index.
        """

        result = self._index_manager.build()

        self._documents = result.documents

        self._chunks = result.chunks

        self._embeddings = result.embeddings

    def retrieve(
        self,
        query: str,
        k: int = 5,
        history: list[str] | None = None,
    ) -> str:
        """
        Retrieve the top-k relevant chunks.
        """

        rewrited_query = self.query_rewriter.rewrite(query)

        query_embedding = self._embedder.embed_query(
            rewrited_query
        )

        scores, indices = self._vector_store.search(
            query_embedding,
            k,
        )

        results: list[SearchResult] = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index == -1:
                continue

            results.append(
                SearchResult(
                    chunk=self._chunks[index],
                    score=float(score),
                )
            )

        return "\n\n".join(r.chunk.text for r in results)