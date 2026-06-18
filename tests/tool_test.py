from app.llm.unsloth_vlm import UnslothVLM
from app.tools.calculator import CalculatorTool
from app.llm.tool_schema import tool_to_schema
from pprint import pprint as ppr

from app.tools.file_reader import FileReaderTool
from app.tools.registry import ToolRegistry
from app.tools.web_search import WebSearchTool

registry = ToolRegistry()

registry.register(
    CalculatorTool()
)

registry.register(
    FileReaderTool()
)

registry.register(
    WebSearchTool()
)

tools = registry.get_tool_schemas()

model = UnslothVLM("unsloth/Qwen3-VL-4B-Instruct-unsloth-bnb-4bit")

response = model.generate_tool_call(
    user_input="What is 25 * 47?",
    tools=tools,
)

print(response)
print(type(response))