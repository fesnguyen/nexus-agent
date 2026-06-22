from langchain_core.messages import ToolMessage
from app.core.app import container

def tool_node(state):

    first_tool_call = state["messages"][-1].tool_calls[0]

    tool_name = first_tool_call["name"]
    tool_args = first_tool_call["args"]
    tool_id = first_tool_call["id"]

    tool = container.tool_registry.get(tool_name)

    result = tool.run(**tool_args)

    return {
        "messages": [
            ToolMessage(
                content=str(result),
                tool_call_id=tool_id,
                name=tool_name,
            )
        ],
    }