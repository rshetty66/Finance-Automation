---
description: Generate weekly sprint progress report
argument-hint: [sprint-number]
---

# Sprint Report

Generate a comprehensive weekly progress report for the current sprint. Available only in Phase 3 (Execution) and beyond.

## Input

- **sprint-number** (optional): Sprint number. If omitted, calculate from project start date and current week.

## Process

### 1. Validate Project Phase

Read `project-state.md`:
- Verify current phase is 3, 4, or 5 (Execution, Monitoring, or Closure)
- If phase < 3, display error: "Sprint reports are only available during Execution phase (3) and beyond"
- Continue only if phase >= 3

### 2. Determine Sprint Number

If sprint-number not provided in argument:
- Calculate from project_state.md `phase_start_date` or project initiation date
- Use ISO week numbering: sprint 1 = week 1, sprint 2 = week 2, etc.
- Display calculated sprint number to user

If sprint-number provided:
- Validate it's a positive integer
- Use provided value

### 3. Read Project Plan

Read `02-planning/project-plan.md` to get:
- Planned milestones for this sprint
- Planned work items and deliverables
- Sprint duration and dates
- Success criteria

### 4. Read Current Project State

Read `project-state.md` to get:
- Artifacts completed this sprint
- Artifacts in progress this sprint
- Artifacts blocked or at risk
- Current phase status

### 5. Query Project Tracker (~~project tracker)

Contact external project tracker (if integrated) to pull:
- Current sprint tasks and their status
- Burndown rate and velocity
- Blockers and risks reported
- Team capacity and utilization

If no external tracker:
- Log note: "Project tracker integration not available - using project-state.md only"

### 6. Trigger Monitor Progress Skill

Call skill #18 (monitor-progress) with parameters:
```
artifact_id: "18"
report_type: "progress"
sprint_number: [calculated or provided]
project_path: "."
```

Skill will produce comprehensive analysis including:
- Actual vs. planned progress
- Schedule variance
- Budget variance (if available)
- Risk trajectory
- Next week forecast

### 7. Save Report

Create new file: `reports/weekly-status-{YYYY-MM-DD}.md`

Include in report:
- Sprint number and date range
- Executive summary
- Planned vs. actual comparison
- Completed work items (with links to artifacts)
- In-progress work items (% complete, blockers)
- Upcoming items (next week plan)
- Risks and issues (from risk register)
- Stakeholder metrics and KPIs
- Recommendations for next week
- Appendix: Full monitor-progress skill output

Format example:
```markdown
# Sprint [N] Status Report
**Week of**: [Date Range]
**Generated**: [TIMESTAMP]

## Executive Summary
[1-2 paragraph overview of sprint health: on track/at risk/blocked]

## Progress vs. Plan

### Planned Work
- [X] Artifact 1: Completed
- [ ] Artifact 2: In Progress (75%)
- [ ] Artifact 3: Not started (blocked: awaiting input)

### Schedule Performance
- Planned completion: X artifacts
- Actual completion: Y artifacts
- Schedule variance: ±Z%

### Quality Metrics
[From monitor-progress output]

## Risks & Issues
| Risk | Impact | Mitigation | Status |
|---|---|---|---|

## Next Steps
- Week [N+1] priorities
- Recommended actions
- Decision points for stakeholders

---

*Full analysis: [monitor-progress skill output]*
```

### 8. Update Project State

Update `project-state.md`:
- Set `last_sprint_report_date` to today
- Update artifact statuses based on report findings
- Note any phase progression

### 9. Log Action

Append to `logs/log.md`:
```
[TIMESTAMP] | SPRINT-REPORT | completed | Generated sprint [N] status report (week of [DATE])
```

### 10. Present Report

Display report summary to user with:
- Sprint health status (Green/Yellow/Red)
- Key achievements this week
- Critical blockers
- Recommended focus areas for next week
- Link to full report file

## Completion

Offer follow-up actions:
- "Review the full report at [path]"
- "Update risks in risk register with `/next-step`"
- "Schedule stakeholder communication using ~~email"
- "Use `/status` to see overall project health"

## Constraints

- Reports only available Phase 3+
- One report per week (using date to prevent duplicates)
- Monitor-progress skill must be available
- Project tracker integration optional but recommended
