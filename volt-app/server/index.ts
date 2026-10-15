/**
 * VOLT Agentic Console API.
 *
 *   GET  /api/catalog   agents, workflows, services, skills, intake, health
 *   GET  /api/agents/:id   one agent incl. its VOLT system prompt
 *   GET  /api/skills/:id   one skill's SKILL.md
 *   POST /api/run       Server-Sent Events stream of a run (see shared/events.ts)
 *   GET  /api/healthz
 *
 * In production it also serves the built React app from dist/.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import express from "express";
import { z } from "zod";
import { loadCatalog, loadSkillBody, rankSkills } from "./catalog.js";
import { runLocalTool, schemas, type ToolName } from "./tools.js";
import { BENCHMARKS } from "./analytics.js";
import { MODEL, errorMessage, getSession, intakeFor, runLive, type Emit } from "./orchestrator.js";
import { runDemo } from "./demo.js";
import { ORCHESTRATOR_LANE, type CatalogResponse, type RunMode, type VoltEvent } from "../shared/events.js";

const catalog = loadCatalog();
const app = express();
app.use(express.json({ limit: "1mb" }));

/** Live when any Claude credential source is configured; VOLT_MODE overrides. */
function detectMode(): RunMode {
  const forced = process.env.VOLT_MODE;
  if (forced === "live" || forced === "demo") return forced;
  const env = ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_PROFILE", "ANTHROPIC_FEDERATION_RULE_ID"];
  if (env.some((k) => process.env[k])) return "live";
  return fs.existsSync(path.join(os.homedir(), ".config", "anthropic")) ? "live" : "demo";
}
const mode = detectMode();

app.get("/api/healthz", (_req, res) => {
  res.json({ ok: true, mode, model: MODEL, agents: catalog.agents.length });
});

app.get("/api/catalog", (_req, res) => {
  const body: CatalogResponse = {
    source: catalog.source,
    mode,
    model: MODEL,
    agents: catalog.agents.map(({ systemPrompt: _p, ...a }) => a),
    workflows: catalog.workflows,
    services: catalog.services,
    intake: catalog.intake,
    layerColors: catalog.layerColors,
    skills: catalog.skills.map(({ industry: _i, ...s }) => s),
    health: catalog.health,
    benchmarks: BENCHMARKS.map(({ pcf: _p, ...b }) => b),
  };
  res.json(body);
});

app.get("/api/agents/:id", (req, res) => {
  const agent = catalog.agentById.get(req.params.id);
  if (!agent) return void res.status(404).json({ error: "unknown agent" });
  res.json({
    ...agent,
    workflows: catalog.workflows.filter((w) => w.agents.includes(agent.id)).map((w) => w.id),
    services: catalog.services.filter((s) => s.agents.includes(agent.id)).map((s) => s.code),
  });
});

/** Skill Finder: ranked skill matches for a free-text task. */
app.get("/api/skills", (req, res) => {
  const q = String(req.query.q ?? "").slice(0, 500);
  res.json(
    rankSkills(catalog, q, 12).map(({ skill, score }) => ({
      ...skill,
      score,
      usedBy: catalog.agents.filter((a) => a.skills.includes(skill.id)).map((a) => a.id),
    })),
  );
});

/** Direct access to the deterministic analytics tools (same code the agents call). */
const DIRECT_TOOLS = new Set<ToolName>(["apqc_benchmark", "score_maturity", "appraise_investment", "build_value_case", "find_agents", "find_skills"]);
app.post("/api/tools/:name", (req, res) => {
  const name = req.params.name as ToolName;
  if (!DIRECT_TOOLS.has(name)) return void res.status(404).json({ error: "unknown tool" });
  const parsed = schemas[name].safeParse(req.body);
  if (!parsed.success) return void res.status(400).json({ error: parsed.error.message });
  const r = runLocalTool(catalog, name as Exclude<ToolName, "consult_agent">, parsed.data);
  res.status(r.ok ? 200 : 400).json(r);
});

app.get("/api/skills/:id", (req, res) => {
  const meta = catalog.skillById.get(req.params.id);
  const body = loadSkillBody(req.params.id);
  if (!meta || !body) return void res.status(404).json({ error: "unknown skill" });
  res.json({ ...meta, body: body.body, truncated: body.truncated });
});

app.get("/api/workflows/:id/intake", (req, res) => {
  if (!catalog.workflowById.has(req.params.id)) return void res.status(404).json({ error: "unknown workflow" });
  res.json(intakeFor(catalog, req.params.id));
});

const RunBody = z.object({
  sessionId: z.string().max(100).optional(),
  prompt: z.string().min(1).max(20000),
  workflowId: z.string().optional(),
  intake: z.record(z.string(), z.string()).optional(),
  agentId: z.string().optional(),
  demo: z.boolean().optional(),
});

app.post("/api/run", async (req, res) => {
  const parsed = RunBody.safeParse(req.body);
  if (!parsed.success) return void res.status(400).json({ error: parsed.error.message });
  const body = parsed.data;

  res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive" });
  const controller = new AbortController();
  res.on("close", () => controller.abort());
  const emit: Emit = (e: VoltEvent) => {
    if (!res.writableEnded) res.write(`data: ${JSON.stringify(e)}\n\n`);
  };

  const runMode: RunMode = body.demo || mode === "demo" ? "demo" : "live";
  const session = getSession(body.sessionId);
  const kind = body.workflowId ? "workflow" : body.agentId && body.agentId !== "rudra" ? "agent" : "orchestrate";
  const title = body.workflowId
    ? catalog.workflowById.get(body.workflowId)?.name ?? body.workflowId
    : body.agentId
      ? catalog.agentById.get(body.agentId)?.name ?? body.agentId
      : "Rudra orchestration";
  emit({ type: "run_start", runId: crypto.randomUUID(), sessionId: session.id, mode: runMode, model: runMode === "live" ? MODEL : "simulator", kind, title });

  try {
    if (runMode === "demo") await runDemo(catalog, body, emit, controller.signal);
    else await runLive(catalog, body, session, emit, controller.signal);
  } catch (err) {
    if (!controller.signal.aborted) emit({ type: "error", lane: ORCHESTRATOR_LANE, message: errorMessage(err) });
  }
  emit({ type: "done", sessionId: session.id });
  res.end();
});

if (process.env.NODE_ENV === "production") {
  const dist = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../dist");
  app.use(express.static(dist));
  app.get(/^(?!\/api\/).*/, (_req, res) => res.sendFile(path.join(dist, "index.html")));
}

const port = Number(process.env.PORT ?? 8787);
app.listen(port, () => {
  console.log(`VOLT Agentic Console API on http://localhost:${port} (${mode} mode, model ${MODEL})`);
  console.log(`Catalog: ${catalog.agents.length} agents, ${catalog.workflows.length} workflows, ${catalog.skills.length} skills from ${catalog.source.name}@${catalog.source.commit?.slice(0, 7) ?? "?"}`);
});
