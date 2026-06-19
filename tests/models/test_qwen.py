from app.models.qwen import QwenModel


def test_model_returns_decision():

    model = QwenModel()

    result = model.invoke(
        [
            type(
                "Msg",
                (),
                {
                    "content": "hello"
                },
            )()
        ]
    )

    assert result.action == "respond"