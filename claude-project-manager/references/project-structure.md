# Project Structure Template

**Purpose:** Standard folder and file organization for managed projects. Claude reads this when running `/init-project` to create the directory tree and establish naming conventions.

**Version:** 1.0

---

## Directory Tree

```
{project-name}/
├── CLAUDE.md                          # Project config & plugin settings
├── project-state.md                   # Live status tracking (artifact table)
│
├── 01-initiation/                     # Phase 1: Scope & stakeholders
│   ├── questionnaire-{nnn}.md
│   ├── questionnaire-answers-{nnn}.md
│   ├── project-charter.md
│   ├── stakeholder-map.md
│   ├── risk-register.md
│   └── estimate-{nnn}.xlsx
│
├── 02-planning/                       # Phase 2: Roadmap & resources
│   ├── project-plan.md
│   ├── resource-plan.md
│   ├── project-budget.xlsx
│   ├── comm-plan.md
│   ├── risk-register.md               # (updated copy)
│   └── approval-letter.md
│
├── 03-execution/                      # Phase 3–5: Delivery & launch
│   ├── comparison-table-{nnn}.md      # (phase 3 prototype review)
│   ├── launch-checklist.md            # (phase 5)
│   ├── handover-checklist.md          # (phase 5)
│   ├── change-impact-{nnn}.md         # (change requests)
│   └── response-plan-{nnn}.md         # (incidents)
│
├── 04-closure/                        # Phase 6: Wrap-up & lessons
│   ├── actual-cost.md
│   ├── actual-timeline.md
│   ├── plan-fact-report.md
│   ├── closure-report.md
│   ├── lessons-questionnaire.md
│   ├── lessons-answers.md
│   └── handover-protocol.md
│
├── meetings/                          # All meeting agendas & protocols
│   ├── agenda-go-no-go-{YYYY-MM-DD}.md
│   ├── protocol-go-no-go-{YYYY-MM-DD}.md
│   ├── agenda-demo-{YYYY-MM-DD}.md
│   ├── protocol-demo-{YYYY-MM-DD}.md
│   ├── agenda-sprint-plan-{YYYY-MM-DD}.md
│   ├── protocol-sprint-plan-{YYYY-MM-DD}.md
│   ├── agenda-sprint-demo-{YYYY-MM-DD}.md
│   └── protocol-sprint-demo-{YYYY-MM-DD}.md
│
├── reports/                           # Periodic status & progress
│   ├── weekly-status-{YYYY-MM-DD}.md
│   ├── deviation-report-{YYYY-MM-DD}.md
│   ├── progress-report-{YYYY-MM-DD}.md
│   └── sync-report-{YYYY-MM-DD}.md
│
├── input/                             # READ-ONLY: External data & answers
│   ├── stakeholder-answers-{nnn}.md
│   ├── team-list.md
│   ├── constraints.md
│   ├── market-context.md
│   ├── comparison-data.md             # (phase 3)
│   ├── meeting-notes-{YYYY-MM-DD}.md  # (from Mode C meetings)
│   ├── execution-status.md            # (team updates)
│   ├── change-request-{nnn}.md        # (user submitted)
│   ├── incident-report-{nnn}.md       # (from production)
│   └── time-tracking-{YYYY-MM-DD}.md  # (team logged hours)
│
├── drafts/                            # Mode B draft artifacts (temporary)
│   ├── email-draft-questionnaire-{YYYY-MM-DD}.md
│   ├── email-draft-approval-{YYYY-MM-DD}.md
│   ├── email-draft-meeting-{YYYY-MM-DD}.md
│   └── draft-{artifact-name}-{YYYY-MM-DD}.md
│
├── logs/
│   └── log.md                         # Complete action log (appended)
│
└── archive/                           # (created at phase 6)
    ├── 01-initiation/
    ├── 02-planning/
    ├── 03-execution/
    ├── 04-closure/
    ├── meetings/
    ├── reports/
    └── project-state-FINAL-{YYYY-MM-DD}.md
```

---

## Naming Conventions

### File Names

**Kebab-case:** All lowercase, words separated by hyphens.

```
✓ project-charter.md
✓ weekly-status.md
✗ ProjectCharter.md
✗ Weekly Status.md
```

**Date Suffix:** YYYY-MM-DD format, appended for timestamped files.

```
✓ agenda-go-no-go-2026-04-13.md
✓ time-tracking-2026-04-13.md
✗ agenda-go-no-go-13-04-2026.md
✗ agenda-go-no-go-April 13.md
```

