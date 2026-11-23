"""Key-concept extraction service."""

from backend.prompts import CONCEPTS_PROMPT
from backend.services._validation import require_text_list
from backend.services.summary_service import JsonGenerator


class ConceptsService:
    """Extract the central concepts for a research topic."""

    def __init__(self, client: JsonGenerator) -> None:
        self._client = client

    def generate(self, topic: str, *, expanded: bool = False) -> list[str]:
        """Generate and validate key concepts, adding breadth for broad topics."""
        concept_count = "8-10" if expanded else "5-8"
        prompt = CONCEPTS_PROMPT.format(topic=topic, concept_count=concept_count)
        return require_text_list(self._client.generate_json(prompt), "concepts")

    def extract(self, topic: str) -> list[str]:
        """Backward-compatible alias for concept generation."""
        return self.generate(topic)
