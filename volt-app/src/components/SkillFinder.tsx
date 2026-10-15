import { useEffect, useState } from "react";
import type { CatalogResponse } from "../../shared/events";
import { getJSON } from "../api";
import { Markdown } from "./Markdown";

interface Match {
  id: string;
  name: string;
  description: string;
  category: string;
  resources: string[];
  score: number;
  usedBy: string[];
}

const SUGGESTIONS = ["nostro reconciliation", "IFRS 17 CSM", "month-end close acceleration", "OSFI capital", "lease accounting", "Workday financials", "value creation plan", "chart of accounts design"];

/** Skill Finder: rank VOLT's skill packs against a task, then read the one you need. */
export function SkillFinder({ catalog, onOpenAgent }: { catalog: CatalogResponse; onOpenAgent: (id: string) => void }) {
  const [q, setQ] = useState("");
  const [matches, setMatches] = useState<Match[] | null>(null);
  const [open, setOpen] = useState<{ id: string; body: string; truncated: boolean } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!q.trim()) return setMatches(null);
    const t = setTimeout(() => {
      getJSON<Match[]>(`/api/skills?q=${encodeURIComponent(q)}`).then(setMatches);
    }, 200);
    return () => clearTimeout(t);
  }, [q]);

  const openSkill = async (id: string) => {
    setLoading(true);
    try {
      setOpen(await getJSON(`/api/skills/${encodeURIComponent(id)}`));
    } finally {
      setLoading(false);
    }
  };

  if (open) {
    return (
      <div className="stack" style={{ maxWidth: 900 }}>
        <button className="btn ghost sm" style={{ alignSelf: "flex-start" }} onClick={() => setOpen(null)}>
          ← Back to results
        </button>
        <div className="micro">skill · {open.id}</div>
        {open.truncated && <div className="muted">Long skill: showing the first 120K characters.</div>}
        <div className="card">
          <Markdown text={open.body.replace(/^---[\s\S]*?---\s*/, "")} />
        </div>
      </div>
    );
  }

  const list: Match[] = matches ?? [];
  return (
    <div className="stack">
      <div>
        <h1 className="page-title">Skill Finder</h1>
        <p className="page-sub">
          Describe a task and the Skill Finder ranks VOLT's {catalog.skills.length} skill packs against it, the same ranking agents use
          through the <code>find_skills</code> tool before they load a method pack.
        </p>
      </div>
      <input className="input" autoFocus placeholder="What are you trying to do? e.g. reconcile nostro accounts" value={q} onChange={(e) => setQ(e.target.value)} />
      {!q && (
        <div className="row">
          {SUGGESTIONS.map((s) => (
            <span key={s} className="chip click" onClick={() => setQ(s)}>
              {s}
            </span>
          ))}
        </div>
      )}
      {loading && <span className="spinner" />}
      {matches && list.length === 0 && <div className="empty">No skill matches. Try different words.</div>}
      <div className="stack">
        {list.map((m) => (
          <div key={m.id} className="card interactive" onClick={() => openSkill(m.id)}>
            <div className="row" style={{ justifyContent: "space-between" }}>
              <b>{m.id}</b>
              <span className="row">
                <span className="chip">{m.category}</span>
                <span className="usage">score {m.score}</span>
              </span>
            </div>
            <div className="body" style={{ fontSize: 13, margin: "6px 0" }}>
              {m.description}
            </div>
            <div className="row">
              {m.resources.length > 0 && <span className="muted" style={{ fontSize: 12 }}>{m.resources.length} reference files</span>}
              {m.usedBy.slice(0, 6).map((a) => (
                <span
                  key={a}
                  className="chip click"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenAgent(a);
                  }}
                >
                  {catalog.agents.find((x) => x.id === a)?.name ?? a}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
