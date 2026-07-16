from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import (
    AutoModel,
    AutoTokenizer,
)

from app.vision.base_vision_worker import BaseVisionWorker


class MiniCPMVWorker(BaseVisionWorker):
    """
    MiniCPM-V 2.6 worker.

    This worker supports multiple vision tasks by changing the prompt.

    Examples
    --------
    Caption
        "Describe this image in detail."

    OCR
        "Extract all visible text from this image."

    Object Detection
        "List every visible object in this image."
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:
        super().__init__(model_name)

        self._model: Any | None = None
        self._tokenizer: AutoTokenizer | None = None

    def load(self) -> None:
        """
        Load the MiniCPM-V model.

        Safe to call multiple times.
        """

        if self.is_loaded:
            return

        print(
            f"Loading MiniCPM-V worker '{self.model_name}'..."
        )

        self._model = AutoModel.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            attn_implementation="sdpa",
            torch_dtype=torch.bfloat16,
            resume_download=True,
        )

        self._model = (
            self._model
            .eval()
            .cuda()
        )

        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        )

        self._loaded = True

        print(
            f"MiniCPM-V worker '{self.model_name}' loaded."
        )

    def unload(self) -> None:
        """
        Release model resources.
        """

        self._model = None
        self._tokenizer = None

        self._loaded = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def process(
        self,
        image: Image.Image,
        prompt: str,
    ) -> str:
        """
        Execute a MiniCPM-V vision task.

        Parameters
        ----------
        image
            PIL image.

        prompt
            Natural language instruction.

        Returns
        -------
        str
            Model response.
        """

        if not self.is_loaded:
            raise RuntimeError(
                "MiniCPMVWorker has not been loaded."
            )

        assert self._model is not None
        assert self._tokenizer is not None

        messages = [
            {
                "role": "user",
                "content": [
                    image,
                    prompt,
                ],
            }
        ]

        response = self._model.chat(
            image=None,
            msgs=messages,
            tokenizer=self._tokenizer,
            sampling=False,
            stream=False,
        )

        return response