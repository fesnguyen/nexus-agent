# Knowledge base data used by RAG.
from configs.base_settings import DATA_DIR

# Agent-specific data (conversation history, memory, etc.).
AGENT_DIR = DATA_DIR / "agent"

# SQLite database for agent state.
AGENT_DB_PATH = AGENT_DIR / "agent.db"

# FAISS index for semantic memory.
MEMORY_FAISS_PATH = AGENT_DIR / "agent" / "semantic.faiss"

# User images directory
CHAT_IMAGES_DIR = DATA_DIR / "agent" / "chat_images"