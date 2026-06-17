from app.agent.tool_argument_extractor import (
    ToolArgumentExtractor,
)
from app.agent.tool_router import ToolRouter

from app.llm.base import BaseModel

from app.tools.registry import ToolRegistry
from app.tools.schema_registry import (
    TOOL_SCHEMAS,
)


class Agent:
    """
    Nexus Agent.

    Responsibilities:
        - Select the appropriate tool
        - Extract tool arguments
        - Validate arguments
        - Execute tools
    """

    def __init__(
        self,
        model: BaseModel,
        registry: ToolRegistry,
    ) -> None:

        self.model = model
        self.registry = registry

        self.router = ToolRouter(
            model=model,
            registry=registry,
        )

        self.argument_extractor = (
            ToolArgumentExtractor(
                model=model,
            )
        )

    def run(
        self,
        user_input: str,
    ):
        """
        Execute a user request.

        Flow:
            User Input
                ↓
            Tool Router
                ↓
            Argument Extraction
                ↓
            Pydantic Validation
                ↓
            Tool Execution
        """

        # Step 1: Select tool
        tool_name = self.router.route(
            user_input
        )

        # Step 2: Get schema
        schema_cls = TOOL_SCHEMAS[
            tool_name
        ]

        # Step 3: Extract arguments
        arguments = (
            self.argument_extractor.extract(
                tool_name=tool_name,

                # Temporary manual schema
                schema={
                    field_name: str(field.annotation)
                    for field_name, field
                    in schema_cls.model_fields.items()
                },

                user_input=user_input,
            )
        )

        # Step 4: Validate with Pydantic
        tool_input = schema_cls(
            **arguments
        )

        # Step 5: Execute tool
        tool = self.registry.get(
            tool_name
        )

        return tool.run(
            tool_input
        )