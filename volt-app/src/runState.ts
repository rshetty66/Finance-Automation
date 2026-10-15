import { ORCHESTRATOR_LANE, type RunKind, type RunMode, type VoltEvent } from "../shared/events";

export interface ActivityItem {
  id: string;
  kind: "status" | "tool" | "error" | "fallback" | "phase";
  text: string;
  detail?: string;
  data?: unknown;
  pending?: boolean;
  isError?: boolean;
}

export interface Lane {
  id: string;
  agentId: string;
  name: string;
  layer: string;
  icon: string;
  brief: string;
  parentLane: string;
  text: string;
  activity: ActivityItem[];
  state: "running" | "done" | "failed";
  phase?: number;
}

export interface Run {
  id: string;
  prompt: string;
  title: string;
  kind: RunKind;
  mode?: RunMode;
  model?: string;
  sessionId?: string;
  text: string;
  activity: ActivityItem[];
  lanes: Record<string, Lane>;
  laneOrder: string[];
  phases: { name: string; agents: string[]; state: "running" | "done" }[];
  usage: { input: number; output: number; cacheRead: number };
  state: "running" | "done" | "stopped";
  startedAt: number;
  finishedAt?: number;
}

export function newRun(prompt: string, title: string, kind: RunKind): Run {
  return {
    id: crypto.randomUUID(),
    prompt,
    title,
    kind,
    text: "",
    activity: [],
    lanes: {},
    laneOrder: [],
    phases: [],
    usage: { input: 0, output: 0, cacheRead: 0 },
    state: "running",
    startedAt: Date.now(),
  };
}

/** Pure reducer: folds one orchestrator event into the run's view model. */
export function applyEvent(run: Run, e: VoltEvent): Run {
  const r: Run = { ...run, lanes: { ...run.lanes } };
  const lane = (id: string) => (id === ORCHESTRATOR_LANE ? null : r.lanes[id]);
  const pushActivity = (laneId: string, item: ActivityItem) => {
    const l = lane(laneId);
    if (l) r.lanes[laneId] = { ...l, activity: [...l.activity, item] };
    else r.activity = [...r.activity, item];
  };
  const updateActivity = (laneId: string, id: string, patch: Partial<ActivityItem>) => {
    const map = (xs: ActivityItem[]) => xs.map((x) => (x.id === id ? { ...x, ...patch } : x));
    const l = lane(laneId);
    if (l) r.lanes[laneId] = { ...l, activity: map(l.activity) };
    else r.activity = map(r.activity);
  };

  switch (e.type) {
    case "run_start":
      return { ...r, mode: e.mode, model: e.model, sessionId: e.sessionId, title: e.title, kind: e.kind };
    case "phase_start":
      r.phases = [...r.phases];
      r.phases[e.index] = { name: e.name, agents: e.agents, state: "running" };
      return r;
    case "phase_end":
      r.phases = r.phases.map((p, i) => (i === e.index ? { ...p, state: "done" } : p));
      return r;
    case "agent_start": {
      if (e.lane === ORCHESTRATOR_LANE) return r; // direct-agent runs render in the main lane
      const phase = e.lane.split(":").length === 3 ? Number(e.lane.split(":")[1]) : undefined;
      r.lanes[e.lane] = { id: e.lane, agentId: e.agentId, name: e.name, layer: e.layer, icon: e.icon, brief: e.brief, parentLane: e.parentLane, text: "", activity: [], state: "running", phase };
      r.laneOrder = [...r.laneOrder, e.lane];
      return r;
    }
    case "agent_end": {
      const l = lane(e.lane);
      if (l) r.lanes[e.lane] = { ...l, state: e.ok ? "done" : "failed" };
      return r;
    }
    case "text_delta": {
      const l = lane(e.lane);
      if (l) r.lanes[e.lane] = { ...l, text: l.text + e.text };
      else r.text += e.text;
      return r;
    }
    case "status":
      pushActivity(e.lane, { id: crypto.randomUUID(), kind: "status", text: e.text });
      return r;
    case "tool_call":
      pushActivity(e.lane, { id: e.callId, kind: "tool", text: e.name, detail: summariseInput(e.input), pending: true });
      return r;
    case "tool_result":
      updateActivity(e.lane, e.callId, { pending: false, detail: e.summary, data: e.data, isError: e.isError });
      return r;
    case "fallback":
      pushActivity(e.lane, { id: crypto.randomUUID(), kind: "fallback", text: `Fallback ${e.from} → ${e.to}` });
      return r;
    case "usage":
      r.usage = { input: r.usage.input + e.inputTokens, output: r.usage.output + e.outputTokens, cacheRead: r.usage.cacheRead + e.cacheReadTokens };
      return r;
    case "error":
      pushActivity(e.lane, { id: crypto.randomUUID(), kind: "error", text: e.message, isError: true });
      return r;
    case "done":
      return { ...r, sessionId: e.sessionId, state: r.state === "stopped" ? "stopped" : "done", finishedAt: Date.now() };
  }
}

function summariseInput(input: unknown): string {
  if (!input || typeof input !== "object") return "";
  const o = input as Record<string, unknown>;
  const v = o.query ?? o.agent_id ?? o.skill_id ?? o.metric ?? "";
  return String(v).slice(0, 120);
}
