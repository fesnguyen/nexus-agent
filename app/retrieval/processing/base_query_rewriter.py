from __future__ import annotations

from abc import ABC, abstractmethod


class BaseQueryRewriter(ABC):
    """
    Base class for query rewriters.

    A query rewriter transforms a user query into a better
    retrieval query before embedding and vector search.
    """

    @abstractmethod
    def rewrite(
        self,
        query: str,
    ) -> str:
        """
        Rewrite a user query.

        Parameters
        ----------
        query:
            Original user query.

        Returns
        -------
        str
            Rewritten query.
        """
        raise NotImplementedError