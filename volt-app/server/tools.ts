/**
 * Tool surface exposed to the VOLT agents.
 *
 * Each tool has a Zod schema (used to validate model-supplied input before it
 * runs) and a JSON schema derived from it for the API. Execution of
 * `consult_agent` lives in the orchestrator because it re-enters the
 * agent loop; everything else is pure and runs here.
 */
import { z } from "zod";
import type Anthropic from "@anthropic-ai/sdk";
import { type Catalog, loadSkillBody, rankAgents, rankSkills } from "./catalog.js";
import { BENCHMARKS, appraiseInvestment, buildValueCase, compareToBenchmark, MATURITY_DIMENSIONS, scoreMaturity } from "./analytics.js";

export const schemas = {
  find_agents: z.object({
    query: z.string().describe("What the engagement needs, in plain language (e.g. 'Oracle FCCS intercompany eliminations')."),
    limit: z.number().int().min(1).max(10).optional().describe("Max agents to return (default 5)."),
  }),
  find_skills: z.object({
    query: z.string().describe("The task or topic to find skill packs for (e.g. 'nostro reconciliation', 'IFRS 17 CSM')."),
    limit: z.number().int().min(1).max(10).optional().describe("Max skills to return (default 5)."),
  }),
  consult_agent: z.object({
    agent_id: z.string().describe("Exact VOLT agent id from the roster, e.g. 'oracle-gl-specialist'."),
    brief: z.string().describe("Self-contained brief: client context, the specific question, constraints, and the deliverable expected back."),
  }),
  load_skill: z.object({
    skill_id: z.string().describe("Skill id from find_skills or the agent's skill list, e.g. 'apqc-benchmarks'."),
    resource: z.string().optional().describe("Optional reference file inside the skill (e.g. 'references/erm-framework.md')."),
  }),
  apqc_benchmark: z.object({
    metric: z.string().describe(`Metric key or name. Keys: ${BENCHMARKS.map((b) => b.key).join(", ")}`),
    client_value: z.number().optional().describe("Client's current value in the metric's unit, to place them in a quartile."),
  }),
  score_maturity: z.object({
    scores: z
      .array(
        z.object({
          dimension: z.string().describe(`One of: ${MATURITY_DIMENSIONS.join("; ")}`),
          current: z.number().min(1).max(5),
          target: z.number().min(1).max(5).optional(),
          evidence: z.string().optional(),
        }),
      )
      .min(1),
  }),
  appraise_investment: z.object({
    initial_investment: z.number().describe("Up-front investment (positive number)."),
    cash_flows: z.array(z.number()).min(1).describe("Net cash flow per year after the investment, year 1 first."),
    discount_rate: z.number().describe("Hurdle rate as a decimal, e.g. 0.08."),
  }),
  build_value_case: z.object({
    finance_ftes: z.number(),
    loaded_cost_per_fte: z.number(),
    automation_pct: z.number().min(0).max(100).describe("Share of finance effort automated/released at steady state, 0-100."),
    one_time_investment: z.number(),
    annual_run_cost: z.number().optional(),
    ramp_years: z.number().optional(),
    horizon_years: z.number().int().min(1).max(10).optional(),
    discount_rate: z.number().optional(),
    close_days_current: z.number().optional(),
    close_days_target: z.number().optional(),
  }),
} as const;

export type ToolName = keyof typeof schemas;

const descriptions: Record<ToolName, string> = {
  find_agents:
    "Search the VOLT registry of 236 agents and return the best matches with layer and remit. Use when unsure which specialist owns a question.",
  find_skills:
    "Skill Finder: rank VOLT's ~390 skill packs (frameworks, methods, reference material) against a task and return the best matches. Use before load_skill when you do not already know the skill id.",
  consult_agent:
    "Delegate a focused workstream question to one VOLT specialist agent. The specialist works independently with its own methodology and returns a written deliverable. Call several in the same turn to run them in parallel when the request spans workstreams.",
  load_skill: "Load a VOLT skill pack (or one of its reference files) into context.",
  apqc_benchmark:
    "Look up an APQC finance benchmark (top quartile / median / bottom quartile) and optionally place a client value in its quartile with gap-to-median and gap-to-top-quartile.",
  score_maturity:
    "Score the 7-dimension finance maturity model (1 Ad Hoc to 5 Leading): returns overall level, per-dimension gaps, top priority gaps and unassessed dimensions.",
  appraise_investment: "Compute NPV, IRR, payback and profitability index for an investment and its yearly cash flows.",
  build_value_case:
    "Build a finance transformation value case from FTEs, loaded cost, automation %, investment and run cost: yearly benefit ramp plus NPV/IRR/payback.",
};

function jsonSchema(schema: z.ZodType): Anthropic.Tool.InputSchema {
  const { $schema: _ignored, ...rest } = z.toJSONSchema(schema) as Record<string, unknown>;
  return rest as Anthropic.Tool.InputSchema;
}

export function toolDefs(names: ToolName[]): Anthropic.Beta.BetaTool[] {
  return names.map((name) => ({
    name,
    description: descriptions[name],
    input_schema: jsonSchema(schemas[name]) as Anthropic.Beta.BetaTool.InputSchema,
    eager_input_streaming: true,
  }));
}

