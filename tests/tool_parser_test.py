from app.agent.tool_parser import (
    parse_tool_call,
)

response = """
<tool_call>
{
    "name": "calculator",
    "arguments": {
        "expression": "25 * 47"
    }
}
</tool_call>
"""

tool_call = parse_tool_call(
    response
)

print(tool_call)
print(type(tool_call))