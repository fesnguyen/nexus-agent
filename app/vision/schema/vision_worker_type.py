from enum import StrEnum


class VisionWorkerType(StrEnum):
    """
    Supported vision worker implementations.

    Each worker encapsulates a concrete vision model and may
    provide one or more vision capabilities.
    """
    # Incompatibility for florence, check known_issues.md
    FLORENCE = "florence"

    # Future workers
    MINI_CPM = "mini_cpm"

    SMOL_VLM = "smol_vlm"
    PADDLE_OCR = "paddle_ocr"
    SIGLIP = "siglip"