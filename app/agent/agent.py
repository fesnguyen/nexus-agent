from app.agent.agent_state import AgentState
from app.agent.planner import Planner
from app.agent.react_planner import ReActPlanner
from app.agent.tool_call import ToolCall

from app.agent.tool_caller import ToolCaller
from app.llm.base import BaseModel

from app.tools.registry import ToolRegistry


MAX_ITERATIONS = 5

FINAL_ANSWER_PROMPT = """
Answer the user's request using the available observations.

Do not call tools.
Provide a final response.
"""


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
        tool_caller: ToolCaller,
    ) -> None:

        self.model = model
        self.tool_caller = tool_caller

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

        state = AgentState(
            user_input=user_input
        )

        for _ in range(MAX_ITERATIONS):

            decision = self.planner.plan(
                state
            )

            if decision.action == "final_answer":

                state.system_prompt = (
                    FINAL_ANSWER_PROMPT,
                )

                return self.model.generate_text(
                    state,
                )

            tool_call = self.model.generate_tool_call(
                state=state,
                tools=self.tool_caller.registry.get_tool_schemas(),
            )

            if tool_call is None:
                raise RuntimeError(
                    "Planner requested a tool but "
                    "the model did not generate one."
                )

            result = self.tool_caller.execute(
                tool_call
            )

            state.observations.append(
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