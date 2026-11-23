"""Semantic Scholar Academic Graph API client."""

from __future__ import annotations

import json
import logging
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

PAPER_SEARCH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search"
PAPER_FIELDS = "title,authors,year,citationCount,abstract,url,paperId"


class SemanticScholarError(RuntimeError):
    """Raised when scholarly search fails or returns an invalid response."""


class SemanticScholarClient:
    """Search Semantic Scholar and preserve its relevance ranking."""

    def __init__(self, *, timeout: float = 20.0, api_key: str | None = None) -> None:
        self._timeout = timeout
        self._api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    def search_papers(self, query: str, *, limit: int = 100) -> list[dict[str, Any]]:
        """Return scholarly search results in relevance order.

        Semantic Scholar's search endpoint orders results by relevance. When
        equal explicit relevance scores are available, citation count is used
        as a secondary ranking signal.
        """
        if not query.strip():
            raise ValueError("A non-empty search query is required.")
        if limit < 1:
            raise ValueError("Search limit must be greater than zero.")

        params = urlencode({"query": query, "limit": min(limit, 100), "fields": PAPER_FIELDS})
        headers = {
            "Accept": "application/json",
            "User-Agent": "AI-Research-Assistant/1.0 (scholarly paper discovery)",
        }
        if self._api_key:
            headers["x-api-key"] = self._api_key
        request = Request(f"{PAPER_SEARCH_ENDPOINT}?{params}", headers=headers)
        try:
            with urlopen(request, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            logger.warning("Semantic Scholar returned HTTP %s", exc.code)
            if exc.code == 429:
                raise SemanticScholarError(
                    "Semantic Scholar rate limit reached. Please wait briefly and try again."
                ) from exc
            raise SemanticScholarError(
                f"Semantic Scholar paper search failed with HTTP {exc.code}."
            ) from exc
        except (URLError, TimeoutError) as exc:
            logger.exception("Could not reach Semantic Scholar")
            raise SemanticScholarError(
                "Could not reach Semantic Scholar. Check your connection and try again."
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            logger.exception("Semantic Scholar returned an unreadable response")
            raise SemanticScholarError(
                "Semantic Scholar returned an unreadable response."
            ) from exc

        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise SemanticScholarError("Semantic Scholar returned an unexpected response format.")

        records = [
            dict(item, _relevance_rank=index)
            for index, item in enumerate(payload["data"])
            if isinstance(item, dict)
        ]
        records.sort(
            key=lambda item: (
                -self._relevance_value(item, item["_relevance_rank"]),
                -self._citation_count(item.get("citationCount")),
                item["_relevance_rank"],
            )
        )
        return records

    @staticmethod
    def _relevance_value(paper: dict[str, Any], rank: int) -> float:
        """Use an API score when available; otherwise preserve returned order."""
        score = paper.get("score")
        if isinstance(score, (int, float)):
            return float(score)
        return -float(rank)

    @staticmethod
    def _citation_count(value: object) -> int:
        """Normalize citation counts for safe sorting."""
        return value if isinstance(value, int) and value >= 0 else 0
