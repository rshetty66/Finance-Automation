import { useMemo, useState } from "react";
import type { CatalogResponse, RunKind, RunRequest } from "../../shared/events";

interface Props {
  catalog: CatalogResponse;
  onOpenAgent: (id: string) => void;
  onLaunch: (req: RunRequest, title: string, kind: RunKind) => void;
}

/** VOLT consulting services catalogue: practice → sub-practice → service, with agent/workflow coverage. */
export function Services({ catalog, onOpenAgent, onLaunch }: Props) {
  const [practice, setPractice] = useState("");
  const practices = useMemo(() => [...new Set(catalog.services.map((s) => s.practice))], [catalog]);
  const services = catalog.services.filter((s) => !practice || s.practice === practice);
  const bySub = new Map<string, typeof services>();
  for (const s of services) bySub.set(`${s.practice} › ${s.subPractice}`, [...(bySub.get(`${s.practice} › ${s.subPractice}`) ?? []), s]);
  const agentName = (id: string) => catalog.agents.find((a) => a.id === id)?.name ?? id;
  const wf = (id: string) => catalog.workflows.find((w) => w.id === id);

  return (
    <div className="stack">
      <div>
        <h1 className="page-title">Consulting Services</h1>
        <p className="page-sub">
          The {catalog.services.length} services in VOLT's catalogue, each mapped to the agents, workflows and skills that deliver it.
          Coverage: {Object.entries(catalog.health.servicesByCoverage).map(([k, v]) => `${v} ${k}`).join(" · ")}.
        </p>
      </div>
      <div className="row">
        <span className={`chip click`} style={!practice ? { borderColor: "var(--accent)" } : {}} onClick={() => setPractice("")}>
          All
        </span>
        {practices.map((p) => (
          <span key={p} className="chip click" style={practice === p ? { borderColor: "var(--accent)" } : {}} onClick={() => setPractice(p)}>
            {p}
          </span>
        ))}
      </div>
      {[...bySub.entries()].map(([group, list]) => (
        <div key={group} className="stack" style={{ gap: 8 }}>
          <div className="micro">{group}</div>
          <div className="card table-wrap" style={{ padding: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Coverage</th>
                  <th>Agents</th>
                  <th>Run</th>
                </tr>
              </thead>
              <tbody>
                {list.map((s) => (
                  <tr key={s.code}>
                    <td style={{ minWidth: 240 }}>
                      <b>{s.name}</b> <span className="muted">{s.code}</span>
                      <div className="body" style={{ fontSize: 12 }}>
                        {s.description}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${s.coverage}`}>{s.coverage}</span>
                    </td>
                    <td>
                      <div className="row">
                        {s.agents.map((a) => (
                          <span key={a} className="chip click" onClick={() => onOpenAgent(a)}>
                            {agentName(a)}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div className="stack" style={{ gap: 4 }}>
                        {s.workflows.filter(wf).map((w) => (
                          <button
                            key={w}
                            className="btn sm"
                            onClick={() => {
                              const prompt = window.prompt(`Describe the client situation for "${s.name}" (${wf(w)!.name})`);
                              if (prompt?.trim()) onLaunch({ prompt: `${s.name}: ${prompt.trim()}`, workflowId: w }, `${wf(w)!.icon} ${wf(w)!.name}`, "workflow");
                            }}
                          >
                            ▸ {wf(w)!.name}
                          </button>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
