from pathlib import Path

# Number of parent directories from this file to the project root.
ROOT_PARENT_ORDER = 1

ROOT_DIR = Path(__file__).resolve().parents[ROOT_PARENT_ORDER]

# Root directory for persistent application data.
DATA_DIR = ROOT_DIR / "data"