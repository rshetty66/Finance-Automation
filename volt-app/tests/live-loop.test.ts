import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { startMockAnthropic } from "./mockAnthropic";
import type { VoltEvent } from "../shared/events";

let mock: Awaited<ReturnType<typeof startMockAnthropic>>;
let orchestrator: typeof import("../server/orchestrator");
let catalog: ReturnType<typeof import("../server/catalog").loadCatalog>;

beforeAll(async () => {
  mock = await startMockAnthropic();
  process.env.ANTHROPIC_API_KEY = "test-key";
  process.env.ANTHROPIC_BASE_URL = mock.url;
  orchestrator = await import("../server/orchestrator");
  catalog = (await import("../server/catalog")).loadCatalog();
});
afterAll(() => mock.close());

async function run(req: Parameters<typeof orchestrator.runLive>[1]) {
  const events: VoltEvent[] = [];
  await orchestrator.runLive(catalog, req, orchestrator.getSession(), (e) => events.push(e), new AbortController().signal);
  return events;
}

describe("live agent loop (mocked Messages API)", () => {
  it("orchestrates parallel specialist consults and synthesises", async () => {
    const events = await run({ prompt: "12 day close on SAP" });
    const started = events.filter((e) => e.type === "agent_start").map((e) => (e as { agentId: string }).agentId);
    expect(started).toEqual(["sap-fico-specialist", "oracle-arcs-lead"]);
    expect(events.some((e) => e.type === "status" && e.text.includes("parallel"))).toBe(true);
    const bench = events.find((e) => e.type === "tool_result" && e.name === "apqc_benchmark");
    expect(bench && "summary" in bench && bench.summary).toContain("Bottom quartile");
    const rudraText = events.filter((e) => e.type === "text_delta" && e.lane === "rudra").map((e) => (e as { text: string }).text).join("");
    expect(rudraText).toContain("Final answer from Rudra");
  });

  it("sends the expected request shape", () => {
    const first = mock.requests[0];
    expect(first.headers["anthropic-beta"]).toContain("server-side-fallback-2026-07-01");
    expect(first.body.model).toBe("claude-opus-5-5");
    expect(first.body.thinking).toEqual({ type: "adaptive", display: "updates" });
    expect(first.body.fallbacks).toBe("default");
    expect(first.body.system[0].cache_control).toEqual({ type: "ephemeral" });
    // All tool results of one turn come back in a single user message.
    const synth = mock.requests.find((r) => r.body.tools.some((t: { name: string }) => t.name === "consult_agent") && Array.isArray(r.body.messages.at(-1).content));
    expect(synth?.body.messages.at(-1).content.map((c: { tool_use_id: string }) => c.tool_use_id)).toEqual(["tu_a", "tu_b", "tu_c"]);
  });

  it("runs a workflow phase by phase", async () => {
    const events = await run({ prompt: "Insurer close", workflowId: "close-optimization" });
    const phases = events.filter((e) => e.type === "phase_start");
    expect(phases.length).toBe(catalog.workflowById.get("close-optimization")!.phases.length);
    expect(events.filter((e) => e.type === "agent_end").every((e) => (e as { ok: boolean }).ok)).toBe(true);
  });
});
