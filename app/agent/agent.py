from app.agent.react_planner import ReActPlanner
from app.agent.tool_call import ToolCall

from app.llm.base import BaseModel

from app.tools.registry import ToolRegistry
from app.tools.schema_registry import TOOL_SCHEMAS


MAX_ITERATIONS = 5


class Agent:
    """
    Nexus ReAct Agent.

    Flow:

        User Input
            ↓
        Planner
            ↓
        Tool Call
            ↓
        Tool Execution
            ↓
        Observation
            ↓
        Planner
            ↓
        Final Answer
    """

    def __init__(
        self,
        model: BaseModel,
        registry: ToolRegistry,
    ) -> None:

        self.model = model
        self.registry = registry

        self.planner = ReActPlanner(
            model=model,
            registry=registry,
        )

    def run(
        self,
        user_input: str,
    ) -> str:
        """
        Execute an iterative ReAct loop.

        Args:
            user_input:
                Original user request.

        Returns:
            Final agent response.
        """

        observations: list[str] = []

        for step in range(MAX_ITERATIONS):

            action = self.planner.plan(
                user_input=user_input,
                observations=observations,
            )

            # Agent decided it can answer.
            if action.action == "final_answer":

                return action.content

            # Agent decided to use a tool.
            if action.action == "tool":

                tool_call = ToolCall.model_validate(
                    action.content
                )

                observation = self._execute_tool(
                    tool_call
                )

                observations.append(
                    observation
                )

                continue

            raise ValueError(
                f"Unknown action: {action.action}"
            )

        raise RuntimeError(
            f"Maximum iterations ({MAX_ITERATIONS}) reached."
        )

    def _execute_tool(
        self,
        tool_call: ToolCall,
    ) -> str:
        """
        Validate and execute a tool call.

        Returns:
            Observation string.
        """

        if (
            tool_call.tool
            not in self.registry.list_tools()
        ):
            raise ValueError(
                f"Unknown tool: {tool_call.tool}"
            )

        schema_cls = TOOL_SCHEMAS[
            tool_call.tool
        ]

        tool_input = schema_cls(
            **tool_call.arguments
        )

        tool = self.registry.get(
            tool_call.tool
        )

        result = tool.run(
            tool_input
        )

        return (
            f"Tool: {tool_call.tool}\n"
            f"Result:\n{result}"
        )