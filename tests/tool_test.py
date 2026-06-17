from app.agent.tool_caller import ToolCaller
from app.llm.unsloth_vlm import UnslothVLM
from app.tools.registry import ToolRegistry
from app.tools.calculator import CalculatorTool
from app.tools.file_reader import FileReaderTool
from app.tools.web_search import WebSearchTool

model = UnslothVLM(
    model_name="unsloth/Qwen3-VL-4B-Instruct-unsloth-bnb-4bit"
)

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

tool_caller = ToolCaller(model, registry)

tool_call = tool_caller.generate_tool_call(
    "Search latest Qwen3 release"
)

print(tool_call)