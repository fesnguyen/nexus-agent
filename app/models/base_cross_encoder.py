from abc import ABC

from sentence_transformers import CrossEncoder

from app.models.cross_encoder_manager import CrossEncoderManager


class BaseCrossEncoder(ABC):

    def __init__(
        self,
        cross_encoder_manager: CrossEncoderManager,
        model_name: str,
    ) -> None:
        self._cross_encoder_manager = cross_encoder_manager
        self._model_name = model_name

        self._cross_encoder_manager.register(
            model_name,
        )

    @property
    def cross_encoder(self) -> CrossEncoder:
        return self._cross_encoder_manager.get_model(
            self._model_name,
        )

    def predict(
        self,
        *args,
        **kwargs,
    ):
        return self.cross_encoder.predict(
            *args,
            **kwargs,
        )