"""Scholarly paper discovery service backed only by Semantic Scholar records."""

from __future__ import annotations

from typing import Any, Protocol

from backend.tools.semantic_scholar_client import SemanticScholarClient

PAPER_RESULT_LIMIT = 5


class PaperSearchClient(Protocol):
    """Interface implemented by the Semantic Scholar client and test doubles."""

    def search_papers(self, query: str, *, limit: int = 100) -> list[dict[str, Any]]: ...


class PaperService:
    """Search, rank, and normalize real papers returned by Semantic Scholar."""

    def __init__(self, client: PaperSearchClient | None = None) -> None:
        self._client = client if client is not None else SemanticScholarClient()

    def search_papers(self, topic: str) -> list[dict[str, Any]]:
        """Return up to five relevant papers with source-backed metadata.

        No LLM is used to create or enrich paper records. ``why_it_matters`` is
        a deterministic note describing the record's match to the query.
        """
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("A non-empty research topic is required to search for papers.")

        results = self._client.search_papers(topic.strip(), limit=100)
        normalized = [
            self._normalize_paper(record, topic.strip())
            for record in results
            if isinstance(record, dict)
        ]
        return normalized[:PAPER_RESULT_LIMIT]

    @staticmethod
    def _normalize_paper(paper: dict[str, Any], topic: str) -> dict[str, Any]:
        title = paper.get("title")
        title = title.strip() if isinstance(title, str) else ""

        raw_authors = paper.get("authors")
        authors: list[str] = []
        if isinstance(raw_authors, list):
            authors = [
                author["name"].strip()
                for author in raw_authors
                if isinstance(author, dict)
                and isinstance(author.get("name"), str)
                and author["name"].strip()
            ]

        year = paper.get("year")
        year = year if isinstance(year, int) and year > 0 else None
        citation_count = paper.get("citationCount")
        citation_count = (
            citation_count
            if isinstance(citation_count, int) and citation_count >= 0
            else 0
        )
        abstract = paper.get("abstract")
        abstract = abstract.strip() if isinstance(abstract, str) else ""

        url = paper.get("url")
        if not isinstance(url, str) or not url.strip():
            paper_id = paper.get("paperId")
            url = (
                f"https://www.semanticscholar.org/paper/{paper_id}"
                if isinstance(paper_id, str) and paper_id.strip()
                else ""
            )

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "citation_count": citation_count,
            "abstract": abstract,
            "url": url.strip() if isinstance(url, str) else "",
            "why_it_matters": (
                f"Selected by Semantic Scholar as a relevant match for “{topic}”."
            ),
            "source": "Semantic Scholar",
            "relevance_rank": paper.get("_relevance_rank"),
        }
