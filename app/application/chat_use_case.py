"""
Chat service.
"""

from __future__ import annotations
import os
import shutil
import uuid

from fastapi import File, UploadFile

from app.api.schemas.conversation import Conversation
from app.memory.conversation.conversation_service import ConversationService
from app.utils import extract_user_message
from configs.agent_settings import CHAT_IMAGES_DIR


class ChatUseCase:
    """
    Application service responsible for processing chat requests.
    """

    def __init__(
        self,
        workflow,
        conversation_service: ConversationService,
    ):
        self.workflow = workflow
        self.conversation_service = conversation_service
        os.makedirs(CHAT_IMAGES_DIR, exist_ok=True)

    def chat(
        self,
        conversation_id: str,
        message: str,
        attachments: list[UploadFile] = File([]),
    ) -> tuple[str, list[str]]:
        """
        Process a single chat message.
        """

        # Ensure conversation exists
        conversation = self.conversation_service.get_conversation(
            conversation_id,
        )

        if conversation is None:

            self.conversation_service.create_conversation(
                conversation_id=conversation_id,
                title=message[:40] if message else "New Conversation",
            )

        image_urls = []
        if attachments:
            for attachment in attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    img_url = self.save_image_attachment(attachment)
                    image_urls.append(img_url)

        # Persist user message here since user message belong to service, not agent
        self.conversation_service.save_user_message(
            conversation_id=conversation_id,
            content=message,
            image_urls=image_urls
        )

        # Load complete history
        history = self.conversation_service.build_history(
            conversation_id=conversation_id,
        )

        state = {
            # conversation_id will be a mark of appending handle message to db
            "conversation_id": conversation_id,
            "messages": history,
        }

        # Invoke workflow
        assistant_response = self.workflow.invoke(state)

        return assistant_response["messages"][-1].content
    

    def save_image_attachment(self, file: UploadFile) -> str:
        """Saves the image locally and returns the relative path/URL."""
        # Generate a unique filename to prevent collisions
        ext = os.path.splitext(file.filename)[1] or ".png"
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(CHAT_IMAGES_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return file_path