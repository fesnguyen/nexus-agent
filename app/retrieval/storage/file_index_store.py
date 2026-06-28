"""
File index store.

Responsibilities
----------------
Persist indexing state for each source document.

This store is used to determine whether a document
needs to be re-indexed.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class IndexedFile:
    """
    Indexing information for one source file.
    """

    source: Path
    content_hash: str
    embedding_model: str
    chunk_count: int


class FileIndexStore:
    """
    SQLite storage for indexed files.
    """

    def __init__(
        self,
        database: Path,
    ) -> None:

        self._database = database

        self._initialize()

    def add(
        self,
        indexed_file: IndexedFile,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                INSERT OR REPLACE INTO indexed_files
                (
                    source,
                    content_hash,
                    embedding_model,
                    chunk_count
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(indexed_file.source),
                    indexed_file.content_hash,
                    indexed_file.embedding_model,
                    indexed_file.chunk_count,
                ),
            )

            connection.commit()

    def get(
        self,
        source: Path,
    ) -> IndexedFile | None:

        with sqlite3.connect(self._database) as connection:

            cursor = connection.execute(
                """
                SELECT
                    source,
                    content_hash,
                    embedding_model,
                    chunk_count
                FROM indexed_files
                WHERE source = ?
                """,
                (str(source),),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return IndexedFile(
            source=Path(row[0]),
            content_hash=row[1],
            embedding_model=row[2],
            chunk_count=row[3],
        )

    def delete(
        self,
        source: Path,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                DELETE FROM indexed_files
                WHERE source = ?
                """,
                (str(source),),
            )

            connection.commit()

    def clear(
        self,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                DELETE FROM indexed_files
                """
            )

            connection.commit()

    @staticmethod
    def compute_hash(
        path: Path,
    ) -> str:
        """
        Compute SHA256 hash of a file.
        """

        return hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

    def _initialize(
        self,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS indexed_files
                (
                    source TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    embedding_model TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL
                )
                """
            )

            connection.commit()