import json
import re

from app.memory.long_term.models import Memory, MemoryExtractionResult
from app.memory.long_term.models import MemoryType
from app.models.base import BaseLLM

from langchain_core.messages import SystemMessage, HumanMessage

from app.models.model_manager import ModelManager
from app.prompt.system_prompts import MEMORY_EXTRACTION_PROMPT
from app.tools.registry import ToolRegistry

class MemoryExtractor:

    def __init__(self, model_manager: ModelManager) -> None:
        self._model_manager = model_manager

    def extract(
        self,
        messages,
    ) -> list:

        conversation = []

        for message in messages:

            role = getattr(
                message,
                "type",
                "unknown",
            )

            conversation.append(
                f"{role}: {message.content}"
            )

        result = self._model_manager.invoke(
            messages=[
                SystemMessage(
                    content=MEMORY_EXTRACTION_PROMPT
                ),
                HumanMessage(
                    content="\n".join(
                        conversation
                    )
                ),
            ],
            tool=ToolRegistry(),
            response_model=MemoryExtractionResult,
        )

        return result.memories