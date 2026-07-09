import json
import re

from app.memory.long_term.models import Memory, MemoryExtractionResult
from app.memory.long_term.models import MemoryType
from app.models.base import BaseLLM

from langchain_core.messages import SystemMessage, HumanMessage

from app.models.model_manager import ModelManager
from app.tools.registry import ToolRegistry


MEMORY_EXTRACTION_PROMPT = """
You are a memory extraction system. Identify information to store as long-term memory.

Store only:
1. preference: Permanent settings, coding style, constraints (e.g., framework choices).
2. fact: Static truths about the user's hardware, OS, background, or environment.
3. project: Multi-step goals, requirements, or tech stacks of active applications.
4. context: Fluid situational background (e.g., active debugging tasks, file states).
5. episode: Narrative, timestamped logs of specific past milestones or solved bugs.

Do NOT store: Greetings, small talk, raw tool outputs, or transient requests.

Return JSON only. Keep 'content' strings self-contained. The key "memories" always exist even only one memory element.

Schema:
{
  "memories": [
    {
      "type": "preference" | "fact" | "project" | "context" | "episode",
      "content": "clear summary string"
    }
  ]
}
"""


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