from app.tools.schemas import (
    CalculatorInput,
    FileReaderInput,
    WebSearchInput,
)

TOOL_SCHEMAS = {
    "calculator": CalculatorInput,
    "file_reader": FileReaderInput,
    "web_search": WebSearchInput,
}