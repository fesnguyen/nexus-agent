"""
Chat service.
"""

from __future__ import annotations
from dataclasses import asdict
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import uuid

from fastapi import File, UploadFile

from app.memory.conversation.conversation_service import ConversationService
from app.memory.long_term.memory_ingestion_service import MemoryIngestionService
from app.vision.vision_service import VisionService
from configs.agent_settings import CHAT_IMAGES_DIR


class ChatUseCase:
    """
    Application service responsible for processing chat requests.
    """

    def __init__(
        self,
        workflow,
        conversation_service: ConversationService,
        vision_service: VisionService,
        memory_ingestion_service: MemoryIngestionService,
    ):
        self.workflow = workflow
        self.conversation_service = conversation_service
        self.vision_service = vision_service
        self.memory_ingestion_service = memory_ingestion_service

        os.makedirs(CHAT_IMAGES_DIR, exist_ok=True)

    def chat(
        self,
        conversation_id: str,
        message: str,
        attachments: list[UploadFile] = File([]),
    ) -> str:
        """
        Process a single chat message.
        """

        # Ensure conversation exists
        self.conversation_service.create_conversation_if_not_exist(
                conversation_id=conversation_id,
                title=message[:40] if message else "New Conversation",
            )

        # Store and extract image content, get attachments for save in sqlite
        db_image_attachments = self.handle_attachments(attachments)

        # Persist user message here since user message belong to service, not agent
        self.conversation_service.save_user_message(
            conversation_id=conversation_id,
            content=message,
            attachments=db_image_attachments,
        )

        # Load completed history
        history = self.conversation_service.build_history(
            conversation_id=conversation_id,
        )

        # Load attachments' extracted contents
        attachments_context = self.conversation_service.get_conversation_attachments(
            conversation_id,
        )

        # Invoke workflow with messages and attachments' extracted contents
        state = {
            # conversation_id will be a mark of appending handle message to db
            "conversation_id": conversation_id,
            "messages": history,
            "attachments": attachments_context,
        }
        assistant_response = self.workflow.invoke(state)

        assistant_message = assistant_response["messages"][-1]

        history.append(
            self.conversation_service.format_assistant_chat_message(
                assistant_message.content
            )
        )

        self.memory_ingestion_service.ingest(history)

        return assistant_message.content
    
    
    def handle_attachments(
        self,
        attachments: list[UploadFile] = File([]),
    ) -> list[UploadFile]:
        """
        Handle attachments: Separate attachment by type, storing them then,
        extract their contents and return (currently) images one
        """
        if attachments:
            image_attachments = []
            for attachment in attachments:
                # Handle image type attachments
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    storage_path = self.store_image_attachment(attachment)

                    extraction = self.vision_service.extract(
                        image_path=Path(storage_path),
                    )

                    image_attachments.append(
                        {
                            "type": "image",
                            "storage_path": storage_path,
                            "mime_type": attachment.content_type,
                            "extracted_content": json.dumps(asdict(extraction)),
                            "created_at": datetime.now(UTC).isoformat()
                        }
                    )
            
            return image_attachments


    def store_image_attachment(self, file: UploadFile) -> str:
        """Saves the image locally and returns the relative path/URL."""
        # Generate a unique filename to prevent collisions
        ext = os.path.splitext(file.filename)[1] or ".png"
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(CHAT_IMAGES_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return file_path