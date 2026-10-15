/**
 * Offline simulator. Runs when no Claude credentials are configured (or the
 * user ticks "demo"), so the console can be explored without an API key.
 *
 * It exercises the same deterministic machinery as live runs (agent routing,
 * the Skill Finder, APQC benchmarks, workflow phase sequencing) and emits the
 * same event stream. The prose is assembled from the VOLT registry and is
 * clearly labelled as simulated: no model is called.
 */
import { type AgentDef, type Catalog, rankAgents, rankSkills } from "./catalog.js";
import { compareToBenchmark } from "./analytics.js";
import { intakeFor, type Emit } from "./orchestrator.js";
import { ORCHESTRATOR_LANE, type RunRequest } from "../shared/events.js";

const sleep = (ms: number, signal: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const t = setTimeout(resolve, ms);
    signal.addEventListener("abort", () => { clearTimeout(t); reject(new Error("aborted")); }, { once: true });
  });

async function streamText(lane: string, text: string, emit: Emit, signal: AbortSignal) {
  const chunks = text.match(/[\s\S]{1,48}/g) ?? [];
  for (const c of chunks) {
    emit({ type: "text_delta", lane, text: c });
    await sleep(12, signal);
  }
}

let callSeq = 0;
async function tool(lane: string, name: string, input: unknown, run: () => { summary: string; data?: unknown }, emit: Emit, signal: AbortSignal) {
  const callId = `demo_${++callSeq}`;
  emit({ type: "tool_call", lane, callId, name, input });
  await sleep(250, signal);
  const r = run();
  emit({ type: "tool_result", lane, callId, name, summary: r.summary, data: r.data });
  return r.data;
}

/** Pull client metrics out of free text so the benchmark tool has something to place. */
export function extractMetrics(prompt: string): { metric: string; value: number }[] {
  const out: { metric: string; value: number }[] = [];
  const close = prompt.match(/close[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:business\s+|working\s+)?days?/i) ?? prompt.match(/(\d+(?:\.\d+)?)\s*(?:business\s+|working\s+)?days?[^.]{0,20}close/i);
  if (close) out.push({ metric: "days_to_close", value: Number(close[1]) });
  const dso = prompt.match(/\bDSO\b[^0-9]{0,15}(\d+(?:\.\d+)?)/i);
  if (dso) out.push({ metric: "dso", value: Number(dso[1]) });
  const dpo = prompt.match(/\bDPO\b[^0-9]{0,15}(\d+(?:\.\d+)?)/i);
  if (dpo) out.push({ metric: "dpo", value: Number(dpo[1]) });
  const invoice = prompt.match(/\$\s?(\d+(?:\.\d+)?)\s*(?:per|\/)\s*invoice/i);
  if (invoice) out.push({ metric: "cost_per_invoice_ap", value: Number(invoice[1]) });
  return out;
}

function lens(agent: AgentDef): string {
  const sentences = agent.systemPrompt.replace(/\s+/g, " ").split(/(?<=\.)\s/).slice(0, 2).join(" ");
  return sentences.length > 420 ? sentences.slice(0, 420) + "…" : sentences;
}

function specialistNote(catalog: Catalog, agent: AgentDef, focus: string): string {
  const skills = agent.skills.filter((s) => catalog.skillById.has(s)).slice(0, 6);
  const missing = agent.skills.filter((s) => !catalog.skillById.has(s)).length;
  return `**${agent.icon} ${agent.name}** · _${agent.layer}_

${agent.description}

- **Lens:** ${lens(agent)}
- **Focus on this brief:** ${focus}
- **VOLT skills it draws on:** ${skills.length ? skills.map((s) => `\`${s}\``).join(", ") : "general registry knowledge"}${missing ? ` (${missing} registered skill(s) not shipped in this package)` : ""}
- **Keywords it owns:** ${agent.keywords.slice(0, 8).join(", ")}

