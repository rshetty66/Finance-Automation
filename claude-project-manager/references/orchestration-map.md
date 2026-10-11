# Orchestration Map — 21 Skills

**Purpose:** Dependency map and sequencing guide for project-manager plugin. Claude reads this to determine which skill to run next after completing one.

---

## Phase Structure (6 Phases)

### Phase 1 — Initiation
Establish project scope, identify stakeholders, baseline risks, and effort.

```
generate-questionnaire (#1)
    ↓ [wait for answers]
generate-charter (#2)
    ↓
generate-stakeholder-map (#3) ‖ generate-risk-register (#5)
    ↓
generate-estimate (#4)
    ↓
coordinate-meeting (#6, Go/No-Go)
```

**Entry:** User runs `/init-project`  
**Exit:** Go/No-Go decision made  
**Key artifacts:** project-charter.md, stakeholder-map.md, risk-register.md, estimate.xlsx

---

### Phase 2 — Planning
Define execution roadmap, allocate resources, budget, and communication strategy.

```
generate-project-plan (#7)
    ↓
generate-resource-plan (#8)
    ↓
generate-budget (#9) ‖ generate-risk-register (#11) ‖ generate-comm-plan (#10)
    ↓
generate-approval-letter (#12)
```

**Entry:** Go/No-Go decision = Yes  
**Exit:** Approval letter signed  
**Key artifacts:** project-plan.md, resource-plan.md, project-budget.xlsx, comm-plan.md

---

### Phase 3 — Prototyping
Prove feasibility with limited scope; gather feedback before full commitment.

```
coordinate-executors (#13)
    ↓ [work by team]
generate-comparison-table (#14)
    ↓
coordinate-meeting (#15, demo)
    ↓
generate-meeting-protocol (#16)
```

**Entry:** Approval letter signed  
**Exit:** Prototype review protocol completed  
**Key artifacts:** comparison-table.md, meeting-protocol.md

---

### Phase 4 — Development (Per Sprint)
Execute planned work in time-boxed sprints with progress monitoring.

```
coordinate-meeting (#17, sprint planning)
    ↓
[sprint work by team]
    ↓
monitor-progress (#18, daily) ‖ monitor-progress (#19, weekly)
    ↓
[if change request] → generate-change-impact (#21)
    ↓
coordinate-meeting (#20, sprint demo)
    ↓
[repeat for next sprint]
```

**Entry:** Prototyping complete  
**Exit:** All sprints delivered  
**Key artifacts:** sprint-plan.md, progress-report.md, change-impact.md

---

### Phase 5 — Launch
Prepare go-live, execute cutover, monitor for incidents.

```
generate-checklist (#22, launch) ‖ coordinate-executors (#23)
    ↓
monitor-progress (#25, sync)
    ↓
coordinate-meeting (#26, post-launch review)
    ↓
[if incident] → generate-response-plan (#27)
```

**Entry:** All sprints complete  
**Exit:** System stable, handover initiated  
**Key artifacts:** launch-checklist.md, response-plan.md

---

### Phase 6 — Closure
Capture actuals, document lessons learned, archive project.

```
monitor-progress (#28, collect actuals)
    ↓
generate-plan-fact-report (#29)
    ↓
generate-questionnaire (#30, lessons learned)
    ↓
generate-closure-report (#31)
    ↓
generate-checklist (#32, handover)
```

**Entry:** System stable  
**Exit:** Project archived  
**Key artifacts:** plan-fact-report.md, closure-report.md, lessons.md, handover-checklist.md

---

## Dependency Graph

### Inputs to Each Skill

