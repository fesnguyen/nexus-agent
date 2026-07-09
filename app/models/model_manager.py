from typing import Type

from pydantic import BaseModel

from app.contracts.agent_decision import AgentDecision
from app.models.base import BaseLLM
from app.models.factory import ModelFactory
from app.tools.registry import ToolRegistry


class ModelManager:
    """
    Owns the application's active language model.

    Future responsibilities:
    - Lazy loading
    - Model switching
    - Model unloading
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

    @property
    def current_model_name(self) -> str:
        return self._model_name

    def invoke(
            self, 
            messages,
            tool: ToolRegistry,
            response_model: Type[BaseModel] = AgentDecision,
    ) -> BaseModel:
        return self._ensure_model().invoke(
                messages,
                tool,
                response_model
            )
    
    def _ensure_model(self) -> BaseLLM:
        if self._model is None:
            print(f"Loading model: {self._model_name}")

            self._model = ModelFactory.create(
                self._model_name,
                self._model_path,
                tool_registry=self._tool_registry,
            )

        return self._model