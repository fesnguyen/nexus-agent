"""
Conversation API.
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.api.schemas.api_conversation_schema import (
    ConversationResponse,
    ConversationsResponse,
)

router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.get("")
async def get_conversations(
    request: Request,
) -> ConversationsResponse:
    """
    Return all conversations together with the active conversation.
    """

    conversation_use_case = request.app.state.application.conversation

    return conversation_use_case.get_conversations()


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    request: Request,
) -> ConversationResponse:
    """
    Return a conversation and all of its messages.
    """

    conversation_use_case = request.app.state.application.conversation

    return conversation_use_case.get_conversation(
        conversation_id,
    )