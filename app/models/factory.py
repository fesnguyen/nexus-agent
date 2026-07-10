from typing import Literal

from app.models.unsloth_model import UnslothModel


class ModelFactory:

    @staticmethod
    def create(
        backend: Literal["Unsloth" , "Ollama"],
        model_name: str,
        **kwargs,
    ):

        if backend == "Unsloth":
            return UnslothModel(
                    model_name,
                    **kwargs,
                )

        raise ValueError(
            f"Unknown backend: {backend}"
        )