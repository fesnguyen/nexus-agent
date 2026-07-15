from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.vision.schema.vision_extraction_result import VisionExtractionResult
from app.vision.capability.vision_captioner import VisionCaptioner


class VisionService:
    """
    High-level vision service.

    Orchestrates all vision capabilities.
    """

    def __init__(
        self,
        captioner: VisionCaptioner,
    ) -> None:
        self._captioner = captioner

    def extract(
        self,
        image_path: Path,
    ) -> VisionExtractionResult:
        """
        Extract structured information from an image.
        """

        image = Image.open(image_path).convert("RGB")

        return VisionExtractionResult(
            caption=self._captioner.extract(
                image=image,
            ),
        )