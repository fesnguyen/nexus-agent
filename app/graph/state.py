from typing import Annotated
from typing import TypedDict

from langgraph.graph.message import add_messages

from app.graph.states.memory import MemoryState
from app.graph.states.multimodal import MultimodalState
from app.graph.states.planning import PlanningState
from app.graph.states.retrieval import RetrievalState
from app.graph.states.tool import ToolState


class State(TypedDict, total=False):

    # conversation
    messages: Annotated[list, add_messages]
    user_query: str

    # domains
    planning: PlanningState
    tools: ToolState
    retrieval: RetrievalState
    memory: MemoryState
    multimodal: MultimodalState

    # output
    response: str

    # routing
    next_node: str
    is_complete: bool