> Simulated output: connect a Claude API key for this agent's full reasoning.
`;
}

async function benchmarkBlock(lane: string, prompt: string, emit: Emit, signal: AbortSignal): Promise<string> {
  const rows: string[] = [];
  for (const m of extractMetrics(prompt)) {
    const r = (await tool(lane, "apqc_benchmark", { metric: m.metric, client_value: m.value }, () => {
      const c = compareToBenchmark(m.metric, m.value);
      return "error" in c ? { summary: c.error } : { summary: `${c.benchmark.metric}: client ${m.value} → ${c.quartile}`, data: c };
    }, emit, signal)) as ReturnType<typeof compareToBenchmark> | undefined;
    if (r && !("error" in r)) {
      rows.push(`| ${r.benchmark.metric} | ${r.clientValue} | ${r.benchmark.top25} | ${r.benchmark.median} | ${r.quartile} | ${r.gapToTop25} ${r.benchmark.unit} |`);
    }
  }
  return rows.length
    ? `\n### APQC position\n| Metric | Client | Top quartile | Median | Position | Gap to top quartile |\n|---|---|---|---|---|---|\n${rows.join("\n")}\n`
    : "";
}

export async function runDemo(catalog: Catalog, req: RunRequest, emit: Emit, signal: AbortSignal) {
  const L = ORCHESTRATOR_LANE;

  if (req.workflowId) {
    const wf = catalog.workflowById.get(req.workflowId);
    if (!wf) throw new Error(`Unknown workflow '${req.workflowId}'`);
    const answered = intakeFor(catalog, wf.id).filter((q) => req.intake?.[q.key]);
    for (const [index, phase] of wf.phases.entries()) {
      emit({ type: "phase_start", index, name: phase.name, agents: phase.agents });
      await Promise.all(
        phase.agents.map(async (id) => {
          const agent = catalog.agentById.get(id)!;
          const lane = `${wf.id}:${index}:${id}`;
          emit({ type: "agent_start", lane, parentLane: L, agentId: id, name: agent.name, layer: agent.layer, icon: agent.icon, brief: `${phase.name}: ${req.prompt}` });
          emit({ type: "status", lane, text: `Working the ${phase.name} phase` });
          await streamText(lane, specialistNote(catalog, agent, `${phase.name} contribution for “${req.prompt.slice(0, 140)}”`), emit, signal);
          emit({ type: "agent_end", lane, agentId: id, ok: true });
        }),
      );
      emit({ type: "phase_end", index, name: phase.name });
    }
    emit({ type: "status", lane: L, text: "Rudra is synthesising the workflow deliverable" });
    const bench = await benchmarkBlock(L, req.prompt, emit, signal);
    await streamText(
      L,
      `## ${wf.icon} ${wf.name} — workflow deliverable (simulated)

**Request:** ${req.prompt}
${answered.length ? `\n**Intake:**\n${answered.map((q) => `- ${q.question} — ${req.intake![q.key]}`).join("\n")}\n` : ""}
${wf.description}

| Phase | Agents engaged |
|---|---|
${wf.phases.map((p) => `| ${p.name} | ${p.agents.map((a) => catalog.agentById.get(a)?.name ?? a).join(", ")} |`).join("\n")}
${bench}
### What a live run produces
Each phase's agents run in parallel on Claude with their VOLT system prompts, see earlier phases' outputs, and Rudra reconciles them into an executive deliverable with a recommendations table, risks and next steps.
`,
      emit,
      signal,
    );
    return;
  }

  if (req.agentId && req.agentId !== "rudra") {
    const agent = catalog.agentById.get(req.agentId);
    if (!agent) throw new Error(`Unknown agent '${req.agentId}'`);
    emit({ type: "agent_start", lane: L, parentLane: "", agentId: agent.id, name: agent.name, layer: agent.layer, icon: agent.icon, brief: req.prompt });
    const skills = (await tool(L, "find_skills", { query: req.prompt }, () => {
      const r = rankSkills(catalog, req.prompt, 4);
      return { summary: r.map((x) => x.skill.id).join(", ") || "no matches", data: r.map((x) => ({ skill_id: x.skill.id, description: x.skill.description.slice(0, 200) })) };
    }, emit, signal)) as { skill_id: string }[];
    const bench = await benchmarkBlock(L, req.prompt, emit, signal);
    await streamText(L, `${specialistNote(catalog, agent, req.prompt)}\n**Skill Finder matches:** ${skills.map((s) => `\`${s.skill_id}\``).join(", ") || "none"}\n${bench}`, emit, signal);
    emit({ type: "agent_end", lane: L, agentId: agent.id, ok: true });
    return;
  }

  emit({ type: "status", lane: L, text: `Routing the request across ${catalog.agents.length} VOLT agents` });
  const ranked = (await tool(L, "find_agents", { query: req.prompt, limit: 5 }, () => {
    const r = rankAgents(catalog, req.prompt, 5);
    return { summary: r.map((x) => x.agent.name).join(", ") || "no matches", data: r.map((x) => ({ agent_id: x.agent.id, name: x.agent.name, layer: x.agent.layer, relevance: Math.round(x.score * 10) / 10 })) };
  }, emit, signal)) as { agent_id: string }[];
  const skills = (await tool(L, "find_skills", { query: req.prompt, limit: 5 }, () => {
    const r = rankSkills(catalog, req.prompt, 5);
    return { summary: r.map((x) => x.skill.id).join(", ") || "no matches", data: r.map((x) => ({ skill_id: x.skill.id, category: x.skill.category, description: x.skill.description.slice(0, 200) })) };
  }, emit, signal)) as { skill_id: string }[];

  const panel = ranked.slice(0, 3).map((r) => catalog.agentById.get(r.agent_id)!);
  emit({ type: "status", lane: L, text: `Delegating to ${panel.map((a) => a.name).join(", ")} in parallel` });
  await Promise.all(
    panel.map(async (agent) => {
      const callId = `demo_${++callSeq}`;
      emit({ type: "tool_call", lane: L, callId, name: "consult_agent", input: { agent_id: agent.id, brief: req.prompt } });
      emit({ type: "agent_start", lane: callId, parentLane: L, agentId: agent.id, name: agent.name, layer: agent.layer, icon: agent.icon, brief: req.prompt });
      await streamText(callId, specialistNote(catalog, agent, req.prompt), emit, signal);
      emit({ type: "agent_end", lane: callId, agentId: agent.id, ok: true });
      emit({ type: "tool_result", lane: L, callId, name: "consult_agent", summary: `${agent.name} delivered (simulated)` });
    }),
  );

  const bench = await benchmarkBlock(L, req.prompt, emit, signal);
  const workflows = catalog.workflows
    .map((w) => ({ w, hits: w.agents.filter((a) => panel.some((p) => p.id === a)).length }))
    .filter((x) => x.hits > 0)
    .sort((a, b) => b.hits - a.hits)
    .slice(0, 3);

  await streamText(
    L,
    `## Rudra — engagement framing (simulated)

**Request:** ${req.prompt}

I routed this across the VOLT registry and convened a panel of ${panel.length} specialists. In a live run each one reasons on Claude with its VOLT system prompt and I reconcile their findings into one deliverable.

| Specialist | Layer | Why they are on the panel |
|---|---|---|
${panel.map((a) => `| ${a.icon} ${a.name} | ${a.layer} | ${a.description} |`).join("\n")}
${bench}
### Skill Finder
${skills.length ? skills.map((s) => `- \`${s.skill_id}\` — ${catalog.skillById.get(s.skill_id)?.description.slice(0, 160) ?? ""}`).join("\n") : "- No strong skill matches."}

### Recommended VOLT workflows
${workflows.length ? workflows.map(({ w }) => `- **${w.icon} ${w.name}** (\`${w.id}\`): ${w.description}`).join("\n") : "- None matched this panel; ask Rudra in live mode for a tailored plan."}

> Demo mode: routing, skill matching, benchmarks and workflow sequencing above are real VOLT logic; the narrative is assembled from the registry. Set \`ANTHROPIC_API_KEY\` for live multi-agent reasoning.
`,
    emit,
    signal,
  );
}
