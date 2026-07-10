from threading import Lock

from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    """
    Owns the application's embedding models.

    Responsibilities
    ----------------
    - Register embedding models.
    - Load embedding models.
    - Cache loaded models.
    - Provide SentenceTransformer instances.

    Future
    ------
    - Background initialization.
    - Model unloading.
    - Model switching.
    """

    def __init__(self) -> None:
        self._models: dict[str, SentenceTransformer | None] = {}
        self._locks: dict[str, Lock] = {}

    def register(
        self,
        model_name: str,
    ) -> None:
        """
        Register an embedding model.

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
        Load an embedding model.

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
                f"Loading embedding model '{model_name}'..."
            )

            self._models[model_name] = SentenceTransformer(
                model_name,
            )

            print(
                f"Embedding model '{model_name}' loaded."
            )

    def initialize(self) -> None:
        """
        Load all registered embedding models.
        """

        for model_name in self._models:
            self.load_model(model_name)

    def get_model(
        self,
        model_name: str,
    ) -> SentenceTransformer:
        """
        Get an embedding model.

        Automatically loads the model if necessary.
        """

        self.load_model(model_name)

        model = self._models[model_name]
        assert model is not None

        return model