from app.agent.react_planner import ReActPlanner

from app.llm.unsloth_vlm import UnslothVLM

from app.tools.registry import ToolRegistry
from app.tools.calculator import CalculatorTool
from app.tools.file_reader import FileReaderTool
from app.tools.web_search import WebSearchTool

model = UnslothVLM(
    model_name="unsloth/Qwen3-VL-4B-Instruct-unsloth-bnb-4bit"
)

registry = ToolRegistry()

planner = ReActPlanner(model, registry)

action = planner.plan(
    user_input="What is 25 * 47?",
    observations=["Tool: calculator\nResult:\n1175"],
)

print(action)