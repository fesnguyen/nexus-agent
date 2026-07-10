from threading import Lock

from sentence_transformers import CrossEncoder


class CrossEncoderManager:
    """
    Owns the application's cross encoder models.

    Responsibilities
    ----------------
    - Register cross encoder models.
    - Load cross encoder models.
    - Cache loaded models.
    - Provide CrossEncoder instances.

    Future
    ------
    - Background initialization.
    - Model unloading.
    - Model switching.
    """

    def __init__(self) -> None:
        self._models: dict[str, CrossEncoder | None] = {}
        self._locks: dict[str, Lock] = {}

    def register(
        self,
        model_name: str,
    ) -> None:
        """
        Register a cross encoder model.

        Safe to call multiple times.
        """

        self._models.setdefault(
            model_name,
            None,
        )

    def load_model(
        self,
        model_name: str,
    ) -> None:
        """
        Load a cross encoder model.

        Safe to call multiple times.
        """

        self.register(model_name)

        if self._models[model_name] is not None:
            return

        lock = self._locks.setdefault(
            model_name,
            Lock(),
        )

        with lock:
            if self._models[model_name] is not None:
                return

            print(
                f"Loading cross encoder model '{model_name}'..."
            )

            self._models[model_name] = CrossEncoder(
                model_name,
            )

            print(
                f"Cross encoder model '{model_name}' loaded."
            )

    def initialize(self) -> None:
        """
        Load all registered cross encoder models.
        """

        for model_name in self._models:
            self.load_model(model_name)

    def get_model(
        self,
        model_name: str,
    ) -> CrossEncoder:
        """
        Get a cross encoder model.

        Automatically loads the model if necessary.
        """

        self.load_model(model_name)

        model = self._models[model_name]
        assert model is not None

        return model