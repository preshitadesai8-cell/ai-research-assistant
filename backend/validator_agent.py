"""Deterministic completeness and quality validation for generated reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.models.execution_plan import ExecutionPlan

ACTION_SECTIONS: dict[str, tuple[str, ...]] = {
    "summary": ("summary",),
    "concepts": ("key_concepts",),
    "questions": ("research_questions",),
    "roadmap": ("further_study", "learning_roadmap"),
    "future_directions": ("future_directions",),
    "research_keywords": ("research_keywords",),
}


@dataclass(frozen=True)
class ValidationResult:
    """Quality score and actionable warnings for a report."""

    score: int
    status: str
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable validation result."""
        return {"score": self.score, "status": self.status, "warnings": list(self.warnings)}


class ValidatorAgent:
    """Check that planned tasks produced complete, non-empty report sections."""

    def validate(
        self, plan: ExecutionPlan, report_sections: dict[str, Any]
    ) -> ValidationResult:
        """Validate all sections required by the execution plan and score quality."""
        warnings: list[str] = []
        deductions = 0
        required_sections = tuple(
            section
            for action in plan.actions
            for section in ACTION_SECTIONS[action]
        )

        for section in required_sections:
            if section not in report_sections:
                warnings.append(f"Required section '{section}' is missing.")
                deductions += 25
            elif not self._has_content(report_sections[section]):
                warnings.append(f"Required section '{section}' is empty.")
                deductions += 20

        if self._has_content(report_sections.get("summary")):
            summary = report_sections["summary"]
            if isinstance(summary, str) and len(summary.split()) < 12:
                warnings.append("The summary is unusually brief; consider regenerating it.")
                deductions += 5

        if self._has_content(report_sections.get("key_concepts")):
            concepts = report_sections["key_concepts"]
            if isinstance(concepts, list) and len(concepts) < 3:
                warnings.append("The report contains fewer than three key concepts.")
                deductions += 5

        if self._has_content(report_sections.get("research_questions")):
            questions = report_sections["research_questions"]
            if isinstance(questions, list) and len(questions) < 3:
                warnings.append("The report contains fewer than three research questions.")
                deductions += 5

        if self._has_content(report_sections.get("learning_roadmap")):
            roadmap = report_sections["learning_roadmap"]
            if isinstance(roadmap, list) and len(roadmap) < 3:
                warnings.append("The learning roadmap contains fewer than three steps.")
                deductions += 5

        score = max(0, 100 - deductions)
        status = "high_quality" if score >= 85 else "needs_review" if score >= 65 else "low_quality"
        return ValidationResult(score=score, status=status, warnings=tuple(warnings))

    @classmethod
    def _has_content(cls, value: Any) -> bool:
        """Return whether a generated field contains non-whitespace content."""
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple)):
            return bool(value) and all(cls._has_content(item) for item in value)
        if isinstance(value, dict):
            return bool(value) and all(cls._has_content(item) for item in value.values())
        return value is not None
