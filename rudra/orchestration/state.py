"""
Orchestration state for the LangGraph graph.

Uses TypedDict (required by LangGraph) that mirrors the Pydantic RudraState
model.  Conversion helpers translate between the two representations.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Optional

from typing_extensions import TypedDict


class GraphState(TypedDict, total=False):
    """
    LangGraph-compatible state dictionary.

    LangGraph requires TypedDict for state; we use Annotated reducers
    for fields that accumulate across nodes (agent_outputs, citations).
    """

    # User input
    query: str
    reporting_basis: str
    output_format: str
    audience: str

    # Routing
    primary_agent: str
    secondary_agents: list[str]
    routing_confidence: float
    routing_intent: str

    # Working context
    normalized_facts: dict[str, Any]
    agent_outputs: Annotated[dict[str, Any], _merge_dicts]
    active_agent: str

    # Control flow
    requires_human_review: bool
    human_feedback: str
    iteration_count: int
    current_step: str
    error: Optional[str]

    # Final outputs
    final_response: str
    citations: Annotated[list[str], operator.add]

    # Session
    session_id: str


def _merge_dicts(left: dict, right: dict) -> dict:
    """Reducer that merges dicts (used for agent_outputs accumulation)."""
    merged = {**left} if left else {}
    if right:
        merged.update(right)
    return merged


def initial_state(
    query: str,
    reporting_basis: str = "BOTH",
    output_format: str = "narrative",
    audience: str = "controller",
    session_id: str = "",
) -> GraphState:
    """Create a fresh initial state for a new orchestration run."""
    return GraphState(
        query=query,
        reporting_basis=reporting_basis,
        output_format=output_format,
        audience=audience,
        primary_agent="",
        secondary_agents=[],
        routing_confidence=0.0,
        routing_intent="",
        normalized_facts={},
        agent_outputs={},
        active_agent="",
        requires_human_review=False,
        human_feedback="",
        iteration_count=0,
        current_step="start",
        error=None,
        final_response="",
        citations=[],
        session_id=session_id,
    )
