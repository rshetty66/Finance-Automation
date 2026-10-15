import { useEffect, useState } from "react";
import type { CatalogResponse } from "../../shared/events";
import { runTool } from "../api";

/** Direct access to the deterministic tools the agents use for numbers. */
export function Analytics({ catalog }: { catalog: CatalogResponse }) {
  return (
    <div className="stack" style={{ maxWidth: 1000 }}>
      <div>
        <h1 className="page-title">Analytics Tools</h1>
        <p className="page-sub">
          The same deterministic tools agents call for figures (APQC benchmarks, value case, NPV/IRR), so numbers in deliverables come
          from code, not model arithmetic. Use them directly here.
        </p>
      </div>
      <BenchmarkTool catalog={catalog} />
      <ValueCaseTool />
    </div>
  );
}

function BenchmarkTool({ catalog }: { catalog: CatalogResponse }) {
  const [metric, setMetric] = useState(catalog.benchmarks[2]?.key ?? catalog.benchmarks[0].key);
  const [value, setValue] = useState("12");
  const b = catalog.benchmarks.find((x) => x.key === metric)!;
  const [result, setResult] = useState<{ quartile?: string; gapToMedian?: number; gapToTop25?: number } | null>(null);

  useEffect(() => {
    const v = Number(value);
    if (value === "" || Number.isNaN(v)) return setResult(null);
    runTool<{ quartile: string; gapToMedian: number; gapToTop25: number }>("apqc_benchmark", { metric, client_value: v }).then((r) => setResult(r.ok ? r.data! : null));
  }, [metric, value]);

  // Axis from best to worst, padded beyond the quartile points.
  const best = b.lowerIsBetter ? Math.min(b.top25, Number(value) || b.top25) : Math.max(b.top25, Number(value) || b.top25);
  const worst = b.lowerIsBetter ? Math.max(b.bottom25, Number(value) || 0) : Math.min(b.bottom25, Number(value) || b.bottom25);
  const span = Math.abs(worst - best) * 1.15 || 1;
  const start = b.lowerIsBetter ? best - span * 0.05 : best + span * 0.05;
  const pos = (v: number) => Math.min(100, Math.max(0, (Math.abs(v - start) / span) * 100));

  return (
    <div className="card stack">
      <div className="micro">APQC benchmark position</div>
      <div className="row" style={{ flexWrap: "nowrap" }}>
        <select className="select" value={metric} onChange={(e) => setMetric(e.target.value)}>
          {catalog.benchmarks.map((x) => (
            <option key={x.key} value={x.key}>
              {x.metric}
            </option>
          ))}
        </select>
        <input className="input" style={{ maxWidth: 140 }} inputMode="decimal" value={value} onChange={(e) => setValue(e.target.value)} aria-label="Client value" />
      </div>
      <div className="bench-wrap">
        {value !== "" && !Number.isNaN(Number(value)) && (
          <div className="bench-marker" style={{ left: `${pos(Number(value))}%` }}>
            client {value}
          </div>
        )}
        <div className="bench-bar">
          <div style={{ flex: `0 0 ${pos(b.top25)}%` }}>Top 25%</div>
          <div style={{ flex: `0 0 ${pos(b.median) - pos(b.top25)}%` }}>2nd</div>
          <div style={{ flex: `0 0 ${pos(b.bottom25) - pos(b.median)}%` }}>3rd</div>
          <div>Bottom</div>
        </div>
      </div>
      <div className="stats">
        <Stat label="Top quartile" value={`${b.top25} ${b.unit}`} />
        <Stat label="Median" value={`${b.median} ${b.unit}`} />
        <Stat label="Bottom quartile" value={`${b.bottom25} ${b.unit}`} />
        <Stat label="Client position" value={result?.quartile ?? "—"} />
        <Stat label="Gap to top quartile" value={result ? `${result.gapToTop25} ${b.unit}` : "—"} />
      </div>
      <div className="muted" style={{ fontSize: 12 }}>
        {b.lowerIsBetter ? "Lower is better." : "Higher is better."} Source: APQC Open Standards Benchmarking (built-in sample set).
      </div>
    </div>
  );
}

interface ValueCase {
  capacityReleasedFtes: number;
  steadyStateAnnualSaving: number;
  npv: number;
  irrPct: number | null;
  paybackYears: number | null;
  profitabilityIndex: number;
  yearly: { year: number; realisationPct: number; grossBenefit: number; runCost: number; netBenefit: number }[];
}

function ValueCaseTool() {
  const [f, setF] = useState({ finance_ftes: "140", loaded_cost_per_fte: "115000", automation_pct: "25", one_time_investment: "6000000", annual_run_cost: "450000", ramp_years: "2", horizon_years: "5", discount_rate: "0.08" });
  const [r, setR] = useState<ValueCase | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    const body = Object.fromEntries(Object.entries(f).map(([k, v]) => [k, Number(v)]));
    if (Object.values(body).some((v) => Number.isNaN(v))) return;
    runTool<ValueCase>("build_value_case", body).then((x) => {
      if (x.ok) {
        setR(x.data!);
        setErr("");
      } else setErr(x.error ?? "invalid input");
    });
  }, [f]);

  const field = (k: keyof typeof f, label: string) => (
    <label className="stack" style={{ gap: 4 }}>
      <span className="micro">{label}</span>
      <input className="input" inputMode="decimal" value={f[k]} onChange={(e) => setF({ ...f, [k]: e.target.value })} />
    </label>
  );
  const money = (n: number) => n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

  return (
    <div className="card stack">
      <div className="micro">Finance transformation value case</div>
      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(170px, 1fr))" }}>
        {field("finance_ftes", "Finance FTEs")}
        {field("loaded_cost_per_fte", "Loaded cost / FTE")}
        {field("automation_pct", "Automation %")}
        {field("one_time_investment", "One-time investment")}
        {field("annual_run_cost", "Annual run cost")}
        {field("ramp_years", "Ramp (years)")}
        {field("horizon_years", "Horizon (years)")}
        {field("discount_rate", "Discount rate")}
      </div>
      {err && <div className="body">{err}</div>}
      {r && (
        <>
          <div className="stats">
            <Stat label="Capacity released" value={`${r.capacityReleasedFtes} FTE`} />
            <Stat label="Steady-state saving" value={money(r.steadyStateAnnualSaving)} />
            <Stat label="NPV" value={money(r.npv)} />
            <Stat label="IRR" value={r.irrPct === null ? "n/a" : `${r.irrPct}%`} />
            <Stat label="Payback" value={r.paybackYears === null ? "beyond horizon" : `${r.paybackYears} yrs`} />
          </div>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Realised</th>
                  <th>Gross benefit</th>
                  <th>Run cost</th>
                  <th>Net benefit</th>
                </tr>
              </thead>
              <tbody>
                {r.yearly.map((y) => (
                  <tr key={y.year}>
                    <td>{y.year}</td>
                    <td>{y.realisationPct}%</td>
                    <td>{money(y.grossBenefit)}</td>
                    <td>{money(y.runCost)}</td>
                    <td>{money(y.netBenefit)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <span className="micro">{label}</span>
      <span className="v">{value}</span>
    </div>
  );
}
