# Project Manager — Cowork Plugin

[Русская версия](README.ru.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Claude Cowork](https://img.shields.io/badge/Platform-Claude%20Cowork-6B4FBB.svg)](https://claude.ai)

Plugin for full-cycle IT project management in Claude Cowork. Covers all 32 project management tasks across 6 phases — from initiation to closure. Based on PMBoK 8 + Agile hybrid methodology. Bilingual: English and Russian, auto-detected.

## Quick Start

1. Install the plugin in Claude Cowork
2. Select or create a project folder
3. Run `/init-project [project-name]`
4. Authorize MCP connectors when prompted (Jira, Gmail, Calendar)
5. Approve scheduled task permissions on first run

The plugin initializes the project folder structure and starts Phase 1 automatically.

## What It Does

- Generates 34 types of project documents: charters, plans, budgets, risk registers, protocols, checklists
- Monitors progress and detects schedule and budget deviations automatically
- Coordinates meetings and task assignments via integrations
- Sends email notifications with configurable autonomy levels (auto / CC PM / confirm)
- Runs scheduled checks: daily deviations, weekly status, risk register reviews
- Detects request language automatically — responds in English or Russian

## Skills (21)

| # | Skill | Purpose |
|---|-------|---------|
| 1 | `generate-charter` | Project charter from brief and stakeholder answers |
| 2 | `generate-risk-register` | Risk register (initial + periodic updates) |
| 3 | `generate-project-plan` | Project plan with WBS, milestones, Gantt |
| 4 | `generate-comm-plan` | Communication plan based on stakeholder map |
| 5 | `generate-meeting-protocol` | Meeting protocol from notes |
| 6 | `generate-plan-fact-report` | Plan vs actual comparison (.xlsx) |
| 7 | `generate-closure-report` | Project closure report with lessons learned |
| 8 | `generate-questionnaire` | Client brief or team lessons questionnaire |
| 9 | `generate-stakeholder-map` | Stakeholder analysis and influence map |
| 10 | `generate-estimate` | Timeline and budget estimation (.xlsx) |
| 11 | `generate-budget` | Detailed project budget (.xlsx) |
| 12 | `generate-resource-plan` | Resource allocation plan |
| 13 | `generate-checklist` | Launch / tech readiness / handover checklists |
| 14 | `generate-comparison-table` | Prototype comparison matrix (.xlsx) |
| 15 | `generate-change-impact` | Scope change impact analysis (.xlsx) |
| 16 | `generate-response-plan` | Incident response plan |
| 17 | `generate-approval-letter` | Approval request letter + email |
| 18 | `coordinate-meeting` | Schedule meeting + agenda + protocol template |
| 19 | `monitor-progress` | Progress / deviation / sync / actuals reports |
| 20 | `coordinate-executors` | Task assignment + deadline reminders |
| 21 | `send-email` | Cross-cutting email service (3 autonomy levels) |

## Commands (8)

| Command | Purpose |
|---------|---------|
| `/init-project` | Initialize new project: folders, state, scheduled tasks, Phase 1 chain |
| `/status` | Current project status and next available steps |
| `/next-step` | Recommend next action based on dependency map |
| `/sprint-report` | Weekly sprint progress report |
| `/deviation-check` | Check for schedule and budget deviations |
| `/risk-update` | Review and update risk register |
| `/sync-check` | Cross-stream synchronization report (Phase 5) |
| `/remind-executors` | Send reminders for overdue tasks |

## MCP Integrations

| Server | Purpose |
|--------|---------|
| Atlassian (Jira) | Task management: create, read, update, search |
| Gmail | Email: search, read, create drafts |
| Google Calendar | Events: create, read, search |

All integrations are optional — the plugin works without them by generating file-based artifacts with manual instructions.

## Project Structure

The plugin creates and manages this folder structure:

```
{project-name}/
├── CLAUDE.md                  # Agent instructions (auto-generated)
├── project-state.md           # Artifact status registry
├── 01-initiation/             # Phase 1 artifacts
├── 02-planning/               # Phase 2 artifacts
├── 03-execution/              # Phases 3-5 artifacts
├── 04-closure/                # Phase 6 artifacts
├── meetings/                  # Agendas and protocols
├── reports/                   # Scheduled and periodic reports
├── input/                     # User-provided data (read-only)
├── logs/log.md                # Agent action log
└── archive/                   # Created at project closure
```

## Scheduled Tasks

| Task | Schedule | Phases | Purpose |
|------|----------|--------|---------|
| `weekly-status` | Mon 9:00 | 3–5 | Weekly progress report |
| `daily-deviation` | Mon–Fri 9:00 | 3–5 | Schedule/budget deviation check |
| `risk-update` | Mon 9:00 (per sprint) | 2–5 | Risk register review |
| `sync-streams` | Mon 9:00 | 5 | Cross-stream sync report |
| `executor-reminders` | Mon–Fri 10:00 | 3–5 | Overdue task reminders |

All scheduled tasks are also available as slash commands for manual execution.

## References

| File | Purpose |
|------|---------|
| `orchestration-map.md` | Skill dependency map across 6 phases |
| `agent-rules.md` | Autonomy modes (A/B/C) and boundaries |
| `email-autonomy-rules.md` | Email sending levels (1: auto, 2: CC PM, 3: confirm) |
| `project-structure.md` | Managed project folder template |

## Customization

This plugin uses `~~placeholder` syntax for external tools. See `CONNECTORS.md` for details on replacing default integrations (e.g., Linear instead of Jira, Outlook instead of Gmail).

## License

MIT

---

**Keywords:** Claude Cowork plugin, AI project manager, IT project management automation, PMBoK 8 AI agent, project charter generator, risk register automation, agile project documentation, automated project reporting, project management AI tool, Claude AI agent
