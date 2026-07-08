from app.memory.conversation.conversation_service import ConversationService
from app.memory.conversation.conversation_store import ConversationStore
from app.models.factory import ModelFactory
from app.memory.long_term.extractor import MemoryExtractor
from app.retrieval.processing.embedding_context_compressor import EmbeddingContextCompressor
from app.retrieval.processing.llm_query_rewriter import LLMQueryRewriter
from app.retrieval.rag_service import RAGService
from app.memory.long_term.memory_faiss_store import MemoryFaissStore
from app.memory.long_term.manager import MemoryManager
from app.memory.long_term.sqlite_store import SQLiteMemoryStore
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry
# from app.retrieval.processing.heuristic_query_rewriter import HeuristicQueryRewriter

from configs.agent_settings import (
    AGENT_DB_PATH,
    MEMORY_FAISS_PATH,
)

from configs.knowledge_settings import (
    KNOWLEDGE_DB_PATH,
    KNOWLEDGE_SOURCE_DIR,
    KNOWLEDGE_FAISS_PATH,
)

from app.ranking.reranker import MemoryReranker


class AgentContext:

    def initialize(self):
        print("Container initialization start")

        # ---------------------------------------------------------
        # Conversation
        # ---------------------------------------------------------

        self.conversation_store = ConversationStore(
            db_path=AGENT_DB_PATH,
        )

        self.conversation_service = ConversationService(
            store=self.conversation_store,
        )

        self.tool_registry = ToolRegistry(
            register_all_available=True
        )

        self.memory_store = SQLiteMemoryStore(
            db_path=AGENT_DB_PATH
        )

        self.faiss_store = MemoryFaissStore(
            index_path=MEMORY_FAISS_PATH,
        )

        self.memory_reranker = (
            MemoryReranker()
        )

        print("memory manager init")
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

        self.context_compressor = EmbeddingContextCompressor()

        self.retrieval_service = RAGService(
            knowledge_dir=KNOWLEDGE_SOURCE_DIR,
            db_path=KNOWLEDGE_DB_PATH,
            faiss_path=KNOWLEDGE_FAISS_PATH,
            query_rewriter=self.llm_query_rewriter,
            context_compressor = self.context_compressor,
        )

        self.retrieval_service.initialize()