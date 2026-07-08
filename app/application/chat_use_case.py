"""
Chat service.
"""

from __future__ import annotations

from app.api.schemas.conversation import Conversation
from app.application.conversation_service import ConversationService


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

    def chat(
        self,
        conversation_id: str,
        message: str,
    ) -> str:
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


        # Persist user message here since user message belong to service, not agent
        self.conversation_service.save_user_message(
            conversation_id=conversation_id,
            content=message,
        )

        # Load complete history
        history = self.conversation_service.build_history(
            conversation_id=conversation_id,
        )

        state = {
            # conversation_id will be a mark of appending handle message to db
            "conversation_id": conversation_id,
            "messages": history,
            "images": None,
        }

        # Invoke workflow
        final_state = self.workflow.invoke(state)

        return final_state["messages"][-1].content
    
    def getConversations(self,) -> list[Conversation]:
        """
        Get conversation list
        """

        conversations = self.conversation_service.list_conversations()

        

        