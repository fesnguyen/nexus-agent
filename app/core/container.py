from app.models.factory import ModelFactory
from app.memory.extractor import MemoryExtractor
from app.memory.faiss_store import FaissStore
from app.memory.manager import MemoryManager
from app.memory.sqlite_store import SQLiteMemoryStore
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry
from app.memory.configs.settings import (
    MEMORY_DB_PATH,
    FAISS_INDEX_PATH,
)
from app.memory.reranker import MemoryReranker


class Container:

    def __init__(self) -> None:

        self.tool_registry = ToolRegistry(
            register_all_available=True
        )

        self.memory_store = SQLiteMemoryStore(
            db_path=MEMORY_DB_PATH
        )

        self.faiss_store = FaissStore(
            index_path=FAISS_INDEX_PATH,
        )

        self.memory_reranker = (
            MemoryReranker()
        )

        self.memory_manager = MemoryManager(
            self.memory_store,
            self.faiss_store,
            self.memory_reranker,
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