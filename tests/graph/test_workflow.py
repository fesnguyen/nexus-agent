from langchain_core.messages import HumanMessage

from app.graph.workflow import build_graph


def test_direct_response():

    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="hello"
                )
            ]
        }
    )

    assert result["response"] == "Hello from Nexus."