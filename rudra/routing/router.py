"""
VectorSearchRouter   semantic routing engine for the Rudra framework.

Replaces keyword/trigger-word matching with embedding-based similarity
search.  Applies a business rules overlay after semantic scoring to
handle hard constraints (e.g. M&A queries always include the accounting
policy engine).
"""

from __future__ import annotations

import logging
from typing import Optional

from rudra.agents.registry import AgentRegistry
from rudra.models import (
    AgentMatch,
    PipelineMode,
    RoutingDecision,
)
from rudra.routing.index import AgentCapabilityIndex

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Business rules (applied after semantic scoring)
# ---------------------------------------------------------------------------

_HARD_RULES: list[dict] = [
    {
        "condition_keywords": ["IFRS", "US GAAP", "ASC", "IAS"],
        "must_include": "accounting-policy-engine",
        "reason": "Query references specific accounting standards",
    },
    {
        "condition_keywords": ["M&A", "acquisition", "due diligence", "merger"],
        "must_include": "accounting-policy-engine",
        "reason": "M&A queries need accounting policy analysis",
    },
    {
        "condition_keywords": ["Databricks", "Delta Lake", "pipeline", "streaming"],
        "must_include": "databricks-pipeline-agent",
        "reason": "Data engineering query needs Databricks agent",
    },
    {
        "condition_keywords": ["benchmark", "APQC", "PCF"],
        "must_include": "apqc-researcher",
        "reason": "Benchmarking query needs APQC specialist",
    },
]


def _apply_business_rules(
    query: str,
    primary_id: str,
    secondary_ids: list[str],
) -> list[str]:
    """Apply hard rules to inject agents into the secondary list."""
    query_lower = query.lower()
    additional: list[str] = []

    for rule in _HARD_RULES:
        if any(kw.lower() in query_lower for kw in rule["condition_keywords"]):
            must_include = rule["must_include"]
            if must_include != primary_id and must_include not in secondary_ids:
                additional.append(must_include)
                logger.debug("Business rule injected: %s (%s)", must_include, rule["reason"])

    return additional


def _infer_pipeline_mode(primary_id: str, secondary_count: int) -> PipelineMode:
    """Heuristic to decide pipeline mode."""
    if secondary_count == 0:
        return PipelineMode.SEQUENTIAL
    if secondary_count >= 3:
        return PipelineMode.PARALLEL
    return PipelineMode.SEQUENTIAL


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class VectorSearchRouter:
    """
    Semantic routing engine.

    Usage::

        registry = AgentRegistry.from_directory()
        router = VectorSearchRouter(registry)
        decision = router.route("Analyze our lease portfolio under IFRS 16")
    """

    def __init__(
        self,
        registry: AgentRegistry,
        index: Optional[AgentCapabilityIndex] = None,
    ) -> None:
        self.registry = registry
        self.index = index or AgentCapabilityIndex.from_specs(registry.list_agents())

    def route(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None,
    ) -> RoutingDecision:
        """
        Route a user query to the optimal agent(s).

        Returns a RoutingDecision with primary agent, secondary agents,
        pipeline mode, and disambiguation questions if needed.
        """
        results = self.index.search(query, top_k=top_k, domain_filter=domain_filter)

        if not results:
            all_results = self.index.search_all(query)
            if all_results:
                top = all_results[0]
                return RoutingDecision(
                    query=query,
                    intent="fallback",
                    primary_agent=AgentMatch(
                        agent_id="rudra",
                        confidence=top[1],
                        reason="No agent met confidence threshold; falling back to Rudra",
                    ),
                    pipeline_mode=PipelineMode.SEQUENTIAL,
                )
            return RoutingDecision(
                query=query,
                intent="unknown",
                primary_agent=AgentMatch(
                    agent_id="rudra",
                    confidence=0.0,
                    reason="No agents available",
                ),
            )

        primary_entry, primary_score = results[0]
        secondary_entries = results[1:]

        injected = _apply_business_rules(
            query,
            primary_entry.agent_id,
            [e.agent_id for e, _ in secondary_entries],
        )

        secondary_matches = [
            AgentMatch(
                agent_id=entry.agent_id,
                confidence=score,
                role=f"Secondary support ({entry.domain})",
            )
            for entry, score in secondary_entries
        ]

        for injected_id in injected:
            idx_entry = self.index.get_entry(injected_id)
            if idx_entry:
                secondary_matches.append(
                    AgentMatch(
                        agent_id=injected_id,
                        confidence=idx_entry.confidence_threshold,
                        role="Injected by business rule",
                    )
                )

        needs_disambiguation = (
            len(results) >= 2
            and abs(results[0][1] - results[1][1]) < 0.05
        )

        return RoutingDecision(
            query=query,
            intent=_classify_intent(query),
            primary_agent=AgentMatch(
                agent_id=primary_entry.agent_id,
                confidence=primary_score,
                reason=f"Highest semantic match in domain '{primary_entry.domain}'",
            ),
            secondary_agents=secondary_matches,
            pipeline_mode=_infer_pipeline_mode(primary_entry.agent_id, len(secondary_matches)),
            requires_disambiguation=needs_disambiguation,
            disambiguation_questions=_build_disambiguation(query) if needs_disambiguation else [],
        )


def _classify_intent(query: str) -> str:
    """Simple heuristic intent classifier."""
    q = query.lower()
    if any(w in q for w in ["analyze", "assess", "evaluate", "review"]):
        return "analyze"
    if any(w in q for w in ["draft", "write", "create", "produce"]):
        return "draft"
    if any(w in q for w in ["build", "configure", "implement", "set up"]):
        return "build"
    if any(w in q for w in ["design", "architect"]):
        return "design"
    if any(w in q for w in ["benchmark", "compare"]):
        return "benchmark"
    if any(w in q for w in ["calculate", "model", "forecast"]):
        return "calculate"
    return "general"


def _build_disambiguation(query: str) -> list[str]:
    return [
        "Are you asking about the accounting treatment or the system configuration?",
        "Do you need analysis under IFRS, US GAAP, or both?",
        "Is this for a one-time scenario analysis or ongoing policy development?",
        "What output do you need: policy memo, journal entries, system design, or disclosure?",
    ]
