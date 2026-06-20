from langchain_core.messages import HumanMessage

from app.graph.nodes.agent import agent_node
from app.graph.state import State

def main():

    state = State(
            messages=[
                    HumanMessage("What is your capabilities?")
                ]
        )

    note = agent_node(state)

    print()
    print("RESULT")
    print("=" * 50)
    print(note["response"])


if __name__ == "__main__":
    main()