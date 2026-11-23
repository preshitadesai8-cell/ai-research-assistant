"""Offline tests for planning, task execution, validation, and report assembly."""

from __future__ import annotations

from collections import deque
from types import SimpleNamespace
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest

from backend import groq_client
from backend.agent import ResearchAgent as CompatibleResearchAgent
from backend.models.execution_plan import ExecutionPlan
from backend.planner_agent import PlannerAgent
from backend.research_agent import ResearchAgent
from backend.services.paper_service import PaperService
from backend.services._validation import ServiceResponseError
from backend.services.concepts_service import ConceptsService
from backend.services.future_directions_service import FutureDirectionService
from backend.services.keyword_service import KeywordService
from backend.services.questions_service import QuestionsService
from backend.services.roadmap_service import RoadmapService
from backend.services.summary_service import SummaryService
from backend.validator_agent import ValidatorAgent
from backend.tools import semantic_scholar_client
from backend.tools.semantic_scholar_client import SemanticScholarClient, SemanticScholarError
from config.settings import Settings


class FakeClient:
    """Return queued JSON objects without calling an external model."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = deque(responses)
        self.prompts: list[str] = []

    def generate_json(self, prompt: str) -> dict[str, Any]:
        self.prompts.append(prompt)
        return self._responses.popleft()


class FakePaperService:
    """Return real-shaped paper records without making a network request."""

    def __init__(self, papers: list[dict[str, Any]] | None = None) -> None:
        self.papers = papers if papers is not None else sample_papers()
        self.queries: list[str] = []

    def search_papers(self, topic: str) -> list[dict[str, Any]]:
        self.queries.append(topic)
        return self.papers


def sample_papers(count: int = 2) -> list[dict[str, Any]]:
    return [
        {
            "title": f"Verified scholarly paper {index}",
            "authors": ["Researcher One", "Researcher Two"],
            "year": 2024,
            "citation_count": 120 - index,
            "abstract": "An abstract retrieved from Semantic Scholar.",
            "url": f"https://www.semanticscholar.org/paper/paper-{index}",
            "why_it_matters": "Selected by Semantic Scholar as a relevant match.",
            "source": "Semantic Scholar",
            "relevance_rank": index - 1,
        }
        for index in range(1, count + 1)
    ]


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
    agent = ResearchAgent(
        client=FakeClient(baseline_responses()),
        paper_service=FakePaperService(),
    )
    assert isinstance(agent, ResearchAgent)
    assert CompatibleResearchAgent is ResearchAgent


@pytest.mark.parametrize(
    ("topic", "topic_type", "difficulty", "actions"),
    [
        (
            "Machine Learning",
            "technical",
            "intermediate",
            ("summary", "concepts", "questions", "roadmap", "papers"),
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
                "papers",
            ),
        ),
        (
            "Emerging technology: generative AI",
            "research",
            "advanced",
            (
                "summary",
                "concepts",
                "questions",
                "future_directions",
                "research_keywords",
                "roadmap",
                "papers",
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
    general_topic_plan = PlannerAgent().plan("Climate change")

    assert beginner_plan.difficulty == "beginner"
    assert beginner_plan.research_depth == "introductory"
    assert "Beginner wording selected a simplified roadmap." in beginner_plan.reasoning
    assert broad_plan.is_broad
    assert "research_keywords" in broad_plan.actions
    assert "papers" not in general_topic_plan.actions


@pytest.mark.parametrize("topic", ["", "  "])
def test_planner_rejects_empty_topic(topic: str) -> None:
    with pytest.raises(ValueError, match="research topic"):
        PlannerAgent().plan(topic)


def test_create_report_executes_baseline_tasks_and_assembles_metadata() -> None:
    client = FakeClient(baseline_responses())
    papers = FakePaperService()
    report = ResearchAgent(client=client, paper_service=papers).create_report("  Machine Learning  ")

    assert report["topic"] == "Machine Learning"
    assert report["topic_type"] == "technical"
    assert report["difficulty"] == "intermediate"
    assert report["execution_plan"]["actions"] == [
        "summary",
        "concepts",
        "questions",
        "roadmap",
        "papers",
    ]
    assert report["report"]["summary"].startswith("A concise overview")
    assert len(report["report"]["key_concepts"]) == 3
    assert len(report["report"]["research_questions"]) == 3
    assert "future_directions" not in report["report"]
    assert report["metadata"]["executed_tasks"] == report["execution_plan"]["actions"]
    assert report["metadata"]["papers_found"] == 2
    assert report["metadata"]["source"] == "Semantic Scholar"
    assert report["metadata"]["external_sources_used"] is True
    assert report["metadata"]["quality_score"] == report["quality_score"]
    assert report["report"]["recommended_papers"] == papers.papers
    assert papers.queries == ["Machine Learning"]
    assert report["quality_score"] == 100
    assert report["quality_status"] == "high_quality"
    assert len(client.prompts) == 4
    assert "intermediate-level" in client.prompts[2]
    assert "an intermediate-appropriate, progressive" in client.prompts[3]


def test_research_topic_executes_research_only_tasks() -> None:
    client = FakeClient(research_responses())
    report = ResearchAgent(
        client=client,
        paper_service=FakePaperService(),
    ).create_report("Quantum Computing Research Trends")

    assert report["execution_plan"]["actions"] == [
        "summary",
        "concepts",
        "questions",
        "future_directions",
        "research_keywords",
        "roadmap",
        "papers",
    ]
    assert report["metadata"]["executed_tasks"] == report["execution_plan"]["actions"]
    assert report["report"]["future_directions"] == ["Scalable methods", "Open evaluation"]
    assert report["report"]["research_keywords"] == ["systematic review", "benchmarking"]
    assert len(client.prompts) == 6
    assert "advanced-level" in client.prompts[2]


def test_paper_search_failure_keeps_report_and_exposes_ui_status() -> None:
    class RateLimitedPaperService:
        def search_papers(self, topic: str) -> list[dict[str, Any]]:
            raise SemanticScholarError(
                "Semantic Scholar rate limit reached. Please wait briefly and try again."
            )

    report = ResearchAgent(
        client=FakeClient(baseline_responses()),
        paper_service=RateLimitedPaperService(),
    ).create_report("Machine Learning")

    assert report["report"]["summary"]
    assert report["report"]["recommended_papers"] == []
    assert report["metadata"]["papers_found"] == 0
    assert "rate limit" in report["metadata"]["task_errors"]["papers"]
    assert any("at least one paper" in warning for warning in report["quality_warnings"])


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


def test_paper_service_normalizes_real_records_and_limits_to_five() -> None:
    class FakeSearchClient:
        def __init__(self) -> None:
            self.query = ""
            self.limit = 0

        def search_papers(self, query: str, *, limit: int = 100) -> list[dict[str, Any]]:
            self.query = query
            self.limit = limit
            return [
                {
                    "title": f"Paper {index}",
                    "authors": [{"name": "Author One"}, {"name": "Author Two"}],
                    "year": 2020 + index,
                    "citationCount": index * 10,
                    "abstract": "  A sourced abstract.  ",
                    "paperId": f"paper-{index}",
                    "_relevance_rank": index,
                }
                for index in range(6)
            ]

    client = FakeSearchClient()
    papers = PaperService(client).search_papers("Machine Learning")

    assert len(papers) == 5
    assert client.query == "Machine Learning"
    assert client.limit == 100
    assert papers[0]["title"] == "Paper 0"
    assert papers[0]["authors"] == ["Author One", "Author Two"]
    assert papers[0]["abstract"] == "A sourced abstract."
    assert papers[0]["url"] == "https://www.semanticscholar.org/paper/paper-0"
    assert papers[0]["source"] == "Semantic Scholar"
    assert "Semantic Scholar" in papers[0]["why_it_matters"]


def test_semantic_scholar_client_builds_request_and_preserves_relevance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "data": [
            {"title": "Most relevant", "score": 0.9, "citationCount": 1},
            {"title": "Tie, more cited", "score": 0.8, "citationCount": 50},
            {"title": "Tie, fewer cited", "score": 0.8, "citationCount": 4},
        ]
    }
    request_url = ""
    api_key_header = ""

    class FakeResponse:
        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            import json

            return json.dumps(payload).encode("utf-8")

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        nonlocal request_url, api_key_header
        request_url = request.full_url
        api_key_header = request.get_header("X-api-key")
        assert timeout == 20.0
        assert request.get_header("User-agent").startswith("AI-Research-Assistant")
        return FakeResponse()

    monkeypatch.setattr(semantic_scholar_client, "urlopen", fake_urlopen)
    papers = SemanticScholarClient(api_key="semantic-test-key").search_papers(
        "AI & machine learning", limit=20
    )

    query = parse_qs(urlparse(request_url).query)
    assert urlparse(request_url).path == "/graph/v1/paper/search"
    assert query["query"] == ["AI & machine learning"]
    assert query["limit"] == ["20"]
    assert "abstract" in query["fields"][0]
    assert api_key_header == "semantic-test-key"
    assert [paper["title"] for paper in papers] == [
        "Most relevant",
        "Tie, more cited",
        "Tie, fewer cited",
    ]


def test_semantic_scholar_client_surfaces_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    def raise_rate_limit(*args: object, **kwargs: object) -> None:
        raise HTTPError(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            429,
            "Too Many Requests",
            {},
            None,
        )

    monkeypatch.setattr(semantic_scholar_client, "urlopen", raise_rate_limit)
    with pytest.raises(SemanticScholarError, match="rate limit"):
        SemanticScholarClient().search_papers("Machine Learning")


def test_paper_validator_checks_minimum_count_titles_and_urls() -> None:
    plan = PlannerAgent().plan("Machine Learning")
    sections = {
        "summary": "A sufficiently long summary that explains the main topic clearly and accurately.",
        "key_concepts": ["Concept one", "Concept two", "Concept three"],
        "research_questions": ["Question one?", "Question two?", "Question three?"],
        "further_study": ["Area one"],
        "learning_roadmap": [
            {"step": "One", "description": "First step."},
            {"step": "Two", "description": "Second step."},
            {"step": "Three", "description": "Third step."},
        ],
        "recommended_papers": [{"title": " ", "url": ""}],
    }

    result = ValidatorAgent().validate(plan, sections)
    empty_result = ValidatorAgent().validate(plan, {**sections, "recommended_papers": []})

    assert any("empty title" in warning for warning in result.warnings)
    assert any("valid URL" in warning for warning in result.warnings)
    assert any("at least one paper" in warning for warning in empty_result.warnings)


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
