from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

KNOWLEDGE_DIR = (
    PROJECT_ROOT
    / "knowledge"
)

DATABASE = (
    PROJECT_ROOT
    / "app"
    / "vectorstore"
    / "retrieval.db"
)