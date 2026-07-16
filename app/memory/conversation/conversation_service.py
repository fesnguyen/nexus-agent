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

from app.memory.conversation.application_conversation_schemas import ( 
    Attachment,
    Conversation
)
from app.memory.conversation.conversation_store import ConversationStore


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

    def create_conversation_if_not_exist(
        self,
        conversation_id: str,
        title: str,
    ) -> None:
        """
        Insert new conversation into sqlite db, do nothing if already exist
        """

        now = datetime.now(UTC).isoformat()

        self.store.create_conversation_if_not_exist(
            conversation_id=conversation_id,
            title=title,
            created_at=now,
            updated_at=now,
        )

    def list_conversations(self):
        """Simply load all conversations, no messages"""
        return self.store.list_conversations()

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation:
        """Get Conversation and its messages/attachments by id"""
        conversation = self.store.get_conversation(
            conversation_id,
        )
        if conversation is not None:
            conversation.messages = self.store.get_chat_messages(
                conversation_id
            )

        

        return conversation

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
        attachments: list[Attachment] | None = None
    ) -> None:
        """
        Persist a user message.

        Attachments are stored separately in the attachments table.
        """

        message_id = self._append_message(
            conversation_id=conversation_id,
            role="user",
            type="chat",
            content=content,
        )

        self.store.append_attachments(
            message_id=message_id,
            attachments=attachments,
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
    ) -> int:

        return self.store.append_message(
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
        """
        Base on the historical messages from db, rebuild the chat history
        Assistant role message need to include "thought", "response" and "tool_calls"
        to make its behaviours consistent
        """

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
                            # Need message_id to map attachments
                            additional_kwargs={
                                "message_id": row["id"],
                            },
                        )
                    )

                case ("assistant", "chat"):
                    history.append(
                        AIMessage(
                            content=json.dumps(
                                {
                                    "thought": "Ignored",
                                    "response": row["content"],
                                    "tool_calls": [],
                                }
                            )
                        )
                    )

                case ("assistant", "tool_call"):
                    history.append(
                        AIMessage(
                            # Persistent tool message to avoid model hallucination
                            content=json.dumps(
                                {
                                    "thought": "Ignored",
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
    

    def get_conversation_attachments(
        self,
        conversation_id: str,
    ) -> list[Attachment]:
        """
        Return all attachments belonging to a conversation.
        """

        rows = self.store.get_attachments_by_conversation_id(
            conversation_id,
        )

        return [
            Attachment(
                id=row["id"],
                message_id=row["message_id"],
                type=row["type"],
                storage_path=row["storage_path"],
                mime_type=row["mime_type"],
                extracted_content=json.loads(
                    row["extracted_content"]
                ),
                created_at=row["created_at"],
            )
            for row in rows
        ]