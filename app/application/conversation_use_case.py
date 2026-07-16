"""
Conversation service.
"""

from __future__ import annotations
import dataclasses

# use_case only access to api schemas, not application schemas
from app.api.schemas.api_conversation_schemas import (
    ConversationDTO,
    ConversationResponseDTO,
    ConversationsResponseDTO,
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

    def get_conversations(self) -> ConversationsResponseDTO:
        """
        Return all conversations together with the active conversation' messages.

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
            ConversationDTO(
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

        return ConversationsResponseDTO(
            items=response_items
        )

    def get_conversation(
        self,
        conversation_id: str,
    ) -> ConversationResponseDTO:
        """
        Return a single conversation with its messages.

        Used when use swap conversation
        """

        conversation = self._conversation_service.get_conversation(
            conversation_id,
        )

        dto_data = ConversationDTO.model_validate(conversation)

        return ConversationResponseDTO(
            data=dto_data,
        )