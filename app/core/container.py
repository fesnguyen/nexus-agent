from app.models.factory import ModelFactory
from app.memory.extractor import MemoryExtractor
from app.retrieval.processing.llm_query_rewriter import LLMQueryRewriter
from app.retrieval.service import RAGService
from app.vectorstore.faiss_store import FaissStore
from app.memory.manager import MemoryManager
from app.memory.sqlite_store import SQLiteMemoryStore
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry
from app.retrieval.processing.heuristic_query_rewriter import HeuristicQueryRewriter
from app.memory.configs.settings import (
    MEMORY_DB_PATH,
    FAISS_INDEX_PATH,
)
from app.retrieval.configs.settings import (
    KNOWLEDGE_DIR,
    DATABASE,
)
from app.ranking.reranker import MemoryReranker


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

        # self.heuristic_query_rewriter = HeuristicQueryRewriter()
        self.llm_query_rewriter = LLMQueryRewriter(self.model)

        self.retrieval_service = RAGService(
            knowledge_dir=KNOWLEDGE_DIR,
            database=DATABASE,
            query_rewriter=self.llm_query_rewriter
        )

        self.retrieval_service.initialize()

        # future

        self.vector_store = None

        self.session_store = None