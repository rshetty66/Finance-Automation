# Email Template E4 — Schedule Deviation Notification

**Autonomy level:** 2 (draft — PM reviews and confirms before sending via send-email)
**Used in:** monitor-progress, deviation-check mode, Task #19

---

## Recipients

**To:** {PM_NAME} — Project Manager
**CC:** {STAKEHOLDERS — from stakeholder-map.md, role: sponsor/key stakeholder}
**Subject:** [{PROJECT_NAME}] Schedule deviation alert — Sprint {SPRINT_NUMBER}

---

## Email Body

Hi {RECIPIENT_NAME},

This is an automated status update for project **{PROJECT_NAME}**.

**Deviation detected — Sprint {SPRINT_NUMBER}**

| Severity | {CRITICAL / MODERATE / MINOR} |
|----------|-------------------------------|
| Overdue tasks | {OVERDUE_COUNT} |
| Max delay | {MAX_DELAY_DAYS} days |
| Budget deviation | {BUDGET_DEVIATION_PERCENT}% |

**Overdue tasks:**
{LIST_OF_OVERDUE_TASKS}
- {TASK_NAME} — {ASSIGNEE}, delayed by {N} days (due: {ORIGINAL_DUE_DATE})

**Impact assessment:**
{IMPACT_DESCRIPTION — which milestones are at risk, what is unblocked by resolving this}

**Recommended actions:**
1. {RECOMMENDED_ACTION_1}
2. {RECOMMENDED_ACTION_2}

Full deviation report: `reports/deviation-report-{DATE}.md`

Please review and confirm whether you'd like me to send additional notifications to task owners.

Best regards,
AI Project Manager | {PROJECT_NAME}

---

## Agent Instructions

- Populate all `{}` placeholders from deviation-report-{date}.md
- Recipients: PM always in To; sponsors/key stakeholders in CC per stakeholder-map.md
- Do NOT send until PM confirms — this is Level 2 (draft)
- Save draft as: `reports/email-draft-deviation-{DATE}.md`
- Notify PM in chat: "Deviation email draft ready — review at reports/email-draft-deviation-{DATE}.md"
