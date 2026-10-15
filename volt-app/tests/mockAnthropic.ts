/**
 * Minimal streaming mock of POST /v1/messages, used to exercise the live agent
 * loop (tool execution, parallel consults, request shape) without an API key.
 * Rudra consults two specialists and benchmarks in one turn; specialists call
 * find_skills once, then answer.
 */
import http from "node:http";
import type { AddressInfo } from "node:net";

export interface Captured { headers: http.IncomingHttpHeaders; body: any }

let n = 0;
const sse = (res: http.ServerResponse, events: any[]) => {
  res.writeHead(200, { "content-type": "text/event-stream" });
  for (const e of events) res.write(`event: ${e.type}\ndata: ${JSON.stringify(e)}\n\n`);
  res.end();
};
const msg = (id: string, blocks: any[], stop: string) => {
  const ev: any[] = [{ type: "message_start", message: { id, type: "message", role: "assistant", model: "claude-opus-5-5", content: [], stop_reason: null, usage: { input_tokens: 100, output_tokens: 0, cache_read_input_tokens: 50 } } }];
  blocks.forEach((b: any, i: number) => {
    if (b.type === "text") {
      ev.push({ type: "content_block_start", index: i, content_block: { type: "text", text: "" } });
      ev.push({ type: "content_block_delta", index: i, delta: { type: "text_delta", text: b.text } });
    } else if (b.type === "thinking") {
      ev.push({ type: "content_block_start", index: i, content_block: { type: "thinking", thinking: "", signature: "" } });
      ev.push({ type: "content_block_delta", index: i, delta: { type: "thinking_delta", thinking: b.thinking } });
      ev.push({ type: "content_block_delta", index: i, delta: { type: "signature_delta", signature: "sig" } });
    } else {
      ev.push({ type: "content_block_start", index: i, content_block: { type: "tool_use", id: b.id, name: b.name, input: {} } });
      ev.push({ type: "content_block_delta", index: i, delta: { type: "input_json_delta", partial_json: JSON.stringify(b.input) } });
    }
    ev.push({ type: "content_block_stop", index: i });
  });
  ev.push({ type: "message_delta", delta: { stop_reason: stop, stop_sequence: null }, usage: { output_tokens: 42 } });
  ev.push({ type: "message_stop" });
  return ev;
};

export async function startMockAnthropic(): Promise<{ url: string; requests: Captured[]; close: () => void }> {
  const requests: Captured[] = [];
  const server = http.createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    const b = JSON.parse(body);
    requests.push({ headers: req.headers, body: b });
    const isRudra = b.tools.some((t: any) => t.name === "consult_agent");
    const last = b.messages.at(-1);
    const hasResults = Array.isArray(last.content) && last.content.some((c: any) => c.type === "tool_result");
    n++;
    if (isRudra && !hasResults)
      return sse(res, msg(`m${n}`, [
        { type: "thinking", thinking: "Routing to FI/CO and ARCS leads in parallel" },
        { type: "tool_use", id: "tu_a", name: "consult_agent", input: { agent_id: "sap-fico-specialist", brief: "Close acceleration on S/4" } },
        { type: "tool_use", id: "tu_b", name: "consult_agent", input: { agent_id: "oracle-arcs-lead", brief: "Recon automation" } },
        { type: "tool_use", id: "tu_c", name: "apqc_benchmark", input: { metric: "days_to_close", client_value: 12 } },
      ], "tool_use"));
    if (isRudra) return sse(res, msg(`m${n}`, [{ type: "text", text: "## Synthesis\nFinal answer from Rudra." }], "end_turn"));
    if (!hasResults) return sse(res, msg(`m${n}`, [{ type: "tool_use", id: `tu_s${n}`, name: "find_skills", input: { query: "close management" } }], "tool_use"));
    return sse(res, msg(`m${n}`, [{ type: "text", text: "Specialist deliverable." }], "end_turn"));
  });
});
  await new Promise<void>((r) => server.listen(0, r));
  const { port } = server.address() as AddressInfo;
  return { url: `http://127.0.0.1:${port}`, requests, close: () => server.close() };
}
