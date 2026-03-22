"""
EvaluationHarness   runs golden test cases against agents and the router.

Supports two evaluation modes:
1. **Routing evaluation**: Tests that the router selects the correct agent.
2. **Agent evaluation**: Tests that agent responses contain expected content
   (requires an LLM API key, so can run in offline/online modes).
"""

from __future__ import annotations

import logging
from typing import Optional

from rudra.eval.metrics import EvalMetrics

logger = logging.getLogger(__name__)


class EvaluationHarness:
    """
    Run evaluation suites against the Rudra framework.

    Usage::

        from rudra.eval import EvaluationHarness

        harness = EvaluationHarness()
        metrics = harness.eval_routing()
        print(metrics.summary())
    """

    def __init__(
        self,
        agents_dir: Optional[str] = None,
    ) -> None:
        self._agents_dir = agents_dir

    def eval_routing(self) -> EvalMetrics:
        """
        Evaluate the vector-search router against golden test cases.

        Does NOT require an API key   runs entirely locally using
        sentence-transformers embeddings.
        """
        from pathlib import Path
        from rudra.agents.registry import AgentRegistry
        from rudra.routing.router import VectorSearchRouter
        from rudra.eval.test_cases.routing import ROUTING_TEST_CASES

        agents_dir = Path(self._agents_dir) if self._agents_dir else None
        registry = AgentRegistry.from_directory(agents_dir)
        router = VectorSearchRouter(registry)

        metrics = EvalMetrics()

        for case in ROUTING_TEST_CASES:
            try:
                decision = router.route(case["query"])
                actual_primary = decision.primary_agent.agent_id
                expected_primary = case["expected_primary"]

                passed = actual_primary == expected_primary

                details = {
                    "query": case["query"],
                    "expected": expected_primary,
                    "actual": actual_primary,
                    "confidence": decision.primary_agent.confidence,
                    "category": case.get("category", ""),
                }

                if "expected_secondary_contains" in case:
                    secondary_ids = [a.agent_id for a in decision.secondary_agents]
                    for expected_sec in case["expected_secondary_contains"]:
                        if expected_sec not in secondary_ids:
                            details["missing_secondary"] = expected_sec

                metrics.add_result(case["id"], passed, details)

                status = "PASS" if passed else "FAIL"
                logger.info(
                    "[%s] %s | expected=%s actual=%s conf=%.3f",
                    status, case["id"], expected_primary, actual_primary,
                    decision.primary_agent.confidence,
                )

            except Exception as exc:
                metrics.add_error(case["id"], str(exc))
                logger.error("[ERROR] %s: %s", case["id"], exc)

        return metrics

    async def eval_agent(
        self,
        agent_id: str,
        test_cases: Optional[list[dict]] = None,
    ) -> EvalMetrics:
        """
        Evaluate an agent's response quality against golden test cases.

        Requires an API key for LLM calls.
        """
        from pathlib import Path
        from rudra.agents.registry import AgentRegistry
        from rudra.agents.invoker import AgentInvoker
        from rudra.models import AgentRequest

        if test_cases is None:
            if agent_id == "accounting-policy-engine":
                from rudra.eval.test_cases.accounting_policy import ACCOUNTING_POLICY_TEST_CASES
                test_cases = ACCOUNTING_POLICY_TEST_CASES
            else:
                return EvalMetrics()

        agents_dir = Path(self._agents_dir) if self._agents_dir else None
        registry = AgentRegistry.from_directory(agents_dir)
        invoker = AgentInvoker()
        agent = registry.get(agent_id)

        if agent is None:
            metrics = EvalMetrics()
            metrics.add_error("setup", f"Agent '{agent_id}' not found")
            return metrics

        agent.bind_invoker(invoker)
        metrics = EvalMetrics()

        for case in test_cases:
            try:
                request = AgentRequest(
                    agent_id=agent_id,
                    query=case["query"],
                )
                result = await agent.invoke(request)

                if not result.succeeded:
                    metrics.add_error(case["id"], result.error or "Agent failed")
                    continue

                response_lower = result.response.lower()

                checks_passed = True
                details: dict = {"response_length": len(result.response)}

                if "expected_contains" in case:
                    for expected in case["expected_contains"]:
                        if expected.lower() not in response_lower:
                            checks_passed = False
                            details.setdefault("missing_terms", []).append(expected)

                if "expected_standards" in case:
                    for std in case["expected_standards"]:
                        if std.lower() not in response_lower:
                            checks_passed = False
                            details.setdefault("missing_standards", []).append(std)

                metrics.add_result(case["id"], checks_passed, details)

            except Exception as exc:
                metrics.add_error(case["id"], str(exc))

        return metrics

    def eval_tools(self) -> EvalMetrics:
        """Evaluate the built-in tools (standards search, benchmarks)."""
        from rudra.tools.standards import search_standards
        from rudra.tools.benchmarks import get_apqc_benchmark

        metrics = EvalMetrics()

        # Standards search tests
        results = search_standards("lease IFRS 16 right of use")
        passed = any("IFRS 16" in r.get("standard", "") for r in results)
        metrics.add_result("tool_standards_lease", passed, {"results_count": len(results)})

        results = search_standards("revenue recognition ASC 606")
        passed = any("ASC 606" in r.get("standard", "") for r in results)
        metrics.add_result("tool_standards_revenue", passed, {"results_count": len(results)})

        # Benchmark tests
        result = get_apqc_benchmark("days_to_close")
        passed = "median" in result and result["median"] == 6.5
        metrics.add_result("tool_benchmark_close", passed, result)

        result = get_apqc_benchmark("dso", percentile="top_25")
        passed = "requested_percentile" in result
        metrics.add_result("tool_benchmark_dso", passed, result)

        result = get_apqc_benchmark("nonexistent_metric")
        passed = "error" in result
        metrics.add_result("tool_benchmark_not_found", passed, result)

        return metrics
