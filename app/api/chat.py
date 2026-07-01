"""
Chat API
"""

from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, Form
from langchain_core.messages import HumanMessage
from PIL import Image


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

@router.post("")
async def chat(
    request: Request,
    message: str = Form(...),
    image: UploadFile | None = File(default=None),
):
    """
    Chat with Nexus.
    """

    workflow = request.app.state.workflow

    images = []

    if image is not None:
        images.append(Image.open(image.file))

    state = {
        "messages": [
            HumanMessage(
                content=message,
            )
        ],
        "images": images,
    }

    result = workflow.invoke(state)

    return {
        "response": result["response"],
    }