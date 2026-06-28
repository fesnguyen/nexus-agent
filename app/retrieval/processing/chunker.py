"""
Document chunker.

Responsibilities
----------------
- Split documents into smaller chunks.
- Preserve document metadata.
- Generate deterministic chunk IDs.

Input
-----
list[Document]

Output
------
list[Chunk]
"""

from __future__ import annotations

import hashlib
from copy import deepcopy

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.retrieval.schema import Chunk, Document


class Chunker:
    """
    Split documents into retrievable chunks.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
    ) -> None:

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
        )

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Chunk]:
        """
        Chunk multiple documents.
        """

        chunks: list[Chunk] = []

        for document in documents:
            chunks.extend(
                self.chunk_document(document)
            )

        return chunks

    def chunk_document(
        self,
        document: Document,
    ) -> list[Chunk]:
        """
        Chunk a single document.
        """

        pieces = self._splitter.split_text(
            document.text
        )

        chunks: list[Chunk] = []

        for index, text in enumerate(pieces):

            chunks.append(
                Chunk(
                    id=self._generate_chunk_id(
                        document.source,
                        index,
                    ),
                    source=document.source,
                    text=text,
                    chunk_index=index,
                    metadata=deepcopy(
                        document.metadata
                    ),
                )
            )

        return chunks

    @staticmethod
    def _generate_chunk_id(
        source,
        index: int,
    ) -> str:
        """
        Generate a deterministic chunk ID.
        """

        payload = (
            f"{source}:{index}"
        ).encode("utf-8")

        return hashlib.sha256(
            payload
        ).hexdigest()