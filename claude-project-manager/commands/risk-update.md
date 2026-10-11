---
description: Review and update the project risk register
---

# Risk Update Command

## Purpose
Periodically review and update the project risk register based on current project state, recent deviation data, and meeting discussions. Maintain risk mitigation strategies as project progresses.

## Steps

1. **Determine current phase**
   - Read `project-state.md`
   - Confirm phase for context (risk register updates are active across all phases)

2. **Retrieve current risk register**
   - Read `01-initiation/risk-register.md`
   - Note current version and last update date

3. **Gather recent evidence**
   - Read all deviation reports in `reports/` (most recent first, up to last 30 days)
   - Read all meeting protocols in `meetings/` (most recent first, up to last 3 meetings)
   - Identify emerging risks and risk status changes

4. **Trigger risk generation in update mode**
   - Call `generate-risk-register` skill with:
     - `mode=update` (not initial)
     - Current risk register version
     - Recent deviation report summaries
     - Key discussion items from meetings
   - Skill will review existing risks and recommend updates/additions

5. **Present draft to user**
   - Display updated risk register as draft
   - Highlight changes from previous version (new risks, closed risks, updated priorities)
   - Show risk scoring changes
   - Include mitigation strategy updates

6. **Wait for user approval**
   - Request user review and approval of draft
   - Allow user to comment or request modifications
   - Do not proceed without explicit approval

7. **Save updated register**
   - After approval, save updated register to `01-initiation/risk-register.md`
   - Preserve version history (update version number incrementally)

8. **Update project state**
   - Update `project-state.md` with:
     - Last risk review timestamp
     - Risk register version
     - Number of active risks by priority
   - Log action in project audit trail
