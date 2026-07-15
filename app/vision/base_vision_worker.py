from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from tkinter import Image
from typing import Any


class BaseVisionWorker(ABC):
    """
    Base class for all vision workers.

    A vision worker encapsulates a concrete vision model
    implementation (e.g. Florence-2, MiniCPM-V, PaddleOCR).

    Responsibilities
    ----------------
    - Own the model resources.
    - Load the model.
    - Release the model.
    - Execute inference.

    Notes
    -----
    - Workers are managed by VisionWorkerManager.
    - Multiple capabilities may share the same worker instance.
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:
        """
        Parameters
        ----------
        model_name
            Model identifier understood by this worker.
        """
        self._model_name = model_name
        self._loaded = False

    @property
    def model_name(self) -> str:
        """
        Return the configured model name.
        """
        return self._model_name

    @property
    def is_loaded(self) -> bool:
        """
        Whether the model has been loaded.
        """
        return self._loaded

    @abstractmethod
    def load(self) -> None:
        """
        Load model resources.

        Safe to call multiple times.
        """
        ...

    @abstractmethod
    def unload(self) -> None:
        """
        Release model resources.

        Safe to call multiple times.
        """
        ...

    @abstractmethod
    def process(
        self,
        image: Image.Image,
        prompt: str,
    ) -> Any:
        """
        Execute inference.

        Parameters
        ----------
        image_path
            Path to the input image.

        prompt
            Worker-specific instruction.

        Returns
        -------
        Any
            Worker-specific inference result.
        """
        ...