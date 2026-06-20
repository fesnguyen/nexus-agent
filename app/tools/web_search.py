from typing import Any

import requests

from app.tools.base import BaseTool
from app.tools.schemas.tool_schemas import WebSearchInput


class WebSearchTool(BaseTool):
    """
    Search the web using a self-hosted SearXNG instance.

    Returns:
        A normalized list of search results independent
        of the underlying search provider.
    """

    name = "web_search"

    description = (
        "Search the web using SearXNG."
    )

    input_schema = WebSearchInput

    def __init__(
        self,
        searx_url: str = "http://localhost:8080"
    ) -> None:
        self.searx_url = searx_url.rstrip("/")

    def run(
        self,
        tool_input: WebSearchInput
    ) -> list[dict[str, Any]]:
        """
        Execute a web search.

        Args:
            tool_input:
                Search query and result count.

        Returns:
            Normalized search results.
        """

        try:
            response = requests.get(
                f"{self.searx_url}/search",
                params={
                    "q": tool_input.query,
                    "format": "json",
                },
                timeout=10,
            )

            # Raises HTTPError for 4xx/5xx responses.
            response.raise_for_status()

        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Failed to communicate with SearXNG: {exc}"
            ) from exc

        try:
            payload = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "SearXNG returned invalid JSON."
            ) from exc

        results = []

        for item in payload.get("results", [])[
            : tool_input.num_results
        ]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                }
            )

        return results