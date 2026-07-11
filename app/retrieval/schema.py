"""
Core data models for the retrieval subsystem.

These models are shared across the entire RAG pipeline.

Pipeline
--------
Knowledge File
    ↓
Document
    ↓
Chunk
    ↓
Embedding
    ↓
Vector Search
    ↓
SearchResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from app.retrieval.storage.file_index_store import IndexedFile


@dataclass(slots=True)
class Document:
    """
    A document loaded from the knowledge base.

    This is the output of the ingestion layer before chunking.
    """

    source: Path

    text: str

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Chunk:
    """
    A chunk generated from a document.

    Each chunk represents the smallest retrievable unit.
    """

    id: str

    source: Path

    text: str

    chunk_index: int

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IndexedChunk:
    """
    A chunk together with its embedding.

    Produced by the embedding stage before indexing.
    """

    chunk: Chunk

    embedding: np.ndarray


@dataclass(slots=True)
class SearchResult:
    """
    Result returned by a retriever.
    """

    chunk: Chunk

    score: float


@dataclass(slots=True)
class SyncPlan:
    added: list[Document]
    modified: list[Document]
    deleted: list[IndexedFile]