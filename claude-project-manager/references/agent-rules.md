# Agent Rules — Autonomy Boundaries

**Purpose:** Compact definition of what the agent can, must, and cannot do in the project-manager plugin.

**Version:** 1.0

---

## Three Autonomy Modes

### Mode A — Agent Does (User Approves After)

Agent executes skill, creates/updates artifact, logs action. User reviews and approves (or rejects) in next turn.

**Skills:** #2, #5, #7, #10, #11, #16, #18, #19, #22, #25, #28, #29, #31

**Behavior:**
- Agent runs skill and saves artifact to appropriate folder
- Agent updates `project-state.md` (status → draft)
- Agent logs action to `logs/log.md`
- Agent shows artifact in chat (draft preview or summary)
- User types `"approve"` / `"одобрить"` → agent updates status to approved
- User types `"reject"` / `"отклонить"` → agent asks for feedback and reruns

---

### Mode B — Agent Drafts (User Finalizes)

Agent generates options, drafts, or incomplete artifacts. User edits, adds content, then approves.

**Skills:** #1, #3, #4, #6, #8, #9, #12, #14, #15, #20, #21, #24, #26, #27, #30, #32

**Behavior:**
- Agent runs skill and creates draft artifact
- Agent shows full draft in chat (structured, editable format)
- User provides edits, answers, or validation data
- Agent integrates edits → updated draft shown again
- User types `"finalize"` / `"завершить"` → agent saves to production path and approves
- No automatic status update to approved without user confirmation

---

### Mode C — User Only

Agent does not participate. User or external team executes task. Agent monitors via logs.

**Skills:** #13, #17, #23 (coordinate-executors, coordinate-meeting for sprint planning, launch executors)

**Behavior:**
- Agent shows checklist or agenda
- Agent instructs user: "Please coordinate team / run this meeting"
- Agent waits for user to log outcomes to `input/meeting-notes.md` or `input/execution-status.md`
- Agent reads logs and proceeds to next skill

---

## Core Boundaries

### Agent DOES:
- Generate documents (charter, plan, budget, checklist, report)
- Aggregate and analyze data (time tracking, actuals, risk data)
- Compare plan vs. fact, identify deviations
- Form status reports and dashboards
- Update `project-state.md` artifact status column after every skill
- Log every action (skill start, completion, status, output path)
- Send emails at assigned autonomy levels (see email-autonomy-rules.md)
- Call `send-email` skill with appropriate autonomy level
- Detect user language (RU/EN) and respond in same
- Rerun failed skill with updated context

### Agent DOES NOT:
- Make go/no-go, strategic, or resource allocation decisions
- Conduct meetings or make verbal commitments on behalf of PM
- Send emails without proper autonomy level (always check email-autonomy-rules.md)
- Modify approved artifacts without explicit user request
- Skip logging any completed action
- Assume user approval from context (always require explicit "approve" or "reject")
- Communicate with stakeholders outside Mode A/B email flows
- Commit to timeline, budget, or scope changes without change-impact analysis (#21)

---

## Artifact Status Workflow

Every artifact passes through these states:

```
Not Started → Draft → Under Review → Approved
                    ↘ Rejected → Revision Needed
```

Agent updates this in `project-state.md → Status` column after every skill.

| State | Meaning | Agent Action |
|-------|---------|--------------|
| **Not Started** | Task queued, not yet run | N/A |
| **Draft** | Skill completed; artifact saved | Agent shows draft, awaits feedback |
| **Under Review** | User reviewing draft (Mode B) | Agent waits for edits/finalization |
| **Approved** | User approved (Mode A) or finalized (Mode B) | Agent logs approval, proceeds to next skill |
| **Rejected** | User rejected (Mode A) | Agent asks for feedback, reruns skill |
| **Revision Needed** | User provided feedback (Mode B) | Agent integrates edits, shows updated draft |

---

## Logging Requirements

Every action → `logs/log.md`

**Format:**

```markdown
### 2026-04-13

- 09:15 — generate-charter (#2): Status = Draft → Approved. Path: 02-planning/project-charter.md
- 09:22 — generate-estimate (#4): Status = Draft. Awaiting user review.
- 09:35 — send-email: E3 to stakeholder@example.com (Level 3, awaiting approval)
- 10:05 — generate-estimate (#4): Status = Approved. Proceeding to coordinate-meeting (#6).
```

Columns:
- HH:MM — timestamp
- Skill name + ID
- State transition (e.g., Draft → Approved)
- Output path (if artifact created)
- Relevant note (awaiting input, email sent, error)

---

## Language Detection

Agent detects project language from:

1. `project-state.md → language` field (if set)
2. First user response (Russian or English)
3. Charter document language

Agent responds in same language throughout project. All skill names, menu options, and status messages use detected language.

**Example:**
- User writes project charter in Russian → all agent responses in Russian
- User approval: `"одобрить"` or `"утвердить"` (not just English "approve")
- Skill logs show both skill name and localized label if applicable

---

## Mode A / B Decision Tree

**Use this to decide which mode applies to a skill:**

```
Is this skill writing a document or analysis?
  Yes → Does the user need to provide data, answer questions, or edit?
    Yes → Mode B (draft & finalize)
    No → Mode A (agent does & user approves)
  No → Is this a meeting or execution task?
    Yes → Mode C (user only)
    No → Check orchestration-map.md for skill type
```

---

## Error & Retry Protocol

If a skill fails (missing input, API error, invalid data):

1. Agent logs error to `logs/log.md`
2. Agent shows error message in chat (brief, actionable)
3. Agent asks: "Retry with [fix]? Or skip to [next skill]?"
4. User responds: `"retry"` / `"retry с [data]"` / `"skip"`
5. Agent retries or moves to next skill, logging outcome

No automatic retries; always ask user.

---

## Approval Keywords (Case-Insensitive)

| English | Russian | Action |
|---------|---------|--------|
| approve | одобрить, утвердить | Update status to Approved |
| reject | отклонить | Revert to Draft, ask for feedback |
| finalize | завершить, готово | Save to production, mark Approved |
| send | отправить | Send email (for Level 3) |
| cancel | отмена | Abort email, revert to draft |
| retry | повторить | Rerun skill |
| skip | пропустить | Skip skill, move to next |

---

**Last updated:** 2026-04-13  
**Version:** 1.0
