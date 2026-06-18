from typing import TypedDict


class MultimodalState(TypedDict, total=False):
    images: list[str]
    files: list[str]