from langchain_core.messages import HumanMessage

from app.graph.workflow import build_workflow


graph = build_workflow()

result = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="Search latest Qwen release"
            )
        ]
    }
)

print()

print("RESPONSE")
print("=" * 50)

print(
    result.get("response")
)

print()

print("STATE")
print("=" * 50)

print(result)