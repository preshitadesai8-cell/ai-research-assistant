"""Summary-generation service."""

from typing import Protocol

from backend.prompts import SUMMARY_PROMPT
from backend.services._validation import require_text


class JsonGenerator(Protocol):
    """Interface implemented by the Groq client and test doubles."""

    def generate_json(self, prompt: str) -> dict[str, object]: ...


class SummaryService:
    """Generate concise topic summaries."""

    def __init__(self, client: JsonGenerator) -> None:
        self._client = client

    def generate(self, topic: str) -> str:
        """Generate and validate the topic summary."""
        return require_text(self._client.generate_json(SUMMARY_PROMPT.format(topic=topic)), "summary")
