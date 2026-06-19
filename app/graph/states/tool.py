from typing import Any
from typing import TypedDict


class ToolState(TypedDict, total=False):
    selected_tool: str
    tool_input: dict[str, Any]

    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]