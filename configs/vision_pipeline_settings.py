from app.vision.schema.vision_worker_type import VisionWorkerType

# Incompatibility for florence, check known_issues.md
FLORENCE_WORKER_MODEL = "microsoft/Florence-2-base-ft"

# OOM, need to check for alightweight checkpoint
MINI_CPM_WORKER_MODEL = "openbmb/MiniCPM-V-2_6"

SMOL_VLM_WORKER_MODEL = "HuggingFaceTB/SmolVLM-500M-Instruct"

RAPID_OCR_WORKER_MODEL = "RapidOCR"

# Capability backends
VISION_CAPTIONER_WORKER = VisionWorkerType.SMOL_VLM

VISION_OCR_WORKER = VisionWorkerType.RAPID_OCR