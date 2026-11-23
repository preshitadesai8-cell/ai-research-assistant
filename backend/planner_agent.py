"""Rule-driven planning agent for topic analysis and task selection."""

from __future__ import annotations

import re

from backend.models.execution_plan import ExecutionPlan

RESEARCH_SIGNALS = (
    "research",
    "trend",
    "trends",
    "survey",
    "frontier",
    "state-of-the-art",
    "state of the art",
    "emerging",
    "literature review",
)
TECHNICAL_SIGNALS = (
    "machine learning",
    "artificial intelligence",
    "generative ai",
    "large language model",
    "blockchain",
    "robotics",
    "computer vision",
    "data science",
    "cloud computing",
    "internet of things",
    "neural network",
    "quantum",
    "algorithm",
    "programming",
    "computer science",
    "statistics",
    "cryptography",
    "biotechnology",
    "engineering",
    "mathematical",
)
BEGINNER_SIGNALS = ("beginner", "introductory", "basics", "for beginners", "starting with")
ADVANCED_SIGNALS = ("advanced", "doctoral", "phd", "frontier", "state-of-the-art")
BROAD_SIGNALS = (
    "overview",
    "introduction to",
    "impact of",
    "role of",
    "applications of",
    "in general",
    "basics of",
    "broad overview",
)


class PlannerAgent:
    """Analyze the topic and select an ordered set of research tasks."""

    def plan(self, topic: str) -> ExecutionPlan:
        """Classify a topic, assess its level, and create a dynamic task plan."""
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("Please enter a research topic.")

        normalized_topic = re.sub(r"\s+", " ", topic).strip()
        normalized = normalized_topic.casefold()
        words = re.findall(r"[a-z0-9]+", normalized)
        has_research_signal = self._contains_any(normalized, RESEARCH_SIGNALS)
        has_technical_signal = self._contains_any(normalized, TECHNICAL_SIGNALS)
        is_broad = self._contains_any(normalized, BROAD_SIGNALS) or (
            len(words) == 1 and words[0] in {"science", "technology", "history", "biology", "physics"}
        )
        is_beginner = self._contains_any(normalized, BEGINNER_SIGNALS)
        is_advanced = self._contains_any(normalized, ADVANCED_SIGNALS)

        if has_research_signal:
            topic_type = "research"
        elif has_technical_signal:
            topic_type = "technical"
        else:
            topic_type = "academic"

        if is_beginner:
            difficulty = "beginner"
            complexity = "low"
            research_depth = "introductory"
        elif is_advanced or has_research_signal:
            difficulty = "advanced"
            complexity = "high"
            research_depth = "deep"
        elif is_broad:
            difficulty = "intermediate"
            complexity = "moderate"
            research_depth = "exploratory"
        else:
            difficulty = "intermediate" if has_technical_signal else "foundational"
            complexity = "moderate" if has_technical_signal else "low"
            research_depth = "standard"

        actions = ["summary", "concepts", "questions"]
        if has_research_signal:
            actions.extend(("future_directions", "research_keywords"))
        actions.append("roadmap")
        if is_broad and "research_keywords" not in actions:
            actions.append("research_keywords")
        if has_technical_signal or has_research_signal:
            actions.append("papers")

        reasoning = [
            f"Classified as {topic_type} based on the topic wording and domain signals.",
            f"Detected {complexity} complexity and selected {difficulty} difficulty.",
            f"Selected {research_depth} research depth.",
        ]
        if has_research_signal:
            reasoning.append(
                "Research/trend language triggered future-directions and keyword tasks."
            )
        if "papers" in actions:
            reasoning.append(
                "Technical and research topics benefit from authoritative academic references; selected Semantic Scholar paper discovery."
            )
        if is_broad:
            reasoning.append(
                "Broad-scope wording triggered expanded concept coverage and topic-narrowing keywords."
            )
        if is_beginner:
            reasoning.append("Beginner wording selected a simplified roadmap.")
        if is_advanced:
            reasoning.append("Advanced-level wording selected higher-level research questions.")

        return ExecutionPlan(
            topic=normalized_topic,
            topic_type=topic_type,
            difficulty=difficulty,
            complexity=complexity,
            research_depth=research_depth,
            actions=tuple(actions),
            reasoning=tuple(reasoning),
            is_broad=is_broad,
        )

    @staticmethod
    def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
        return any(phrase in text for phrase in phrases)
