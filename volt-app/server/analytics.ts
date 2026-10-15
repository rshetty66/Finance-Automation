/**
 * Deterministic finance analytics the agents call as tools, so numbers in
 * deliverables come from code rather than from the model's arithmetic.
 *
 * Benchmark values are ported from rudra/tools/benchmarks.py (APQC Open
 * Standards Benchmarking, built-in sample set).
 */

export interface Benchmark {
  key: string;
  metric: string;
  pcf: string;
  top25: number;
  median: number;
  bottom25: number;
  unit: string;
  /** true when a lower value is better performance */
  lowerIsBetter: boolean;
}

export const BENCHMARKS: Benchmark[] = [
  { key: "total_cost_finance_pct_revenue", metric: "Total Cost to Perform Finance Function (% of Revenue)", pcf: "9.0", top25: 0.6, median: 1.0, bottom25: 1.8, unit: "% of revenue", lowerIsBetter: true },
  { key: "finance_ftes_per_billion", metric: "Finance FTEs per $1B Revenue", pcf: "9.0", top25: 40, median: 70, bottom25: 120, unit: "FTEs", lowerIsBetter: true },
  { key: "days_to_close", metric: "Days to Close the Books", pcf: "9.3", top25: 4, median: 6.5, bottom25: 10, unit: "days", lowerIsBetter: true },
  { key: "cost_per_invoice_ap", metric: "Cost to Process a Single AP Invoice", pcf: "9.6", top25: 2, median: 8, bottom25: 15, unit: "USD", lowerIsBetter: true },
  { key: "dso", metric: "Days Sales Outstanding (DSO)", pcf: "9.2", top25: 30, median: 40, bottom25: 55, unit: "days", lowerIsBetter: true },
  { key: "dpo", metric: "Days Payable Outstanding (DPO)", pcf: "9.6", top25: 35, median: 45, bottom25: 60, unit: "days", lowerIsBetter: false },
  { key: "journal_entries_per_fte", metric: "Journal Entries Processed per FTE", pcf: "9.3", top25: 3500, median: 2000, bottom25: 1200, unit: "entries/FTE", lowerIsBetter: false },
  { key: "accounts_payable_cost_pct_revenue", metric: "AP Cost as % of Revenue", pcf: "9.6", top25: 0.03, median: 0.07, bottom25: 0.15, unit: "% of revenue", lowerIsBetter: true },
  { key: "budget_accuracy", metric: "Budget Accuracy (Variance %)", pcf: "9.1", top25: 3, median: 7, bottom25: 15, unit: "% variance", lowerIsBetter: true },
  { key: "finance_cost_per_employee", metric: "Total Finance Cost per Employee", pcf: "9.0", top25: 800, median: 1500, bottom25: 2800, unit: "USD", lowerIsBetter: true },
  { key: "accounts_receivable_cost_pct_revenue", metric: "AR Cost as % of Revenue", pcf: "9.2", top25: 0.02, median: 0.05, bottom25: 0.12, unit: "% of revenue", lowerIsBetter: true },
  { key: "intercompany_transactions_pct_automated", metric: "Intercompany Transactions % Automated", pcf: "9.11", top25: 90, median: 60, bottom25: 30, unit: "%", lowerIsBetter: false },
];

export const PCF_CATEGORIES: Record<string, string> = {
  "9.0": "Manage Financial Resources",
  "9.1": "Perform Planning and Management Accounting",
  "9.2": "Perform Revenue Accounting",
  "9.3": "Perform General Accounting and Reporting",
  "9.4": "Manage Fixed Asset Project Accounting",
  "9.5": "Process Payroll",
  "9.6": "Process Accounts Payable and Expense Reimbursements",
  "9.7": "Manage Treasury",
  "9.8": "Manage Internal Controls",
  "9.9": "Manage Taxes",
  "9.10": "Manage International Funds/Compliance",
  "9.11": "Perform Intercompany Accounting",
};

export function findBenchmark(metric: string): Benchmark | undefined {
  const q = metric.toLowerCase().trim().replace(/\s+/g, "_");
  return (
    BENCHMARKS.find((b) => b.key === q) ??
    BENCHMARKS.find((b) => b.key.includes(q) || b.metric.toLowerCase().includes(metric.toLowerCase()))
  );
}

export interface BenchmarkComparison {
  benchmark: Benchmark;
  pcfCategory: string;
  clientValue?: number;
  quartile?: "Top quartile" | "Second quartile" | "Third quartile" | "Bottom quartile";
  gapToMedian?: number;
  gapToTop25?: number;
}

export function compareToBenchmark(metric: string, clientValue?: number): BenchmarkComparison | { error: string; available: string[] } {
  const b = findBenchmark(metric);
  if (!b) return { error: `Unknown metric '${metric}'`, available: BENCHMARKS.map((x) => x.key) };
  const out: BenchmarkComparison = { benchmark: b, pcfCategory: PCF_CATEGORIES[b.pcf] ?? "" };
  if (clientValue === undefined || Number.isNaN(clientValue)) return out;
  const better = (x: number, y: number) => (b.lowerIsBetter ? x <= y : x >= y);
  out.clientValue = clientValue;
  out.quartile = better(clientValue, b.top25)
    ? "Top quartile"
    : better(clientValue, b.median)
      ? "Second quartile"
      : better(clientValue, b.bottom25)
        ? "Third quartile"
        : "Bottom quartile";
  // Positive gap = improvement still required to reach the reference point.
  const sign = b.lowerIsBetter ? 1 : -1;
  out.gapToMedian = round(Math.max(0, sign * (clientValue - b.median)));
  out.gapToTop25 = round(Math.max(0, sign * (clientValue - b.top25)));
  return out;
}

