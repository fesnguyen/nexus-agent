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
- FAISS
- SQLite
"""

from __future__ import annotations

from pathlib import Path
from threading import Lock

from app.models.embedding_manager import EmbeddingManager
from app.retrieval.index_manager import IndexManager
from app.retrieval.ingestion.loader import Loader
from app.retrieval.ingestion.parser import Parser
from app.retrieval.processing.base_context_compressor import BaseContextCompressor
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
        db_path: Path,
        faiss_path: Path,
        embedding_manager: Embedder,
        query_rewriter: BaseQueryRewriter,
        context_compressor: BaseContextCompressor,
        chunk_size: int = 1500,
        chunk_overlap: int = 300,
    ) -> None:
        
        # Initialize
        self.db_path = db_path
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.faiss_path = faiss_path
        self.faiss_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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

        self._embedding_manager = embedding_manager

        #
        # Storage
        #

        self._chunk_store = ChunkStore(db_path)

        self._file_index_store = FileIndexStore(db_path)

        self._mapping_store = MappingStore(db_path)

        self._vector_store = FaissStore(
            index_path=faiss_path,
        )

        #
        # Index manager
        #

        self._index_manager = IndexManager(
            loader=self._loader,
            chunker=self._chunker,
            embedding_manager=self._embedding_manager,
            chunk_store=self._chunk_store,
            file_index_store=self._file_index_store,
            mapping_store=self._mapping_store,
            vector_store=self._vector_store,
        )

        self.query_rewriter = query_rewriter

        self.context_compressor = context_compressor

        #
        # Runtime cache
        #

        self._documents: list[Document] = []

        self._chunks: list[Chunk] = []

        self._embeddings = None

        self._lock = Lock()

    def initialize(self) -> None:
        """
        Build the retrieval index.
        """

        with self._lock:
            plan = self._index_manager.detect_changes()
            print(plan)

            if self._index_manager.exists():
                result = self._index_manager.load()
            else:
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

        query_embedding = self._embedding_manager.embed_query(
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

        # Context compression
        compressed_result = self.context_compressor.compress(query, results)

        return compressed_result