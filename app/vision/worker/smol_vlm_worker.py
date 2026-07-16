from __future__ import annotations

from typing import Any

import torch
from PIL import Image
from transformers import (
    AutoModelForImageTextToText,
    AutoProcessor,
)

from app.vision.base_vision_worker import BaseVisionWorker


class SmolVLMWorker(BaseVisionWorker):
    """
    SmolVLM vision worker.

    Supports any vision task through natural language prompts.

    Examples
    --------
    - Describe this image in detail.
    - Extract all visible text.
    - List every object in this image.
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:
        super().__init__(model_name)

        self._processor: AutoProcessor | None = None
        self._model: AutoModelForImageTextToText | None = None
        self._device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

    def load(self) -> None:
        """
        Load SmolVLM.

        Safe to call multiple times.
        """

        if self.is_loaded:
            return

        print(
            f"Loading SmolVLM worker '{self.model_name}'..."
        )

        self._processor = AutoProcessor.from_pretrained(
            self.model_name,
        )

        self._model = AutoModelForImageTextToText.from_pretrained(
            self.model_name,
            torch_dtype=(
                torch.bfloat16
                if self._device == "cuda"
                else torch.float32
            ),
            attn_implementation="sdpa",
        ).to(self._device)

        print("Model dtype:", self._model.dtype)
        print("Vision tower dtype:", self._model.model.vision_model.dtype)

        for name, tensor in self._model.named_buffers():
            if tensor.is_floating_point():
                print(name, tensor.dtype)

        for name, param in self._model.named_parameters():
            if param.dtype != torch.bfloat16:
                print(name, param.dtype)

        self._model.eval()

        self._loaded = True

        print(
            f"SmolVLM worker '{self.model_name}' loaded."
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
        image: Image.Image,
        prompt: str,
    ) -> str:
        """
        Execute a vision task.

        Parameters
        ----------
        image
            PIL image.

        prompt
            Natural language instruction.

        Returns
        -------
        str
            Generated response.
        """

        if not self.is_loaded:
            raise RuntimeError(
                "SmolVLMWorker has not been loaded."
            )

        assert self._processor is not None
        assert self._model is not None

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        chat_prompt = self._processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
        )

        inputs = self._processor(
            text=chat_prompt,
            images=[image],
            return_tensors="pt",
        )

        inputs = {
            key: (
                value.to(
                    device=self._device,
                    dtype=torch.bfloat16,
                )
                if torch.is_floating_point(value)
                else value.to(self._device)
            )
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            generated_ids = self._model.generate(
                **inputs,
                max_new_tokens=512,
            )

        prompt_length = inputs["input_ids"].shape[1]

        generated_ids = generated_ids[
            :,
            prompt_length:,
        ]

        response = self._processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]

        return response