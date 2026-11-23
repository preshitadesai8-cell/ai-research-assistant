"""Goal-driven research agent with planning, execution, and validation."""

from __future__ import annotations

import logging
from typing import Any

from backend.groq_client import GroqClient
from backend.models.execution_plan import ExecutionPlan
from backend.planner_agent import PlannerAgent
from backend.report_generator import ReportGenerator
from backend.services.concepts_service import ConceptsService
from backend.services.future_directions_service import FutureDirectionService
from backend.services.keyword_service import KeywordService
from backend.services.questions_service import QuestionsService
from backend.services.roadmap_service import RoadmapService
from backend.services.summary_service import SummaryService
from backend.validator_agent import ValidatorAgent

logger = logging.getLogger(__name__)

TASK_MAP: dict[str, type[Any]] = {
    "summary": SummaryService,
    "concepts": ConceptsService,
    "questions": QuestionsService,
    "roadmap": RoadmapService,
    "future_directions": FutureDirectionService,
    "research_keywords": KeywordService,
}


class ResearchAgent:
    """Plan a topic-specific workflow, execute selected tasks, and validate it."""

    def __init__(
        self,
        client: Any | None = None,
        planner: PlannerAgent | None = None,
        validator: ValidatorAgent | None = None,
        report_generator: ReportGenerator | None = None,
    ) -> None:
        """Create task services using one shared model client."""
        shared_client = client if client is not None else GroqClient()
        self._planner = planner if planner is not None else PlannerAgent()
        self._validator = validator if validator is not None else ValidatorAgent()
        self._report_generator = (
            report_generator if report_generator is not None else ReportGenerator()
        )
        self._services: dict[str, Any] = {
            action: service_type(shared_client) for action, service_type in TASK_MAP.items()
        }

    def plan(self, topic: str) -> ExecutionPlan:
        """Expose the planning stage for UI display and independent inspection."""
        return self._planner.plan(topic)

    def create_report(self, topic: str) -> dict[str, Any]:
        """Run planning, selected tasks, report validation, and report assembly."""
        plan = self.plan(topic)
        logger.info(
            "Planned research workflow: type=%s difficulty=%s tasks=%s",
            plan.topic_type,
            plan.difficulty,
            ", ".join(plan.actions),
        )
        task_outputs: dict[str, Any] = {}
        for action in plan.actions:
            logger.info("Executing research task: %s", action)
            task_outputs[action] = self._execute_action(action, plan)

        sections = self._report_generator.organize(task_outputs)
        validation = self._validator.validate(plan, sections)
        logger.info(
            "Research report validation completed: status=%s score=%s",
            validation.status,
            validation.score,
        )
        return self._report_generator.generate(plan, task_outputs, validation)

    def generate_summary(self, topic: str) -> str:
        """Run only the summary task."""
        return self._services["summary"].generate(self._validate_topic(topic))

    def extract_concepts(self, topic: str) -> list[str]:
        """Run only the concept task."""
        return self._services["concepts"].generate(self._validate_topic(topic))

    def generate_questions(self, topic: str) -> list[str]:
        """Run only the question task."""
        return self._services["questions"].generate(self._validate_topic(topic))

    def generate_roadmap(self, topic: str) -> dict[str, Any]:
        """Run only the roadmap task."""
        return self._services["roadmap"].generate(self._validate_topic(topic))

    def _execute_action(self, action: str, plan: ExecutionPlan) -> Any:
        """Dispatch a selected plan action to its task-specific service."""
        service = self._services[action]
        if action == "summary":
            return service.generate(plan.topic)
        if action == "concepts":
            return service.generate(plan.topic, expanded=plan.is_broad)
        if action == "questions":
            return service.generate(plan.topic, difficulty=plan.difficulty)
        if action == "roadmap":
            return service.generate(plan.topic, difficulty=plan.difficulty)
        if action == "future_directions":
            return service.generate(plan.topic)
        if action == "research_keywords":
            return service.generate(plan.topic)
        raise ValueError(f"No task executor is registered for action '{action}'.")

    @staticmethod
    def _validate_topic(topic: str) -> str:
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("Please enter a research topic.")
        return topic.strip()
