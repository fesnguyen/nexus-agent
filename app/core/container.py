from app.memory.extractor import MemoryExtractor
from app.memory.manager import MemoryManager
from app.memory.sqlite_store import SQLiteMemoryStore
from app.models.base import BaseLLM
from app.models.factory import ModelFactory
from app.tools.registry import ToolRegistry
from app.memory.configs.settings import (
    MEMORY_DB_PATH,
)


class Container:

    def __init__(self) -> None:

        self.tool_registry = ToolRegistry(
            register_all_available=True
        )

        self.memory_store = SQLiteMemoryStore(
            db_path=MEMORY_DB_PATH
        )

        self.memory_manager = MemoryManager(
            self.memory_store
        )

        self.model: BaseLLM = ModelFactory.create(
            "qwen",
            "unsloth/Qwen3-4B-Instruct-2507-bnb-4bit",
            tool_registry = self.tool_registry,
        )

        self.memory_extractor = MemoryExtractor(self.model)

        # future

        self.vector_store = None

        self.memory_store = None

        self.session_store = None