---
description: Show current project status and next available steps
---

# Project Status

Display comprehensive current state of the project including phase, artifacts, recent activity, and recommended next actions.

## Process

### 1. Read Project State

Read `project-state.md` to extract:
- Current phase
- Count artifacts by status (not started, in progress, approved, completed)
- Last update timestamp

### 2. Read Recent Logs

Read the last 10 entries from `logs/log.md` to show:
- Recent actions taken
- Artifacts processed
- Status changes

### 3. Determine Available Next Steps

Read `references/orchestration-map.md` to:
- Identify artifacts with status "approved" whose dependent skills haven't started
- Find all "not started" artifacts with satisfied dependencies
- List available immediate next steps

### 4. Check Scheduled Tasks Status

If scheduled tasks exist at `config/scheduled-tasks.md`:
- List all 5 tasks (weekly-status, daily-deviation, risk-update, sync-streams, executor-reminders)
- Show enabled/disabled status
- Show last run timestamp if available
- Show next scheduled run time

### 5. Display Status Summary

Present to user in this format:

```
# Project Status Report

## Current Phase
Phase [N] of 5: [Phase Name]

## Artifact Summary
- Completed: X artifacts
- In Progress: Y artifacts
- Approved (pending execution): Z artifacts
- Not Started (dependencies met): W artifacts
- Not Started (blocked): V artifacts

## Recent Activity (Last 10 actions)
[Display table with timestamp, artifact, status, notes]

## Scheduled Tasks Status
- weekly-status: [ENABLED/DISABLED] | Last run: [DATE] | Next: [DATE]
- daily-deviation: [ENABLED/DISABLED] | Last run: [DATE] | Next: [DATE]
- risk-update: [ENABLED/DISABLED] | Last run: [DATE] | Next: [DATE]
- sync-streams: [ENABLED/DISABLED] | Last run: [DATE] | Next: [DATE]
- executor-reminders: [ENABLED/DISABLED] | Last run: [DATE] | Next: [DATE]

## Recommended Next Steps

1. [Step 1 with rationale and artifact reference]
2. [Step 2 with rationale and artifact reference]
3. [Step 3 with rationale and artifact reference]

---

Use `/next-step` to get detailed guidance on the recommended next action.
Use `/init-project` to create a new project.
Use `/sprint-report` to generate a weekly status report for Phase 3+.
```

### 6. Highlight Critical Information

If any conditions exist, call them out:
- If Phase 1 not complete, show blocker preventing Phase 2
- If tasks are disabled when they should be enabled, note this
- If critical artifacts are overdue, flag for user attention

## Completion

Provide next action prompt to user at end of report.
