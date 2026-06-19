from app.contracts.agent_decision import AgentDecision
from app.contracts.tool_call import ToolCall
from app.models.base import BaseLLM


class QwenModel(BaseLLM):

    def invoke(self, messages) -> AgentDecision:

        last_message = messages[-1].content.lower()

        if "search" in last_message:

            return AgentDecision(
                thought="User requests external information.",
                action="tool",
                tool_call=ToolCall(
                    name="search",
                    arguments={
                        "query": last_message,
                    },
                ),
            )

        return AgentDecision(
            thought="Direct response is sufficient.",
            action="respond",
            response="Hello from Nexus.",
        )