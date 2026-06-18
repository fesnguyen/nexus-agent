from typing import Any
from typing import TypedDict


class RetrievalState(TypedDict, total=False):
    documents: list[dict[str, Any]]
    context: str