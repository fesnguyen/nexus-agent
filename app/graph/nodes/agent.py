from app.graph.nodes.factory import ModelFactory


model = ModelFactory.create(
    "qwen",
    "unsloth/Qwen3-4B-Instruct-2507-bnb-4bit"
)


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