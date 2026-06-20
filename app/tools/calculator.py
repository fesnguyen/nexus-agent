from simpleeval import simple_eval, InvalidExpression

from app.tools.base import BaseTool
from app.tools.schemas.tool_schemas import CalculatorInput


class CalculatorTool(BaseTool):
    """
    Perform arithmetic calculations.

    Future Extensions:
        - Scientific functions
        - Unit conversions
        - Symbolic math (SymPy)
    """

    name = "calculator"

    description = (
        "Evaluate arithmetic expressions safely."
    )

    input_schema = CalculatorInput

    def run(self, **kwargs) -> str:
        """
        Execute a calculation.

        Args:
            tool_input:
                CalculatorInput schema.

        Returns:
            String representation of result.

        Raises:
            ValueError:
                If expression cannot be evaluated.
        """

        tool_input = self.input_schema(
            **kwargs
        )

        try:
            result = simple_eval(tool_input.expression)
            return str(result)

        except InvalidExpression as exc:
            raise ValueError(
                f"Invalid expression: {tool_input.expression}"
            ) from exc