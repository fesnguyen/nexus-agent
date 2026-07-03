"""
Conversation service.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.memory.conversation_store import ConversationStore


class ConversationService:
    """
    Business logic for conversation management.

    Responsible for:
    - Conversation CRUD
    - Persisting messages
    - Reconstructing LangChain history
    - Returning UI chat history

    Not responsible for:
    - Workflow execution
    - LLM inference
    """

    def __init__(
        self,
        store: ConversationStore,
    ):
        self.store = store

    # ------------------------------------------------------------------
    # Conversation
    # ------------------------------------------------------------------

    def create_conversation(
        self,
        conversation_id: str,
        title: str,
    ) -> None:

        now = datetime.now(UTC).isoformat()

        self.store.create_conversation(
            conversation_id=conversation_id,
            title=title,
            created_at=now,
            updated_at=now,
        )

    def list_conversations(self):
        return self.store.list_conversations()

    def get_conversation(
        self,
        conversation_id: str,
    ):
        return self.store.get_conversation(
            conversation_id,
        )

    def rename_conversation(
        self,
        conversation_id: str,
        title: str,
    ) -> None:

        self.store.rename_conversation(
            conversation_id,
            title,
        )

    def delete_conversation(
        self,
        conversation_id: str,
    ) -> None:

        self.store.delete_conversation(
            conversation_id,
        )

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def save_user_message(
        self,
        conversation_id: str,
        content: str,
    ) -> None:

        self._append_message(
            conversation_id=conversation_id,
            role="user",
            type="chat",
            content=content,
        )

    def save_tool_call(
        self,
        conversation_id: str,
        tool_call,
    ) -> None:

        self._append_message(
            conversation_id=conversation_id,
            role="assistant",
            type="tool_call",
            content=json.dumps(tool_call),
        )

    def save_tool_result(
        self,
        conversation_id: str,
        content: str,
    ) -> None:

        self._append_message(
            conversation_id=conversation_id,
            role="tool",
            type="tool_result",
            content=content,
        )

    def save_assistant_response(
        self,
        conversation_id: str,
        response: str,
    ) -> None:

        self._append_message(
            conversation_id=conversation_id,
            role="assistant",
            type="chat",
            content=response,
        )

    def _append_message(
        self,
        conversation_id: str,
        role: str,
        type: str,
        content: str,
    ) -> None:

        self.store.append_message(
            conversation_id=conversation_id,
            role=role,
            type=type,
            content=content,
            created_at=datetime.now(UTC).isoformat(),
        )

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def build_history(
        self,
        conversation_id: str,
    ) -> list[BaseMessage]:

        history: list[BaseMessage] = []

        rows = self.store.get_messages(
            conversation_id,
        )

        for row in rows:

            match (row["role"], row["type"]):

                case ("system", _):
                    history.append(
                        SystemMessage(
                            content=row["content"],
                        )
                    )

                case ("user", _):
                    history.append(
                        HumanMessage(
                            content=row["content"],
                        )
                    )

                case ("assistant", "chat"):
                    history.append(
                        AIMessage(
                            content=json.dumps(
                                {
                                    "response": row["content"],
                                    "tool_calls": [],
                                }
                            )
                        )
                    )

                case ("assistant", "tool_call"):
                    history.append(
                        AIMessage(
                            content=json.dumps(
                                {
                                    "response": "",
                                    "tool_calls": [
                                        json.loads(row["content"])
                                    ],
                                }
                            ),
                            tool_calls=[
                                json.loads(row["content"])
                            ],
                        )
                    )

                case ("tool", "tool_result"):
                    history.append(
                        ToolMessage(
                            content=row["content"],
                            tool_call_id="",
                        )
                    )

                case _:
                    raise ValueError(
                        f"Unknown message type: {row['role']} / {row['type']}"
                    )

        return history

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def get_chat_messages(
        self,
        conversation_id: str,
    ):

        return self.store.get_chat_messages(
            conversation_id,
        )