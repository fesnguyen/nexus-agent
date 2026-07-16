"""
Chat API
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, File

from app.api.schemas.api_chat_schema import ChatRequest, ChatResponse


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

@router.post("")
async def chat(
    request: Request,
    payload: ChatRequest = Depends(ChatRequest.as_form)
) -> ChatResponse:
    """
    Chat with Nexus.
    """

    chat_use_case = request.app.state.application.chat

    response = chat_use_case.chat(
        conversation_id=payload.conversation_id,
        message=payload.message,
        attachments=payload.attachments,
    )

    return ChatResponse(
        content=response,
    )
    