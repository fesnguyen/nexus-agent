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

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


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

@dataclass(slots=True)
class Chunk:
    """
    Represents one chunk of text.

    Later this will become retrieval/schema.py.
    """

    id: str

    source: Path

    text: str

    chunk_index: int


@dataclass(slots=True)
class SearchResult:
    """
    Retrieval result.

    Returned by retrieve().
    """

    chunk: Chunk

    score: float


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
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:

        self._embedding_model_name = embedding_model

        self._chunk_size = chunk_size

        self._chunk_overlap = chunk_overlap

        #
        # Components
        #
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self._embedder = SentenceTransformer(
            embedding_model
        )

        #
        # Runtime state
        #
        self._chunks: list[Chunk] = []

        self._index: faiss.Index | None = None

        self._embeddings: np.ndarray | None = None


    # =========================================================================
    # Knowledge Loading
    # =========================================================================

    def load_knowledge(self) -> None:
        """
        Load every markdown file from the knowledge directory.

        Pipeline
        --------
        knowledge/
              ↓
        Read markdown files
              ↓
        Chunk each document
              ↓
        Store chunks in memory

        This method does NOT generate embeddings.
        """

        self._chunks.clear()

        markdown_files = sorted(
            KNOWLEDGE_DIR.rglob("*.md")
        )

        if not markdown_files:
            print("[RAG] No markdown files found.")
            return

        print(f"[RAG] Loading {len(markdown_files)} markdown file(s)...")

        for path in markdown_files:
            self._load_markdown_file(path)

        print(f"[RAG] Loaded {len(self._chunks)} chunk(s).")

    def _load_markdown_file(
        self,
        path: Path,
    ) -> None:
        """
        Read a single markdown file and split it into chunks.
        """

        text = path.read_text(
            encoding="utf-8"
        )

        pieces = self._splitter.split_text(text)

        self._build_chunks(
            source=path,
            pieces=pieces,
        )

    def _build_chunks(
        self,
        source: Path,
        pieces: list[str],
    ) -> None:
        """
        Convert text pieces into Chunk objects.
        """

        for index, text in enumerate(pieces):

            chunk = Chunk(
                id=f"{source.stem}_{index}",
                source=source,
                text=text,
                chunk_index=index,
            )

            self._chunks.append(chunk)


    # =========================================================================
    # Embedding
    # =========================================================================

    def _get_embedder(self) -> SentenceTransformer:
        """
        Lazily load the embedding model.

        The model is only loaded when embeddings are actually needed.
        This makes knowledge loading much faster.
        """

        if self._embedder is None:
            print(f"[RAG] Loading embedding model: {self._embedding_model_name}")

            self._embedder = SentenceTransformer(
                self._embedding_model_name
            )

        return self._embedder

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

        embedder = self._get_embedder()

        print(
            f"[RAG] Embedding {len(self._chunks)} chunk(s)..."
        )

        texts = [
            chunk.text
            for chunk in self._chunks
        ]

        embeddings = embedder.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        self._embeddings = embeddings.astype(
            np.float32
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


    def _embed_query(
        self,
        query: str,
    ) -> np.ndarray:
        """
        Generate an embedding for a user query.
        """

        embedder = self._get_embedder()

        embedding = embedder.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.astype(
            np.float32
        ).reshape(1, -1)


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

        query_embedding = self._embed_query(
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

        return results



if __name__ == "__main__":

    rag = RAGService()

    rag.load_knowledge()

    rag.embed_chunks()

    rag.build_index()

    print()

    results = rag.retrieve(
        "What is LangGraph?"
    )

    for result in results:

        print("=" * 80)

        print(
            f"Score: {result.score:.4f}"
        )

        print(result.chunk.source)

        print()

        print(result.chunk.text[:300])