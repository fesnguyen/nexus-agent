from app.llm.base import BaseModel

from app.llm.prompts import (
    FINAL_RESPONSE_PROMPT,
)


class ResponseGenerator:

    def __init__(
        self,
        model: BaseModel,
    ) -> None:

        self.model = model

    def generate(
        self,
        user_input: str,
        tool_name: str,
        tool_result,
    ) -> str:

        prompt = FINAL_RESPONSE_PROMPT.format(
            user_input=user_input,
            tool_name=tool_name,
            tool_result=tool_result,
        )

        return self.model.generate_text(
            prompt
        )