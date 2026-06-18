from typing import Any

from app.tools.base import BaseTool


def tool_to_schema(
    tool: BaseTool,
) -> dict[str, Any]:
    """
    Convert a Nexus tool into an OpenAI/HuggingFace
    compatible function schema.
    """

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema.model_json_schema(),
        },
    }