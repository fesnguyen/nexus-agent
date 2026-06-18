from typing import Annotated
from typing import TypedDict

from langgraph.graph.message import add_messages

from app.graph.schemas.memory import MemoryState
from app.graph.schemas.multimodal import MultimodalState
from app.graph.schemas.planning import PlanningState
from app.graph.schemas.retrieval import RetrievalState
from app.graph.schemas.tool import ToolState


class NexusState(TypedDict, total=False):

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