from app.tools.registry import ToolRegistry

def tool_node(state):

    tool_name = state["tools"]["selected_tool"]

    tool_input = state["tools"]["tool_input"]

    registry = ToolRegistry(registry_all_available=True)
    
    tool = registry.get(tool_name)

    result = tool.run(**tool_input)

    return {
        "tools": {
            "tool_results": [result]
        },
        "next_node": "finish"
    }