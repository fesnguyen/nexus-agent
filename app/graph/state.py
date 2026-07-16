from typing import Annotated, NotRequired
from typing import TypedDict

from langgraph.graph.message import add_messages

from app.memory.conversation.conversation_schemas import Attachment


class State(TypedDict, total=False):

    # =====================
    # Message centric, this is the only source of truth for agent decision
    # =====================
    messages: Annotated[list, add_messages]

    # =====================
    # Extracted attachment context
    # =====================
    attachments: list[Attachment]

    # =====================
    # Conversation id to manage conversation history
    # =====================
    conversation_id: str

    # =====================
    # Domain States
    # =====================
    memory_context: NotRequired[str]
    retrieval_context: NotRequired[str]