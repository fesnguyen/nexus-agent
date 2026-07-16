from dataclasses import dataclass


@dataclass(slots=True)
class VisionExtractionResult:
    """
    Unified output of the vision pipeline.
    """

    caption: str = ""

    ocr: str = ""