#<Not used florence-2 anymore since version incompability>

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import (
    AutoImageProcessor,
    AutoModelForCausalLM,
    AutoProcessor,
)

from app.vision.base_vision_worker import BaseVisionWorker


class FlorenceWorker(BaseVisionWorker):
    """
    Florence-2 vision worker.

    Supports multiple vision tasks by changing the prompt.

    Examples
    --------
    <CAPTION>
    <OCR>
    <OD>
    <DENSE_REGION_CAPTION>
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:
        super().__init__(model_name)

        self._processor: AutoImageProcessor | None = None
        self._model: AutoModelForCausalLM | None = None

    def load(self) -> None:
        """
        Load the Florence model.

        Safe to call multiple times.
        """

        if self.is_loaded:
            return

        print(
            f"Loading Florence worker '{self.model_name}'..."
        )

        self._processor = AutoImageProcessor.from_pretrained(
            self.model_name,
            trust_remote_code=False,
        )

        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        
        self._loaded = True

        print(
            f"Florence worker '{self.model_name}' loaded."
        )

    def unload(self) -> None:
        """
        Release model resources.
        """

        self._processor = None
        self._model = None

        self._loaded = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def process(
        self,
        image_path: Path,
        prompt: str,
    ) -> Any:
        """
        Execute a Florence vision task.

        Parameters
        ----------
        image_path
            Path to the image.

        prompt
            Florence task prompt.

            Examples
            --------
            <CAPTION>
            <OCR>
            <OD>
            <DENSE_REGION_CAPTION>

        Returns
        -------
        Any
            Parsed Florence output.
        """

        if not self.is_loaded:
            raise RuntimeError(
                "FlorenceWorker has not been loaded."
            )

        assert self._processor is not None
        assert self._model is not None

        image = Image.open(image_path).convert("RGB")

        inputs = self._processor(
            text=prompt,
            images=image,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self._model.device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            generated_ids = self._model.generate(
                **inputs,
                max_new_tokens=512,
                num_beams=3,
                do_sample=False,
            )

        generated_text = self._processor.batch_decode(
            generated_ids,
            skip_special_tokens=False,
        )[0]

        result = self._processor.post_process_generation(
            generated_text,
            task=prompt,
            image_size=image.size,
        )

        return result