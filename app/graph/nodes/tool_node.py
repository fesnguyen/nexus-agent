from langchain_core.messages import ToolMessage
from app.core.app import agent_context

def tool_node(state):

    first_tool_call = state["messages"][-1].tool_calls[0]

    tool_name = first_tool_call["name"]
    tool_args = first_tool_call["args"]
    tool_id = first_tool_call["id"]

    # Persist assistant tool call
    agent_context.conversation_service.save_tool_call(
        conversation_id=state["conversation_id"],
        tool_call=first_tool_call,
    )

    # Tool execution
    tool = agent_context.tool_registry.get(tool_name)
    result = tool.run(**tool_args)

    # Persist tool result
    result_text = str(result)
    agent_context.conversation_service.save_tool_result(
        conversation_id=state["conversation_id"],
        content=result_text,
    )

    return {
        "messages": [
            ToolMessage(
                content=str(result),
                tool_call_id=tool_id,
                name=tool_name,
            )
        ],
    }