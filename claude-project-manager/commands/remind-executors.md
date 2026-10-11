---
description: Send reminders for overdue tasks to executors
---

# Remind Executors Command

## Purpose
Identify overdue tasks and send timely reminders to responsible executors. Maintains task momentum and escalation awareness during execution phases (3-5).

## Steps

1. **Verify project state**
   - Read `project-state.md`
   - Confirm project is in phase 3, 4, or 5
   - If not in these phases, inform user this command requires active execution phase and exit

2. **Query overdue tasks**
   - Query ~~project tracker for tasks where:
     - Deadline has passed (status_date > due_date)
     - Task status is NOT completed/closed
   - Retrieve task details: title, due date, executor, priority, impact
   - Sort by due date (most overdue first)

3. **Check for overdue tasks**
   - If no overdue tasks found:
     - Log "No overdue tasks detected"
     - Complete command
   - If overdue tasks exist:
     - Proceed to step 4

4. **Group by executor**
   - Group overdue tasks by assigned executor (owner)
   - For each executor, compile:
     - List of overdue tasks (title, due date, days overdue)
     - Task priorities and impact
     - Summary count

5. **Prepare reminders**
   - For each executor with overdue tasks:
     - Trigger `coordinate-executors` skill with:
       - Executor name/contact
       - Overdue task list
       - Request executor to prioritize completion or provide status update
     - Skill will format reminder message appropriate to executor role

6. **Send reminders via email**
   - Read `references/email-autonomy-rules.md` for autonomy level 1 rules
   - For each executor reminder:
     - Send email to executor
     - Include: overdue task summary, due dates, impact assessment
     - Use autonomy level 1 (send automatically, no approval required)
   - CC project manager for visibility

7. **Log all sent reminders**
   - Create reminder log entry with:
     - Executor names
     - Number of overdue tasks per executor
     - Timestamp of reminder send
     - Task references

8. **Update project state**
   - Update `project-state.md` with:
     - Last reminder check timestamp
     - Number of overdue tasks as of check date
     - Executors notified
   - Log action in project audit trail
