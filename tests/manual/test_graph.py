from langchain_core.messages import HumanMessage

from app.graph.workflow import build_graph


def main():

    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is your capabilities?"
                )
            ]
        }
    )

    print(result)


if __name__ == "__main__":
    main()