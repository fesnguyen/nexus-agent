from app.agent.planner import Planner
from app.agent.react_planner import ReActPlanner
from app.agent.tool_call import ToolCall

from app.llm.base import BaseModel

from app.tools.registry import ToolRegistry


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

        self.planner = Planner(
            model=model,
        )

    def run(
        self,
        user_input: str,
    ) -> str:
        """
        Execute the agent workflow.

        Flow:
            User Request
                ↓
            Planner
                ↓
            Tool?
                ↓
            Tool Execution
                ↓
            Observation
                ↓
            Planner
                ↓
            Final Answer
        """

        observations: list[str] = []

        for _ in range(MAX_ITERATIONS):

            decision = self.planner.plan(
                user_input=user_input,
                observations=observations,
            )

            if decision.action == "final_answer":

                final_prompt = f"""
User Request:
{user_input}

Observations:
{chr(10).join(observations)}

Answer the user.
"""

                return self.model.generate_text(
                    prompt=final_prompt,
                )

            tool_call = self.model.generate_tool_call(
                user_input=user_input,
                tools=self.registry.get_tool_schemas(),
            )

            if tool_call is None:
                raise RuntimeError(
                    "Planner requested a tool but "
                    "the model did not generate one."
                )

            tool = self.registry.get(
                tool_call.tool
            )

            schema_cls = (
                tool.input_schema
            )

            tool_input = schema_cls(
                **tool_call.arguments
            )

            result = tool.run(
                tool_input
            )

            observations.append(
                f"""
Tool: {tool_call.tool}

Arguments:
{tool_call.arguments}

Result:
{result}
"""
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