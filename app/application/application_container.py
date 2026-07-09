

from app.application.chat_use_case import ChatUseCase
from app.application.conversation_use_case import ConversationUseCase


class ApplicationContainer:
    """
    Container of use cases for business logic
    Expected to be set in api state and called by api
    """

    def __init__(
        self,
        chat_use_case: ChatUseCase,
        conversation_use_case: ConversationUseCase,
    ):
        self.chat = chat_use_case
        self.conversation = conversation_use_case
