"""
Knowledge loader.

Responsibilities
----------------
- Discover supported knowledge files.
- Delegate parsing to the parser.
- Return a list of Document objects.

This module intentionally does NOT perform:

- Chunking
- Embedding
- Indexing
- Vector storage

Pipeline
--------
knowledge/
      │
      ▼
Loader
      │
      ▼
Parser
      │
      ▼
Document
"""

from __future__ import annotations

from pathlib import Path

from app.retrieval.ingestion.parser import Parser
from app.retrieval.schema import Document


class Loader:
    """
    Load every supported document from the knowledge base.
    """

    def __init__(
        self,
        knowledge_dir: Path,
        parser: Parser,
    ) -> None:
        self._knowledge_dir = knowledge_dir
        self._parser = parser

    def load(self) -> list[Document]:
        """
        Load all supported documents.

        Returns
        -------
        list[Document]
        """

        documents: list[Document] = []

        for path in self._discover_files():

            document = self._parser.parse(path)

            documents.append(document)

        return documents

    def _discover_files(self) -> list[Path]:
        """
        Discover every supported file recursively.
        """

        files: list[Path] = []

        for extension in self._parser.supported_extensions:

            files.extend(
                self._knowledge_dir.rglob(f"*{extension}")
            )

        return sorted(files)