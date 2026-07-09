"""
Conversation service.
"""

from __future__ import annotations
import dataclasses

from app.api.schemas.conversation import (
    Conversation,
    ConversationResponse,
    ConversationsResponse,
)
from app.memory.conversation.conversation_service import ConversationService


class ConversationUseCase:
    """
    Business logic for conversation management.

    Responsible for:
    - Loading conversations
    - Loading a single conversation
    """

    def __init__(
        self,
        conversation_service: ConversationService,
    ) -> None:
        self._conversation_service = conversation_service

    def get_conversations(self) -> ConversationsResponse:
        """
        Return all conversations together with the active conversation.

        This endpoint is used when the application starts so the frontend
        can initialize both the sidebar and chat view with a single request.
        """

        conversations = self._conversation_service.list_conversations()

        active_conversation = None

        if conversations:
            active_conversation = self._conversation_service.get_conversation(
                conversations[0].id,
            )
        
        response_items = [
            Conversation(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                messages=(
                    # Map dataclass object to Pydantic object
                    [dataclasses.asdict(m) for m in active_conversation.messages]
                    if active_conversation and active_conversation.id == c.id
                    else []
                ),
            )
            for c in conversations
        ]

        return ConversationsResponse(
            items=response_items
        )

    def get_conversation(
        self,
        conversation_id: str,
    ) -> ConversationResponse:
        """
        Return a conversation and all of its messages.
        """

        conversation = self._conversation_service.get_conversation(
            conversation_id,
        )

        return ConversationResponse(
            data=conversation,
        )