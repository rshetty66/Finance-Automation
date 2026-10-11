---
Template: email-tpl-questionnaire-lessons
Type: Instruction for send-email / agent
Task: #30
Level: 2 (copy to human — agent sends, PM in CC)
Attachment: questionnaire-lessons.md → send as .md
---

# Instruction: Lessons Learned Questionnaire Email

## Send Parameters

| Parameter | Value |
|-----------|-------|
| Recipients | `{{recipient_emails}}` (comma-separated list) |
| CC | `{{pm_email}}` |
| Subject | Lessons Learned Questionnaire — Project {{project_name}} |
| Attachment | `questionnaire-lessons.md` |
| Autonomy level | 2 — agent sends, PM automatically in CC |

## Email Body

---

Subject: Lessons Learned Questionnaire — Project {{project_name}}

Team,

Project **{{project_name}}** has been completed. Please take 15–20 minutes to fill in the attached questionnaire.

Your input will help us improve future projects — better processes, communication, and technical approaches.

Please submit your responses by **{{deadline}}**. Any format is fine — you can fill in the attached file or reply by email.

Thank you for your contribution to the project.

{{pm_name}}

---

## Agent Instructions

1. Retrieve the list of recipients from the managed project's CLAUDE.md (team section).
2. Verify that `questionnaire-lessons.md` has been created.
3. Substitute values in the email body: `{{project_name}}`, `{{pm_name}}`, `{{deadline}}`, `{{recipient_emails}}`.
4. Add `{{pm_email}}` to CC.
5. Send via Gmail MCP (level 2 — no confirmation required, but PM is in CC).
6. Log in `logs/log.md`: send date, recipient list.
