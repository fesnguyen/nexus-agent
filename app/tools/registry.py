from app.tools.base import BaseTool


class ToolRegistry:
    """
    Central registry storing all tools available to Nexus.
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found")

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())