"""
Embedding-based context compressor.

Workflow
--------
SearchResult
        │
        ▼
Split chunk into sentences
        │
        ▼
Embed every sentence
        │
        ▼
Embed query
        │
        ▼
Cosine similarity
        │
        ▼
Top-N sentences
        │
        ▼
Compressed context
"""

from __future__ import annotations

import re

import numpy as np
from sentence_transformers import SentenceTransformer

from app.retrieval.processing.base_context_compressor import (
    BaseContextCompressor,
)
from app.retrieval.schema import SearchResult


class EmbeddingContextCompressor(BaseContextCompressor):

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        top_k_sentences: int = 8,
    ) -> None:

        self._embedder = SentenceTransformer(
            model_name
        )

        self._top_k_sentences = top_k_sentences

    def compress(
        self,
        query: str,
        results: list[SearchResult],
    ) -> str:

        sentences: list[str] = []

        # Segment the retrieved text chunk into individual sentences
        for result in results:
            sentences.extend(
                self._split_sentences(
                    result.chunk.text
                )
            )

        if not sentences:
            return ""

        # Compute normalized vector embeddings for all extracted sentences
        sentence_embeddings = self._embedder.encode(
            sentences,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # Compute a normalized vector embedding for the user's query
        query_embedding = self._embedder.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # Calculate cosine similarity scores via dot product of normalized vectors
        scores = np.dot(
            sentence_embeddings,
            query_embedding,
        )

        # Get the indices of the top-K highest scoring sentences
        indices = np.argsort(
            scores
        )[::-1][: self._top_k_sentences]

        # Sort selected indices to preserve the sentences' original narrative order
        selected = [
            sentences[i]
            for i in sorted(indices)
        ]

        return "\n\n".join(selected)

    def _split_sentences(
        self,
        text: str,
    ) -> list[str]:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]