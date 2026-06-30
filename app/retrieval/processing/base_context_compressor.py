"""
Base context compressor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.retrieval.schema import SearchResult


class BaseContextCompressor(ABC):
    """
    Base class for context compressors.
    """

    @abstractmethod
    def compress(
        self,
        query: str,
        results: list[SearchResult],
    ) -> str:
        """
        Compress retrieved search results into a smaller context.
        """
        raise NotImplementedError