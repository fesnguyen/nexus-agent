from app.models.base import BaseLLM
from app.models.factory import ModelFactory
from app.tools.registry import ToolRegistry


class Container:

    def __init__(self) -> None:

        self.tool_registry = ToolRegistry(
            register_all_available=True
        )

        self.model: BaseLLM = ModelFactory.create(
            "qwen",
            "unsloth/Qwen3-4B-Instruct-2507-bnb-4bit",
            tool_registry = self.tool_registry,
        )

        # future

        self.vector_store = None

        self.memory_store = None

        self.session_store = None