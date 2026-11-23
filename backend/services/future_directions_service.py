"""Future-research direction generation service."""

from backend.prompts import FUTURE_DIRECTIONS_PROMPT
from backend.services._validation import require_text_list
from backend.services.summary_service import JsonGenerator


class FutureDirectionService:
    """Suggest research directions and open problems for a topic."""

    def __init__(self, client: JsonGenerator) -> None:
        self._client = client

    def generate(self, topic: str) -> list[str]:
        """Generate and validate future research directions."""
        prompt = FUTURE_DIRECTIONS_PROMPT.format(topic=topic)
        return require_text_list(self._client.generate_json(prompt), "future_directions")
