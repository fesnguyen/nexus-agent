from app.tools.base import BaseTool


class ToolRegistry:
    """
    Central registry storing all tools available to Nexus.
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.
        """

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' already registered."
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """
        Retrieve a tool by name.
        """

        try:
            return self._tools[name]

        except KeyError as exc:
            raise ValueError(
                f"Tool '{name}' not found."
            ) from exc


    def list_tools(self) -> list[str]:
        return list(self._tools.keys())