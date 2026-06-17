from app.agent.agent import Agent

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
    registry=registry,
)

response = agent.run(
    "What is 25 * 47?"
)

print(response)