export const ORCHESTRATOR_TOOLS: ToolName[] = [
  "find_agents",
  "find_skills",
  "consult_agent",
  "load_skill",
  "apqc_benchmark",
  "score_maturity",
  "appraise_investment",
  "build_value_case",
];

export const SPECIALIST_TOOLS: ToolName[] = ["find_skills", "load_skill", "apqc_benchmark", "score_maturity", "appraise_investment", "build_value_case"];

export type LocalResult = { ok: true; data: unknown; summary: string } | { ok: false; error: string };

/** Runs every tool except consult_agent. Input must already be validated. */
export function runLocalTool(catalog: Catalog, name: Exclude<ToolName, "consult_agent">, input: unknown): LocalResult {
  switch (name) {
    case "find_agents": {
      const { query, limit } = input as z.infer<typeof schemas.find_agents>;
      const ranked = rankAgents(catalog, query, limit ?? 5).map(({ agent, score }) => ({
        agent_id: agent.id,
        name: agent.name,
        layer: agent.layer,
        remit: agent.description,
        relevance: Math.round(score * 10) / 10,
      }));
      return { ok: true, data: ranked, summary: ranked.map((r) => r.name).join(", ") || "no matches" };
    }
    case "find_skills": {
      const { query, limit } = input as z.infer<typeof schemas.find_skills>;
      const ranked = rankSkills(catalog, query, limit ?? 5).map(({ skill, score }) => ({
        skill_id: skill.id,
        category: skill.category,
        description: skill.description.slice(0, 300),
        resources: skill.resources.slice(0, 8),
        relevance: score,
      }));
      return { ok: true, data: ranked, summary: ranked.map((r) => r.skill_id).join(", ") || "no matches" };
    }
    case "load_skill": {
      const { skill_id, resource } = input as z.infer<typeof schemas.load_skill>;
      const skill = loadSkillBody(skill_id);
      if (!skill) {
        const near = rankSkills(catalog, skill_id.replace(/-/g, " "), 5).map((r) => r.skill.id);
        return { ok: false, error: `Skill '${skill_id}' is not shipped in this VOLT package. Closest: ${near.join(", ") || "none"}` };
      }
      if (resource) {
        const text = skill.resources[resource];
        if (!text) return { ok: false, error: `No resource '${resource}' in ${skill_id}. Available: ${Object.keys(skill.resources).join(", ") || "none"}` };
        return { ok: true, data: text, summary: `${skill_id}/${resource}` };
      }
      const refs = Object.keys(skill.resources);
      const data = skill.body + (refs.length ? `\n\n---\nReference files (load with resource=...): ${refs.join(", ")}` : "");
      return { ok: true, data, summary: `${skill_id} (${Math.round(skill.body.length / 1000)}k chars${skill.truncated ? ", truncated" : ""})` };
    }
    case "apqc_benchmark": {
      const { metric, client_value } = input as z.infer<typeof schemas.apqc_benchmark>;
      const r = compareToBenchmark(metric, client_value);
      if ("error" in r) return { ok: false, error: `${r.error}. Available: ${r.available.join(", ")}` };
      return {
        ok: true,
        data: r,
        summary: `${r.benchmark.metric}: top25 ${r.benchmark.top25} / median ${r.benchmark.median}${r.quartile ? ` → client ${r.clientValue} (${r.quartile})` : ""}`,
      };
    }
    case "score_maturity": {
      const { scores } = input as z.infer<typeof schemas.score_maturity>;
      const r = scoreMaturity(scores);
      return { ok: true, data: r, summary: `Overall ${r.overall} (${r.overallLevel}); priority gaps: ${r.priorityGaps.join(", ")}` };
    }
    case "appraise_investment": {
      const i = input as z.infer<typeof schemas.appraise_investment>;
      const r = appraiseInvestment({ initialInvestment: i.initial_investment, cashFlows: i.cash_flows, discountRate: i.discount_rate });
      return { ok: true, data: r, summary: `NPV ${fmt(r.npv)}, IRR ${r.irrPct ?? "n/a"}%, payback ${r.paybackYears ?? "n/a"} yrs` };
    }
    case "build_value_case": {
      const v = input as z.infer<typeof schemas.build_value_case>;
      const r = buildValueCase({
        financeFtes: v.finance_ftes,
        loadedCostPerFte: v.loaded_cost_per_fte,
        automationPct: v.automation_pct,
        oneTimeInvestment: v.one_time_investment,
        annualRunCost: v.annual_run_cost,
        rampYears: v.ramp_years,
        horizonYears: v.horizon_years,
        discountRate: v.discount_rate,
        closeDaysCurrent: v.close_days_current,
        closeDaysTarget: v.close_days_target,
      });
      return { ok: true, data: r, summary: `Saving ${fmt(r.steadyStateAnnualSaving)}/yr, NPV ${fmt(r.npv)}, payback ${r.paybackYears ?? "n/a"} yrs` };
    }
  }
}

export function fmt(n: number): string {
  const abs = Math.abs(n);
  const s = abs >= 1e9 ? `${(abs / 1e9).toFixed(2)}B` : abs >= 1e6 ? `${(abs / 1e6).toFixed(2)}M` : abs >= 1e3 ? `${(abs / 1e3).toFixed(1)}K` : abs.toFixed(0);
  return `${n < 0 ? "-" : ""}$${s}`;
}
