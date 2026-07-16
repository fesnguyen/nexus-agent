from typing import Literal

from app.models.unsloth_model import UnslothModel
from app.models.unsloth_vision_model import UnslothVisionModel


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
        
        if backend == "UnslothVision":
            return UnslothVisionModel(
                model_name,
                **kwargs,
            )

        raise ValueError(
            f"Unknown backend: {backend}"
        )