from typing import Any
# Type-safe data validation and serialization for Python applications.
from pydantic import BaseModel, Field
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


class CalculatorInput(BaseModel):
    """
    Input schema for CalculatorTool.
    """

    expression: str = Field(
        min_length=1, # At least one character
        description="Arithmetic expression to evaluate."
    )


class FileReaderInput(BaseModel):
    """
    Input schema for FileReaderTool.
    """

    path: str = Field(
        min_length=1,
        description="Path of file to read."
    )


class WebSearchInput(BaseModel):
    """
    Input schema for WebSearchTool.
    """

    query: str = Field(
        min_length=1,
        description="Search query."
    )

    num_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results."
    )