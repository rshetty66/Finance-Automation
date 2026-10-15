import { useEffect, useMemo, useState } from "react";
import type { CatalogResponse } from "../../shared/events";
import { getJSON } from "../api";

export function Agents({ catalog, onOpen }: { catalog: CatalogResponse; onOpen: (id: string) => void }) {
  const [q, setQ] = useState("");
  const [layer, setLayer] = useState("");
  const layers = useMemo(() => [...new Set(catalog.agents.map((a) => a.layer))].sort(), [catalog]);
  const ql = q.toLowerCase();
  const agents = catalog.agents.filter(
    (a) => (!layer || a.layer === layer) && (!ql || `${a.name} ${a.id} ${a.description} ${a.keywords.join(" ")}`.toLowerCase().includes(ql)),
  );

  return (
    <div className="stack">
      <div>
        <h1 className="page-title">Agent Registry</h1>
        <p className="page-sub">
          All {catalog.agents.length} VOLT agents across {layers.length} layers. Open one to see its system prompt, skills and the workflows and
          services that use it, or chat with it directly.
        </p>
      </div>
      <div className="row" style={{ flexWrap: "nowrap" }}>
        <input className="input" placeholder="Search agents, keywords…" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="select" style={{ maxWidth: 260 }} value={layer} onChange={(e) => setLayer(e.target.value)}>
          <option value="">All layers</option>
          {layers.map((l) => (
            <option key={l}>{l}</option>
          ))}
        </select>
      </div>
      <div className="muted" style={{ fontSize: 12 }}>
        {agents.length} shown
      </div>
      <div className="grid">
        {agents.map((a) => (
          <div key={a.id} className="card interactive" onClick={() => onOpen(a.id)}>
            <div className="row" style={{ justifyContent: "space-between", flexWrap: "nowrap" }}>
              <b>
                {a.icon} {a.name}
              </b>
            </div>
            <div className="micro" style={{ margin: "4px 0 6px" }}>
              {a.layer}
            </div>
            <div className="body" style={{ fontSize: 13 }}>
              {a.description}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface AgentDetail {
  id: string;
  name: string;
  layer: string;
  icon: string;
  description: string;
  keywords: string[];
  skills: string[];
  systemPrompt: string;
  workflows: string[];
  services: string[];
}

export function AgentDrawer({ catalog, agentId, onClose, onChat }: { catalog: CatalogResponse; agentId: string; onClose: () => void; onChat: (id: string) => void }) {
  const [a, setA] = useState<AgentDetail | null>(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    setA(null);
    getJSON<AgentDetail>(`/api/agents/${encodeURIComponent(agentId)}`).then(setA, (e) => setErr(String(e)));
  }, [agentId]);
  const shipped = new Set(catalog.skills.map((s) => s.id));

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <aside className="drawer" role="dialog" aria-label="Agent details">
        {!a ? (
          <div className="empty">{err || <span className="spinner" />}</div>
        ) : (
          <div className="stack">
            <div className="drawer-head">
              <div>
                <div className="micro">{a.layer}</div>
                <h2 className="page-title">
                  {a.icon} {a.name}
                </h2>
                <div className="body">{a.description}</div>
              </div>
              <button className="btn ghost" onClick={onClose} aria-label="Close">
                ✕
              </button>
            </div>
            <div className="row">
              <button className="btn primary" onClick={() => onChat(a.id)}>
                Chat with {a.name}
              </button>
              <code className="muted">{a.id}</code>
            </div>
            {a.keywords.length > 0 && (
              <div>
                <div className="micro">Routing keywords</div>
                <div className="row" style={{ marginTop: 6 }}>
                  {a.keywords.map((k) => (
                    <span key={k} className="chip">
                      {k}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {a.skills.length > 0 && (
              <div>
                <div className="micro">Registered skills</div>
                <div className="row" style={{ marginTop: 6 }}>
                  {a.skills.map((s) => (
                    <span key={s} className="chip" title={shipped.has(s) ? "shipped" : "not shipped in this package"} style={shipped.has(s) ? {} : { opacity: 0.5, textDecoration: "line-through" }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {(a.workflows.length > 0 || a.services.length > 0) && (
              <div>
                <div className="micro">Used by</div>
                <div className="row" style={{ marginTop: 6 }}>
                  {a.workflows.map((w) => (
                    <span key={w} className="chip">
                      ⚙ {catalog.workflows.find((x) => x.id === w)?.name ?? w}
                    </span>
                  ))}
                  {a.services.map((s) => (
                    <span key={s} className="chip">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <div>
              <div className="micro">VOLT system prompt</div>
              <pre className="card" style={{ whiteSpace: "pre-wrap", marginTop: 6, color: "var(--heading)" }}>
                {a.systemPrompt}
              </pre>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}
