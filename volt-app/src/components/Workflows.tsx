import { useState } from "react";
import type { CatalogResponse, RunKind, RunRequest } from "../../shared/events";

type Workflow = CatalogResponse["workflows"][number];

interface Props {
  catalog: CatalogResponse;
  onLaunch: (req: RunRequest, title: string, kind: RunKind) => void;
  onOpenAgent: (id: string) => void;
}

export function Workflows({ catalog, onLaunch, onOpenAgent }: Props) {
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<Workflow | null>(null);
  const filtered = catalog.workflows.filter((w) => `${w.name} ${w.description} ${w.id}`.toLowerCase().includes(q.toLowerCase()));

  if (selected) return <WorkflowLauncher catalog={catalog} wf={selected} onBack={() => setSelected(null)} onLaunch={onLaunch} onOpenAgent={onOpenAgent} />;

  return (
    <div className="stack">
      <div>
        <h1 className="page-title">Workflows</h1>
        <p className="page-sub">
          VOLT's {catalog.workflows.length} multi-phase workflows. Phases run in order, agents within a phase run in parallel and build on
          earlier phases, and Rudra synthesises the final deliverable.
        </p>
      </div>
      <input className="input" placeholder="Filter workflows…" value={q} onChange={(e) => setQ(e.target.value)} />
      <div className="grid">
        {filtered.map((w) => (
          <div key={w.id} className="card interactive stack" style={{ gap: 8 }} onClick={() => setSelected(w)}>
            <div className="row" style={{ justifyContent: "space-between" }}>
              <b>
                {w.icon} {w.name}
              </b>
              <span className="micro">{w.phases.length} phases</span>
            </div>
            <div className="body" style={{ fontSize: 13 }}>
              {w.description}
            </div>
            <div className="row">
              {w.phases.map((p, i) => (
                <span key={i} className="chip">
                  {i + 1}. {p.name}
                </span>
              ))}
            </div>
            <div className="muted" style={{ fontSize: 12 }}>
              {new Set(w.phases.flatMap((p) => p.agents)).size} agents
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function WorkflowLauncher({ catalog, wf, onBack, onLaunch, onOpenAgent }: { catalog: CatalogResponse; wf: Workflow; onBack: () => void } & Omit<Props, "catalog">) {
  const questions = catalog.intake[wf.id] ?? catalog.intake["default"] ?? [];
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [prompt, setPrompt] = useState("");
  const name = (id: string) => catalog.agents.find((a) => a.id === id);
  const agentCalls = wf.phases.reduce((n, p) => n + p.agents.length, 0);

  return (
    <div className="stack" style={{ maxWidth: 900 }}>
      <button className="btn ghost sm" style={{ alignSelf: "flex-start" }} onClick={onBack}>
        ← All workflows
      </button>
      <div>
        <h1 className="page-title">
          {wf.icon} {wf.name}
        </h1>
        <p className="page-sub">{wf.description}</p>
      </div>

      <div className="card">
        <div className="micro" style={{ marginBottom: 10 }}>
          Execution plan · {agentCalls} agent runs + Rudra synthesis
        </div>
        <div className="stack" style={{ gap: 10 }}>
          {wf.phases.map((p, i) => (
            <div key={i} className="row" style={{ alignItems: "flex-start" }}>
              <span className="chip" style={{ minWidth: 150 }}>
                {i + 1}. {p.name}
              </span>
              <div className="row">
                {p.agents.map((a) => (
                  <span key={a} className="chip click" onClick={() => onOpenAgent(a)}>
                    {name(a)?.icon} {name(a)?.name ?? a}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card stack">
        <div className="micro">Engagement intake</div>
        {questions.map((q) => (
          <label key={q.key} className="stack" style={{ gap: 6 }}>
            <span className="body">{q.question}</span>
            {q.options?.length ? (
              <select className="select" value={answers[q.key] ?? ""} onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })}>
                <option value="">— choose —</option>
                {q.options.map((o) => (
                  <option key={o}>{o}</option>
                ))}
              </select>
            ) : (
              <input className="input" value={answers[q.key] ?? ""} onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })} />
            )}
          </label>
        ))}
        <label className="stack" style={{ gap: 6 }}>
          <span className="body">Client situation and request</span>
          <textarea className="textarea" rows={5} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Client, industry, scale, platforms, pain points, what the deliverable must answer…" />
        </label>
        <div className="row" style={{ justifyContent: "flex-end" }}>
          <button
            className="btn primary"
            disabled={!prompt.trim()}
            onClick={() => onLaunch({ prompt: prompt.trim(), workflowId: wf.id, intake: answers }, `${wf.icon} ${wf.name}`, "workflow")}
          >
            Launch workflow
          </button>
        </div>
      </div>
    </div>
  );
}
