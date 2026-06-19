from app.contracts.agent_decision import AgentDecision
from app.contracts.tool_call import ToolCall


def test_direct_response():

    decision = AgentDecision(
        thought="Simple question",
        action="respond",
        response="Hello",
    )

    assert decision.action == "respond"
    assert decision.response == "Hello"


def test_tool_response():

    decision = AgentDecision(
        thought="Need search",
        action="tool",
        tool_call=ToolCall(
            name="search",
            arguments={
                "query": "qwen"
            },
        ),
    )

    assert decision.tool_call.name == "search"