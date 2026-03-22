"""
CLI entry point for the Rudra framework.

Provides commands for agent management, routing, evaluation, and
interactive sessions.

Usage::

    rudra agents list
    rudra agents show accounting-policy-engine
    rudra route "Analyze our lease portfolio under IFRS 16"
    rudra eval routing
    rudra eval tools
    rudra run "Design a COA for our multi-entity structure"
    rudra benchmarks list
    rudra benchmarks get days_to_close
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="rudra",
        description="Rudra   Skills-based multi-agent framework for finance transformation",
    )
    parser.add_argument("--agents-dir", type=str, default=None, help="Path to agent definitions directory")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- agents ---
    agents_parser = subparsers.add_parser("agents", help="Manage agents")
    agents_sub = agents_parser.add_subparsers(dest="agents_action")

    agents_sub.add_parser("list", help="List all agents")
    show_parser = agents_sub.add_parser("show", help="Show agent details")
    show_parser.add_argument("agent_id", type=str)

    # --- route ---
    route_parser = subparsers.add_parser("route", help="Route a query to the best agent")
    route_parser.add_argument("query", type=str)
    route_parser.add_argument("--top-k", type=int, default=5)

    # --- eval ---
    eval_parser = subparsers.add_parser("eval", help="Run evaluation suites")
    eval_sub = eval_parser.add_subparsers(dest="eval_action")
    eval_sub.add_parser("routing", help="Evaluate routing accuracy")
    eval_sub.add_parser("tools", help="Evaluate built-in tools")
    eval_agent_parser = eval_sub.add_parser("agent", help="Evaluate a specific agent")
    eval_agent_parser.add_argument("agent_id", type=str)

    # --- run ---
    run_parser = subparsers.add_parser("run", help="Run the full orchestration pipeline")
    run_parser.add_argument("query", type=str)
    run_parser.add_argument("--basis", type=str, default="BOTH", choices=["IFRS", "US_GAAP", "BOTH"])
    run_parser.add_argument("--format", type=str, default="narrative", choices=["narrative", "json", "table"])
    run_parser.add_argument("--audience", type=str, default="controller")

    # --- benchmarks ---
    bench_parser = subparsers.add_parser("benchmarks", help="Access APQC benchmarks")
    bench_sub = bench_parser.add_subparsers(dest="bench_action")
    bench_sub.add_parser("list", help="List available benchmarks")
    bench_get = bench_sub.add_parser("get", help="Get a specific benchmark")
    bench_get.add_argument("metric", type=str)
    bench_get.add_argument("--percentile", type=str, default=None)
    bench_get.add_argument("--industry", type=str, default=None)

    # --- standards ---
    std_parser = subparsers.add_parser("standards", help="Search accounting standards")
    std_parser.add_argument("query", type=str)
    std_parser.add_argument("--category", type=str, default=None, choices=["IFRS", "US_GAAP"])
    std_parser.add_argument("-k", type=int, default=5)

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.command is None:
        parser.print_help()
        return

    if args.command == "agents":
        _handle_agents(args)
    elif args.command == "route":
        _handle_route(args)
    elif args.command == "eval":
        _handle_eval(args)
    elif args.command == "run":
        asyncio.run(_handle_run(args))
    elif args.command == "benchmarks":
        _handle_benchmarks(args)
    elif args.command == "standards":
        _handle_standards(args)


def _handle_agents(args) -> None:
    from rudra.agents.registry import AgentRegistry

    agents_dir = Path(args.agents_dir) if args.agents_dir else None
    registry = AgentRegistry.from_directory(agents_dir)

    if args.agents_action == "list":
        specs = registry.list_agents()
        print(f"\n{'ID':<35} {'Domain':<25} {'Model':<12} {'Tools'}")
        print("=" * 100)
        for spec in specs:
            tool_names = [t.name for t in spec.tools]
            print(f"{spec.id:<35} {spec.domain:<25} {spec.model:<12} {', '.join(tool_names[:3])}")
        print(f"\nTotal: {len(specs)} agents")

    elif args.agents_action == "show":
        spec = registry.get_spec(args.agent_id)
        if spec is None:
            print(f"Agent '{args.agent_id}' not found")
            sys.exit(1)
        print(json.dumps(spec.model_dump(), indent=2, default=str))


def _handle_route(args) -> None:
    from rudra.agents.registry import AgentRegistry
    from rudra.routing.router import VectorSearchRouter

    agents_dir = Path(args.agents_dir) if args.agents_dir else None
    registry = AgentRegistry.from_directory(agents_dir)
    router = VectorSearchRouter(registry)

    decision = router.route(args.query, top_k=args.top_k)
    print(json.dumps(decision.model_dump(), indent=2))


def _handle_eval(args) -> None:
    from rudra.eval.harness import EvaluationHarness

    harness = EvaluationHarness(agents_dir=args.agents_dir)

    if args.eval_action == "routing":
        metrics = harness.eval_routing()
        print("\n=== Routing Evaluation ===")
        print(json.dumps(metrics.summary(), indent=2))
        print("\nDetailed results:")
        for r in metrics.results:
            status = "PASS" if r["passed"] else "FAIL"
            details = r.get("details", {})
            print(f"  [{status}] {r['case_id']}: "
                  f"expected={details.get('expected', '?')} "
                  f"actual={details.get('actual', '?')} "
                  f"conf={details.get('confidence', 0):.3f}")

    elif args.eval_action == "tools":
        metrics = harness.eval_tools()
        print("\n=== Tools Evaluation ===")
        print(json.dumps(metrics.summary(), indent=2))
        for r in metrics.results:
            status = "PASS" if r["passed"] else "FAIL"
            print(f"  [{status}] {r['case_id']}")

    elif args.eval_action == "agent":
        metrics = asyncio.run(harness.eval_agent(args.agent_id))
        print(f"\n=== Agent Evaluation: {args.agent_id} ===")
        print(json.dumps(metrics.summary(), indent=2))


async def _handle_run(args) -> None:
    from rudra.agents.registry import AgentRegistry
    from rudra.agents.invoker import AgentInvoker
    from rudra.routing.router import VectorSearchRouter
    from rudra.orchestration.graph import RudraGraph

    agents_dir = Path(args.agents_dir) if args.agents_dir else None
    registry = AgentRegistry.from_directory(agents_dir)
    router = VectorSearchRouter(registry)
    invoker = AgentInvoker()

    graph = RudraGraph.build(registry, router, invoker)

    print(f"\n>>> Routing query: {args.query}")
    print(f">>> Basis: {args.basis} | Format: {args.format} | Audience: {args.audience}")
    print("=" * 80)

    result = await graph.run(
        query=args.query,
        reporting_basis=args.basis,
        output_format=args.format,
        audience=args.audience,
    )

    print("\n--- FINAL RESPONSE ---")
    print(result.get("final_response", "(no response)"))
    print("\n--- METADATA ---")
    print(f"Primary agent: {result.get('primary_agent', '?')}")
    print(f"Secondary agents: {result.get('secondary_agents', [])}")
    print(f"Routing confidence: {result.get('routing_confidence', 0):.3f}")


def _handle_benchmarks(args) -> None:
    from rudra.tools.benchmarks import get_apqc_benchmark, list_benchmarks

    if args.bench_action == "list":
        benchmarks = list_benchmarks()
        print(f"\n{'Key':<45} {'Metric':<55} {'PCF'}")
        print("=" * 110)
        for b in benchmarks:
            print(f"{b['key']:<45} {b['metric']:<55} {b['pcf']}")

    elif args.bench_action == "get":
        result = get_apqc_benchmark(args.metric, industry=args.industry, percentile=args.percentile)
        print(json.dumps(result, indent=2, default=str))


def _handle_standards(args) -> None:
    from rudra.tools.standards import search_standards

    results = search_standards(args.query, category=args.category, k=args.k)
    for r in results:
        print(f"\n[{r.get('category', '?')}] {r['standard']}   {r['topic']}")
        print(f"  {r['key_rules'][:200]}...")


if __name__ == "__main__":
    main()
