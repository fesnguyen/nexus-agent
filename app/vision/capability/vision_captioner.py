from __future__ import annotations

from pathlib import Path
from tkinter import Image

from app.vision.base_vision_capability import BaseVisionCapability
from app.vision.schema.vision_worker_type import VisionWorkerType
from app.vision.vision_worker_manager import VisionWorkerManager
from configs.vision_pipeline_settings import (
    VISION_CAPTIONER_WORKER,
)


class VisionCaptioner(BaseVisionCapability):
    """
    Image captioning capability.

    Uses the configured vision worker to generate a natural
    language description of an image.
    """

    _SMOL_VLM_PROMPT = """
    Describe the image accurately and concisely.

    Focus only on information that is directly visible.

    Include:
    - The main subjects.
    - Important objects.
    - Their actions or interactions.
    - The surrounding scene if relevant.

    Do not guess, infer, or assume information that is not visible.
    Do not identify people.
    Do not include explanations, reasoning, or chain of thought.

    Return only the description.
    """

    # When create new or update a capability, make sure config the right prompt
    _PROMPTS = {
        VisionWorkerType.FLORENCE: "<CAPTION>",
        VisionWorkerType.SMOL_VLM: _SMOL_VLM_PROMPT,
    }

    def __init__(
        self,
        worker_manager: VisionWorkerManager,
    ) -> None:
        super().__init__(
            worker_manager=worker_manager,
            worker_type=VISION_CAPTIONER_WORKER,
        )

    def extract(
        self,
        image: Image.Image,
    ) -> str:
        """
        Generate an image caption.
        """

        return self._process(
            image=image,
            prompt=self._PROMPTS[self._worker_type],
        )