import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.memory.base import BaseMemoryStore
from app.memory.models import Memory
from app.memory.models import MemoryType


class SQLiteMemoryStore(BaseMemoryStore):
    """
    SQLite-backed memory repository.

    Responsibilities:

    - Persist memories
    - Maintain FTS5 index
    - Perform lexical retrieval
    - Return Memory entities

    Does NOT:

    - Generate embeddings
    - Perform reranking
    - Build prompts
    """

    def __init__(
        self,
        db_path: str,
    ) -> None:

        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    # ==================================================
    # Database
    # ==================================================

    def _connection(
        self,
    ) -> sqlite3.Connection:

        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
        )

        conn.row_factory = sqlite3.Row

        return conn

    def _initialize_database(
        self,
    ) -> None:

        with self._connection() as conn:

            # ------------------------------------------
            # Primary memory table
            # ------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (

                    id TEXT PRIMARY KEY,

                    type TEXT NOT NULL,

                    content TEXT NOT NULL,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL
                )
                """
            )

            # ------------------------------------------
            # FTS5 search index
            # ------------------------------------------

            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
                USING fts5(
                    id UNINDEXED,
                    content
                )
                """
            )

            # ------------------------------------------
            # Insert trigger
            # ------------------------------------------

            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS memories_ai
                AFTER INSERT ON memories
                BEGIN

                    INSERT INTO memories_fts(
                        id,
                        content
                    )
                    VALUES (
                        NEW.id,
                        NEW.content
                    );

                END;
                """
            )

            # ------------------------------------------
            # Delete trigger
            # ------------------------------------------

            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS memories_ad
                AFTER DELETE ON memories
                BEGIN

                    DELETE FROM memories_fts
                    WHERE id = OLD.id;

                END;
                """
            )

            # ------------------------------------------
            # Update trigger
            # ------------------------------------------

            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS memories_au
                AFTER UPDATE ON memories
                BEGIN

                    DELETE FROM memories_fts
                    WHERE id = OLD.id;

                    INSERT INTO memories_fts(
                        id,
                        content
                    )
                    VALUES (
                        NEW.id,
                        NEW.content
                    );

                END;
                """
            )

            conn.commit()

    # ==================================================
    # CRUD
    # ==================================================

    def save(
        self,
        memories: list[Memory],
    ) -> None:

        if not memories:
            return

        rows = [
            (
                memory.id,
                memory.type.value,
                memory.content,
                memory.created_at.isoformat(),
                datetime.now(UTC).isoformat(),
            )
            for memory in memories
        ]

        with self._connection() as conn:

            conn.executemany(
                """
                INSERT OR REPLACE INTO memories (

                    id,
                    type,
                    content,
                    created_at,
                    updated_at

                )
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )

            conn.commit()


    def get(
        self,
        memory_id: str,
    ) -> Memory | None:

        with self._connection() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM memories
                WHERE id = ?
                """,
                (memory_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_memory(row)

    def delete(
        self,
        memory_id: str,
    ) -> None:

        with self._connection() as conn:

            conn.execute(
                """
                DELETE FROM memories
                WHERE id = ?
                """,
                (memory_id,),
            )

            conn.commit()

    # ==================================================
    # Search
    # ==================================================

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Memory]:

        with self._connection() as conn:

            rows = conn.execute(
                """
                SELECT
                    m.*
                FROM memories m
                JOIN memories_fts f
                    ON m.id = f.id
                WHERE memories_fts MATCH ?
                ORDER BY bm25(
                    memories_fts
                )
                LIMIT ?
                """,
                (
                    self._format_for_fts(query),
                    limit,
                ),
            ).fetchall()

        return [
            self._row_to_memory(row)
            for row in rows
        ]

    # ==================================================
    # Mapping
    # ==================================================

    def _row_to_memory(
        self,
        row: sqlite3.Row,
    ) -> Memory:

        return Memory(
            id=row["id"],
            type=MemoryType(
                row["type"]
            ),
            content=row["content"],
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                row["updated_at"]
            ),
        )
    
    def _format_for_fts(self, user_input: str) -> str:
        """
        Add double quotes around the input string to ensure it is treated as a single token in FTS.
        """

        if not user_input or not user_input.strip():
            return ""
        escaped_input = user_input.replace('"', '""')
        return f'"{escaped_input}"'