**ID Suffix:** Sequential number for multiple versions or iterations (e.g., questionnaire #1, #2).

```
✓ questionnaire-001.md
✓ change-impact-002.md
✗ questionnaire-v1.md
✗ change-impact-v2.md
```

**File Extensions:**
- `.md` for text (documents, plans, reports, checklists, protocols)
- `.xlsx` for calculations (budget, estimate, actuals tracking)

### Folder Structure Rules

- Phase folders (01–04) are immutable and always present
- Subfolders should not be created within phase folders (flatten: store all phase 1 artifacts in `01-initiation/`)
- `input/` and `drafts/` are temporary working folders
- `logs/` contains only `log.md` (single file)
- `archive/` is created automatically at phase 6 closure

---

## Artifact Mapping (34 Total)

### Phase 1 — Initiation (7 artifacts)

| # | Artifact | File | Status | Location |
|---|----------|------|--------|----------|
| 1 | Questionnaire | questionnaire-001.md | Draft | 01-initiation/ |
| 2 | Charter | project-charter.md | Approved | 01-initiation/ |
| 3 | Stakeholder Map | stakeholder-map.md | Approved | 01-initiation/ |
| 4 | Estimate | estimate-001.xlsx | Approved | 01-initiation/ |
| 5 | Risk Register | risk-register.md | Approved | 01-initiation/ |
| 6a | Go/No-Go Agenda | agenda-go-no-go-{date}.md | Draft | meetings/ |
| 6b | Go/No-Go Protocol | protocol-go-no-go-{date}.md | Approved | meetings/ |

### Phase 2 — Planning (6 artifacts)

| # | Artifact | File | Status | Location |
|---|----------|------|--------|----------|
| 7 | Project Plan | project-plan.md | Approved | 02-planning/ |
| 8 | Resource Plan | resource-plan.md | Approved | 02-planning/ |
| 9 | Budget | project-budget.xlsx | Approved | 02-planning/ |
| 10 | Comm Plan | comm-plan.md | Approved | 02-planning/ |
| 11 | Risk Register (Updated) | risk-register.md | Approved | 02-planning/ |
| 12 | Approval Letter | approval-letter.md | Approved | 02-planning/ |

### Phase 3 — Prototyping (4 artifacts)

| # | Artifact | File | Status | Location |
|---|----------|------|--------|----------|
| 13 | Executor Coordination | (meeting notes in input/) | Completed | input/execution-status.md |
| 14 | Comparison Table | comparison-table-001.md | Approved | 03-execution/ |
| 15a | Demo Agenda | agenda-demo-{date}.md | Draft | meetings/ |
| 15b | Demo Protocol | protocol-demo-{date}.md | Approved | meetings/ |
| 16 | Meeting Protocol | (above, 15b) | Approved | meetings/ |

### Phase 4 — Development (9 artifacts + repeating)

| # | Artifact | File | Status | Location |
|---|----------|------|--------|----------|
| 17a | Sprint Plan Agenda | agenda-sprint-plan-{date}.md | Draft | meetings/ |
| 17b | Sprint Plan Notes | (meeting notes in input/) | Completed | input/ |
| 18 | Daily Progress | progress-report-{date}.md | Approved | reports/ |
| 19 | Weekly Progress | weekly-status-{date}.md | Approved | reports/ |
| 20a | Sprint Demo Agenda | agenda-sprint-demo-{date}.md | Draft | meetings/ |
| 20b | Sprint Demo Protocol | protocol-sprint-demo-{date}.md | Approved | meetings/ |
| 21 | Change Impact | change-impact-{nnn}.md | Approved | 03-execution/ |
| — | Deviation Report | deviation-report-{date}.md | Approved | reports/ |
| — | Sync Report | sync-report-{date}.md | Approved | reports/ |

**Note:** Skills #18, #19, #20 repeat once per sprint. #17 runs at sprint start. #21 runs on-demand for change requests.

### Phase 5 — Launch (7 artifacts)

| # | Artifact | File | Status | Location |
|---|----------|------|--------|----------|
| 22 | Launch Checklist | launch-checklist.md | Approved | 03-execution/ |
| 23 | Launch Execution | (meeting notes in input/) | Completed | input/execution-status.md |
| 25 | Post-Launch Monitoring | sync-report-{date}.md | Approved | reports/ |
| 26a | Post-Launch Review Agenda | (meeting notes) | Draft | meetings/ |
| 26b | Post-Launch Review Protocol | (meeting notes) | Approved | meetings/ |
| 27 | Incident Response | response-plan-{nnn}.md | Approved | 03-execution/ |
| — | Handover Checklist | handover-checklist.md | Draft | 03-execution/ |

### Phase 6 — Closure (7 artifacts)

| # | Artifact | File | Status | Location |
|---|----------|------|--------|----------|
| 28 | Actual Cost & Timeline | actual-cost.md, actual-timeline.md | Approved | 04-closure/ |
| 29 | Plan-Fact Report | plan-fact-report.md | Approved | 04-closure/ |
| 30 | Lessons Questionnaire | lessons-questionnaire.md | Draft | 04-closure/ |
| 31 | Closure Report | closure-report.md | Approved | 04-closure/ |
| 32 | Handover Checklist | handover-protocol.md | Approved | 04-closure/ |
| — | Project State (Final) | project-state-FINAL-{date}.md | Archived | archive/ |
| — | Archived Logs | log-FINAL-{date}.md | Archived | archive/ |

---

## project-state.md Template

This file is the live dashboard. Agent updates it after every skill.

```markdown
# Project State — {project-name}

**Status:** Initiation | Planning | Execution | Launch | Closure  
**Language:** RU | EN  
**PM Email:** user@example.com  
**Last Updated:** 2026-04-13 10:15  

---

## Current Phase: Phase {n}

**Phase Name:** Initiation | Planning | Execution | Launch | Closure

---

## Artifact Status Table

| # | Artifact | File Path | Status | Date | Skill | Notes |
|---|----------|-----------|--------|------|-------|-------|
| 1 | Questionnaire | 01-initiation/questionnaire-001.md | Draft | 2026-04-13 | #1 | Awaiting user answers |
| 2 | Charter | 01-initiation/project-charter.md | Approved | 2026-04-13 | #2 | Generated from Q1 answers |
| 3 | Stakeholder Map | 01-initiation/stakeholder-map.md | Draft | — | #3 | Waiting for #2 completion |
| 4 | Estimate | 01-initiation/estimate-001.xlsx | Not Started | — | #4 | Queued after #2 |
| 5 | Risk Register | 01-initiation/risk-register.md | Not Started | — | #5 | Queued after #2 |
| 6 | Go/No-Go Meeting | meetings/protocol-go-no-go-{date}.md | Not Started | — | #6 | Scheduled for TBD |
| ... | ... | ... | ... | ... | ... | ... |

---

## Next Actions

1. **Immediate:** User approves Questionnaire (#1) answers
2. **Then:** Run generate-charter (#2)
3. **Parallel:** Run #3 (stakeholder-map) and #5 (risk-register) after #2 approved

---

## Dependencies Blocked

- #7 (project-plan) awaiting #2 (charter)
- #8 (resource-plan) awaiting #7 (project-plan)

---

## Change Requests (Submitted)

| ID | Type | Status | Submitted | Impact Assessed |
|----|------|--------|-----------|-----------------|
| CR-001 | Scope | Pending | 2026-04-12 | No → Run #21 |

---

## Incidents (Logged)

| ID | Type | Status | Logged | Response |
|----|------|--------|--------|----------|
| INC-001 | Delivery Delay | Open | 2026-04-10 | TBD |

---

## Key Metrics

| Metric | Planned | Actual | Delta | Status |
|--------|---------|--------|-------|--------|
| Budget | $100K | — | — | On Track |
| Timeline | 12 weeks | — | — | On Track |
| Team Size | 5 | — | — | Pending |

---

## Configuration

**Project:** {project-name}  
**Owner (PM):** {pm-name}  
**Start Date:** 2026-04-13  
**End Date (Planned):** TBD  
**Status Cadence:** Weekly  

---

## Communication

**Primary Contact:** {pm-email}  
**Escalation:** {escalation-contact}  
**Stakeholder List:** See 01-initiation/stakeholder-map.md  

---

**Log:** See logs/log.md for detailed action history.
```

---

## Folder Access Rules

| Folder | Agent | User |
|--------|-------|------|
| 01–04 | Read, Write artifacts only | Read, Approve artifacts |
| meetings/ | Write agendas & protocols | Run meetings, provide notes |
| reports/ | Write status & progress reports | Read, Review |
| input/ | Read all files | Write answers, data, notes |
| drafts/ | Write drafts (Mode B) | Review, Edit, Request finalization |
| logs/ | Append to log.md only | Read |
| archive/ | Write at phase 6 only | Read |
| CLAUDE.md, project-state.md | Update status columns | Edit config |

---

## Phase Transition Checklist

Before advancing phase:

- [ ] All artifacts in current phase approved
- [ ] All Mode A/B artifacts reviewed by user
- [ ] All Mode C tasks completed (user logged outcomes)
- [ ] `project-state.md` updated with phase name
- [ ] `logs/log.md` shows phase transition entry
- [ ] Change requests resolved or logged

---

**Last updated:** 2026-04-13  
**Version:** 1.0
