from app.graph.state import State
from app.graph.nodes.tool import tool_node
from app.tools.schemas.tool_schemas import CalculatorInput

def main():

    state = State(
            tools={
                "selected_tool": "calculator",
                "tool_input": {
                    "expression": "2 + 3"
                }
            },
        )

    note = tool_node(state)

    print()
    print("RESULT")
    print("=" * 50)
    print(note)
    print()


if __name__ == "__main__":
    main()