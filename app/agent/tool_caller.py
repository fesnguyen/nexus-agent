from app.agent.tool_call import ToolCall

from app.tools.registry import ToolRegistry


class ToolCaller:

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:

        self.registry = registry

    def execute(
        self,
        tool_call: ToolCall,
    ):
        """
        Validate and execute a tool call.
        """

        tool = self.registry.get(
            tool_call.tool
        )

        schema_cls = (
            tool.input_schema
        )

        tool_input = schema_cls(
            **tool_call.arguments
        )

        return tool.run(
            tool_input
        )