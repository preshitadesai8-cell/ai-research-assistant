"""Offline tests for planning, task execution, validation, and report assembly."""

from __future__ import annotations

from collections import deque
from types import SimpleNamespace
from typing import Any

import pytest

from backend import groq_client
from backend.agent import ResearchAgent as CompatibleResearchAgent
from backend.models.execution_plan import ExecutionPlan
from backend.planner_agent import PlannerAgent
from backend.research_agent import ResearchAgent
from backend.services._validation import ServiceResponseError
from backend.services.concepts_service import ConceptsService
from backend.services.future_directions_service import FutureDirectionService
from backend.services.keyword_service import KeywordService
from backend.services.questions_service import QuestionsService
from backend.services.roadmap_service import RoadmapService
from backend.services.summary_service import SummaryService
from backend.validator_agent import ValidatorAgent
from config.settings import Settings


class FakeClient:
    """Return queued JSON objects without calling an external model."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = deque(responses)
        self.prompts: list[str] = []

    def generate_json(self, prompt: str) -> dict[str, Any]:
        self.prompts.append(prompt)
        return self._responses.popleft()


def baseline_responses() -> list[dict[str, Any]]:
    return [
        {
            "summary": (
                "A concise overview explains the topic and its main context, "
                "including important applications, core ideas, and common limitations."
            )
        },
        {"concepts": ["Foundations", "Applications", "Evaluation"]},
        {
            "questions": [
                "How does the approach work?",
                "What evidence supports its use?",
                "What are its limitations?",
            ]
        },
        {
            "further_study": ["Ethics", "Evaluation"],
            "roadmap": [
                {"step": "Learn foundations", "description": "Study the core principles."},
                {"step": "Review applications", "description": "Compare practical use cases."},
                {"step": "Apply the ideas", "description": "Complete a small project."},
            ],
        },
    ]


def research_responses() -> list[dict[str, Any]]:
    responses = baseline_responses()
    responses.insert(3, {"future_directions": ["Scalable methods", "Open evaluation"]})
    responses.insert(4, {"research_keywords": ["systematic review", "benchmarking"]})
    return responses


def test_agent_initialization_and_legacy_import() -> None:
    agent = ResearchAgent(client=FakeClient(baseline_responses()))
    assert isinstance(agent, ResearchAgent)
    assert CompatibleResearchAgent is ResearchAgent


@pytest.mark.parametrize(
    ("topic", "topic_type", "difficulty", "actions"),
    [
        (
            "Machine Learning",
            "technical",
            "intermediate",
            ("summary", "concepts", "questions", "roadmap"),
        ),
        (
            "Quantum Computing Research Trends",
            "research",
            "advanced",
            (
                "summary",
                "concepts",
                "questions",
                "future_directions",
                "research_keywords",
                "roadmap",
            ),
        ),
    ],
)
def test_planner_classifies_topics_and_selects_dynamic_tasks(
    topic: str, topic_type: str, difficulty: str, actions: tuple[str, ...]
) -> None:
    plan = PlannerAgent().plan(topic)

    assert plan.topic_type == topic_type
    assert plan.difficulty == difficulty
    assert plan.actions == actions
    assert plan.research_depth == ("deep" if topic_type == "research" else "standard")


def test_planner_detects_beginner_and_broad_topics() -> None:
    beginner_plan = PlannerAgent().plan("Beginner guide to machine learning")
    broad_plan = PlannerAgent().plan("Introduction to climate change")

    assert beginner_plan.difficulty == "beginner"
    assert beginner_plan.research_depth == "introductory"
    assert "Beginner wording selected a simplified roadmap." in beginner_plan.reasoning
    assert broad_plan.is_broad
    assert "research_keywords" in broad_plan.actions


@pytest.mark.parametrize("topic", ["", "  "])
def test_planner_rejects_empty_topic(topic: str) -> None:
    with pytest.raises(ValueError, match="research topic"):
        PlannerAgent().plan(topic)


def test_create_report_executes_baseline_tasks_and_assembles_metadata() -> None:
    client = FakeClient(baseline_responses())
    report = ResearchAgent(client=client).create_report("  Machine Learning  ")

    assert report["topic"] == "Machine Learning"
    assert report["topic_type"] == "technical"
    assert report["difficulty"] == "intermediate"
    assert report["execution_plan"]["actions"] == [
        "summary",
        "concepts",
        "questions",
        "roadmap",
    ]
    assert report["report"]["summary"].startswith("A concise overview")
    assert len(report["report"]["key_concepts"]) == 3
    assert len(report["report"]["research_questions"]) == 3
    assert "future_directions" not in report["report"]
    assert report["metadata"]["executed_tasks"] == report["execution_plan"]["actions"]
    assert report["metadata"]["external_sources_used"] is False
    assert report["quality_score"] == 100
    assert report["quality_status"] == "high_quality"
    assert len(client.prompts) == 4
    assert "intermediate-level" in client.prompts[2]
    assert "an intermediate-appropriate, progressive" in client.prompts[3]


def test_research_topic_executes_research_only_tasks() -> None:
    client = FakeClient(research_responses())
    report = ResearchAgent(client=client).create_report("Quantum Computing Research Trends")

    assert report["execution_plan"]["actions"] == [
        "summary",
        "concepts",
        "questions",
        "future_directions",
        "research_keywords",
        "roadmap",
    ]
    assert report["metadata"]["executed_tasks"] == report["execution_plan"]["actions"]
    assert report["report"]["future_directions"] == ["Scalable methods", "Open evaluation"]
    assert report["report"]["research_keywords"] == ["systematic review", "benchmarking"]
    assert len(client.prompts) == 6
    assert "advanced-level" in client.prompts[2]


def test_broad_topic_expands_concepts_and_selects_keywords() -> None:
    responses = baseline_responses()
    responses.append({"research_keywords": ["regional impacts", "adaptation policy"]})
    client = FakeClient(responses)
    report = ResearchAgent(client=client).create_report("Introduction to climate change")

    assert report["execution_plan"]["is_broad"] is True
    assert "research_keywords" in report["execution_plan"]["actions"]
    assert "8-10 central concepts" in client.prompts[1]
    assert report["report"]["research_keywords"] == ["regional impacts", "adaptation policy"]


def test_validator_detects_missing_and_empty_required_sections() -> None:
    plan = PlannerAgent().plan("Machine Learning")
    result = ValidatorAgent().validate(
        plan,
        {"summary": "", "key_concepts": ["one"], "research_questions": ["why?"]},
    )

    assert result.score < 100
    assert result.status == "low_quality"
    assert any("summary" in warning and "empty" in warning for warning in result.warnings)
    assert any("learning_roadmap" in warning and "missing" in warning for warning in result.warnings)


def test_execution_plan_rejects_unknown_task() -> None:
    with pytest.raises(ValueError, match="Unknown execution plan actions"):
        ExecutionPlan(
            topic="Example",
            topic_type="academic",
            difficulty="foundational",
            complexity="low",
            research_depth="standard",
            actions=("summary", "not_a_task"),
            reasoning=(),
        )


def test_summary_service_returns_validated_summary() -> None:
    service = SummaryService(FakeClient([{"summary": "Validated summary."}]))
    assert service.generate("Climate change") == "Validated summary."


def test_concepts_service_returns_validated_concepts() -> None:
    service = ConceptsService(FakeClient([{"concepts": ["Climate", "Adaptation"]}]))
    assert service.extract("Climate change") == ["Climate", "Adaptation"]


def test_questions_service_returns_validated_questions() -> None:
    service = QuestionsService(FakeClient([{"questions": ["What changes over time?"]}]))
    assert service.generate("Climate change") == ["What changes over time?"]


def test_roadmap_service_returns_complete_learning_plan() -> None:
    response = {
        "further_study": ["Policy"],
        "roadmap": [{"step": "Start", "description": "Read an introduction."}],
    }
    assert RoadmapService(FakeClient([response])).generate("Climate change") == response


def test_optional_research_services_validate_responses() -> None:
    directions = FutureDirectionService(
        FakeClient([{"future_directions": ["Better evaluation"]}])
    )
    keywords = KeywordService(FakeClient([{"research_keywords": ["systematic review"]}]))

    assert directions.generate("AI research trends") == ["Better evaluation"]
    assert keywords.generate("AI research trends") == ["systematic review"]


def test_service_rejects_invalid_model_response() -> None:
    service = ConceptsService(FakeClient([{"concepts": ["valid", 3]}]))
    with pytest.raises(ServiceResponseError, match="concepts"):
        service.extract("Climate change")


def test_groq_client_uses_responses_api_and_parses_json(monkeypatch: pytest.MonkeyPatch) -> None:
    request: dict[str, Any] = {}

    class FakeResponses:
        def create(self, **kwargs: Any) -> SimpleNamespace:
            request.update(kwargs)
            return SimpleNamespace(output_text='{"summary": "A useful summary."}')

    class FakeOpenAI:
        def __init__(self, **kwargs: Any) -> None:
            request["client"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setattr(groq_client, "load_settings", lambda: Settings(groq_api_key="test-key"))
    monkeypatch.setattr(groq_client, "OpenAI", FakeOpenAI)

    result = groq_client.GroqClient().generate_json("Summarize this topic.")

    assert result == {"summary": "A useful summary."}
    assert request["client"]["base_url"] == "https://api.groq.com/openai/v1"
    assert request["model"] == "openai/gpt-oss-20b"
    assert request["input"] == "Summarize this topic."
