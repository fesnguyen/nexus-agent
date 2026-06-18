from app.agent.agent import Agent

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

agent = Agent(
    model=model,
    tool_caller=ToolCaller(registry),
)

response = agent.run(
    "What is AI news today? I need newest information!"
)

print(response)