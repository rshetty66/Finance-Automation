# Email Template E5 — Stream Desynchronization Notification

**Autonomy level:** 2 (draft — PM reviews and confirms before sending via send-email)
**Used in:** monitor-progress, sync-streams mode, Task #25

---

## Recipients

**To:** {PM_NAME} — Project Manager; {DEV_LEAD}; {MARKETING_LEAD}; {OPS_LEAD}
**CC:** {SPONSOR — from stakeholder-map.md}
**Subject:** [{PROJECT_NAME}] Stream sync alert — Launch phase update

---

## Email Body

Hi team,

Automated stream synchronization report for project **{PROJECT_NAME}** — Launch Phase.

**Current sync status: {IN SYNC / MINOR DESYNC / CRITICAL DESYNC}**

| Stream | Status | Key issue |
|--------|--------|-----------|
| Development | 🟢/🟡/🔴 {STATUS} | {KEY_ISSUE or "None"} |
| Marketing | 🟢/🟡/🔴 {STATUS} | {KEY_ISSUE or "None"} |
| Operations | 🟢/🟡/🔴 {STATUS} | {KEY_ISSUE or "None"} |

**Cross-stream dependency issues:**
{DEPENDENCY_ISSUES — list of blocking cross-stream dependencies}
- {DEPENDENCY_DESCRIPTION} — affects {STREAM}, resolution owner: {OWNER}

**Required actions before next sync check:**
| Action | Owner | Deadline |
|--------|-------|----------|
| {ACTION_1} | {OWNER} | {DATE} |
| {ACTION_2} | {OWNER} | {DATE} |

Full sync report: `reports/sync-report-{DATE}.md`

Please confirm your stream updates are reflected correctly and flag any corrections.

Best regards,
AI Project Manager | {PROJECT_NAME}

---

## Agent Instructions

- Populate all `{}` from sync-report-{date}.md
- Recipients: PM + all stream leads in To; sponsor in CC per stakeholder-map.md
- Do NOT send until PM confirms — Level 2 (draft)
- Save draft as: `reports/email-draft-sync-{DATE}.md`
- Notify PM in chat: "Stream sync email draft ready — review at reports/email-draft-sync-{DATE}.md"
