# Email Autonomy Rules

**Version:** 1.0  
**Location in plugin:** `references/email-autonomy-rules.md`  
**Used by:** generate-questionnaire, generate-approval-letter, monitor-progress, coordinate-meeting, coordinate-executors

---

## Purpose

This reference defines the three autonomy levels for email delivery in the project-manager plugin. Skills that send emails use this file to determine the correct level without loading the full `send-email` SKILL.md.

---

## Autonomy Levels

### Level 1 — Send Automatically

Send without showing the draft or asking for PM confirmation.

**When to use:** Routine, time-sensitive, low-risk emails to known internal recipients.

**Email types:** E6 (deadline reminders), E7 (weekly status reports)

**Behavior:**
- Email is sent immediately via Gmail MCP
- PM sees only a one-line log notification in chat
- No draft file is created

---

### Level 2 — Send with PM Copy

Send automatically and add the PM to CC.

**When to use:** Alerts to stakeholders that the PM should be aware of, but not need to approve individually.

**Email types:** E4 (deadline deviation alert), E5 (stream sync deviation alert)

**Behavior:**
- Email sent to recipient(s) with PM added to CC
- PM email sourced from `cc_pm` parameter or `project-state.md → pm_email`
- No confirmation required; PM sees a chat notification

---

### Level 3 — Confirm Before Sending

Show a full draft in chat and wait for PM approval.

**When to use:** Important outbound communications — client-facing, approval-requiring, or high-visibility.

**Email types:** E1 (client questionnaire), E2 (team questionnaire), E3 (document approval), E8 (meeting status)

**Behavior:**
- Draft saved to `drafts/email-draft-{type}-{date}.md`
- Full preview shown in chat (To, Subject, Attachments, body)
- PM must type: `"send"` / `"отправить"` / `"confirm"` / `"подтвердить"`
- PM may provide edits — draft is updated and shown again
- `"cancel"` / `"отмена"` aborts without sending

---

## Level Assignment Table

| Email Type | Recipient | Level | Auto-send |
|-----------|----------|-------|-----------|
| E1 | External client | 3 | No |
| E2 | Internal team | 2 | Yes + CC PM |
| E3 | External stakeholder | 3 | No |
| E4 | External stakeholder | 2 | Yes + CC PM |
| E5 | External stakeholder | 2 | Yes + CC PM |
| E6 | Internal executor | 1 | Yes |
| E7 | External stakeholders | 1 | Yes |
| E8 | External stakeholders | 3 | No |

---

## Fallback Rule (Gmail Unavailable)

Regardless of level: if Gmail MCP is unavailable, save draft to `drafts/email-draft-{type}-{date}.md` and notify PM. Do not retry automatically.

---

**Last updated:** 2026-04-13  
**Version:** 1.0
