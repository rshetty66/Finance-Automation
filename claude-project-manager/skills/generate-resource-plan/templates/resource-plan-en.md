# Artifact Schema: resource-plan.md (EN)

The `resource-plan.md` file contains 4 sections. Below is the structure of each section.

---

## Header Block

| Field | Value |
|-------|-------|
| Project | {project name} |
| PM | {PM name} |
| Date | {date generated} |
| Version | 1.0 (draft) |
| Sources | project-plan.md, team-list.md |

---

## Assumptions

Minimum 3 items (agent fills with specific values):

1. Phase durations taken from project-plan.md ({plan version date}).
2. FTE allocation for internal team members — {uniform across project / phase-specific} —
   based on team-list.md data.
3. {Rates taken from team-list.md. / Internal team members are on the operational budget —
   cost columns are left blank. External resources: contract amounts as stated in team-list.md.}
4. {Additional agent assumptions, if applicable.}

---

## Section 1 — Internal Team

### Composition

| # | Role | Name | Grade | Base Allocation |
|---|------|------|-------|:---------------:|
| 1 | {role} | {name} | {grade} | {%} |
| … | … | … | … | … |

---

## Section 2 — Allocation Matrix (FTE)

Cell values represent FTE (share of full-time). 0 = role not active in phase.

| Role | Ph1 ({X} mo) | Ph2 ({X} mo) | Ph3 ({X} mo) | Ph4 ({X} mo) | Ph5 ({X} mo) | Ph6 ({X} mo) |
|------|:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|
| {role 1} | {FTE} | {FTE} | {FTE} | {FTE} | {FTE} | {FTE} |
| {role 2} | {FTE} | {FTE} | {FTE} | {FTE} | {FTE} | {FTE} |
| … | … | … | … | … | … | … |

### Person-Months by Role and Phase

Calculation: person-months = FTE × phase duration (months). Rounded to 1 decimal.

| Role | Ph1 | Ph2 | Ph3 | Ph4 | Ph5 | Ph6 | Total (p-m) | Rate ($/mo) | Total ($) |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:-----------:|:-----------:|:---------:|
| {role 1} | — | — | — | — | — | — | — | {rate / —} | {amount / —} |
| {role 2} | — | — | — | — | — | — | — | {rate / —} | {amount / —} |
| … | … | … | … | … | … | … | … | … | … |
| **Total (p-m)** | — | — | — | — | — | — | — | — | — |
| **Total ($)** | — | — | — | — | — | — | — | — | — |

> Note: if internal team rates are not available (operational budget) —
> columns "Rate" and "Total ($)" are left blank "—".
> To calculate the project budget, run generate-budget (task #9).

---

## Section 3 — External Resources

Contractors and outsourced specialists with fixed-price engagements.

| # | Role | Vendor | Phases | Period | Budget | Scope |
|---|------|--------|--------|--------|:------:|-------|
| 1 | {role} | {vendor} | {Ph3–Ph4} | {dates} | ${amount} | {scope description} |
| … | … | … | … | … | … | … |

**Total external resources:** ${amount}

> If no external resources — state: "No external resources planned."

---

## Section 4 — Phase Load Summary

| Phase | Duration | Person-Months (int.) | Cost (int.) | Cost (ext.) | Total |
|-------|:--------:|:--------------------:|:-----------:|:-----------:|:-----:|
| 1 — Initiation | {X} mo | — | — / — | — | — |
| 2 — Planning | {X} mo | — | — / — | — | — |
| 3 — Prototyping | {X} mo | — | — / — | — | — |
| 4 — Development | {X} mo | — | — / — | — | — |
| 5 — Launch | {X} mo | — | — / — | — | — |
| 6 — Closure | {X} mo | — | — / — | — | — |
| **Total** | **{X} mo** | **—** | **— / —** | **—** | **—** |

> "— / —" in the cost column: first value — when rates are available, second — when not.
> When internal team rates are absent, the cell remains blank "—".

---

## Resource Plan Risks

| # | Risk Description | Role | Phase | Recommendation |
|---|-----------------|------|-------|----------------|
| 1 | {description} | {role} | {phase} | {action} |

> If no risks detected — state: "No resource plan risks detected."
