---
description: Synchronize and report on parallel workstreams (Phase 5)
---

# Sync Check Command

## Purpose
Review cross-stream dependencies and synchronization status in Phase 5. Identify cross-workstream blockers, dependency conflicts, and synchronization issues between dev, marketing, and ops streams.

## Steps

1. **Verify phase 5 status**
   - Read `project-state.md`
   - Check `phase` field
   - If not phase 5:
     - Inform user: "Sync check is only available in Phase 5 (execution wind-down)"
     - Do not proceed
   - If phase 5, continue

2. **Query cross-stream tasks**
   - Query ~~project tracker for all active tasks across workstreams:
     - Development (dev)
     - Marketing (marketing)
     - Operations (ops)
   - Retrieve task status, dependencies, and assigned executors
   - Identify tasks with cross-stream dependencies

3. **Analyze synchronization**
   - Map task dependencies across streams
   - Identify critical path items requiring cross-stream coordination
   - Detect blocked tasks awaiting completion from other streams
   - Note tasks on track vs at-risk

4. **Generate sync report**
   - Trigger `monitor-progress` skill with `report_type=sync`
   - Include:
     - Cross-stream dependency matrix
     - Blocker identification and impact
     - At-risk items requiring escalation
     - Recommended actions to unblock

5. **Save report**
   - Save report to `reports/sync-report-{YYYY-MM-DD}.md`
   - Include timestamp and phase confirmation

6. **Highlight critical blockers**
   - Extract high-impact cross-stream blockers
   - For each blocker:
     - Show affected workstreams
     - Show impact (tasks/timeline affected)
     - Show recommended resolution path

7. **Update project state**
   - Update `project-state.md` with:
     - Last sync check timestamp
     - Number of active cross-stream blockers
     - Critical path status
   - Log action in project audit trail
