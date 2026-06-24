from app.models.qwen import QwenModel
from app.tools.registry import ToolRegistry
# from app.models.gemma import GemmaModel
# from app.models.llama import LlamaModel


class ModelFactory:

    @staticmethod
    def create(
        provider: str,
        model_name: str,
        **kwargs,
    ):

        if provider == "qwen":
            return QwenModel(
                    model_name,
                    **kwargs,
                )

        # if provider == "gemma":
        #     return GemmaModel(model_name)

        # if provider == "llama":
        #     return LlamaModel(model_name)

        raise ValueError(
            f"Unknown provider: {provider}"
        )