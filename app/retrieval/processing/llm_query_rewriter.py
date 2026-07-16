"""
LLM query rewriter.

Responsibilities
----------------
Rewrite user queries into standalone retrieval queries.

This implementation uses an LLM to understand
conversation context and improve retrieval quality.
"""

from __future__ import annotations

from app.models.base import BaseModel
from app.models.model_manager import ModelManager
from app.retrieval.processing.base_query_rewriter import (
    BaseQueryRewriter,
)
from langchain_core.messages import (
    SystemMessage
)
from pydantic import BaseModel


SYSTEM_PROMPT = """
You are a query rewriting assistant.

Your task is to rewrite the user's latest query into a
standalone search query for Retrieval-Augmented Generation (RAG).

Always return valid JSON.

Schema:

{
  "rewritten_query": string,
}

Rules
-----
- Preserve the user's original intent.
- Expand pronouns using the conversation history.
- Keep important keywords.
- Remove conversational filler.
- Do NOT answer the question.
- Do NOT invent information.
- Output JSON only.
""".strip()

class RewrittenQuery(BaseModel):
    rewritten_query: str

class LLMQueryRewriter(BaseQueryRewriter):
    """
    Rewrite retrieval queries using an LLM.
    """

    def __init__(
        self,
        model_manager: ModelManager,
    ) -> None:

        self._model_manager = model_manager

    def rewrite(
        self,
        query: str,
        history: list[str] | None = None,
    ) -> str:
        """
        Rewrite a user query into a standalone retrieval query.
        """

        history = history or []

        system_prompt = self._build_prompt(
            query=query,
            history=history,
        )

        result = self._model_manager.invoke_structured(
            messages=[
                SystemMessage(
                    content=system_prompt
                ),
            ],
            response_model=RewrittenQuery,
        )

        return result.rewritten_query

    def _build_prompt(
        self,
        query: str,
        history: list[str],
    ) -> str:
        """
        Build the prompt for the LLM.
        """

        conversation = "\n".join(history)

        return f"""
{SYSTEM_PROMPT}
Conversation History
--------------------
{conversation}

Latest User Query
-----------------
{query}

Rewrite the latest user query into a standalone retrieval query.
Only output the rewritten query as JSON.
""".strip()