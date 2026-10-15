# VOLT Agentic Console

A React + Node agentic AI application that gives the capabilities in the `volt_deploy` package
(VOLT: Vision, Orchestrate, Launch, Transform) a working interface. It runs on Claude: Rudra, VOLT's master orchestrator,
delegates to VOLT's specialist agents, which find and load VOLT skill packs and call deterministic finance tools.

```
React UI (Vite)  ──SSE──▶  Node API (Express)  ──▶  Claude Messages API (streaming tool loop)
  Console · Workflows        orchestrator.ts          Rudra ─┬─ consult_agent ×N (parallel)
  Agents · Skill Finder      tools.ts                        ├─ find_agents / find_skills / load_skill
  Services · Analytics       catalog.ts  ◀── data/volt-catalog.json + volt-skills.json.gz
  Capability Health          analytics.ts (APQC, maturity, NPV/IRR, value case)
```

## What it enables

| VOLT capability (validated in `volt_deploy`) | How the console exposes it |
|---|---|
| Agent registry: 236 agents in 48 layers, each with a system prompt (`agents.AGENT_REGISTRY`) | **Agents** view; chat with any agent directly; every agent runs on its own VOLT system prompt |
| Rudra orchestration and agent routing (`route_to_agent`, `api/graph/supervisor`) | **Console**: Rudra routes, delegates to several specialists in parallel and synthesises one deliverable |
| 35 multi-phase workflows (`agents.WORKFLOWS`) and intake questions (`WORKFLOW_INTAKE`) | **Workflows**: intake form, then phases run in order, agents in parallel within a phase, then Rudra synthesis |
| Consulting services catalogue: 60 services with coverage ratings (`CONSULTING_SERVICES`) | **Services**: practice → sub-practice → service, launch the mapped workflow |
| Skill discovery: 391 skills (`discover_all_skills`) | **Skill Finder** view, plus the `find_skills` / `load_skill` tools agents call |
| APQC benchmarking, maturity diagnostics and value cases | **Analytics** view, plus `apqc_benchmark`, `score_maturity`, `appraise_investment`, `build_value_case` tools |
| Package integrity (skill provenance, registry consistency) | **Capability Health**: what the registry references against what the package ships |

## Run it

```bash
cd volt-app
npm install
cp .env.example .env            # set ANTHROPIC_API_KEY for live mode; leave empty for demo mode
npm run dev                     # API on :8787, UI on http://localhost:5173
```

Production: `npm run build && npm start` serves the built UI and the API together on `PORT` (default 8787).

**Demo mode.** With no Claude credentials (or the *demo* toggle on), the console runs an offline simulator.
Routing, the Skill Finder, benchmarks and workflow sequencing are real, and agent prose is assembled from the
registry and labelled as simulated.

**Live mode** uses `claude-opus-5-5` with adaptive thinking. Progress updates stream into the activity feed,
the system prompt is cached, and server-side refusal fallback (`fallbacks: "default"`) is on. Set
`VOLT_FALLBACKS=off` when going through a gateway, Bedrock or Vertex. Effort is `high` for Rudra and `medium`
for specialists (`VOLT_ORCHESTRATOR_EFFORT` / `VOLT_SPECIALIST_EFFORT`).

## Refreshing from your `volt_deploy` folder

The catalog in `data/` was exported from `volt_deploy@59787eb`. To re-export after VOLT changes:

```bash
python -I scripts/export_volt_catalog.py "C:\Users\<you>\Documents\Claude\Cowork\Finance Innovation Hub\volt_deploy"
```

The script imports VOLT's own registry module, so the console sees exactly what the VOLT runtime sees.

## Tests

```bash
npm test            # catalog, routing, Skill Finder, analytics, tool schemas, and the live agent loop against a mocked Messages API
npm run typecheck
```

## Evaluation of `volt_deploy@59787eb`

**What's there.** A FastAPI backend with a Next.js UI, 1,870 files. It has:

- 236 agents
- 35 workflows
- 60 services: 29 full coverage, 29 partial, 2 gaps
- 391 shipped skills
- 9 MCP connectors: Oracle ERP/EPM, SAP S/4HANA, SAP Concur, OneStream, Workday HCM, reconciliation, image generation, F-VOLT
- a reconciliation engine and a deliverable generator
- 34 test modules covering routing, the agent loop, workflows, skill provenance and output contracts

**Findings the console surfaces or fixes:**

1. **Skills that are referenced but not shipped.** Agents and services reference 94 skill ids the package does not contain; 12 agents lose some or all of their skill packs.
   - Most are `*-automation` connectors.
   - Several are document skills: `pdf`, `xlsx`, `pptx`, `docx`.
   - The **Capability Health** view lists them. `load_skill` answers with the closest shipped skills instead of failing silently.
2. **Weak keyword routing.** `route_to_agent()` counts raw keyword substrings, which sends 4 of 6 sample requests to a generic agent:

   | Request | VOLT `route_to_agent` | Console router (top match) |
   |---|---|---|
   | Our month-end close takes 12 days on SAP S/4HANA | si-functional-lead | sap-fico-specialist |
   | Day 1 readiness for an acquisition | ma-due-diligence-agent | business-readiness-lead (ma-day1-readiness-lead ranked 2nd) |
   | Workday payroll implementation | si-functional-lead | workday-payroll-lead |
   | reconcile nostro accounts | consolidation-reporting-agent | oracle-arcs-lead (`banking-nostro-recon` via Skill Finder) |
   | OSFI BCAR capital ratio · IFRS 16 lease portfolio | correct | correct |

   The console's BM25-style router weighs keywords, name, description and the system prompt. In live mode Rudra makes the final routing decision anyway.
3. **An orphaned intake set.** `WORKFLOW_INTAKE["reconciliation"]` matches no workflow id, so its questions are never shown.
4. **Agents outside every workflow.** 92 agents are in no workflow or service, so they are reachable only through chat. The console makes all of them addressable.
5. **Inert CI.** `.github/workflows/deploy-azure.yml` cannot run from this folder; VOLT's own README already flags this.

**Not ported (yet).** The Python engines stay in `volt_deploy`: reconciliation, the PPTX/DOCX export templates, SharePoint sync, and the MCP connectors. A natural next step is a bridge tool that calls VOLT's FastAPI endpoints for those capabilities from inside an agent turn.
