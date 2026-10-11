# Email Template E7 — Weekly Status Distribution

**Autonomy level:** 1 (autonomous — sent without PM confirmation)
**Used in:** monitor-progress, weekly-status mode (Scheduled Task Р1)

---

## Recipients

**To:** {STAKEHOLDERS — from comm-plan.md, weekly status distribution list}
**CC:** {PM_NAME} — Project Manager
**Subject:** [{PROJECT_NAME}] Weekly Status — Sprint {SPRINT_NUMBER}, Week {WEEK_NUMBER}

---

## Email Body

Hi {RECIPIENT_NAME},

Please find the weekly project status update for **{PROJECT_NAME}**.

**Overall status: {GREEN — On track / YELLOW — At risk / RED — Critical issues}**

**Sprint {SPRINT_NUMBER} progress:**
- Completion: {COMPLETION_PERCENT}% ({TASKS_COMPLETED}/{TASKS_PLANNED} tasks)
- Velocity: {VELOCITY} story points
- Schedule status: {ON TRACK / MINOR DELAYS / DELAYED — {MAX_DELAY_DAYS} days}
- Budget status: {ON TRACK / MINOR OVERRUN / OVER BUDGET — {DEVIATION_PERCENT}%}

**This week's highlights:**
- {ACHIEVEMENT_1}
- {ACHIEVEMENT_2}

**Key issues / Blockers:**
{KEY_ISSUES or "No critical issues this week."}
- {ISSUE_DESCRIPTION} — Owner: {OWNER}

**Next sprint focus:**
- {NEXT_FOCUS_1}
- {NEXT_FOCUS_2}

**Next milestone:** {MILESTONE_NAME} — {MILESTONE_DATE}

Full weekly report: `reports/weekly-status-{DATE}.md`

Best regards,
AI Project Manager | {PROJECT_NAME}

*This status update is generated automatically every Monday at 9:00 AM.*
*To unsubscribe or change frequency, contact {PM_EMAIL}.*

---

## Agent Instructions

- Populate all `{}` from weekly-status-{date}.md
- Recipients: per weekly distribution list in comm-plan.md (or stakeholder-map.md if comm-plan unavailable)
- PM always in CC
- Level 1 — send autonomously via send-email WITHOUT PM confirmation
- Attachment: convert weekly-status-{date}.md → .docx, attach to email
- Log in logs/log.md: "{DATE}: email E7 sent — weekly status Sprint {SPRINT_NUMBER}"
