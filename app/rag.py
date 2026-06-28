"""
app/rag.py

===============================================================================
Nexus Retrieval-Augmented Generation (RAG) Service
===============================================================================

This module starts as a single-file implementation.

The goal is NOT to keep everything in one file forever.
The goal is to build a complete, working RAG pipeline first.

Evolution roadmap:

Version 1
---------
One file containing:
    - Knowledge loading
    - Chunking
    - Embedding
    - FAISS indexing
    - Retrieval

Version 2
---------
Split into modules:

retrieval/
    loader.py
    chunker.py
    embedder.py
    vector_store.py
    retriever.py

Version 3
---------
Introduce persistence:
    - SQLite metadata
    - FAISS persistence
    - Incremental indexing

Version 4
---------
Production features:
    - Query rewriting
    - Hybrid retrieval
    - Re-ranking
    - Context compression

The public API should remain stable:

    rag = RAGService()
    rag.build_index()
    context = rag.retrieve(query)

The rest of Nexus should never need to know how retrieval works internally.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.retrieval.processing.embedder import Embedder

from app.retrieval.ingestion.loader import Loader
from app.retrieval.processing.chunker import Chunker


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

VECTORSTORE_DIR = PROJECT_ROOT / "app" / "vectorstore"

VECTORSTORE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =============================================================================
# Internal Data Models
# =============================================================================

from app.retrieval.ingestion.parser import Parser
from app.retrieval.schema import (
    Chunk,
    Document,
    SearchResult
)


# =============================================================================
# Main RAG Service
# =============================================================================

class RAGService:
    """
    Retrieval service for Nexus.

    Responsibilities
    ----------------
    - Load markdown files
    - Chunk documents
    - Generate embeddings
    - Build FAISS index
    - Retrieve relevant chunks

    Non-responsibilities
    --------------------
    - LLM generation
    - Conversation memory
    - Tool calling
    - Agent workflow
    """

    def __init__(
        self,
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        chunk_size: int = 1500, # ~ 250 tokens
        chunk_overlap: int = 300, # ~ 50 tokens overlap at the end of each chunk
    ) -> None:
        
        self._chunk_size = chunk_size

        self._chunk_overlap = chunk_overlap

        #
        # Components
        #

        self._embedder = Embedder(
            model_name=embedding_model,
        )

        #
        # Runtime state
        #

        self._index: faiss.Index | None = None

        self._embeddings: np.ndarray | None = None

        self._loader = Loader(
            knowledge_dir=KNOWLEDGE_DIR,
            parser=Parser(),
        )

        self._chunker = Chunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self._documents: list[Document] = []
        self._chunks: list[Chunk] = []


    # =========================================================================
    # Knowledge Loading
    # =========================================================================

    def load_knowledge(self) -> None:
        """
        Load and chunk every supported document from the knowledge directory.

        Pipeline
        --------
        knowledge/
            ↓
        Loader
            ↓
        Parser
            ↓
        Document
            ↓
        Chunker
            ↓
        Chunk
        """

        print("[RAG] Loading knowledge...")

        self._documents = self._loader.load()

        self._chunks = self._chunker.chunk_documents(
            self._documents
        )

        print(
            f"[RAG] Loaded {len(self._documents)} document(s)."
        )

        print(
            f"[RAG] Generated {len(self._chunks)} chunk(s)."
        )

    def embed_chunks(self) -> None:
        """
        Generate embeddings for every chunk.

        Pipeline
        --------
        Chunk
            ↓
        Sentence Transformer
            ↓
        Embedding Matrix

        Result
        ------
        self._embeddings

        Shape:

            (num_chunks, embedding_dimension)
        """

        if not self._chunks:
            raise RuntimeError(
                "Knowledge has not been loaded."
            )
        
        print(
            f"[RAG] Embedding {len(self._chunks)} chunk(s)..."
        )

        self._embeddings = self._embedder.embed(
            self._chunks
        )

        print(
            f"[RAG] Embedding shape: {self._embeddings.shape}"
        )


    # =========================================================================
    # FAISS
    # =========================================================================

    def build_index(self) -> None:
        """
        Build an in-memory FAISS index.

        Pipeline
        --------
        Embedding Matrix
              ↓
        FAISS IndexFlatIP
              ↓
        Ready for retrieval
        """

        if self._embeddings is None:
            raise RuntimeError(
                "Embeddings have not been generated."
            )

        dimension = self._embeddings.shape[1]

        print(
            f"[RAG] Building FAISS index ({dimension} dimensions)..."
        )

        #
        # Since embeddings are already normalized,
        # inner product == cosine similarity.
        #
        self._index = faiss.IndexFlatIP(
            dimension
        )

        self._index.add(
            self._embeddings
        )

        print(
            f"[RAG] Indexed {self._index.ntotal} chunk(s)."
        )
        
    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[SearchResult]:
        """
        Retrieve the k most relevant chunks.
        """

        if self._index is None:
            raise RuntimeError(
                "Index has not been built."
            )
        
        # =========================================================================
        # Query rewrite:
        # LLM rewrite, HyDE (Hypothetical Document Embeddings, 
        # Multi-query generation, History-aware rewriting), 
        # =========================================================================

        query_embedding = self._embedder.embed_query(
            query
        )

        scores, indices = self._index.search(
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

        # =========================================================================
        # Hybrid Retrieval:
        # bm25 + Faiss
        # =========================================================================

        # =========================================================================
        # Re-ranker:
        # Select 20 chunks -> rerank
        # =========================================================================

        return results



if __name__ == "__main__":

    # =========================================================================
    # Incremental Indexing ⭐⭐⭐:
    # File changed -> rebuild that file only
    # =========================================================================

    rag = RAGService()

    rag.load_knowledge()

    rag.embed_chunks()

    # =========================================================================
    # Multi-source Retrieval ⭐⭐⭐:
    # Retrievel from multiple sources
    # =========================================================================

    rag.build_index()

    print()

    # =========================================================================
    # Metadata Filtering:
    # Handle large number of files, reduce noise
    # =========================================================================

    # =========================================================================
    # Parent Document Retrieval:
    # Retrieve nearby chunks (Intuitively, and proofully a MUST)
    # =========================================================================

    # =========================================================================
    # Multi-Vector Retrieval ⭐⭐:
    # embed title, heading, body, summary
    # =========================================================================

    # =========================================================================
    # Caching ⭐⭐⭐:
    # Cache query embedding and retrieval result
    # =========================================================================

    results = rag.retrieve(
        "How to finetune large language model using Unsloth?"
    )

    # =========================================================================
    # Context compression:
    # 1000 to 80 tokens is ideal :D
    # =========================================================================

    for result in results:

        print("=" * 80)

        print(
            f"Score: {result.score:.4f}"
        )

        print(result.chunk.source)

        print()

        print(result.chunk.text[:300])