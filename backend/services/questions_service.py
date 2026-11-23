"""Research-question generation service."""

from backend.prompts import QUESTIONS_PROMPT
from backend.services._validation import require_text_list
from backend.services.summary_service import JsonGenerator


class QuestionsService:
    """Generate open-ended questions for further investigation."""

    def __init__(self, client: JsonGenerator) -> None:
        self._client = client

    def generate(self, topic: str, *, difficulty: str = "intermediate") -> list[str]:
        """Generate and validate research questions."""
        prompt = QUESTIONS_PROMPT.format(topic=topic, difficulty=difficulty)
        return require_text_list(self._client.generate_json(prompt), "questions")