| Skill | # | Requires from |
|-------|---|---------------|
| generate-questionnaire | 1 | project-state.md |
| generate-charter | 2 | questionnaire-answers.md |
| generate-stakeholder-map | 3 | project-charter.md |
| generate-estimate | 4 | project-charter.md |
| generate-risk-register | 5 | project-charter.md |
| coordinate-meeting | 6 | all of phases 1–5 (context-dependent) |
| generate-project-plan | 7 | project-charter.md, estimate.xlsx |
| generate-resource-plan | 8 | project-plan.md |
| generate-budget | 9 | resource-plan.md, estimate.xlsx |
| generate-comm-plan | 10 | project-plan.md, stakeholder-map.md |
| generate-risk-register | 11 | project-plan.md, risk-register.md (#5) |
| generate-approval-letter | 12 | project-plan.md, budget.xlsx, stakeholder-map.md |
| coordinate-executors | 13 | project-plan.md, resource-plan.md |
| generate-comparison-table | 14 | comparison-data.md (from execution) |
| coordinate-meeting | 15 | comparison-table.md |
| generate-meeting-protocol | 16 | meeting-notes.md (from #15) |
| coordinate-meeting | 17 | sprint-plan.md |
| monitor-progress | 18 | project-plan.md, time-tracking.md |
| monitor-progress | 19 | project-plan.md, time-tracking.md |
| coordinate-meeting | 20 | sprint-summary.md |
| generate-change-impact | 21 | project-plan.md, project-budget.xlsx, change-request.md |
| generate-checklist | 22 | project-plan.md, execution-checklist-template.md |
| coordinate-executors | 23 | launch-checklist.md |
| generate-checklist | 24 | handover-template.md |
| monitor-progress | 25 | project-state.md, status-data.md |
| coordinate-meeting | 26 | post-launch-data.md |
| generate-response-plan | 27 | incident-report.md |
| monitor-progress | 28 | actual-cost.md, actual-timeline.md |
| generate-plan-fact-report | 29 | plan data + actuals from #28 |
| generate-questionnaire | 30 | closure-template.md |
| generate-closure-report | 31 | plan-fact-report.md, lessons-answers.md |
| generate-checklist | 32 | handover-template.md |

---

## Data Flow — Key Artifacts

### Charter → Downstream

- **Produced by:** generate-charter (#2)
- **File:** project-charter.md
- **Consumed by:** #7, #5, #4, #3, #11

**Path:** `02-planning/project-charter.md`

### Stakeholder Map → Downstream

- **Produced by:** generate-stakeholder-map (#3)
- **File:** stakeholder-map.md
- **Consumed by:** #10, #6, #12

**Path:** `01-initiation/stakeholder-map.md`

### Project Plan → Downstream

- **Produced by:** generate-project-plan (#7)
- **File:** project-plan.md
- **Consumed by:** #8, #10, #13, #18, #19, #22, #28, #21

**Path:** `02-planning/project-plan.md`

### Resource Plan → Downstream

- **Produced by:** generate-resource-plan (#8)
- **File:** resource-plan.md
- **Consumed by:** #9, #13, #12

**Path:** `02-planning/resource-plan.md`

### Project Budget → Downstream

- **Produced by:** generate-budget (#9)
- **File:** project-budget.xlsx
- **Consumed by:** #12, #21, #29

**Path:** `02-planning/project-budget.xlsx`

### Risk Register → Downstream

- **Produced by:** generate-risk-register (#5, #11)
- **File:** risk-register.md
- **Consumed by:** #7, #29

**Path:** `01-initiation/risk-register.md` (updated in phase 2)

### Meeting Protocols → Log

- **Produced by:** generate-meeting-protocol (#16, #20, #26)
- **Files:** protocol-go-no-go-YYYY-MM-DD.md, protocol-demo-YYYY-MM-DD.md, protocol-sprint-demo-YYYY-MM-DD.md
- **Stored in:** `meetings/`

---

## Email Integration Points

Skills that invoke `send-email`:

1. **generate-questionnaire (#1)** → E1 (external client) or E2 (internal team) — Level 3
2. **generate-approval-letter (#12)** → E3 (approval request) — Level 3
3. **coordinate-meeting (#6, #15, #17, #20, #26)** → E8 (meeting invitation) — Level 3
4. **monitor-progress (#18, #19, #25)** → E6 (status reminder), E7 (weekly report) — Level 1
5. **coordinate-executors (#13, #23)** → E4, E5 (stakeholder alerts) — Level 2

See `email-autonomy-rules.md` for autonomy levels.

---

## Notation Guide

- **→** Sequential dependency (skill A must complete before B starts)
- **‖** Parallel execution (can start simultaneously, no inter-dependency)
- **[wait]** Requires external input (user response, team deliverable, time passage)
- **#n** Skill ID reference

---

## Sequencing Rules

1. **No backtracking:** Once phase exits, return only for approved change requests (skill #21).
2. **Parallel reads:** All skills can read from `project-state.md` and `logs/log.md` simultaneously.
3. **No out-of-order:** Skills must follow phase sequence. Running #10 (comm-plan) before #7 (project-plan) is forbidden.
4. **Incident path:** If incident during launch (phase 5), run #27 (response-plan), then #25 (monitor-progress). Do not restart.
5. **Change requests:** Skill #21 (change-impact) can run at any point in phases 2–5. Update #11 (risk-register) after approval.

---

## Recovery & Restart

If a skill fails or is rejected:

1. User reviews output and requests revision.
2. Same skill re-runs with updated context (user feedback loaded into project-state.md).
3. No phase reset unless user explicitly rolls back to prior phase.

Example: If #12 (approval-letter) is rejected, run #12 again after PM updates project-plan.md.

---

**Last updated:** 2026-04-13  
**Version:** 1.0
