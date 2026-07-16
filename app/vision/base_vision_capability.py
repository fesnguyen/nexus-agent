from __future__ import annotations

from abc import ABC
from pathlib import Path
from tkinter import Image
from typing import Any

from app.vision.vision_worker_manager import VisionWorkerManager
from app.vision.schema.vision_worker_type import VisionWorkerType


class BaseVisionCapability(ABC):
    """
    Base class for all vision capabilities.
    """

    def __init__(
        self,
        worker_manager: VisionWorkerManager,
        worker_type: VisionWorkerType,
    ) -> None:
        self._worker_manager = worker_manager
        self._worker_type = worker_type

        self._worker_manager.register(
            worker_type=self._worker_type,
        )

    def _process(
        self,
        image: Image.Image,
        **kwargs: Any,
    ) -> Any:
        worker = self._worker_manager.get_worker(
            self._worker_type,
        )

        return worker.process(
            image=image,
            **kwargs,
        )