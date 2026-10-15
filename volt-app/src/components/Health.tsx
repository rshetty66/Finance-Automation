import type { CatalogResponse } from "../../shared/events";

/** Integrity checks run on the VOLT package at load time. */
export function Health({ catalog, onOpenAgent }: { catalog: CatalogResponse; onOpenAgent: (id: string) => void }) {
  const h = catalog.health;
  const orphanIntake = Object.keys(catalog.intake).filter((k) => k !== "default" && !catalog.workflows.some((w) => w.id === k));
  const agentsInWorkflows = new Set(catalog.workflows.flatMap((w) => w.agents));
  const unusedAgents = catalog.agents.filter((a) => !agentsInWorkflows.has(a.id) && !catalog.services.some((s) => s.agents.includes(a.id)));

  return (
    <div className="stack" style={{ maxWidth: 1000 }}>
      <div>
        <h1 className="page-title">Capability Health</h1>
        <p className="page-sub">
          Integrity checks run on the VOLT package ({catalog.source.name}@{catalog.source.commit?.slice(0, 7)}, built {catalog.source.built_utc})
          when the console loads it: what the registry promises against what the package ships.
        </p>
      </div>
      <div className="stats">
        <Stat label="Agents" value={catalog.agents.length} />
        <Stat label="Workflows" value={catalog.workflows.length} />
        <Stat label="Skills shipped" value={catalog.skills.length} />
        <Stat label="Skill refs not shipped" value={h.missingSkills.length} />
        <Stat label="Broken agent refs" value={h.missingAgents.length} />
        <Stat label="Services fully covered" value={`${h.servicesByCoverage.full ?? 0}/${catalog.services.length}`} />
      </div>

      <Section title={`Skills referenced but not shipped (${h.missingSkills.length})`} note="Agents fall back to their system prompt for these; load_skill returns the closest shipped skills instead.">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Referenced by</th>
              </tr>
            </thead>
            <tbody>
              {h.missingSkills.map((m) => (
                <tr key={m.skill}>
                  <td>
                    <code>{m.skill}</code>
                  </td>
                  <td>
                    <div className="row">
                      {m.referencedBy.map((r) => {
                        const [kind, id] = r.split(":");
                        return (
                          <span key={r} className={`chip ${kind === "agent" ? "click" : ""}`} onClick={() => kind === "agent" && onOpenAgent(id)}>
                            {kind === "agent" ? catalog.agents.find((a) => a.id === id)?.name ?? id : id}
                          </span>
                        );
                      })}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section title={`Services with partial or no coverage (${catalog.services.filter((s) => s.coverage !== "full").length})`}>
        <div className="row">
          {catalog.services
            .filter((s) => s.coverage !== "full")
            .map((s) => (
              <span key={s.code} className="chip" title={s.description}>
                <span className={`badge ${s.coverage}`}>{s.coverage}</span> {s.name}
              </span>
            ))}
        </div>
      </Section>

      {orphanIntake.length > 0 && (
        <Section title="Intake question sets with no matching workflow" note="Defined in WORKFLOW_INTAKE but never shown, because no workflow has this id.">
          <div className="row">
            {orphanIntake.map((k) => (
              <code key={k} className="chip">
                {k}
              </code>
            ))}
          </div>
        </Section>
      )}

      <Section title={`Agents not used by any workflow or service (${unusedAgents.length})`} note="Reachable through Rudra orchestration and direct chat only.">
        <div className="row">
          {unusedAgents.map((a) => (
            <span key={a.id} className="chip click" onClick={() => onOpenAgent(a.id)}>
              {a.icon} {a.name}
            </span>
          ))}
        </div>
      </Section>
    </div>
  );
}

function Section({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return (
    <div className="card stack" style={{ gap: 8 }}>
      <b>{title}</b>
      {note && <div className="muted" style={{ fontSize: 12 }}>{note}</div>}
      {children}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card stat">
      <span className="micro">{label}</span>
      <span className="v">{value}</span>
    </div>
  );
}
