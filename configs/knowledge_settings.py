# Root directory for persistent application data.
from configs.base_settings import DATA_DIR

KNOWLEDGE_DIR = DATA_DIR / "knowledge"

# Raw knowledge dir
KNOWLEDGE_FILES_PATH = DATA_DIR / "sources"

# SQLite database for the knowledge base.
KNOWLEDGE_DB_PATH = KNOWLEDGE_DIR / "knowledge.db"

# FAISS index for semantic document retrieval.
KNOWLEDGE_FAISS_PATH = KNOWLEDGE_DIR / "rag" / "semantic.faiss"