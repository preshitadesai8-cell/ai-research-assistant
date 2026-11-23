"""Central report assembly and workflow metadata generation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.models.execution_plan import ExecutionPlan
from backend.validator_agent import ValidationResult


class ReportGenerator:
    """Organize selected task outputs and attach plan and validation metadata."""

    @staticmethod
    def organize(task_outputs: dict[str, Any]) -> dict[str, Any]:
        """Map task names and service values to stable report section names."""
        report: dict[str, Any] = {}
        if "summary" in task_outputs:
            report["summary"] = task_outputs["summary"]
        if "concepts" in task_outputs:
            report["key_concepts"] = task_outputs["concepts"]
        if "questions" in task_outputs:
            report["research_questions"] = task_outputs["questions"]
        if "roadmap" in task_outputs:
            learning_plan = task_outputs["roadmap"]
            report["further_study"] = learning_plan["further_study"]
            report["learning_roadmap"] = learning_plan["roadmap"]
        if "future_directions" in task_outputs:
            report["future_directions"] = task_outputs["future_directions"]
        if "research_keywords" in task_outputs:
            report["research_keywords"] = task_outputs["research_keywords"]
        if "papers" in task_outputs:
            report["recommended_papers"] = task_outputs["papers"]
        return report

    def generate(
        self,
        plan: ExecutionPlan,
        task_outputs: dict[str, Any],
        validation: ValidationResult,
        *,
        task_errors: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Return the complete report envelope with decision and quality metadata."""
        errors = task_errors or {}
        return {
            "topic": plan.topic,
            "topic_type": plan.topic_type,
            "difficulty": plan.difficulty,
            "complexity": plan.complexity,
            "research_depth": plan.research_depth,
            "execution_plan": plan.to_dict(),
            "report": self.organize(task_outputs),
            "quality_score": validation.score,
            "quality_status": validation.status,
            "quality_warnings": list(validation.warnings),
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "selected_tasks": list(plan.actions),
                "executed_tasks": list(task_outputs),
                "generation_method": "rule_planned_llm_tasks",
                "external_sources_used": "papers" in task_outputs,
                "papers_found": len(task_outputs.get("papers", [])),
                "source": "Semantic Scholar" if "papers" in task_outputs else None,
                "quality_score": validation.score,
                "task_errors": errors,
            },
        }
