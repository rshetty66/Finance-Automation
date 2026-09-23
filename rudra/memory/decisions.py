"""
Typed decisions   small-answer-space judgments recorded around the agent loop.

Most agent turns are not "write the deliverable"; they are decisions with a
handful of possible answers (which memories to read, which model tier, is
this step safe to run, is the task done, what to keep when compacting).
Recording them as typed values rather than prose makes them cheap to answer,
auditable, and reusable across projects.

Three shapes:

* ``Choice``  pick one label from a fixed set   (e.g. model tier)
* ``Noul``    a yes/no gate                      (e.g. safe to run?  done?)
* ``Score``   a 0..1 relevance per candidate      (e.g. which memories to read)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DecisionType(str, Enum):
    CHOICE = "choice"
    NOUL = "noul"
    SCORE = "score"


class Resolver(str, Enum):
    """Who answered the decision   used for cost tracking."""
    RULE = "rule"          # deterministic code, no model call
    CHEAP = "cheap"        # fast / small model
    MID = "mid"
    FRONTIER = "frontier"  # the deliverable-writing model
    HUMAN = "human"


@dataclass
class TypedDecision:
    """One recorded decision. ``answer`` is always a string for storage."""
    decision_type: DecisionType
    question: str
    answer: str
    options: list[str] = field(default_factory=list)
    rationale: str = ""
    resolved_by: Resolver = Resolver.RULE
    cost_usd: float = 0.0

    def __post_init__(self) -> None:
        self.decision_type = DecisionType(self.decision_type)
        self.resolved_by = Resolver(self.resolved_by)
        if self.decision_type == DecisionType.CHOICE and self.options and self.answer not in self.options:
            raise ValueError(f"Choice answer {self.answer!r} not in options {self.options}")
        if self.decision_type == DecisionType.NOUL and self.answer not in ("yes", "no"):
            raise ValueError(f"Noul answer must be 'yes' or 'no', got {self.answer!r}")


# ---------------------------------------------------------------------------
# Rule-based resolvers   the "no model call" tier
# ---------------------------------------------------------------------------

TIERS = ["cheap", "mid", "frontier", "ask"]

_CHEAP_HINTS = ("rename", "format", "typo", "reformat", "lookup", "list ", "extract", "convert", "copy")
_FRONTIER_HINTS = (
    "design", "architecture", "policy", "judgement", "judgment", "position paper",
    "ifrs", "us gaap", "osfi", "bcar", "capital", "memo", "strategy", "operating model",
)
_IRREVERSIBLE = re.compile(
    r"\b(rm\s+-rf|drop\s+table|truncate|delete|overwrite|force[- ]push|reset\s+--hard|"
    r"post(ing)?\s+journal|submit\s+to\s+(osfi|regulator)|send\s+(email|to\s+client)|wire|payment)\b",
    re.IGNORECASE,
)


def choose_tier(step: str, brief_clear: bool = True) -> TypedDecision:
    """Choice: which model tier should handle this step."""
    s = step.lower()
    if not brief_clear:
        answer, why = "ask", "Brief unclear; a person decides."
    elif any(h in s for h in _FRONTIER_HINTS):
        answer, why = "frontier", "Judgment-heavy or regulatory content."
    elif any(h in s for h in _CHEAP_HINTS) and len(s) < 200:
        answer, why = "cheap", "Mechanical, local, low risk."
    else:
        answer, why = "mid", "Bounded change; default tier."
    return TypedDecision(DecisionType.CHOICE, "Which model should do this step?", answer,
                         options=list(TIERS), rationale=why)


def is_irreversible(action: str) -> TypedDecision:
    """Noul: does this action delete, overwrite, post, or send externally?"""
    hit = _IRREVERSIBLE.search(action)
    return TypedDecision(
        DecisionType.NOUL,
        "Does this action delete, overwrite, or publish data?",
        "yes" if hit else "no",
        rationale=f"matched {hit.group(0)!r}; needs human approval" if hit else "no irreversible verb found",
    )


def is_done(test_output: Optional[str], expected_markers: tuple[str, ...] = ("passed",)) -> TypedDecision:
    """Noul: judged against fresh evidence (test/check output), not the agent's own summary."""
    if not test_output:
        return TypedDecision(DecisionType.NOUL, "Is the task done?", "no", rationale="no fresh evidence")
    out = test_output.lower()
    failed = any(w in out for w in ("failed", "error", "traceback"))
    ok = all(m.lower() in out for m in expected_markers) and not failed
    return TypedDecision(DecisionType.NOUL, "Is the task done?", "yes" if ok else "no",
                         rationale="evidence passes" if ok else "evidence shows failure or missing markers")
