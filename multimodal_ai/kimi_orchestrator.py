"""
Kimi PARL Orchestrator — Parallel Agent Reinforcement Learning pattern.

Implements the FT_AgenticFramework.md recommendation for parallel Rudra
agent execution. Replaces sequential trigger chains with concurrent spawning
of independent specialist agents via the Claude Agent SDK.

Pattern: Orchestrator (Claude) → frozen sub-agents run concurrently →
results merged → fact-check validates → output delivered.
"""

import asyncio
import json
import os
import time
from pathlib import Path

import anthropic
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ResultMessage

AGENTS_DIR = Path(__file__).parent.parent / "Rudra_Agents"
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def _load_agent_definition(agent_name: str) -> str:
    """Load a Rudra agent's .md definition file."""
    agent_file = AGENTS_DIR / f"{agent_name}.md"
    if agent_file.exists():
        return agent_file.read_text()
    return f"You are the {agent_name} specialist agent for finance transformation."


async def spawn_rudra_agent(agent_name: str, task: str, context: dict) -> dict:
    """
    Spawn a single Rudra sub-agent using the Claude Agent SDK.
    Each agent runs independently — no shared state, no blocking.

    Args:
        agent_name: Name matching a file in Rudra_Agents/
        task: Specific task for this agent to complete
        context: Shared context dict (client data, prior outputs, etc.)

    Returns:
        dict with agent name and structured output
    """
    agent_def = _load_agent_definition(agent_name)
    system_prompt = agent_def[:3000]  # YAML frontmatter + core instructions

    result_text = ""
    async for message in query(
        prompt=f"Task: {task}\n\nContext:\n{json.dumps(context, indent=2)}",
        options=ClaudeAgentOptions(
            model="claude-opus-4-6",
            system_prompt=system_prompt,
            allowed_tools=["Read", "Glob"],
            max_turns=10,
            cwd=str(AGENTS_DIR.parent),
        ),
    ):
        if isinstance(message, ResultMessage):
            result_text = message.result

    return {
        "agent": agent_name,
        "task": task,
        "output": result_text,
        "timestamp": time.time(),
    }


async def parallel_rudra_execution(tasks: list[dict]) -> list[dict]:
    """
    PARL (Parallel Agent Reinforcement Learning) pattern from FT_AgenticFramework.md.

    Runs ALL independent Rudra agents concurrently — no sequential trigger chains.
    Results are gathered when all agents complete, then merged by the orchestrator.

    Args:
        tasks: List of dicts, each with keys:
               - agent: str (Rudra agent name)
               - task: str (specific work for this agent)
               - context: dict (optional, shared engagement context)

    Returns:
        List of result dicts from all agents

    Example:
        tasks = [
            {"agent": "si-finance-process-lead", "task": "Analyze R2R gaps", "context": data},
            {"agent": "apqc-researcher", "task": "Benchmark against peers", "context": data},
            {"agent": "si-data-analytics-lead", "task": "Design close dashboard", "context": data},
        ]
        results = await parallel_rudra_execution(tasks)
    """
    coroutines = [
        spawn_rudra_agent(
            t["agent"],
            t["task"],
            t.get("context", {}),
        )
        for t in tasks
    ]

    print(f"[PARL] Spawning {len(coroutines)} agents in parallel...")
    start = time.time()

    results = await asyncio.gather(*coroutines, return_exceptions=True)
    elapsed = time.time() - start

    print(f"[PARL] All agents complete in {elapsed:.1f}s")

    # Filter out exceptions, log them
    clean_results = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"[PARL] Agent '{tasks[i]['agent']}' failed: {r}")
            clean_results.append({
                "agent": tasks[i]["agent"],
                "task": tasks[i]["task"],
                "output": f"Error: {str(r)}",
                "error": True,
            })
        else:
            clean_results.append(r)

    return clean_results


async def merge_agent_outputs(results: list[dict], client_context: dict) -> str:
    """
    Rudra orchestrator synthesizes all parallel agent outputs into a
    unified, executive-grade deliverable.

    Args:
        results: Outputs from parallel_rudra_execution
        client_context: Original engagement context

    Returns:
        Synthesized final output from Rudra
    """
    agents_summary = "\n\n".join(
        f"=== {r['agent']} ===\n{r['output']}"
        for r in results
        if not r.get("error")
    )

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=_load_agent_definition("rudra")[:3000],
        messages=[
            {
                "role": "user",
                "content": f"""You have received specialist outputs from {len(results)} parallel agents.
Synthesize these into a single, board-ready deliverable for the client.

Client Context:
{json.dumps(client_context, indent=2)}

Specialist Agent Outputs:
{agents_summary}

Produce a unified executive summary with:
1. Key findings and recommendations
2. Prioritized action plan
3. Risk flags requiring attention
4. Next steps with owners and timelines""",
            }
        ],
    ) as stream:
        final = stream.get_final_message()

    return next(b.text for b in final.content if b.type == "text")


