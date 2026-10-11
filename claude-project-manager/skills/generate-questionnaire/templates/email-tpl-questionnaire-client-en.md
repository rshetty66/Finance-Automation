---
Template: email-tpl-questionnaire-client
Type: Instruction for send-email / agent
Task: #1
Level: 3 (with confirmation — agent shows draft, human confirms before sending)
Attachment: questionnaire-client.md → convert to .docx before sending
---

# Instruction: Client Questionnaire Email

## Send Parameters

| Parameter | Value |
|-----------|-------|
| Recipient | `{{recipient_email}}` |
| CC | `{{pm_email}}` |
| Subject | Project {{project_name}} — Requirements Questionnaire |
| Attachment | `questionnaire-client.docx` |
| Autonomy level | 3 — show draft to human, send only after confirmation |

## Email Body

---

Subject: Project {{project_name}} — Requirements Questionnaire

Dear {{recipient_name}},

Please find attached a requirements questionnaire for project **{{project_name}}**.

Your responses will help us accurately capture the project goals, expectations, and constraints — and will serve as the foundation for the project charter. This should take approximately 15–20 minutes.

Please complete the attached questionnaire and send your responses by replying to this email or in any format convenient for you by **{{deadline}}**.

Feel free to reach out with any questions.

Best regards,
{{pm_name}}
{{pm_title}}

---

## Agent Instructions

1. Verify that `questionnaire-client.md` exists and metadata is filled.
2. Convert `questionnaire-client.md` → `questionnaire-client.docx` (via send-email).
3. Substitute values in the email body: `{{recipient_name}}`, `{{project_name}}`, `{{pm_name}}`, `{{pm_title}}`, `{{deadline}}`.
4. Show the email draft to the human.
5. Wait for confirmation.
6. After confirmation — send via Gmail MCP.
7. Log in `logs/log.md`: send date, recipient.
