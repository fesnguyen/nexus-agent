from __future__ import annotations

from PIL import Image
from rapidocr_onnxruntime import RapidOCR

from app.vision.base_vision_worker import BaseVisionWorker


class RapidOCRWorker(BaseVisionWorker):
    """
    RapidOCR worker.

    Extracts visible text from an image using ONNX Runtime.
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:
        super().__init__(model_name)

        self._ocr: RapidOCR | None = None

    def load(self) -> None:
        """
        Load RapidOCR.

        Safe to call multiple times.
        """

        if self.is_loaded:
            return

        print(
            f"Loading RapidOCR worker '{self.model_name}'..."
        )

        self._ocr = RapidOCR()

        self._loaded = True

        print(
            f"RapidOCR worker '{self.model_name}' loaded."
        )

    def unload(self) -> None:
        """
        Release OCR resources.
        """

        self._ocr = None

        self._loaded = False

    def process(
        self,
        image: Image.Image,
    ) -> str:
        """
        Extract visible text from an image.

        Parameters
        ----------
        image
            PIL image.

        prompt
            Ignored. Exists to keep a consistent worker interface.

        Returns
        -------
        str
            Extracted text.
        """

        if not self.is_loaded:
            raise RuntimeError(
                "RapidOCRWorker has not been loaded."
            )

        assert self._ocr is not None

        result, _ = self._ocr(image)

        if result is None:
            return ""

        texts: list[str] = []

        for line in result:
            # line = [box, text, confidence]
            texts.append(line[1])

        return "\n".join(texts)