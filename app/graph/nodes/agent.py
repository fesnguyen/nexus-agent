from app.models.qwen import QwenModel


model = QwenModel()


def agent_node(state):

    decision = model.invoke(
        state["messages"]
    )

    updates = {
        "next_node": decision.action,
    }

    if decision.response:
        updates["response"] = decision.response

    if decision.tool_call:

        updates["tools"] = {
            "selected_tool": decision.tool_call.name,
            "tool_input": decision.tool_call.arguments,
        }

    return updates