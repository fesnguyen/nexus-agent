from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from app.graph.nodes.agent import agent_node
from app.graph.state import State


def route_agent(state):

    action = state["next_node"]

    if action == "tool":
        return "tool"

    return "finish"


def tool_node(state):

    print(
        f"Executing tool: "
        f"{state['tools']['selected_tool']}"
    )

    return {
        "response": "Tool execution placeholder.",
        "next_node": "finish",
    }


def finish_node(state):
    return state


def build_graph():

    graph = StateGraph(State)

    graph.add_node(
        "agent",
        agent_node,
    )

    graph.add_node(
        "tool",
        tool_node,
    )

    graph.add_node(
        "finish",
        finish_node,
    )

    graph.add_edge(
        START,
        "agent",
    )

    graph.add_conditional_edges(
        "agent",
        route_agent,
    )

    graph.add_edge(
        "tool",
        "finish",
    )

    graph.add_edge(
        "finish",
        END,
    )

    return graph.compile()