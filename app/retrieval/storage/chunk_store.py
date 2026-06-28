"""
Chunk store.

Responsibilities
----------------
Persist and retrieve chunks.

This class is the source of truth for retrievable content.

It intentionally knows nothing about:

- FAISS
- Embeddings
- Similarity search
- Indexing workflow
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.retrieval.schema import Chunk


class ChunkStore:
    """
    SQLite storage for chunks.
    """

    def __init__(
        self,
        database: Path,
    ) -> None:

        self._database = database

        self._initialize()

    def add(
        self,
        chunk: Chunk,
    ) -> None:
        """
        Insert or replace a chunk.
        """

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                INSERT OR REPLACE INTO chunks
                (
                    id,
                    source,
                    chunk_index,
                    text,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    chunk.id,
                    str(chunk.source),
                    chunk.chunk_index,
                    chunk.text,
                    json.dumps(chunk.metadata),
                ),
            )

            connection.commit()

    def add_many(
        self,
        chunks: list[Chunk],
    ) -> None:
        """
        Insert multiple chunks.
        """

        with sqlite3.connect(self._database) as connection:

            connection.executemany(
                """
                INSERT OR REPLACE INTO chunks
                (
                    id,
                    source,
                    chunk_index,
                    text,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.id,
                        str(chunk.source),
                        chunk.chunk_index,
                        chunk.text,
                        json.dumps(chunk.metadata),
                    )
                    for chunk in chunks
                ],
            )

            connection.commit()

    def get(
        self,
        chunk_id: str,
    ) -> Chunk | None:

        with sqlite3.connect(self._database) as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    source,
                    chunk_index,
                    text,
                    metadata
                FROM chunks
                WHERE id = ?
                """,
                (chunk_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return Chunk(
            id=row[0],
            source=Path(row[1]),
            chunk_index=row[2],
            text=row[3],
            metadata=json.loads(row[4]),
        )

    def list(
        self,
    ) -> list[Chunk]:

        with sqlite3.connect(self._database) as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    source,
                    chunk_index,
                    text,
                    metadata
                FROM chunks
                ORDER BY source, chunk_index
                """
            )

            rows = cursor.fetchall()

        return [
            Chunk(
                id=row[0],
                source=Path(row[1]),
                chunk_index=row[2],
                text=row[3],
                metadata=json.loads(row[4]),
            )
            for row in rows
        ]

    def find_by_source(
        self,
        source: Path,
    ) -> list[Chunk]:

        with sqlite3.connect(self._database) as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    source,
                    chunk_index,
                    text,
                    metadata
                FROM chunks
                WHERE source = ?
                ORDER BY chunk_index
                """,
                (str(source),),
            )

            rows = cursor.fetchall()

        return [
            Chunk(
                id=row[0],
                source=Path(row[1]),
                chunk_index=row[2],
                text=row[3],
                metadata=json.loads(row[4]),
            )
            for row in rows
        ]

    def delete(
        self,
        chunk_id: str,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                DELETE FROM chunks
                WHERE id = ?
                """,
                (chunk_id,),
            )

            connection.commit()

    def delete_by_source(
        self,
        source: Path,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                DELETE FROM chunks
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
                DELETE FROM chunks
                """
            )

            connection.commit()

    def _initialize(
        self,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks
                (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

            connection.commit()