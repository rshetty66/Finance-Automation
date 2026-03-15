"""
Rudra Multimodal Agentic AI — Main Entry Point.

Demonstrates the full pipeline:
  1. Multimodal input (image/text/voice) → Claude vision extraction
  2. Intent routing (Claude replaces keyword triggers)
  3. Parallel agent execution (Kimi PARL pattern)
  4. Databricks persistence and benchmarking
  5. Rudra orchestrator synthesis

Run:
    python -m multimodal_ai.main --demo month_end_close
    python -m multimodal_ai.main --image /path/to/dashboard.png --doc-type dashboard
    python -m multimodal_ai.main --text "We need to redesign our COA for 3 legal entities"
"""

import argparse
import asyncio
import json
import os
import sys


def demo_intent_routing():
    """Show trigger-free routing vs old keyword table."""
    from multimodal_ai.intent_router import route_to_agent, route_multimodal

    print("\n=== INTENT ROUTING (No Triggers) ===\n")

    test_inputs = [
        ("We need to redesign our Chart of Accounts for 5 legal entities in 3 countries",
         {"source": "text"}),
        ("Our month-end close is taking 9 days. APQC says top quartile is 4 days.",
         {"source": "text"}),
        ("The CFO wants a real-time dashboard showing treasury position and cash forecast",
         {"source": "text"}),
        ("We're implementing Oracle ERP Cloud and need help across all workstreams",
         {"source": "text"}),
    ]

    for text, context in test_inputs:
        print(f"Input: {text[:70]}...")
        result = route_to_agent(text, context)
        print(f"  → Agents: {result['agents']}")
        print(f"  → Parallel: {result['parallel']}")
        print(f"  → Reason: {result.get('reasoning', '')[:100]}")
        print()


async def demo_month_end_close():
    """Run parallel month-end close optimization."""
    from multimodal_ai.kimi_orchestrator import run_month_end_close

    print("\n=== MONTH-END CLOSE OPTIMIZATION (PARL) ===\n")

    client_data = {
        "client": "BMO Financial Group",
        "current_close_days": 9,
        "revenue_usd": 900_000_000,
        "finance_ftes": 85,
        "erp": "Oracle ERP Cloud",
        "entities": 12,
        "pain_points": [
            "Manual intercompany reconciliation",
            "8+ day close cycle",
            "Distributed finance operations",
        ],
    }

    print(f"Client: {client_data['client']}")
    print(f"Current close: {client_data['current_close_days']} days (target: 4 days)")
    print(f"Spawning 4 Rudra agents in parallel...\n")

    result = await run_month_end_close(client_data)

    print(f"\n=== SYNTHESIS ===\n")
    print(result["synthesis"][:1000] + "...")

    return result


async def demo_multimodal_routing(image_path: str, doc_type: str):
    """Process an image and route to agents."""
    from multimodal_ai.multimodal_input import process_and_route
    from multimodal_ai.kimi_orchestrator import parallel_rudra_execution

    print(f"\n=== MULTIMODAL PIPELINE ===\n")
    print(f"Image: {image_path}")
    print(f"Doc type: {doc_type}\n")

    # Step 1: Vision extraction
    print("Step 1: Extracting document content via Claude vision...")
    pipeline_result = process_and_route(image_path=image_path, doc_type=doc_type)

    print(f"\nExtraction preview:\n{pipeline_result['extraction'][:300]}...\n")
    print(f"Step 2: Intent routing selected agents: {pipeline_result['routing']['agents']}")
    print(f"Parallel: {pipeline_result['routing']['parallel']}")

    # Step 3: Run the routed agents
    if pipeline_result["routing"]["agents"]:
        print(f"\nStep 3: Running {len(pipeline_result['routing']['agents'])} agents in parallel...")
        tasks = [
            {
                "agent": agent,
                "task": f"Analyze this {doc_type} document and provide insights. "
                        f"Document content: {pipeline_result['extraction'][:500]}",
                "context": {"doc_type": doc_type},
            }
            for agent in pipeline_result["routing"]["agents"]
        ]
        agent_results = await parallel_rudra_execution(tasks)
        print(f"\nAgents complete. {len(agent_results)} results collected.")

    return pipeline_result


def demo_databricks():
    """Show Databricks integration (mock mode if not connected)."""
    from multimodal_ai.databricks_backend import RudraDataBrain

    print("\n=== DATABRICKS BACKEND ===\n")

    with RudraDataBrain() as brain:
        # Live APQC benchmarks (replaces static table)
        print("Querying live APQC benchmarks for R2R...")
        benchmarks = brain.get_apqc_benchmarks("9.3", "financial_services")
        for bm in benchmarks[:3]:
            print(f"  {bm}")

        # Gap analysis
        print("\nCalculating benchmark gaps for client...")
        client_metrics = {
            "days_to_close": 9.0,
            "ftes_per_1b_revenue": 85.0,
            "cost_pct_revenue": 1.4,
        }
        gaps = brain.get_benchmark_gap(client_metrics, "9.3", "financial_services")
        for metric, gap in gaps.items():
            print(f"  {metric}: current={gap['current']}, top25={gap['top25']}, "
                  f"gap={gap['gap_to_top25']:.1f} ({gap['percentile_position']})")

        # Log agent execution
        print("\nLogging mock agent execution to MLflow...")
        run_id = brain.log_agent_execution(
            agent_name="apqc-researcher",
            task="Benchmark close performance for BMO",
            output="Client is in bottom 50th percentile for close cycle time...",
            metadata={"client": "BMO", "process": "R2R"},
        )
        print(f"  Run ID: {run_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Rudra Multimodal Agentic AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--demo",
        choices=["routing", "month_end_close", "databricks", "all"],
        default="routing",
        help="Demo to run",
    )
    parser.add_argument("--image", help="Image path for multimodal demo")
    parser.add_argument(
        "--doc-type",
        default="general",
        choices=["excel", "dashboard", "pdf_page", "process_flow", "coa", "general"],
    )
    parser.add_argument("--text", help="Text input for intent routing demo")

    args = parser.parse_args()

    if args.image:
        asyncio.run(demo_multimodal_routing(args.image, args.doc_type))
        return

    if args.text:
        from multimodal_ai.intent_router import route_to_agent
        result = route_to_agent(args.text)
        print(json.dumps(result, indent=2))
        return

    if args.demo == "routing" or args.demo == "all":
        demo_intent_routing()

    if args.demo == "databricks" or args.demo == "all":
        demo_databricks()

    if args.demo == "month_end_close" or args.demo == "all":
        asyncio.run(demo_month_end_close())


if __name__ == "__main__":
    main()
