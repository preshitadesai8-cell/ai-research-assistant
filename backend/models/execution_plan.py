"""Validated execution-plan model produced by the planner agent."""

from __future__ import annotations

from dataclasses import dataclass


VALID_ACTIONS = frozenset(
    {
        "summary",
        "concepts",
        "questions",
        "roadmap",
        "future_directions",
        "research_keywords",
        "papers",
    }
)


@dataclass(frozen=True)
class ExecutionPlan:
    """A transparent, ordered plan for exploring a research topic."""

    topic: str
    topic_type: str
    difficulty: str
    complexity: str
    research_depth: str
    actions: tuple[str, ...]
    reasoning: tuple[str, ...]
    is_broad: bool = False

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ValueError("An execution plan requires a non-empty topic.")
        if not self.actions:
            raise ValueError("An execution plan must include at least one action.")
        if len(set(self.actions)) != len(self.actions):
            raise ValueError("Execution plan actions must be unique.")
        unknown_actions = set(self.actions) - VALID_ACTIONS
        if unknown_actions:
            raise ValueError(f"Unknown execution plan actions: {sorted(unknown_actions)}")

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of the plan."""
        return {
            "topic": self.topic,
            "topic_type": self.topic_type,
            "difficulty": self.difficulty,
            "complexity": self.complexity,
            "research_depth": self.research_depth,
            "actions": list(self.actions),
            "reasoning": list(self.reasoning),
            "is_broad": self.is_broad,
        }
