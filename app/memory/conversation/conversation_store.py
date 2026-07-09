"""
Conversation SQLite repository.
"""

from __future__ import annotations

from app.memory.conversation.conversation_schemas import Message
import sqlite3
from pathlib import Path
from typing import TypeVar

from pydantic import TypeAdapter

from app.api.schemas.conversation import Conversation, ConversationSummary


CREATE_CONVERSATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
"""


CREATE_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    conversation_id TEXT NOT NULL,

    role TEXT NOT NULL,

    type TEXT NOT NULL,

    content TEXT default '',

    created_at TIMESTAMP NOT NULL,

    FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);
"""

TRIGGER_UPDATE_CONVERSATION_UPDATED_AT = """
CREATE TRIGGER IF NOT EXISTS update_conversation_updated_at
AFTER INSERT ON messages
BEGIN
    UPDATE conversations
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.conversation_id;
END;
"""


class ConversationStore:
    """
    Repository responsible for persisting conversations and messages.

    This class contains database operations only.
    """

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------

    T = TypeVar("T")

    def _model(self, model: type[T], row: sqlite3.Row) -> T:
        """
        Convert a SQLite row into a validated Pydantic model.
        """
        return model.model_validate(dict(row))
    
    def _models(
        self,
        adapter: TypeAdapter[list[T]],
        rows: list[sqlite3.Row],
    ) -> list[T]:
        """
        Convert SQLite rows into a validated list of Pydantic models using
        a cached TypeAdapter for efficient bulk validation.
        """
        return adapter.validate_python(
            [dict(row) for row in rows]
        )
    
    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def __init__(
        self,
        db_path: str | Path,
    ):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

        self._conversation_summary_adapter = TypeAdapter(
            list[ConversationSummary]
        )

        self._message_adapter = TypeAdapter(
            list[Message]
        )

    def _connect(self) -> sqlite3.Connection:

        connection = sqlite3.connect(self.db_path)

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def _initialize(
        self,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                CREATE_CONVERSATIONS_TABLE
            )

            connection.execute(
                CREATE_MESSAGES_TABLE
            )

            connection.execute(
                TRIGGER_UPDATE_CONVERSATION_UPDATED_AT
            )

            connection.commit()

    # ------------------------------------------------------------------
    # Conversation
    # ------------------------------------------------------------------

    def create_conversation(
        self,
        conversation_id: str,
        title: str,
        created_at: str,
        updated_at: str,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO conversations (
                    id,
                    title,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    title,
                    created_at,
                    updated_at,
                ),
            )

            connection.commit()

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT *
                FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            ).fetchone()

            if cursor is None:
                return None

            return Conversation(
                id=cursor["id"],
                title=cursor["title"],
                created_at=cursor["created_at"],
                updated_at=cursor["updated_at"],
            )

    def list_conversations(
        self,
    ) -> list[Conversation]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM conversations
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [
            Conversation(
                id=row["id"],
                title=row["title"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def rename_conversation(
        self,
        conversation_id: str,
        title: str,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                UPDATE conversations
                SET title = ?
                WHERE id = ?
                """,
                (
                    title,
                    conversation_id,
                ),
            )

            connection.commit()

    def delete_conversation(
        self,
        conversation_id: str,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                DELETE FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            )

            connection.commit()

    # ------------------------------------------------------------------
    # Message
    # ------------------------------------------------------------------

    def append_message(
        self,
        conversation_id: str,
        role: str,
        type: str,
        content: str,
        created_at: str,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO messages (
                    conversation_id,
                    role,
                    type,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    role,
                    type,
                    content,
                    created_at,
                ),
            )

            connection.commit()

    def get_messages(
        self,
        conversation_id: str,
    ) -> list[sqlite3.Row]:

        with self._connect() as connection:

            cursor = connection.execute(
                """
                SELECT *
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            )

            return list(cursor.fetchall())

    def get_chat_messages(
        self,
        conversation_id: str,
    ) -> list[sqlite3.Row]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM messages
                WHERE conversation_id = ?
                AND type = 'chat'
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()

            return [
                Message(
                    id=row["id"],
                    conversation_id=row["conversation_id"],
                    role=row["role"],
                    type=row["type"],
                    content=row["content"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]