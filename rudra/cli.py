"""
CLI entry point for the Rudra framework.

Usage::

    rudra agents list
    rudra route "Analyze our lease portfolio under IFRS 16"
    rudra eval routing
    rudra serve
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
        description="Rudra - Skills-based multi-agent framework for finance transformation",
    )
    parser.add_argument("--agents-dir", type=str, default=None)
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # agents
    agents_parser = subparsers.add_parser("agents", help="Manage agents")
    agents_sub = agents_parser.add_subparsers(dest="agents_action")
    agents_sub.add_parser("list", help="List all agents")
    show_p = agents_sub.add_parser("show", help="Show agent details")
    show_p.add_argument("agent_id", type=str)

    # route
    route_p = subparsers.add_parser("route", help="Route a query")
    route_p.add_argument("query", type=str)
    route_p.add_argument("--top-k", type=int, default=5)

    # eval
    eval_p = subparsers.add_parser("eval", help="Run evaluation suites")
    eval_sub = eval_p.add_subparsers(dest="eval_action")
    eval_sub.add_parser("routing", help="Evaluate routing accuracy")
    eval_sub.add_parser("tools", help="Evaluate built-in tools")

    # benchmarks
    bench_p = subparsers.add_parser("benchmarks", help="Access APQC benchmarks")
    bench_sub = bench_p.add_subparsers(dest="bench_action")
    bench_sub.add_parser("list", help="List available benchmarks")
    bg = bench_sub.add_parser("get", help="Get a specific benchmark")
    bg.add_argument("metric", type=str)

    # standards
    std_p = subparsers.add_parser("standards", help="Search accounting standards")
    std_p.add_argument("query", type=str)
    std_p.add_argument("--category", type=str, default=None)
    std_p.add_argument("-k", type=int, default=5)

    # serve
    subparsers.add_parser("serve", help="Start the web UI server")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(name)s: %(message)s")

    if args.command is None:
        parser.print_help()
        return

    if args.command == "agents":
        _handle_agents(args)
    elif args.command == "route":
        _handle_route(args)
    elif args.command == "eval":
        _handle_eval(args)
    elif args.command == "benchmarks":
        _handle_benchmarks(args)
    elif args.command == "standards":
        _handle_standards(args)
    elif args.command == "serve":
        _handle_serve()


def _handle_agents(args):
    from rudra.agents.registry import AgentRegistry
    registry = AgentRegistry.from_directory(Path(args.agents_dir) if args.agents_dir else None)

    if args.agents_action == "list":
        specs = registry.list_agents()
        print(f"\n{'ID':<35} {'Domain':<25} {'Model':<12} {'Tools'}")
        print("=" * 100)
        for s in specs:
            tools = ", ".join(t.name for t in s.tools[:3])
            print(f"{s.id:<35} {s.domain:<25} {s.model:<12} {tools}")
        print(f"\nTotal: {len(specs)} agents")
    elif args.agents_action == "show":
        spec = registry.get_spec(args.agent_id)
        if spec is None:
            print(f"Agent '{args.agent_id}' not found")
            sys.exit(1)
        print(json.dumps(spec.model_dump(), indent=2, default=str))


def _handle_route(args):
    from rudra.agents.registry import AgentRegistry
    from rudra.routing.router import VectorSearchRouter
    registry = AgentRegistry.from_directory(Path(args.agents_dir) if args.agents_dir else None)
    router = VectorSearchRouter(registry)
    decision = router.route(args.query, top_k=args.top_k)
    print(json.dumps(decision.model_dump(), indent=2))


def _handle_eval(args):
    from rudra.eval.harness import EvaluationHarness
    harness = EvaluationHarness(agents_dir=args.agents_dir)

    if args.eval_action == "routing":
        metrics = harness.eval_routing()
        print("\n=== Routing Evaluation ===")
        print(json.dumps(metrics.summary(), indent=2))
        for r in metrics.results:
            status = "PASS" if r["passed"] else "FAIL"
            d = r.get("details", {})
            print(f"  [{status}] {r['case_id']}: expected={d.get('expected','?')} actual={d.get('actual','?')} conf={d.get('confidence',0):.3f}")
    elif args.eval_action == "tools":
        metrics = harness.eval_tools()
        print("\n=== Tools Evaluation ===")
        print(json.dumps(metrics.summary(), indent=2))
        for r in metrics.results:
            print(f"  [{'PASS' if r['passed'] else 'FAIL'}] {r['case_id']}")


def _handle_benchmarks(args):
    from rudra.tools.benchmarks import get_apqc_benchmark, list_benchmarks
    if args.bench_action == "list":
        for b in list_benchmarks():
            print(f"{b['key']:<45} {b['metric']}")
    elif args.bench_action == "get":
        print(json.dumps(get_apqc_benchmark(args.metric), indent=2, default=str))


def _handle_standards(args):
    from rudra.tools.standards import search_standards
    results = search_standards(args.query, category=args.category, k=args.k)
    for r in results:
        print(f"\n[{r.get('category','?')}] {r['standard']} - {r['topic']}")
        print(f"  {r['key_rules'][:200]}...")


def _handle_serve():
    from rudra.app import start
    start()


if __name__ == "__main__":
    main()
