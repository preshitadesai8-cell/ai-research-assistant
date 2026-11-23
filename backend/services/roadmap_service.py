"""Further-study and learning-roadmap service."""

from typing import TypedDict

from backend.prompts import ROADMAP_PROMPT
from backend.services._validation import ServiceResponseError, require_text_list
from backend.services.summary_service import JsonGenerator


class RoadmapStep(TypedDict):
    """One ordered activity in the learning plan."""

    step: str
    description: str


class LearningPlan(TypedDict):
    """Further-study areas and ordered learning activities."""

    further_study: list[str]
    roadmap: list[RoadmapStep]


class RoadmapService:
    """Create further-study suggestions and an ordered learning roadmap."""

    def __init__(self, client: JsonGenerator) -> None:
        self._client = client

    def generate(self, topic: str, *, difficulty: str = "beginner") -> LearningPlan:
        """Generate and validate a complete learning plan."""
        roadmap_style = (
            "simple, beginner-friendly with short, accessible steps"
            if difficulty == "beginner"
            else f"an {difficulty}-appropriate, progressive"
        )
        prompt = ROADMAP_PROMPT.format(topic=topic, roadmap_style=roadmap_style)
        data = self._client.generate_json(prompt)
        further_study = require_text_list(data, "further_study")
        raw_steps = data.get("roadmap")
        if (
            not isinstance(raw_steps, list)
            or not raw_steps
            or any(
                not isinstance(item, dict)
                or not isinstance(item.get("step"), str)
                or not item["step"].strip()
                or not isinstance(item.get("description"), str)
                or not item["description"].strip()
                for item in raw_steps
            )
        ):
            raise ServiceResponseError(
                "Model response field 'roadmap' must be a non-empty list of step and description objects."
            )

        roadmap: list[RoadmapStep] = [
            {"step": item["step"].strip(), "description": item["description"].strip()}
            for item in raw_steps
        ]
        return {"further_study": further_study, "roadmap": roadmap}
