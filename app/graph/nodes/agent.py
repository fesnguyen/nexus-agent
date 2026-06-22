from app.core.app import container
from app.graph.state import State
from langchain_core.messages import AIMessage

def agent_node(state: State):

    decision = container.model.invoke(
        messages=state["messages"]
    )

    #
    # Tool call
    #
    if decision.tool_calls:

        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        tool.model_dump()
                        for tool in decision.tool_calls
                    ],
                )
            ]
        }

    #
    # Final answer
    #
    return {
        "messages": [
            AIMessage(
                content=decision.response
            )
        ]
    }