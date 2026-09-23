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
    rudra memory brief --project bcar
    rudra memory add "CET1 floor confirmed at 7%" --project bcar --kind fact
    rudra memory recall "intercompany eliminations" --project sprott-erp
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

    # --- memory ---
    mem_parser = subparsers.add_parser("memory", help="Cross-project agent memory")
    mem_parser.add_argument("--db", type=str, default=None, help="Memory DB path (default: RUDRA_MEMORY_DB or ~/.rudra/memory.db)")
    mem_sub = mem_parser.add_subparsers(dest="mem_action")

    mem_proj = mem_sub.add_parser("project", help="Register or update a project")
    mem_proj.add_argument("project_id", type=str)
    mem_proj.add_argument("name", type=str)
    mem_proj.add_argument("--client", type=str, default="")
    mem_proj.add_argument("--description", type=str, default="")
    mem_proj.add_argument("--tags", type=str, default="", help="Comma-separated")
    mem_proj.add_argument("--status", type=str, default="active")

    mem_sub.add_parser("projects", help="List projects")

    mem_add = mem_sub.add_parser("add", help="Remember something")
    mem_add.add_argument("content", type=str)
    mem_add.add_argument("--project", type=str, default=None, help="Omit for a global memory")
    mem_add.add_argument("--kind", type=str, default="fact",
                         choices=["fact", "decision", "lesson", "preference", "question", "summary"])
    mem_add.add_argument("--tags", type=str, default="", help="Comma-separated")
    mem_add.add_argument("--importance", type=float, default=0.5)
    mem_add.add_argument("--pin", action="store_true")

    mem_recall = mem_sub.add_parser("recall", help="Top memories for a query")
    mem_recall.add_argument("query", type=str)
    mem_recall.add_argument("--project", type=str, default=None)
    mem_recall.add_argument("-k", type=int, default=8)
    mem_recall.add_argument("--budget", type=int, default=2000, help="Token budget")
    mem_recall.add_argument("--min-score", type=float, default=0.15)

    mem_brief = mem_sub.add_parser("brief", help="Session-start memory brief")
    mem_brief.add_argument("--project", type=str, default=None)
    mem_brief.add_argument("--query", type=str, default="")

    mem_start = mem_sub.add_parser("start", help="Start a session and print its brief")
    mem_start.add_argument("project_id", type=str)
    mem_start.add_argument("--agent", type=str, default="")
    mem_start.add_argument("--query", type=str, default="")

    mem_end = mem_sub.add_parser("end", help="End a session with a summary")
    mem_end.add_argument("session_id", type=str)
    mem_end.add_argument("summary", type=str)

    mem_forget = mem_sub.add_parser("forget", help="Delete a memory by id")
    mem_forget.add_argument("memory_id", type=int)

    mem_compact = mem_sub.add_parser("compact", help="Keep top-N memories verbatim, drop the rest")
    mem_compact.add_argument("--project", type=str, default=None, help="Omit to compact global memories")
    mem_compact.add_argument("--keep", type=int, default=200)
    mem_compact.add_argument("--dry-run", action="store_true")

    mem_dec = mem_sub.add_parser("decisions", help="List typed decisions and cost by resolver")
    mem_dec.add_argument("--project", type=str, default=None)
    mem_dec.add_argument("--type", type=str, default=None, choices=["choice", "noul", "score"])

    mem_export = mem_sub.add_parser("export", help="Export to JSONL")
    mem_export.add_argument("path", type=str)
    mem_import = mem_sub.add_parser("import", help="Merge a JSONL export")
    mem_import.add_argument("path", type=str)

    mem_hook = mem_sub.add_parser("session-start", help="Hook entry: seed from JSONL if empty, print portfolio brief")
    mem_hook.add_argument("--seed", type=str, default="memory/portfolio.jsonl")
    mem_hook.add_argument("--project", type=str, default=None)

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
    elif args.command == "memory":
        _handle_memory(args)


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


def _handle_memory(args) -> None:
    from rudra.memory.project_memory import ProjectMemory

    def _split(tags: str) -> list[str]:
        return [t.strip() for t in tags.split(",") if t.strip()]

    with ProjectMemory(args.db) as mem:
        action = args.mem_action
        if action == "project":
            mem.register_project(args.project_id, args.name, args.client, args.description,
                                 _split(args.tags), args.status)
            print(f"Registered project {args.project_id}")
        elif action == "projects":
            print(f"\n{'ID':<22} {'Name':<45} {'Status':<10} {'Last active'}")
            print("=" * 95)
            for p in mem.list_projects():
                print(f"{p['id']:<22} {p['name'][:44]:<45} {p['status']:<10} {p['last_active'][:10]}")
        elif action == "add":
            mid = mem.remember(args.content, project=args.project, kind=args.kind, tags=_split(args.tags),
                               importance=args.importance, pinned=args.pin, source="cli")
            print(f"Remembered #{mid}")
        elif action == "recall":
            for m in mem.recall(args.query, project=args.project, k=args.k, token_budget=args.budget,
                                  min_score=args.min_score):
                print(f"#{m.id:<5} {m.score:.3f}  [{m.kind} · {m.project_id or 'global'}] {m.content}")
        elif action == "brief":
            print(mem.brief(args.project, query=args.query))
        elif action == "start":
            sid = mem.start_session(args.project_id, agent_id=args.agent)
            print(f"Session: {sid}\n")
            print(mem.brief(args.project_id, query=args.query))
        elif action == "end":
            mem.end_session(args.session_id, args.summary)
            print(f"Ended {args.session_id}")
        elif action == "forget":
            print("Forgotten" if mem.forget(args.memory_id) else "Not found")
        elif action == "compact":
            dropped = mem.compact(args.project, keep=args.keep, dry_run=args.dry_run)
            verb = "Would drop" if args.dry_run else "Dropped"
            print(f"{verb} {len(dropped)} memories: {dropped}")
        elif action == "decisions":
            for d in mem.list_decisions(args.project, args.type):
                print(f"{d['created_at'][:16]}  {d['decision_type']:<6} {d['answer']:<10} "
                      f"by {d['resolved_by']:<8} {d['question']}")
            print("\nBy resolver:", json.dumps(mem.decision_cost(args.project), indent=2))
        elif action == "export":
            print(f"Exported {mem.export_jsonl(args.path)} records to {args.path}")
        elif action == "import":
            print(f"Imported {mem.import_jsonl(args.path)} records from {args.path}")
        elif action == "session-start":
            seed = Path(args.seed)
            if mem.is_empty() and seed.exists():
                mem.import_jsonl(seed)
            print(mem.brief(args.project))
        else:
            print("Usage: rudra memory {project,projects,add,recall,brief,start,end,forget,"
                  "compact,decisions,export,import,session-start}")


if __name__ == "__main__":
    main()
