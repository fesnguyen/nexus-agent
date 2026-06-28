"""
Vector mapping store.

Responsibilities
----------------
Persist mappings between chunks and vector IDs.

This decouples the retrieval layer from a specific vector database.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class VectorMapping:
    """
    Mapping between a chunk and a vector.
    """

    chunk_id: str
    vector_store: str
    embedding_model: str
    vector_id: int


class MappingStore:
    """
    SQLite storage for vector mappings.
    """

    def __init__(
        self,
        database: Path,
    ) -> None:

        self._database = database

        self._initialize()

    def add(
        self,
        mapping: VectorMapping,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                INSERT OR REPLACE INTO vector_mappings
                (
                    chunk_id,
                    vector_store,
                    embedding_model,
                    vector_id
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    mapping.chunk_id,
                    mapping.vector_store,
                    mapping.embedding_model,
                    mapping.vector_id,
                ),
            )

            connection.commit()

    def get_by_chunk(
        self,
        chunk_id: str,
    ) -> VectorMapping | None:

        with sqlite3.connect(self._database) as connection:

            cursor = connection.execute(
                """
                SELECT
                    chunk_id,
                    vector_store,
                    embedding_model,
                    vector_id
                FROM vector_mappings
                WHERE chunk_id = ?
                """,
                (chunk_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return VectorMapping(*row)

    def get_by_vector(
        self,
        vector_id: int,
    ) -> VectorMapping | None:

        with sqlite3.connect(self._database) as connection:

            cursor = connection.execute(
                """
                SELECT
                    chunk_id,
                    vector_store,
                    embedding_model,
                    vector_id
                FROM vector_mappings
                WHERE vector_id = ?
                """,
                (vector_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return VectorMapping(*row)

    def delete(
        self,
        chunk_id: str,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                DELETE FROM vector_mappings
                WHERE chunk_id = ?
                """,
                (chunk_id,),
            )

            connection.commit()

    def clear(
        self,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                DELETE FROM vector_mappings
                """
            )

            connection.commit()

    def _initialize(
        self,
    ) -> None:

        with sqlite3.connect(self._database) as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_mappings
                (
                    chunk_id TEXT PRIMARY KEY,
                    vector_store TEXT NOT NULL,
                    embedding_model TEXT NOT NULL,
                    vector_id INTEGER NOT NULL
                )
                """
            )

            connection.commit()