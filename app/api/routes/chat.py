"""
Chat API
"""

from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, Form
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from PIL import Image

from app.api.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(
    prefix="/api/chat",
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

    chat_use_case = request.app.state.application.chat

    response = chat_use_case.chat(
        conversation_id=payload.conversation_id,
        message=payload.message,
    )

    return ChatResponse(
        content=response,
    )
    