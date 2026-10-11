# Email Template: Plan Approval Request (E3) — EN

<!-- Agent instruction: this file is used by the send-email skill to send via Gmail.
     Fill all placeholders with actual data. Remove comments before passing to send-email. -->

---

## Email Metadata

**To:**
[[List: Approver Name <email@domain.com> — one per line, from stakeholder-map.md]]

**CC:**
[[Project Sponsor <email>, if found in project-charter.md; otherwise leave blank]]

**Subject:** [[Project Name]] — Request for Plan Approval

**Attachments:**
- `02-planning/project-plan.docx` (convert from project-plan.md)
[[- `02-planning/project-budget.xlsx` — only if file is available]]
[[- `02-planning/resource-plan.docx` (convert from resource-plan.md) — only if file is available]]

**Autonomy level:** 3 — send only after explicit PM confirmation

---

## Email Body

[[Insert full content of approval-letter.md without changes]]

---

<!-- Instructions for send-email:
  1. Verify all attachment files exist and are accessible.
  2. Convert .md → .docx for project-plan.md and resource-plan.md.
  3. Show PM the final email with recipients and attachments for review.
  4. Wait for explicit confirmation: "Send it" / "Confirmed" / "Go ahead".
  5. Send via Gmail MCP.
  6. If Gmail unavailable: save draft, notify PM with manual send instructions.
-->
