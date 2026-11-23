"""Academic research-keyword generation service."""

from backend.prompts import RESEARCH_KEYWORDS_PROMPT
from backend.services._validation import require_text_list
from backend.services.summary_service import JsonGenerator


class KeywordService:
    """Generate keywords that help students search and narrow a topic."""

    def __init__(self, client: JsonGenerator) -> None:
        self._client = client

    def generate(self, topic: str) -> list[str]:
        """Generate and validate search keywords."""
        prompt = RESEARCH_KEYWORDS_PROMPT.format(topic=topic)
        return require_text_list(self._client.generate_json(prompt), "research_keywords")
