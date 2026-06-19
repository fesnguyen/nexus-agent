from langchain_core.messages import HumanMessage

from app.models.qwen import QwenModel


def main():

    model = QwenModel(
        model_name="unsloth/Qwen3-4B-Instruct-2507-bnb-4bit"
    )

    decision = model.invoke(
        [
            HumanMessage(
                content="What is LoRA?"
            )
        ]
    )

    print()
    print("RESULT")
    print("=" * 50)
    print(decision)


if __name__ == "__main__":
    main()