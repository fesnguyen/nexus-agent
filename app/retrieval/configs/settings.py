from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

KNOWLEDGE_DIR = (
    PROJECT_ROOT
    / "knowledge"
)

RETRIEVAL_DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "retrieval"
    / "retrieval.db"
)