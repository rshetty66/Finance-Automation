"""
Evaluation metrics for assessing agent and routing quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalMetrics:
    """Aggregate evaluation metrics."""

    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    results: list[dict[str, Any]] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / max(self.total_cases, 1)

    @property
    def error_rate(self) -> float:
        return self.errors / max(self.total_cases, 1)

    def add_result(self, case_id: str, passed: bool, details: dict | None = None) -> None:
        self.total_cases += 1
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.results.append({
            "case_id": case_id,
            "passed": passed,
            "details": details or {},
        })

    def add_error(self, case_id: str, error: str) -> None:
        self.total_cases += 1
        self.errors += 1
        self.results.append({
            "case_id": case_id,
            "passed": False,
            "error": error,
        })

    def summary(self) -> dict:
        return {
            "total": self.total_cases,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "pass_rate": f"{self.pass_rate:.1%}",
        }

    def __repr__(self) -> str:
        return f"<EvalMetrics total={self.total_cases} pass_rate={self.pass_rate:.1%}>"
