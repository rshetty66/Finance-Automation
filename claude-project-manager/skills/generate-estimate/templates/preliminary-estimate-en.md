# Artifact Schema: Preliminary Estimate (preliminary-estimate.xlsx)

Created by the `generate-estimate` skill. Contains 3 sheets. Used as input for `generate-budget` and `generate-resource-plan`.

---

## Sheet 1: Summary

**Header (rows 1–6):**

| Field | Value |
|-------|-------|
| Project | `{{project_name}}` |
| Project Manager | `{{pm_name}}` |
| Estimate Date | `{{date}}` |
| Version | 1.0 |
| Project Type | `{{project_type}}` |
| Estimation Method | Analogy-based (agent expert knowledge) |

**Assumptions (rows 8–14):**

| # | Assumption |
|---|------------|
| 1 | `{{assumption_1}}` |
| 2 | `{{assumption_2}}` |
| 3 | `{{assumption_3}}` |
| 4 | Rates are market-level as of the estimate date. May require adjustment. |
| 5 | Team utilization assumed at 100% FTE unless otherwise specified. |
| 6 | Marketing budget is included only if GTM is in scope. |

**Summary Table (rows 16–20):**

| Scenario | Duration (weeks) | Budget: Team | Budget: Infrastructure | Budget: Marketing | Total |
|----------|-----------------|--------------|------------------------|-------------------|-------|
| Optimistic | `{{opt_weeks}}` | `{{opt_team}}` | `{{opt_infra}}` | `{{opt_mktg}}` | `{{opt_total}}` |
| Realistic | `{{real_weeks}}` | `{{real_team}}` | `{{real_infra}}` | `{{real_mktg}}` | `{{real_total}}` |
| Pessimistic | `{{pest_weeks}}` | `{{pest_team}}` | `{{pest_infra}}` | `{{pest_mktg}}` | `{{pest_total}}` |

**Agent Recommendation (row 22):**
`{{recommendation}}` — Estimates are preliminary and require PM verification.

---

## Sheet 2: Timeline

**Columns:**

| Phase | Key Deliverables | Optimistic (wks) | Realistic (wks) | Pessimistic (wks) | Notes |
|-------|-----------------|-----------------|-----------------|-------------------|-------|
| 1. Initiation | Charter, stakeholder map, estimates | `{{p1_opt}}` | `{{p1_real}}` | `{{p1_pest}}` | `{{p1_notes}}` |
| 2. Design & Planning | Project plan, budget, comm plan | `{{p2_opt}}` | `{{p2_real}}` | `{{p2_pest}}` | `{{p2_notes}}` |
| 3. Prototyping & Validation | Prototype(s), client demo | `{{p3_opt}}` | `{{p3_real}}` | `{{p3_pest}}` | `{{p3_notes}}` |
| 4. Development & Testing | Working product, QA report | `{{p4_opt}}` | `{{p4_real}}` | `{{p4_pest}}` | `{{p4_notes}}` |
| 5. Launch & GTM | Launched product, marketing materials | `{{p5_opt}}` | `{{p5_real}}` | `{{p5_pest}}` | `{{p5_notes}}` |
| 6. Closure | Closure report, archive | `{{p6_opt}}` | `{{p6_real}}` | `{{p6_pest}}` | `{{p6_notes}}` |
| **Total** | | **`{{total_opt}}`** | **`{{total_real}}`** | **`{{total_pest}}`** | |

> Phases 3 and 5 are optional. If not in scope — set to 0 with note "out of scope".

---

## Sheet 3: Budget

### Section A: Team

| Role | FTE | Opt. duration (wks) | Real. duration (wks) | Pest. duration (wks) | Rate ($/wk) | Total Opt. | Total Real. | Total Pest. |
|------|-----|---------------------|----------------------|----------------------|-------------|-----------|------------|------------|
| `{{role_1}}` | `{{fte_1}}` | `{{opt}}` | `{{real}}` | `{{pest}}` | `{{rate_1}}` | =FTE×opt×rate | =FTE×real×rate | =FTE×pest×rate |
| … | | | | | | | | |
| **Team Total** | | | | | | `{{team_opt}}` | `{{team_real}}` | `{{team_pest}}` |

### Section B: Infrastructure & Tools

| Item | Type (one-time / monthly) | Opt. ($) | Real. ($) | Pest. ($) | Notes |
|------|--------------------------|----------|-----------|-----------|-------|
| Hosting / cloud | monthly | `{{}}` | `{{}}` | `{{}}` | |
| SaaS tools (task tracker, design, CI/CD) | monthly | `{{}}` | `{{}}` | `{{}}` | |
| External APIs / services | monthly | `{{}}` | `{{}}` | `{{}}` | |
| One-time licenses | one-time | `{{}}` | `{{}}` | `{{}}` | |
| **Infrastructure Total** | | `{{infra_opt}}` | `{{infra_real}}` | `{{infra_pest}}` | |

### Section C: Marketing & GTM

> Fill only if GTM is in scope. Otherwise leave rows empty / zeroed out.

| Item | Opt. ($) | Real. ($) | Pest. ($) | Notes |
|------|----------|-----------|-----------|-------|
| Content & copywriting | `{{}}` | `{{}}` | `{{}}` | |
| Design assets | `{{}}` | `{{}}` | `{{}}` | |
| Paid advertising | `{{}}` | `{{}}` | `{{}}` | |
| PR / media | `{{}}` | `{{}}` | `{{}}` | |
| Other | `{{}}` | `{{}}` | `{{}}` | |
| **Marketing Total** | `{{mktg_opt}}` | `{{mktg_real}}` | `{{mktg_pest}}` | |

### Budget Summary Row

| | Optimistic | Realistic | Pessimistic |
|-|-----------|----------|------------|
| Team | `{{team_opt}}` | `{{team_real}}` | `{{team_pest}}` |
| Infrastructure | `{{infra_opt}}` | `{{infra_real}}` | `{{infra_pest}}` |
| Marketing/GTM | `{{mktg_opt}}` | `{{mktg_real}}` | `{{mktg_pest}}` |
| **Grand Total** | **`{{total_opt}}`** | **`{{total_real}}`** | **`{{total_pest}}`** |
