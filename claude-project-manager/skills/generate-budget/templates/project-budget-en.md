# Artifact Schema: project-budget.xlsx (EN)

The file contains 3 sheets. Structure of each sheet is described below.

---

## Sheet 1 — Summary

### Header Block

| Field | Value |
|-------|-------|
| Project | {project name} |
| PM | {PM name} |
| Date | {generation date} |
| Version | 1.0 (draft) |
| Sources | preliminary-estimate.xlsx (realistic scenario), resource-plan.md |

### Assumptions

Minimum 3 assumptions:
1. Budget is based on the realistic scenario from preliminary-estimate.xlsx.
2. Rates are taken from resource-plan.md {or: standard analogy-based rates}.
3. GTM {is included in scope / is not included in scope — Section C zeroed out}.
4. Contingency reserve: {X}% — {rationale: HIGH risk count from risk-register.md / standard}.
5. {Budget ceiling: if specified in constraints.md}.

### Phase Summary Table

| Phase | Description | A: Team | B: Infrastructure | C: GTM | Phase Total |
|-------|-------------|:-------:|:-----------------:|:------:|:-----------:|
| 1 | Initiation | — | — | — | — |
| 2 | Planning | — | — | — | — |
| 3 | Prototyping | — | — | — | — |
| 4 | Development | — | — | — | — |
| 5 | Launch | — | — | — | — |
| 6 | Closure | — | — | — | — |
| **Baseline Budget** | | | | | **—** |
| **Contingency Reserve ({X}%)** | | | | | **—** |
| **TOTAL (Grand Total)** | | | | | **—** |

### Risk Flag (if applicable)

> ⚠ Grand Total [{amount}] exceeds the stated budget ceiling [{ceiling}].
> Recommended: revise scope, reduce team size, or phase the project funding.

---

## Sheet 2 — Budget Detail

Rows are organized by phase → category → cost line item.

| Phase | Category | Item | Unit | Qty | Rate | Total |
|-------|----------|------|------|:---:|:----:|:-----:|
| 1 — Initiation | A: Team | Product Manager | person-month | — | — | — |
| 1 — Initiation | A: Team | Business Analyst | person-month | — | — | — |
| 1 — Initiation | B: Infrastructure | Tools (licenses) | month | — | — | — |
| 1 — Initiation | C: GTM | — | — | — | — | 0 |
| ... | ... | ... | ... | ... | ... | ... |
| 6 — Closure | A: Team | PM (closure) | person-month | — | — | — |
| **Baseline Budget** | | | | | | **—** |
| **Contingency Reserve ({X}%)** | | | | | | **—** |
| **Grand Total** | | | | | | **—** |

### Default Infrastructure Ranges (if no estimate data available)

Use the following ranges when preliminary-estimate.xlsx does not contain infrastructure data:

| Cost Type | Small Project | Medium Project | Large Project |
|-----------|:-------------:|:--------------:|:-------------:|
| Cloud infrastructure (monthly) | $150–400 | $400–1,200 | $1,200–4,000 |
| Tools / licenses (monthly) | $50–200 | $200–600 | $600–2,000 |
| One-time setup costs | $300–700 | $700–2,000 | $2,000–7,000 |

Small: team ≤5 people, duration ≤3 months.
Medium: team 5–15 people, duration 3–9 months.
Large: team 15+ people, duration 9+ months.

---

## Sheet 3 — Resource Detail

Source: resource-plan.md. Shows cost by role × phase.

| Role | Ph1 (p-m) | Ph2 | Ph3 | Ph4 | Ph5 | Ph6 | Total (p-m) | Rate (monthly) | Total ($) |
|------|:---------:|:---:|:---:|:---:|:---:|:---:|:-----------:|:--------------:|:---------:|
| Product Manager | — | — | — | — | — | — | — | — | — |
| Tech Lead | — | — | — | — | — | — | — | — | — |
| Developer | — | — | — | — | — | — | — | — | — |
| Designer | — | — | — | — | — | — | — | — | — |
| QA Engineer | — | — | — | — | — | — | — | — | — |
| Business Analyst | — | — | — | — | — | — | — | — | — |
| **Team Total** | — | — | — | — | — | — | — | | **—** |

Notes:
- Phases where a role is not engaged are marked "—" or "0".
- Rates are taken from resource-plan.md. If not specified — from preliminary-estimate.xlsx (analogy data).
- Sheet 3 totals = Section A in Sheet 2.

---

## Formatting Rules

- Currency: consistent throughout the file (USD or local — determined from resource-plan.md or constraints.md).
- Numbers: no decimal places for amounts > 1,000; two decimal places for hourly rates.
- Formatting: total rows in bold; Grand Total row with distinct background color.
- Zero rows (GTM when not in scope) — keep with value "0" and a note, do not delete.
