from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEMORY_DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "memory"
    / "memory.db"
)

FAISS_INDEX_PATH = (
    PROJECT_ROOT
    / "data"
    / "faiss"
    / "memory.index"
)