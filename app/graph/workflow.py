from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph
from langchain_core.messages import AIMessage

from app.graph.nodes.agent import agent_node
from app.graph.nodes.tool import tool_node
from app.graph.state import State


def route_agent(state):
    """
    Route the agent node in the state graph.
    Currently sequential task execution
    """
    last_message = state["messages"][-1]

    if (
        isinstance(last_message, AIMessage)
        and last_message.tool_calls
    ):
        return "tool"

    return "finish"


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

    graph.add_edge(
        START,
        "agent",
    )

    graph.add_conditional_edges(
        "agent",
        route_agent,
        {
            "tool": "tool",
            "finish": END,
        },
    )

    graph.add_edge(
        "tool",
        "agent",
    )

    return graph.compile()