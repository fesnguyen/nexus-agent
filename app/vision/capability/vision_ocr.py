"""
OCR capability.
"""

from __future__ import annotations

from PIL import Image

from app.vision.base_vision_capability import BaseVisionCapability
from app.vision.vision_worker_manager import VisionWorkerManager
from configs.vision_pipeline_settings import (
    VISION_OCR_WORKER,
)


class VisionOCR(BaseVisionCapability):
    """
    Optical Character Recognition (OCR) capability.

    Uses the configured OCR worker to extract visible
    text from an image.
    """

    def __init__(
        self,
        worker_manager: VisionWorkerManager,
    ) -> None:
        super().__init__(
            worker_manager=worker_manager,
            worker_type=VISION_OCR_WORKER,
        )

    def extract(
        self,
        image: Image.Image,
    ) -> str:
        """
        Extract visible text from an image.
        """

        return self._process(
            image=image,
        )