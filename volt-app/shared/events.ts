/** Event protocol streamed from the orchestrator to the UI (Server-Sent Events). */

export type RunMode = "live" | "demo";

export type VoltEvent =
  | { type: "run_start"; runId: string; sessionId: string; mode: RunMode; model: string; kind: RunKind; title: string }
  | { type: "phase_start"; index: number; name: string; agents: string[] }
  | { type: "phase_end"; index: number; name: string }
  | { type: "status"; lane: string; text: string }
  | { type: "text_delta"; lane: string; text: string }
  | { type: "tool_call"; lane: string; callId: string; name: string; input: unknown }
  | { type: "tool_result"; lane: string; callId: string; name: string; summary: string; data?: unknown; isError?: boolean }
  | { type: "agent_start"; lane: string; parentLane: string; agentId: string; name: string; layer: string; icon: string; brief: string }
  | { type: "agent_end"; lane: string; agentId: string; ok: boolean }
  | { type: "fallback"; lane: string; from: string; to: string }
  | { type: "usage"; lane: string; inputTokens: number; outputTokens: number; cacheReadTokens: number }
  | { type: "error"; lane: string; message: string }
  | { type: "done"; sessionId: string };

export type RunKind = "orchestrate" | "agent" | "workflow";

/** The orchestrator's own lane id; specialist lanes use the consult tool_use id (or phase/agent ids in workflows). */
export const ORCHESTRATOR_LANE = "rudra";

export interface RunRequest {
  sessionId?: string;
  prompt: string;
  /** Run a VOLT multi-phase workflow (e.g. "finance-assessment") on `prompt`. */
  workflowId?: string;
  /** Answers to the workflow intake questions, keyed by question key. */
  intake?: Record<string, string>;
  /** Talk to one VOLT agent directly instead of the Rudra orchestrator. */
  agentId?: string;
  /** Force the offline simulator even when credentials exist. */
  demo?: boolean;
}

export interface CatalogAgent {
  id: string;
  name: string;
  layer: string;
  icon: string;
  color: string;
  description: string;
  keywords: string[];
  skills: string[];
}

export interface CatalogResponse {
  source: { name: string; commit?: string; ref?: string; built_utc?: string };
  mode: RunMode;
  model: string;
  agents: CatalogAgent[];
  workflows: { id: string; name: string; icon: string; description: string; agents: string[]; phases: { name: string; agents: string[] }[] }[];
  services: { code: string; name: string; practice: string; subPractice: string; description: string; agents: string[]; workflows: string[]; skills: string[]; coverage: string }[];
  intake: Record<string, { key: string; question: string; options?: string[] }[]>;
  layerColors: Record<string, string>;
  skills: { id: string; name: string; description: string; category: string; resources: string[] }[];
  health: {
    missingSkills: { skill: string; referencedBy: string[] }[];
    missingAgents: { agent: string; referencedBy: string[] }[];
    servicesByCoverage: Record<string, number>;
  };
  benchmarks: { key: string; metric: string; unit: string; top25: number; median: number; bottom25: number; lowerIsBetter: boolean }[];
}
