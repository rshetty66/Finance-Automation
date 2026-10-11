---
description: Check for schedule and budget deviations
---

# Deviation Check Command

## Purpose
Compare planned vs actual project performance to identify schedule and budget deviations. Runs automated deviation analysis and notifies stakeholders if issues are detected.

## Steps

1. **Verify project state**
   - Read `project-state.md`
   - Confirm project is in phase 3, 4, or 5
   - If not in these phases, inform user this command requires active execution phase

2. **Retrieve planned baselines**
   - Read `02-planning/project-plan.md`
   - Extract planned dates for all major milestones
   - Extract budget allocations per workstream

3. **Query actual performance**
   - Query ~~project tracker for task statuses and completion dates across all workstreams
   - Retrieve actual spend (if available in tracker)
   - Compile actual vs planned data

4. **Analyze deviations**
   - Compare actual task completion dates against planned dates
   - Calculate schedule variance (days behind/ahead)
   - Compare actual spend against budget (if available)
   - Flag any deviations >5% or >5 days as significant

5. **Handle results**
   - If no deviations found:
     - Log "No schedule or budget deviations detected"
     - Complete command
   - If deviations found:
     - Proceed to step 6

6. **Generate deviation report**
   - Trigger `monitor-progress` skill with `report_type=deviations`
   - Include variance analysis and root cause summary

7. **Save report**
   - Save report to `reports/deviation-report-{YYYY-MM-DD}.md`

8. **Notify PM and stakeholders**
   - Read `references/email-autonomy-rules.md` for autonomy level 2 rules
   - Send email to PM with deviations summary
   - CC key stakeholders identified in project charter
   - Include: deviation summary, impact assessment, recommended actions
   - Use autonomy level 2 (send with stakeholders in CC, no approval required)

9. **Update project state**
   - Update `project-state.md` with:
     - Last deviation check timestamp
     - Current deviation status
     - Any escalations triggered
   - Log action in project audit trail
