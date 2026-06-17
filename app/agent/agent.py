from app.agent.response_generator import (
    ResponseGenerator,
)
from app.agent.tool_caller import ToolCaller

from app.llm.base import BaseModel

from app.tools.registry import ToolRegistry
from app.tools.schema_registry import (
    TOOL_SCHEMAS,
)


class Agent:
    """
    Nexus Agent.

    Responsibilities:
        - Generate tool calls
        - Validate tool arguments
        - Execute tools
        - Generate final responses
    """

    def __init__(
        self,
        model: BaseModel,
        registry: ToolRegistry,
    ) -> None:

        self.model = model
        self.registry = registry

        self.tool_caller = ToolCaller(
            model=model,
            registry=registry,
        )

        self.response_generator = (
            ResponseGenerator(
                model=model,
            )
        )

    def run(
        self,
        user_input: str,
    ) -> str:
        """
        Execute a complete agent workflow.

        Flow:
            User Input
                ↓
            Tool Call Generation
                ↓
            Pydantic Validation
                ↓
            Tool Execution
                ↓
            Response Generation
        """

        # Generate tool call.
        tool_call = (
            self.tool_caller.generate_tool_call(
                user_input
            )
        )

        # Ensure the selected tool exists.
        if (
            tool_call.tool
            not in self.registry.list_tools()
        ):
            raise ValueError(
                f"Unknown tool: {tool_call.tool}"
            )

        # Retrieve schema for validation.
        schema_cls = TOOL_SCHEMAS[
            tool_call.tool
        ]

        # Validate tool arguments.
        tool_input = schema_cls(
            **tool_call.arguments
        )

        # Retrieve tool.
        tool = self.registry.get(
            tool_call.tool
        )

        # Execute tool.
        tool_result = tool.run(
            tool_input
        )

        # Generate final answer.
        return self.response_generator.generate(
            user_input=user_input,
            tool_name=tool_call.tool,
            tool_result=tool_result,
        )