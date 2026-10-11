# Email Template E6 — Deadline Reminder (EN)
# Skill: coordinate-executors | Autonomy level: 1 (auto-send)
# Usage: one email per executor; populate all {PLACEHOLDERS} before sending

---

**To:** {EXECUTOR_EMAIL}
**Subject:** [{PROJECT_NAME}] Deadline Reminder — Action Required

---

Hi {EXECUTOR_NAME},

This is an automated reminder from your Project Manager regarding tasks assigned to you in **{PROJECT_NAME}** with upcoming or overdue deadlines.

---

{IF OVERDUE_TASKS}
## Overdue Tasks

The following tasks have passed their due date. Please update their status in {~~project tracker} or contact {PM_NAME} immediately if you need support.

| Task | Due Date | Days Overdue |
|------|----------|:------------:|
{OVERDUE_TASKS}

{/IF}

{IF UPCOMING_TASKS}
## Upcoming Deadlines

The following tasks are due within the next {REMINDER_HORIZON_DAYS} business days. Please ensure they are on track.

| Task | Due Date | Days Remaining |
|------|----------|:--------------:|
{UPCOMING_TASKS}

{/IF}

---

**What to do:**
1. Update task status in {~~project tracker} to reflect current progress.
2. If a deadline cannot be met — notify {PM_NAME} as soon as possible so we can adjust the plan.
3. If you have already completed a task — mark it as Done in {~~project tracker}.

If you have any questions or blockers, reply to this email or contact {PM_NAME} directly.

Thank you for keeping the project on track.

Best regards,
{PM_NAME}
Project Manager | {PROJECT_NAME}

---
*This message was sent automatically by the AI Project Manager agent.*
*To stop receiving these reminders, contact {PM_NAME}.*
