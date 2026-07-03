from typing import Annotated
from typing import Any
from typing import TypedDict

from langgraph.graph.message import add_messages

from app.contracts.tool_call import ToolCall
from app.graph.states.memory import MemoryState
from app.graph.states.multimodal import MultimodalState
from app.graph.states.planning import PlanningState
from app.graph.states.retrieval import RetrievalState
from app.graph.states.tool import ToolState


class State(TypedDict, total=False):

    # =====================
    # Message centric, this is the only source of truth for agent decision
    # =====================
    messages: Annotated[list, add_messages]

    # =====================
    # Conversation id to manage conversation history
    # =====================
    conversation_id: str


    # =====================
    # Domain States
    # =====================

    planning: PlanningState
    retrieval: RetrievalState
    multimodal: MultimodalState

    memory: MemoryState