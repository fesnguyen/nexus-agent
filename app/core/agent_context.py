import asyncio

from app.memory.conversation.conversation_service import ConversationService
from app.memory.conversation.conversation_store import ConversationStore
from app.memory.long_term.extractor import MemoryExtractor
from app.memory.long_term.memory_ingestion_service import MemoryIngestionService
from app.models.cross_encoder_manager import CrossEncoderManager
from app.models.model_manager import ModelManager
from app.models.embedding_manager import EmbeddingManager
from app.retrieval.processing.embedder import Embedder
from app.retrieval.processing.embedding_context_compressor import EmbeddingContextCompressor
from app.retrieval.processing.llm_query_rewriter import LLMQueryRewriter
from app.retrieval.rag_service import RAGService
from app.memory.long_term.memory_faiss_store import MemoryFaissStore
from app.memory.long_term.manager import MemoryManager
from app.memory.long_term.sqlite_store import SQLiteMemoryStore
from app.models.base import BaseLLM
from app.tools.registry import ToolRegistry
# from app.retrieval.processing.heuristic_query_rewriter import HeuristicQueryRewriter

from app.vision.capability.vision_captioner import VisionCaptioner
from app.vision.capability.vision_ocr import VisionOCR
from app.vision.vision_service import VisionService
from app.vision.vision_worker_manager import VisionWorkerManager
from configs.agent_settings import (
    AGENT_DB_PATH,
    MEMORY_FAISS_PATH,
    CHAT_IMAGES_DIR,
)

from configs.knowledge_settings import (
    KNOWLEDGE_DB_PATH,
    KNOWLEDGE_SOURCE_DIR,
    KNOWLEDGE_FAISS_PATH,
)

from app.ranking.reranker import MemoryReranker
from configs.model_settings import CHAT_LLM, CHAT_VLM


class AgentContext:

    def initialize(self):
        print("Container initialization start")

        # ---------------------------------------------------------
        # LLM and SentenceTransformer models manager
        # ---------------------------------------------------------
        # Container of all SentenceTransformer models

        # Embedding models manager for memory faiss store
        # and rag embedder/compressor/...
        self.embedding_manager = EmbeddingManager()

        # Cross encoder model for reranker
        self.cross_encoder_manager = CrossEncoderManager()

        self.tool_registry = ToolRegistry(
            register_all_available=True
        )

        # LLM model manager for memory extractor, query rewriter
        self.model_manager = ModelManager(
            backend="Unsloth",
            model_name=CHAT_LLM,
            tool_registry=self.tool_registry,
        )

        # ---------------------------------------------------------
        # Vision process pipeline
        # ---------------------------------------------------------
        self.vision_worker_manager = VisionWorkerManager()

        self.vision_captioner = VisionCaptioner(
            worker_manager=self.vision_worker_manager,
        )

        self.vision_ocr = VisionOCR(
            worker_manager=self.vision_worker_manager,
        )

        self.vision_service = VisionService(
            captioner=self.vision_captioner,
            ocr=self.vision_ocr,
        )

        # For testing purpose only, uncomment to test vision process pipeline
        # self.vision_worker_manager.initialize()
        # print(self.vision_service.extract(CHAT_IMAGES_DIR / "b33c8d44c4a7b4e14f2ed8f7dc6837b7.jpg"))


        # ---------------------------------------------------------
        # Conversation and Memory
        # ---------------------------------------------------------
        self.conversation_store = ConversationStore(
            db_path=AGENT_DB_PATH,
        )

        self.conversation_service = ConversationService(
            store=self.conversation_store,
        )

        self.memory_store = SQLiteMemoryStore(
            db_path=AGENT_DB_PATH
        )

        self.memory_reranker = MemoryReranker(
            self.cross_encoder_manager
        )

        self.faiss_store = MemoryFaissStore(
            index_path=MEMORY_FAISS_PATH,
            embedding_manager=self.embedding_manager,
        )

        print("memory manager init")
        self.memory_manager = MemoryManager(
            self.memory_store,
            self.faiss_store,
            self.memory_reranker,
        )

        self.memory_extractor = MemoryExtractor(self.model_manager)

        self.memory_ingestion_service = MemoryIngestionService(
            extractor=self.memory_extractor,
            memory_manager=self.memory_manager,
        )

        # ---------------------------------------------------------
        # RAG
        # ---------------------------------------------------------
        # self.heuristic_query_rewriter = HeuristicQueryRewriter()
        self.embedder = Embedder(self.embedding_manager)

        self.llm_query_rewriter = LLMQueryRewriter(self.model_manager)

        self.context_compressor = EmbeddingContextCompressor(
            embedding_manager=self.embedding_manager,
        )

        self.retrieval_service = RAGService(
            knowledge_dir=KNOWLEDGE_SOURCE_DIR,
            db_path=KNOWLEDGE_DB_PATH,
            faiss_path=KNOWLEDGE_FAISS_PATH,
            embedder=self.embedder,
            query_rewriter=self.llm_query_rewriter,
            context_compressor = self.context_compressor,
        )

    def initialize_resources(self) -> None:
        """
        Initialize expensive resources in the background.

        This method should be called after the application
        has finished starting up.
        """
        resources = [
            ("Model Manager", self.model_manager),
            ("Vision process pipeline", self.vision_worker_manager),
            ("Embedding Manager", self.embedding_manager),
            ("Retrieval Service", self.retrieval_service),
            ("Cross Encoder Manager", self.cross_encoder_manager)
        ]

        for name, resource in resources:
            task = asyncio.create_task(
                asyncio.to_thread(resource.initialize)
            )

            # Define a dynamic callback closure tracking the resource name
            def make_callback(res_name):
                def callback(t: asyncio.Task):
                    try:
                        print(f"[INIT SUCCESS] {res_name} completed")
                    except Exception as e:
                        print(f"[INIT FAILURE] {res_name} failed: {e}")
                return callback

            task.add_done_callback(make_callback(name))