# ─── Pre-built Engagement Patterns ─────────────────────────────────────────

async def run_month_end_close(client_data: dict) -> dict:
    """
    Month-end close optimization — 4 agents in parallel, not triggered sequentially.
    Target: reduce 8-10 day close to APQC top-quartile 4 days.
    """
    tasks = [
        {
            "agent": "si-finance-process-lead",
            "task": "Analyze current R2R close timeline. Identify top 3 bottlenecks. "
                    "Recommend automation opportunities for each close step.",
            "context": client_data,
        },
        {
            "agent": "apqc-researcher",
            "task": "Benchmark this client's close performance vs APQC data. "
                    "What is the gap to top quartile? Quantify the value of closing it.",
            "context": client_data,
        },
        {
            "agent": "si-data-analytics-lead",
            "task": "Design a close KPI dashboard. Include: days to close by entity, "
                    "open items aging, intercompany matching status, reconciliation completion.",
            "context": client_data,
        },
        {
            "agent": "fact-check-agent",
            "task": "Audit all benchmarks and statistics cited in this session. "
                    "Map each claim to its APQC source. Flag any unsupported assertions.",
            "context": client_data,
        },
    ]

    results = await parallel_rudra_execution(tasks)
    synthesis = await merge_agent_outputs(results, client_data)

    return {"agent_outputs": results, "synthesis": synthesis}


async def run_erp_implementation_kickoff(client_data: dict) -> dict:
    """
    Full ERP implementation kickoff — all SI workstreams launched simultaneously.
    Replaces sequential workstream activation triggers.
    """
    tasks = [
        {
            "agent": "si-finance-process-lead",
            "task": "Design target state R2R, O2C, P2P processes for the new ERP.",
            "context": client_data,
        },
        {
            "agent": "si-functional-lead",
            "task": "Define Oracle ERP Cloud configuration requirements for GL, AP, AR, CM.",
            "context": client_data,
        },
        {
            "agent": "si-data-architect",
            "task": "Create data migration strategy: legacy extraction, transformation rules, validation.",
            "context": client_data,
        },
        {
            "agent": "si-integration-lead",
            "task": "Design integration architecture: APIs, middleware, B2B/EDI touchpoints.",
            "context": client_data,
        },
        {
            "agent": "si-security-controls-lead",
            "task": "Define SOD matrix and SOX control framework for the new system.",
            "context": client_data,
        },
        {
            "agent": "si-change-management-lead",
            "task": "Develop OCM strategy: stakeholder analysis, training plan, adoption metrics.",
            "context": client_data,
        },
        {
            "agent": "apqc-researcher",
            "task": "Validate business case using APQC benchmarks. Set transformation targets.",
            "context": client_data,
        },
    ]

    results = await parallel_rudra_execution(tasks)
    synthesis = await merge_agent_outputs(results, client_data)

    return {"agent_outputs": results, "synthesis": synthesis}


async def run_coa_redesign(client_data: dict) -> dict:
    """
    Chart of Accounts redesign — design + validation + visualization in parallel.
    """
    tasks = [
        {
            "agent": "coa-designer",
            "task": "Design new COA structure: segment order, natural accounts, "
                    "dimensions, governance model. Handle multi-entity requirements.",
            "context": client_data,
        },
        {
            "agent": "accounting-hub-architect",
            "task": "Design Accounting Hub architecture to consolidate multiple ERP sources "
                    "into the new COA. Define event capture and rules engine.",
            "context": client_data,
        },
        {
            "agent": "creative-designer",
            "task": "Create an interactive COA Explorer prototype that allows stakeholders "
                    "to navigate the new chart of accounts structure visually.",
            "context": client_data,
        },
    ]

    results = await parallel_rudra_execution(tasks)
    synthesis = await merge_agent_outputs(results, client_data)

    return {"agent_outputs": results, "synthesis": synthesis}
