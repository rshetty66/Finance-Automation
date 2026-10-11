---
description: Initialize a new project with folder structure and scheduled tasks
argument-hint: [project-name]
---

# Initialize Project

Create a complete project scaffold with folder structure, configuration files, and automated scheduled tasks.

## Input

- **project-name** (required): Name of the project
- **project-description** (optional): Brief description of what the project is about
- **starting-phase** (optional): Which phase to start in (1-5, default: 1)

## Process

### 1. Gather Project Information

Ask the user for:
- Project name (if not provided in argument)
- Brief description of the project scope and goals
- Starting phase (default to Phase 1 if not specified)
- Confirm phase details before proceeding

### 2. Read Project Structure Template

Read `references/project-structure.md` to understand the folder layout and file structure.

### 3. Create Folder Structure

Create the following directory structure in `${project-root}/`:

```
project-name/
├── 01-initiation/
├── 02-planning/
├── 03-execution/
├── 04-closure/
├── meetings/
├── reports/
├── input/
└── logs/
```

Create subdirectories as specified in project-structure.md reference.

### 4. Generate CLAUDE.md

Create `${project-root}/CLAUDE.md` with:

```markdown
---
role: AI Project Manager Agent
project-name: [USER PROVIDED NAME]
project-description: [USER PROVIDED DESCRIPTION]
current-phase: [STARTING PHASE]
---

# Project Configuration

## References
- Orchestration Map: references/orchestration-map.md
- Agent Rules: references/agent-rules.md
- Email Autonomy Rules: references/email-autonomy-rules.md

## Orchestration Rules

After each skill execution:
1. Update project-state.md with artifact status and metadata
2. Check dependencies against orchestration-map.md
3. Identify blocked vs. available next steps
4. Suggest next step to user
5. Log action in logs/log.md with timestamp, artifact, status

## File Structure Rules

- Input data: Place in input/ folder (read-only)
- Generated artifacts: Place in numbered phase folders (01-, 02-, etc.)
- Meeting notes: Place in meetings/ folder
- Reports: Place in reports/ folder
- Logs: Append to logs/log.md

## Logging Rules

Every action logged as:
```
[TIMESTAMP] | [ARTIFACT] | [STATUS] | [NOTES]
```

## Constraints

- Do NOT modify files in input/ folder
- Do NOT make decisions that require user approval without asking
- Email autonomy levels defined in email-autonomy-rules.md
- Respect project dependencies in orchestration-map.md
```

### 5. Initialize project-state.md

Create `${project-root}/project-state.md` with the artifact status table below.
The full list of 34 artifacts and their dependencies is defined in `references/orchestration-map.md` — consult it for the authoritative source if the table below is updated.

```markdown
---
project-name: [NAME]
phase: [STARTING PHASE]
last-updated: [TIMESTAMP]
---

# Project State Tracking

## Artifact Status Overview

| Artifact ID | Artifact Name | Status | Phase | Notes |
|---|---|---|---|---|
| 1 | Project Questionnaire | not started | 1 | |
| 2 | Project Charter | not started | 1 | depends on #1 |
| 3 | Risk Register | not started | 1 | depends on #2 |
| 4 | Stakeholder Matrix | not started | 2 | depends on #2 |
| 5 | Communication Plan | not started | 2 | depends on #4 |
| ... | ... | not started | ... | |

[Complete 34-artifact list with all statuses initialized to "not started"]
```

### 6. Initialize logs/log.md

Create `${project-root}/logs/log.md` with header:

```markdown
# Project Log

[TIMESTAMP] | PROJECT INIT | in_progress | Initializing project [NAME]
```

### 7. Create Scheduled Tasks

Read `references/scheduled-task-prompts.md` to get full prompt templates for each scheduled task.

Substitute `{project-name}` in each prompt with the actual project name provided by the user.

Create 5 scheduled tasks using the schedule skill. Each task must include the full `prompt` from the reference file:

1. **weekly-status** — `0 9 * * 1` (Monday 9:00 AM)
   - Description: Generate weekly status report for project
   - Prompt: full text from `scheduled-task-prompts.md` § weekly-status, with `{project-name}` substituted
   - enabled: false, notifyOnCompletion: true

2. **daily-deviation** — `0 9 * * 1-5` (Monday–Friday 9:00 AM)
   - Description: Check project deviations and risks
   - Prompt: full text from `scheduled-task-prompts.md` § daily-deviation, with `{project-name}` substituted
   - enabled: false, notifyOnCompletion: true

3. **risk-update** — `0 9 * * 1` (Monday 9:00 AM, biweekly logic in prompt)
   - Description: Review and update risk register
   - Prompt: full text from `scheduled-task-prompts.md` § risk-update, with `{project-name}` substituted
   - enabled: false, notifyOnCompletion: true

4. **sync-streams** — `0 9 * * 1` (Monday 9:00 AM)
   - Description: Synchronize all project streams and statuses
   - Prompt: full text from `scheduled-task-prompts.md` § sync-streams, with `{project-name}` substituted
   - enabled: false, notifyOnCompletion: true

5. **executor-reminders** — `0 10 * * 1-5` (Monday–Friday 10:00 AM)
   - Description: Send overdue task reminders to executors
   - Prompt: full text from `scheduled-task-prompts.md` § executor-reminders, with `{project-name}` substituted
   - enabled: false, notifyOnCompletion: true

Store task definitions summary in `config/scheduled-tasks.md`.

### 8. Activate Phase-Appropriate Tasks

All 5 tasks are created in disabled state (step 7). Activate based on starting phase per architecture §4.4.3:

| Starting Phase | Tasks to Activate |
|---|---|
| Phase 1 — Initiation | None (all remain disabled) |
| Phase 2 — Planning | `risk-update` |
| Phase 3 — Prototyping | `weekly-status`, `daily-deviation`, `risk-update`, `executor-reminders` |
| Phase 4 — Development | `weekly-status`, `daily-deviation`, `risk-update`, `executor-reminders` |
| Phase 5 — Launch | All five: `weekly-status`, `daily-deviation`, `risk-update`, `sync-streams`, `executor-reminders` |

For each activated task: run once manually ("Run now") to pre-approve file access and MCP permissions — prevents permission prompts on automated runs.

Note: `sync-streams` is only active in Phase 5. Do not activate it in earlier phases.

### 9. Start Phase 1 Chain (if starting Phase 1)

Execute in sequence:
1. Trigger `generate-questionnaire` skill
2. Wait for user review and approval
3. Trigger `generate-charter` skill
4. Wait for user review and approval
5. Trigger `generate-risk-register` skill

## Completion

Log final initialization status:
```
[TIMESTAMP] | PROJECT INIT | completed | Project [NAME] initialized at Phase [PHASE]
```

Display summary to user:
- Folder structure created
- Configuration files generated
- Scheduled tasks created (X enabled, Y disabled)
- Phase 1 chain started (if applicable)
- Next steps recommended
