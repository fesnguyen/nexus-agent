from typing import Any
from typing import TypedDict


class MemoryState(TypedDict, total=False):
    memories: list[dict[str, Any]]
    user_profile: dict[str, Any]