export const MATURITY_DIMENSIONS = [
  "Close and Consolidation",
  "Planning and Forecasting",
  "Finance Technology",
  "Operating Model and Organization",
  "Data and Reporting",
  "Controls and Compliance",
  "Change Readiness and Culture",
] as const;

const MATURITY_LEVELS = ["", "Ad Hoc", "Defined", "Managed", "Optimized", "Leading"];

export interface MaturityInput {
  dimension: string;
  current: number;
  target?: number;
  evidence?: string;
}

/** Scores the 7-dimension maturity model from the /diagnose command. */
export function scoreMaturity(scores: MaturityInput[]) {
  const rows = scores.map((s) => {
    const current = clamp(s.current, 1, 5);
    const target = clamp(s.target ?? Math.min(5, current + 1.5), 1, 5);
    return {
      dimension: s.dimension,
      current,
      currentLevel: MATURITY_LEVELS[Math.round(current)],
      target,
      targetLevel: MATURITY_LEVELS[Math.round(target)],
      gap: round(target - current),
      evidence: s.evidence ?? "",
    };
  });
  const avg = (xs: number[]) => (xs.length ? round(xs.reduce((a, b) => a + b, 0) / xs.length) : 0);
  const overall = avg(rows.map((r) => r.current));
  const priorities = [...rows].sort((a, b) => b.gap - a.gap).slice(0, 3).map((r) => r.dimension);
  return {
    overall,
    overallLevel: MATURITY_LEVELS[Math.round(overall)] ?? "",
    targetOverall: avg(rows.map((r) => r.target)),
    dimensions: rows,
    priorityGaps: priorities,
    unassessed: MATURITY_DIMENSIONS.filter((d) => !rows.some((r) => r.dimension.toLowerCase() === d.toLowerCase())),
  };
}

export interface CapitalInput {
  initialInvestment: number;
  cashFlows: number[];
  discountRate: number;
}

/** NPV / IRR / payback for a capital or transformation investment. */
export function appraiseInvestment({ initialInvestment, cashFlows, discountRate }: CapitalInput) {
  const flows = [-Math.abs(initialInvestment), ...cashFlows];
  const npvAt = (r: number) => flows.reduce((acc, cf, t) => acc + cf / Math.pow(1 + r, t), 0);
  const npv = npvAt(discountRate);

  let irr: number | null = null;
  let lo = -0.99, hi = 10;
  if (npvAt(lo) * npvAt(hi) < 0) {
    for (let i = 0; i < 200; i++) {
      const mid = (lo + hi) / 2;
      if (npvAt(lo) * npvAt(mid) <= 0) hi = mid;
      else lo = mid;
    }
    irr = (lo + hi) / 2;
  }

  let cumulative = flows[0];
  let payback: number | null = null;
  for (let t = 1; t < flows.length; t++) {
    const prev = cumulative;
    cumulative += flows[t];
    if (prev < 0 && cumulative >= 0) {
      payback = t - 1 + -prev / flows[t];
      break;
    }
  }

  const pvInflows = cashFlows.reduce((acc, cf, i) => acc + cf / Math.pow(1 + discountRate, i + 1), 0);
  return {
    npv: round(npv),
    irrPct: irr === null ? null : round(irr * 100),
    paybackYears: payback === null ? null : round(payback),
    profitabilityIndex: round(pvInflows / Math.abs(initialInvestment)),
    totalUndiscountedReturn: round(cashFlows.reduce((a, b) => a + b, 0)),
    decision: npv > 0 ? "Value-accretive at the stated hurdle rate" : "Destroys value at the stated hurdle rate",
  };
}

export interface ValueCaseInput {
  financeFtes: number;
  loadedCostPerFte: number;
  automationPct: number;
  closeDaysCurrent?: number;
  closeDaysTarget?: number;
  oneTimeInvestment: number;
  annualRunCost?: number;
  rampYears?: number;
  horizonYears?: number;
  discountRate?: number;
}

/** Finance transformation value case: capacity release + run cost, rolled into NPV/IRR. */
export function buildValueCase(v: ValueCaseInput) {
  const horizon = v.horizonYears ?? 5;
  const ramp = Math.max(1, v.rampYears ?? 2);
  const steadyStateSaving = v.financeFtes * (v.automationPct / 100) * v.loadedCostPerFte;
  const run = v.annualRunCost ?? 0;
  const yearly = Array.from({ length: horizon }, (_, i) => {
    const realised = Math.min(1, (i + 1) / ramp);
    return { year: i + 1, realisationPct: round(realised * 100), grossBenefit: round(steadyStateSaving * realised), runCost: run, netBenefit: round(steadyStateSaving * realised - run) };
  });
  const appraisal = appraiseInvestment({
    initialInvestment: v.oneTimeInvestment,
    cashFlows: yearly.map((y) => y.netBenefit),
    discountRate: v.discountRate ?? 0.08,
  });
  return {
    capacityReleasedFtes: round(v.financeFtes * (v.automationPct / 100)),
    steadyStateAnnualSaving: round(steadyStateSaving),
    closeCycleReductionDays:
      v.closeDaysCurrent !== undefined && v.closeDaysTarget !== undefined ? round(v.closeDaysCurrent - v.closeDaysTarget) : null,
    yearly,
    ...appraisal,
  };
}

function clamp(n: number, lo: number, hi: number) {
  return Math.min(hi, Math.max(lo, Number(n)));
}
function round(n: number) {
  return Math.round(n * 100) / 100;
}
