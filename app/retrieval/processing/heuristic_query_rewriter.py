"""
Heuristic query rewriter.

Responsibilities
----------------
Rewrite user queries using lightweight heuristic rules.

This implementation does not require an LLM.
"""

from __future__ import annotations

import re

from app.retrieval.processing.base_query_rewriter import (
    BaseQueryRewriter,
)


class HeuristicQueryRewriter(BaseQueryRewriter):
    """
    Rewrite queries using simple heuristic rules.
    """

    # Here is just a demo, since heuristic query rewrite is more about domain knowledge
    _ABBREVIATIONS = {
        "llm": "large language model",
        "rag": "retrieval augmented generation",
        "faiss": "facebook ai similarity search",
        "idx": "index",
        "db": "database",
        "cfg": "configuration",
        "ctx": "context",
        "msg": "message",
        "emb": "embedding",
        "embs": "embeddings",
        "vec": "vector",
        "repo": "repository",
    }

    def rewrite(
        self,
        query: str,
        history: list[str] | None = None,
    ) -> str:
        """
        Rewrite a user query.
        """

        query = self._normalize(query)

        query = self._expand_abbreviations(query)

        return query

    def _normalize(
        self,
        text: str,
    ) -> str:
        """
        Normalize query text.
        """

        text = text.lower()

        text = re.sub(
            r"[^\w\s]",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def _expand_abbreviations(
        self,
        text: str,
    ) -> str:
        """
        Expand common abbreviations.
        """

        words = []

        for word in text.split():

            words.append(
                self._ABBREVIATIONS.get(
                    word,
                    word,
                )
            )

        return " ".join(words)