"""
Chat API
"""

from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, Form
from langchain_core.messages import HumanMessage
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

    message = payload.messages[-1]

    workflow = request.app.state.workflow

    # Multimodal model later
    # images = []
    # if image is not None:
    #     images.append(Image.open(image.file))

    state = {
        "messages": [
            HumanMessage(
                content=message.content,
            )
        ],
        "images": None,
    }

    result = workflow.invoke(state)

    return ChatResponse(content=result['messages'][-1].content)