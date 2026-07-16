from __future__ import annotations

from threading import Lock

from app.vision.base_vision_worker import BaseVisionWorker
from app.vision.worker.florence_worker import FlorenceWorker
from app.vision.worker.mini_cpmv_worker import MiniCPMVWorker
from app.vision.worker.rapid_ocr_worker import RapidOCRWorker
from app.vision.worker.smol_vlm_worker import SmolVLMWorker
from configs.vision_pipeline_settings import (
    FLORENCE_WORKER_MODEL,
    MINI_CPM_WORKER_MODEL,
    RAPID_OCR_WORKER_MODEL,
    SMOL_VLM_WORKER_MODEL,
)
from app.vision.schema.vision_worker_type import VisionWorkerType


class VisionWorkerManager:
    """
    Owns all vision workers.

    Responsibilities
    ----------------
    - Create worker instances.
    - Share worker instances.
    - Load workers.
    - Unload workers.
    """

    def __init__(self) -> None:
        self._workers: dict[
            VisionWorkerType,
            BaseVisionWorker,
        ] = {}

        self._locks: dict[
            VisionWorkerType,
            Lock,
        ] = {}

    def register(
        self,
        worker_type: VisionWorkerType,
    ) -> None:
        """
        Register a worker.

        Safe to call multiple times.
        """

        if worker_type in self._workers:
            return

        match worker_type:

            case VisionWorkerType.FLORENCE:

                worker = FlorenceWorker(
                    model_name=FLORENCE_WORKER_MODEL,
                )


            case VisionWorkerType.MINI_CPM:
                worker = MiniCPMVWorker(
                    model_name=MINI_CPM_WORKER_MODEL
                )
            
            case VisionWorkerType.SMOL_VLM:
                worker = SmolVLMWorker(
                    model_name=SMOL_VLM_WORKER_MODEL
                )

            case VisionWorkerType.RAPID_OCR:
                worker = RapidOCRWorker(
                    model_name=RAPID_OCR_WORKER_MODEL
                )

            case _:
                raise ValueError(
                    f"Unsupported vision worker '{worker_type}'."
                )

        self._workers[worker_type] = worker

    def load_worker(
        self,
        worker_type: VisionWorkerType,
    ) -> None:
        """
        Load a worker.

        Safe to call multiple times.
        """

        worker = self.get_worker(
            worker_type,
            load=False,
        )

        if worker.is_loaded:
            return

        lock = self._locks.setdefault(
            worker_type,
            Lock(),
        )

        with lock:

            if worker.is_loaded:
                return

            worker.load()

    def unload_worker(
        self,
        worker_type: VisionWorkerType,
    ) -> None:
        """
        Unload a worker.
        """

        worker = self.get_worker(
            worker_type,
            load=False,
        )

        if worker.is_loaded:
            worker.unload()

    def initialize(self) -> None:
        """
        Load all registered workers.
        """

        for worker_type in self._workers:
            self.load_worker(worker_type)

    def get_worker(
        self,
        worker_type: VisionWorkerType,
        *,
        load: bool = True,
    ) -> BaseVisionWorker:
        """
        Get a registered worker.
        """

        self.register(worker_type)

        if load:
            self.load_worker(worker_type)

        return self._workers[worker_type]