import json

from app.llm.base import BaseModel
from app.llm.prompts import TOOL_ARGUMENT_PROMPT


class ToolArgumentExtractor:
    """
    Uses the model to extract tool arguments
    from a user request.
    """

    def __init__(
        self,
        model: BaseModel,
    ) -> None:
        self.model = model

    def extract(
        self,
        tool_name: str,
        schema: dict,
        user_input: str,
    ) -> dict:
        """
        Extract arguments for a tool.

        Args:
            tool_name:
                Selected tool.

            schema:
                Simplified schema description.

            user_input:
                Original user request.

        Returns:
            Parsed JSON arguments.
        """

        prompt = TOOL_ARGUMENT_PROMPT.format(
            tool_name=tool_name,
            schema=json.dumps(
                schema,
                indent=2,
            ),
            user_input=user_input,
        )

        response = self.model.generate(
            prompt
        )

        try:
            return json.loads(
                response.strip()
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON returned by model:\n{response}"
            ) from exc