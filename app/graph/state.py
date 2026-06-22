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
    # Conversation
    # =====================

    messages: Annotated[list, add_messages]

    # =====================
    # Domain States
    # =====================

    planning: PlanningState
    retrieval: RetrievalState
    memory: MemoryState
    multimodal: MultimodalState

    # =====================
    # Tool Execution
    # =====================

    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]

    # =====================
    # Final Output
    # =====================

    response: str

    # =====================
    # Graph Control
    # =====================

    next_node: str
    is_complete: bool