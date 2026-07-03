"""
Chat API
"""

from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, Form
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from PIL import Image

from app.api.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

@router.post("")
async def chat(
    request: Request,
    payload: ChatRequest,
) -> ChatResponse:
    """
    Chat with Nexus.
    """

    chat_service = request.app.state.chat_service

    response = chat_service.chat(
        conversation_id=payload.conversation_id,
        message=payload.message,
    )

    return ChatResponse(
        content=response,
    )