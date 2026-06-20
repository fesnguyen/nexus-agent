# app/graph/nodes/finish.py

from app.graph.state import State


def finish_node(state: State) -> dict:
    """
    Final node of the Nexus graph.
    """

    return {
        "is_complete": True,
    }