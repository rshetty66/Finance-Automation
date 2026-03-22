#!/usr/bin/env python3
"""Rudra Multi-Model Agent Framework — Main Entry Point.

Usage:
    python main.py                          # Show status and run demo
    python main.py --week1 "Acme Corp"     # Generate 1-week ERP/EPM package
    python main.py --task "revenue recognition for SaaS contract..."
    python main.py --video roadmap         # Generate animated roadmap video
    python main.py --search "IFRS 15 variable consideration"
    python main.py --status                # Show configuration status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from framework import AgentFramework


def print_banner() -> None:
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║           RUDRA MULTI-MODEL AI AGENT FRAMEWORK  v1.0                       ║
║                                                                              ║
║  Models:  Claude Opus 4.6  (Anthropic)   — Deep reasoning                  ║
║           OpenClaw / GPT-4o (OpenAI)     — Orchestration                   ║
║           Qwen 2.5 (Alibaba DashScope)   — Code & multilingual              ║
║                                                                              ║
║  Tools:   Canva MCP        — Executive presentations & dashboards            ║
║           Databricks       — Vector search, analytics & ML pipelines         ║
║           Video Animation  — Animated roadmaps & KPI dashboards              ║
║           ERP/EPM Tools    — Consulting deliverables in 1 week               ║
║                                                                              ║
║  Agents:  Rudra            — Principal consulting orchestrator                ║
║           OpenClaw         — State machine workflow engine                    ║
║           8 Specialists    — Accounting, ERP, EPM, Design, Data              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def run_demo(fw: AgentFramework) -> None:
    """Run a quick demo showing all framework capabilities."""
    print("\n[1/5] Checking framework status...")
    status = fw.status()
    for model_name, cfg in status["models"].items():
        icon = "✓" if cfg["configured"] else "✗ (set API key)"
        print(f"  {icon}  {model_name:12} → {cfg['model']} ({cfg['provider']})")

    print("\n[2/5] Generating 1-week ERP/EPM deliverable package...")
    package = fw.run_week1_package(
        client_name="Sprott Asset Management",
        project_name="Oracle ERP Cloud Transformation",
        erp_system="Oracle ERP Cloud",
        epm_system="Oracle EPM Cloud",
        include_video=True,
        include_canva=True,
    )
    print(f"  ✓  Deliverables: {len(package.get('deliverables', []))} generated")
    if package.get("roadmap_video"):
        print(f"  ✓  Roadmap video: {package['roadmap_video'].get('path', 'N/A')}")
    if package.get("executive_deck"):
        print(f"  ✓  Executive deck: {package['executive_deck'].get('design', {}).get('title', 'N/A')}")

    print("\n[3/5] Searching accounting standards (Databricks Vector Search)...")
    results = fw.search_standards("revenue recognition SaaS contract performance obligations", "IFRS")
    print(f"  ✓  Found {len(results)} relevant standards passages")
    if results:
        print(f"  ↳  Top result: {results[0].get('source', 'N/A')} (score: {results[0].get('score', 0):.2f})")

    print("\n[4/5] Generating animated KPI dashboard video...")
    kpis = [
        {"name": "Days to Close", "value": 5, "target": 4},
        {"name": "Auto-Post Rate %", "value": 78, "target": 85},
        {"name": "Recon Match %", "value": 92, "target": 95},
        {"name": "JE Error Rate %", "value": 2.1, "target": 1.5},
    ]
    video = fw.generate_video_deliverable("kpi_dashboard", {"kpis": kpis, "title": "CFO Close Dashboard"})
    print(f"  ✓  Video: {video.get('path', 'N/A')} ({video.get('engine', 'N/A')} engine)")

    print("\n[5/5] Running accounting analysis (Claude Opus 4.6)...")
    result = fw.run_engagement(
        task="revenue_recognition",
        facts="SaaS company sells 3-year subscription ($120K/yr) bundled with implementation services ($50K one-time) and dedicated support ($20K/yr). Customer pays annually upfront.",
        reporting_basis="IFRS",
        audience="controller",
        client_name="TechCo SaaS",
    )
    print(f"  ✓  Analysis complete ({result.elapsed_seconds:.1f}s) via {result.model_used}")
    if result.output and len(result.output) > 50:
        preview = result.output[:300].replace("\n", " ")
        print(f"  ↳  {preview}...")

    print(f"\n✓ Demo complete. Outputs saved to: {fw.output_dir}/")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rudra Multi-Model Agent Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --status
  python main.py --week1 "Acme Corp" "ERP Transformation"
  python main.py --task "Analyze lease under IFRS 16: 5-year office lease, $500K/year, 5% IBR"
  python main.py --video roadmap --project "Oracle Implementation"
  python main.py --search "IFRS 15 variable consideration"
  python main.py --pipeline "Build finance close pipeline: GL actuals → Delta Lake → Reporting"
        """,
    )
    parser.add_argument("--status", action="store_true", help="Show framework status")
    parser.add_argument("--week1", nargs=2, metavar=("CLIENT", "PROJECT"), help="Generate 1-week package")
    parser.add_argument("--task", type=str, help="Run a consulting task")
    parser.add_argument("--standard", default="IFRS", help="Reporting standard (IFRS/US_GAAP)")
    parser.add_argument("--video", choices=["roadmap", "kpi", "process", "waterfall", "luma"],
                        help="Generate video animation")
    parser.add_argument("--project", default="ERP Transformation", help="Project name for video")
    parser.add_argument("--search", type=str, help="Search accounting standards")
    parser.add_argument("--pipeline", type=str, help="Design Databricks pipeline")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    print_banner()

    fw = AgentFramework(output_dir=args.output)

    if args.status:
        status = fw.status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\nFramework Status:")
            print(f"  Version: {status['framework']}")
            print("\n  Models:")
            for name, cfg in status["models"].items():
                icon = "✓" if cfg["configured"] else "✗"
                print(f"    [{icon}] {name:12} → {cfg['model']} ({cfg['provider']})")
            print("\n  Tools:")
            for name, enabled in status["tools"].items():
                icon = "✓" if enabled else "✗"
                print(f"    [{icon}] {name}")
            print(f"\n  Agents: {', '.join(status['agents'])}")
        return

    if args.week1:
        client_name, project_name = args.week1
        print(f"\nGenerating 1-week ERP/EPM package for: {client_name} — {project_name}")
        result = fw.run_week1_package(client_name, project_name)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\n✓ Package generated in: {fw.output_dir}/deliverables/")
            if result.get("deliverables"):
                print(f"  Deliverables: {len(result['deliverables'])} files")
            if result.get("roadmap_video"):
                print(f"  Video: {result['roadmap_video'].get('path')}")
        return

    if args.task:
        print(f"\nRunning task: {args.task[:80]}...")
        result = fw.run_engagement(task=args.task, reporting_basis=args.standard)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(result.output)
            print(f"\n[Model: {result.model_used} | Time: {result.elapsed_seconds:.1f}s]")
        return

    if args.video:
        print(f"\nGenerating {args.video} animation...")
        video_data = {
            "roadmap": {
                "deliverable_type": "roadmap",
                "data": {
                    "phases": [
                        {"name": "Assess & Design", "start_week": 0, "end_week": 1},
                        {"name": "Build & Configure", "start_week": 1, "end_week": 3},
                        {"name": "Test", "start_week": 3, "end_week": 4},
                        {"name": "Deploy", "start_week": 4, "end_week": 5},
                    ]
                },
            },
            "kpi": {
                "deliverable_type": "kpi_dashboard",
                "data": {
                    "kpis": [
                        {"name": "Close Days", "value": 5, "target": 4},
                        {"name": "Auto-Post %", "value": 78, "target": 85},
                        {"name": "Recon %", "value": 92, "target": 95},
                    ],
                    "title": "CFO Dashboard",
                },
            },
            "process": {
                "deliverable_type": "process_flow",
                "data": {
                    "process_name": "Record-to-Report",
                    "steps": [
                        {"name": "Sub-Ledger Close"},
                        {"name": "Journal Entries"},
                        {"name": "Reconciliation"},
                        {"name": "Consolidation"},
                        {"name": "Financial Reporting"},
                    ],
                },
            },
            "waterfall": {
                "deliverable_type": "waterfall",
                "data": {
                    "title": "Budget vs Actual Variance",
                    "categories": ["Budget", "Volume", "Price", "Mix", "Costs", "Actual"],
                    "values": [10000, 500, -200, 150, -300, 10150],
                },
            },
            "luma": {
                "deliverable_type": "luma",
                "data": {"prompt": f"Professional finance consulting presentation for {args.project}, dark background, data visualization, business charts"},
            },
        }[args.video]

        result = fw.generate_video_deliverable(
            deliverable_type=video_data["deliverable_type"],
            data=video_data["data"],
            project_name=args.project,
        )
        print(f"  ✓ Video generated: {result.get('path')} ({result.get('engine')} engine)")
        return

    if args.search:
        print(f"\nSearching: {args.search}")
        results = fw.search_standards(args.search)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r.get('source', 'Unknown')} (score: {r.get('score', 0):.2f})")
            print(f"    {r.get('chunk', '')[:200]}...")
        return

    if args.pipeline:
        print(f"\nDesigning Databricks pipeline: {args.pipeline[:80]}...")
        result = fw.run_databricks_pipeline(args.pipeline)
        print(f"\n{'='*60}")
        print(result.output)
        print(f"\n[Model: {result.model_used} | Time: {result.elapsed_seconds:.1f}s]")
        return

    # Default: run full demo
    run_demo(fw)


if __name__ == "__main__":
    main()
