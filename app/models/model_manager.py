from threading import Lock

from app.models.base import BaseLLM
from app.models.factory import ModelFactory
from app.tools.registry import ToolRegistry


class ModelManager:
    """
    Owns the application's active language model.

    Responsibilities
    ----------------
    - Own the active model.
    - Load the model.
    - Provide inference.
    - (Future) Switch models.
    - (Future) Unload models.
    """

    def __init__(
        self,
        model_name: str,
        model_path: str,
        tool_registry: ToolRegistry,
    ) -> None:
        self._model_name = model_name
        self._model_path = model_path
        self._tool_registry = tool_registry

        self._model: BaseLLM | None = None
        self._lock = Lock()

    @property
    def current_model_name(self) -> str:
        return self._model_name

    def initialize(self) -> None:
        """
        Load the active model.

        Safe to call multiple times.
        """
        if self._model is not None:
            return

        # Lock method again other call
        with self._lock:
            if self._model is not None:
                return

            self._model = ModelFactory.create(
                self._model_name,
                self._model_path,
                tool_registry=self._tool_registry,
            )

    def invoke(self, *args, **kwargs):
        """
        Run inference using the active model.
        """
        if self._model is None:
            self.initialize()

        return self._model.invoke(*args, **kwargs)