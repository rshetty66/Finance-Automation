---
description: Complete user guide for the Project Manager Cowork plugin — AI-powered IT project management automation through all 6 phases, 21 skills, and 8 slash commands. Step-by-step instructions for non-technical users.
keywords: Claude Cowork plugin, AI project manager, IT project management, PMBoK AI agent, project charter generator, risk register automation, automated project documentation, Cowork project management
---

# User Guide — Project Manager Plugin for Claude Cowork

[Русская версия](USER-GUIDE.ru.md)

**Project Manager** is an AI plugin for Claude Cowork that automates IT project management from start to finish. It covers all 32 project management tasks across 6 phases — generating documents, sending notifications, tracking progress, and coordinating team activity.

No special knowledge of project management software or AI tools is required.

---

## Table of Contents

1. [What This Plugin Does](#1-what-this-plugin-does)
2. [Core Concepts](#2-core-concepts)
3. [Starting a New Project](#3-starting-a-new-project)
4. [Phase 1 — Project Initiation](#4-phase-1--project-initiation)
5. [Phase 2 — Planning](#5-phase-2--planning)
6. [Phase 3 — Prototyping](#6-phase-3--prototyping)
7. [Phase 4 — Development](#7-phase-4--development)
8. [Phase 5 — Launch](#8-phase-5--launch)
9. [Phase 6 — Project Closure](#9-phase-6--project-closure)
10. [Slash Commands Reference](#10-slash-commands-reference)
11. [Email Notifications](#11-email-notifications)
12. [Scheduled Automatic Checks](#12-scheduled-automatic-checks)
13. [Working Without External Integrations](#13-working-without-external-integrations)
14. [Tips for Best Results](#14-tips-for-best-results)
15. [Frequently Asked Questions](#15-frequently-asked-questions)
16. [Glossary](#16-glossary)

---

## 1. What This Plugin Does

Managing an IT project means keeping track of dozens of documents, coordinating a team, monitoring deadlines and budgets, and staying on top of risks — simultaneously. This is time-consuming work that still leaves room for things to slip through the cracks.

The Project Manager plugin acts as your AI project management assistant inside Claude Cowork. You describe your project in plain language, and the plugin generates professional documents, sends notifications, checks for deviations, and guides you through each phase of the project lifecycle.

**What the plugin automates:**

- Generating project documents: charters, plans, budgets, risk registers, protocols, reports, checklists (34 document types)
- Sending email notifications to stakeholders and team members
- Monitoring schedule and budget deviations on a daily and weekly basis
- Running risk register reviews on a sprint-by-sprint schedule
- Coordinating meetings with agendas and protocol templates
- Tracking task completion and sending reminders to executors

**What the plugin does not do:**

- Make final decisions — the PM always reviews and approves documents
- Replace human judgment in complex situations
- Guarantee outcomes — it assists, not manages

---

## 2. Core Concepts

Before diving in, here are five key terms used throughout this guide:

**Skill** — a specialized capability of the plugin. Each skill handles one task: generating a charter, producing a budget, sending reminders, etc. Skills are activated by typing their name or describing what you need in plain language. There are 21 skills in total.

**Slash command** — a shortcut that starts with `/`. Commands like `/status`, `/init-project`, and `/sprint-report` trigger specific plugin actions immediately. There are 8 commands in total.

**Phase** — the plugin follows a 6-phase project lifecycle (Initiation → Planning → Prototyping → Development → Launch → Closure). Each phase has a set of documents and tasks associated with it.

**Artifact** — any document the plugin creates: a charter, a plan, a risk register, etc. Artifacts are saved as files in your project folder.

**Autonomy level** — how independently the plugin acts when sending emails. Level 1: sends automatically. Level 2: sends but copies you. Level 3: shows a draft and waits for your approval before sending.

---

## 3. Starting a New Project

### 3.1 Initialize the Project

Open a Cowork session and run:

```
/init-project [project-name]
```

**Example:**
```
/init-project mobile-app-relaunch
```

Use a short name with hyphens instead of spaces. Latin characters are recommended so the folder name works on all operating systems.

**What happens next:**

The plugin creates the following folder structure in your working directory:

```
mobile-app-relaunch/
├── CLAUDE.md                  ← Agent instructions (auto-generated, don't edit)
├── project-state.md           ← Tracks which artifacts have been created
├── 01-initiation/             ← Phase 1 documents
├── 02-planning/               ← Phase 2 documents
├── 03-execution/              ← Phases 3–5 documents
├── 04-closure/                ← Phase 6 documents
├── meetings/                  ← Meeting agendas and protocols
├── reports/                   ← Scheduled and periodic reports
├── input/                     ← Your source data (place files here)
└── logs/log.md                ← Agent action log
```

### 3.2 Place Your Source Data

Put any existing project documents in the `input/` folder:

- Client brief or requirements document
- Team member list with contacts
- Budget constraints or timeline expectations
- Any previous project data

The plugin reads from this folder but never modifies it.

### 3.3 Start Phase 1

After `/init-project` completes, the plugin will automatically suggest starting Phase 1. You can confirm by typing `yes` or `начнём`, or move straight to the first skill.

---

## 4. Phase 1 — Project Initiation

**Goal of this phase:** understand the project, define its scope, identify stakeholders, and get the first documents approved.

**Documents created in Phase 1:**
- Project Charter
- Stakeholder Map
- Preliminary Estimate (timeline + budget)
- Client Questionnaire (optional)

---

### 4.1 Send a Client Questionnaire

If you need to collect structured information from the client before starting, use this skill first.

**How to activate:**

```
Generate a client questionnaire for the mobile app relaunch project
```

or simply:

```
I need to send a questionnaire to the client
```

**What the plugin will ask you:**
- Project name and client name
- What type of questionnaire: client brief or team retrospective?
- Specific topics to include (optional)

**What you receive:**

A completed questionnaire document (`client-questionnaire.md`) saved to `01-initiation/`. You can send it to the client directly or copy the content into an email.

---

### 4.2 Generate the Project Charter

The charter is the founding document of the project. It defines the goal, scope, team, budget, timeline, and success criteria. Everything starts here.

**How to activate:**

```
Generate a project charter
```

**What the plugin will ask you:**

- Project name and description (what are you building?)
- Client or sponsor name
- Key goal — what should be achieved and by when?
- Scope: what is included, what is explicitly excluded?
- Team: key roles and responsible people
- Budget (approximate range)
- Main constraints or risks you already know about

**Tip:** you can paste the text from the client questionnaire responses here — the plugin will extract the relevant data automatically.

**What you receive:**

A `project-charter.md` file in `01-initiation/`. The plugin will show you a summary and ask for your approval. Once approved, it marks the charter as complete in `project-state.md` and unlocks dependent tasks.

---

### 4.3 Build the Stakeholder Map

The stakeholder map identifies everyone who has an interest in the project — their roles, level of influence, and how they should be communicated with.

**How to activate:**

```
Build a stakeholder map
```

**What the plugin will ask you:**

- List of people involved: names, roles, which organization they belong to
- For each person: their level of influence (High / Medium / Low) and interest in the project
- How they prefer to receive updates (email, meetings, reports)

**What you receive:**

A `stakeholder-map.md` file with an influence/interest matrix and a communication approach for each stakeholder group.

---

### 4.4 Create a Preliminary Estimate

Before committing to a full plan, get a rough estimate of timeline and budget based on the charter.

**How to activate:**

```
Create a preliminary estimate
```

**What the plugin will ask you:**

- Project type (new product, redesign, integration, internal tool?)
- Team composition and approximate size
- Any known deadlines or budget constraints

**What you receive:**

An `estimate.xlsx` file with timeline and budget ranges (optimistic / realistic / pessimistic), plus a brief methodology note explaining how the estimates were calculated.

---

## 5. Phase 2 — Planning

**Goal:** create a detailed, executable plan for the project. All Phase 2 documents depend on the approved charter.

**Documents created in Phase 2:**
- Project Plan (WBS, milestones, Gantt schedule)
- Detailed Budget
- Resource Allocation Plan
- Risk Register
- Communication Plan

---

### 5.1 Generate the Project Plan

**How to activate:**

```
Generate a project plan
```

**What the plugin will ask you:**

- Confirm the charter is approved (or paste key details if not)
- List of phases or major stages
- Key milestones and their target dates
- Team member availability (full-time / part-time)

**What you receive:**

A `project-plan.md` with WBS (Work Breakdown Structure — a structured list of tasks and deliverables), milestones, and a Gantt chart in text format. The plan uses a `WP-XXX` task numbering system, so any document can reference specific tasks by ID.

> Approving the project plan unlocks the Risk Register and Communication Plan.

---

### 5.2 Generate the Detailed Budget

**How to activate:**

```
Generate a project budget
```

**What the plugin will ask you:**

- Team roles and their rates (hourly or monthly)
- Duration per role per phase
- Additional cost categories: software licenses, infrastructure, contractors, contingency

**What you receive:**

A `project-budget.xlsx` with a phase-by-phase cost breakdown, totals, and a contingency reserve line. The budget links to WP task IDs from the project plan.

---

### 5.3 Create a Resource Allocation Plan

**How to activate:**

```
Create a resource allocation plan
```

**What the plugin will ask you:**

- Team member list with their roles
- Which project phases each person is involved in
- Workload percentage per phase (e.g., 50% in Phase 2, 80% in Phase 4)

**What you receive:**

A `resource-plan.md` with a visual allocation table showing who works on what, when, and at what capacity. Highlights potential overloads or gaps.

---

### 5.4 Generate the Risk Register

The risk register is a living document — it starts here in Phase 2 and gets updated throughout the project.

**How to activate:**

```
Generate a risk register
```

**What the plugin will ask you (Phase 2 mode):**

- Risks you already see coming: technical, organizational, business, external
- For each risk: likelihood (Low / Medium / High) and potential impact

**What you receive:**

A `risk-register.md` with each risk scored by probability × impact, a risk level (Low / Medium / High / Critical), and a proposed mitigation action. The register will be updated automatically by the scheduled `risk-update` task during active phases.

---

### 5.5 Generate the Communication Plan

**How to activate:**

```
Generate a communication plan
```

The plugin reads the stakeholder map (if generated) automatically. If not available, it will ask for stakeholder details.

**What you receive:**

A `comm-plan.md` with a communication matrix: who receives what information, in what format, how often, and who is responsible for sending it. Includes an escalation path for issues and decisions.

---

## 6. Phase 3 — Prototyping

**Goal:** evaluate solution options, select the best approach, and get approval to proceed.

**Documents created in Phase 3:**
- Prototype Comparison Table
- Meeting Protocol (from Go/No-Go meeting)
- Approval Letter

---

### 6.1 Compare Prototype Options

When you have 2–4 candidate approaches or solutions, use this skill to score and compare them systematically.

**How to activate:**

```
Compare prototype options
```

**What the plugin will ask you:**

- Number of options to compare (2 to 4)
- Brief description of each option
- Evaluation criteria (the plugin suggests a standard set: technical feasibility, UX quality, cost, timeline, risk — you can customize)
- Weights for each criterion (or use the defaults)

**What you receive:**

A `comparison-table.xlsx` with a weighted scoring matrix, totals per option, and a recommendation. You make the final selection.

---

### 6.2 Generate a Meeting Protocol

Use this skill after any project meeting to create a structured protocol from your notes.

**How to activate:**

```
Generate a meeting protocol
```

**What the plugin will ask you:**

- Meeting date, type, and participants
- Decisions made (paste your rough notes — the plugin will structure them)
- Action items: who does what by when

**What you receive:**

A `meeting-protocol-YYYY-MM-DD.md` file in `meetings/`. Decisions and action items are linked to WP task IDs from the project plan where applicable.

---

### 6.3 Generate an Approval Letter

Use this skill to request formal approval from a client or sponsor before moving to the next phase.

**How to activate:**

```
Generate an approval letter for Phase 3
```

**What you receive:**

A `approval-letter.md` document ready to send, plus an `email-approval.md` template for Gmail. The email includes a summary of what is being approved and a clear call to action.

---

## 7. Phase 4 — Development

**Goal:** execute the project plan through development sprints. Monitor progress, manage changes, and keep the plan current.

**Key skills in Phase 4:**
- Sprint progress reports
- Schedule and budget deviation checks
- Scope change impact assessments

---

### 7.1 Run a Sprint Report

**How to activate:**

```
/sprint-report
```

or

```
Generate a sprint progress report
```

**What the plugin will ask you:**

- Sprint number and dates
- Completed tasks (paste from Jira, or describe in plain text)
- In-progress and blocked tasks
- Any issues or decisions needed

**What you receive:**

A `sprint-report-SXX.md` file in `reports/`. Includes completed vs. planned comparison, blockers summary, and recommended actions.

> If Jira MCP is connected, the plugin pulls task status automatically — you only need to confirm or correct.

---

### 7.2 Check for Deviations

**How to activate:**

```
/deviation-check
```

The plugin compares current progress against the project plan and budget. It flags:
- Tasks behind schedule (by how many days)
- Budget lines overspent or at risk
- Risks that have materialized

**What you receive:**

A `deviation-report-YYYY-MM-DD.md` in `reports/`. If deviations exceed thresholds, the plugin drafts a stakeholder notification email for your review.

---

### 7.3 Assess a Scope Change Request

When a client or stakeholder requests a change to the project scope, use this skill before agreeing.

**How to activate:**

```
Assess scope change request: add social media integration to the mobile app
```

**What the plugin will ask you:**

- Description of the requested change
- Who requested it and why
- Preliminary view on complexity

**What you receive:**

A `change-impact-CR-XXX.xlsx` with impact analysis across three dimensions: timeline delta, budget delta, and risk level. The plugin rates the change as Low / Medium / High impact and recommends approval, deferral, or rejection. You make the final call.

---

## 8. Phase 5 — Launch

**Goal:** prepare and execute the project launch. Coordinate parallel workstreams and have incident response ready.

**Documents created in Phase 5:**
- Launch Readiness Checklist
- Technical Readiness Checklist
- Handover-to-Operations Checklist
- Incident Response Plan
- Cross-stream Synchronization Report

---

### 8.1 Generate Checklists

**How to activate:**

```
Generate a launch readiness checklist
```

or

```
Generate a technical readiness checklist
```

or

```
Generate a handover checklist
```

The plugin will pre-populate each checklist with standard items from a PMBoK-aligned template, enriched with data from your project plan. You review and finalize before use.

**What you receive:**

- `launch-checklist.md` — all conditions to verify before go-live
- `tech-readiness-checklist.md` — technical and infrastructure checks
- `handover-checklist.md` — steps for handing the project over to operations

---

### 8.2 Create an Incident Response Plan

Prepare before launch, not after something breaks.

**How to activate:**

```
Create an incident response plan
```

**What the plugin will ask you:**

- Most likely incident types for your project (technical failure, deployment error, PR crisis, etc.)
- Key people responsible for response
- Escalation path

**What you receive:**

A `response-plan-INC.md` with severity levels (Critical / High / Medium / Low), response procedures for each type, a communication plan, and post-incident tasks.

---

### 8.3 Cross-stream Sync Report

When multiple workstreams run in parallel during launch, use this command to check alignment.

**How to activate:**

```
/sync-check
```

**What you receive:**

A `sync-report-YYYY-MM-DD.md` showing the status of each workstream, dependencies between them, blockers, and critical path items requiring immediate attention.

---

## 9. Phase 6 — Project Closure

**Goal:** formally close the project. Document what happened, what was learned, and hand over the outcomes.

**Documents created in Phase 6:**
- Plan vs. Actual Report
- Project Closure Report

---

### 9.1 Generate a Plan vs. Actual Report

**How to activate:**

```
Generate a plan vs. actual report
```

**What the plugin will ask you:**

- Planned vs. actual timeline (start date, end date, milestone dates)
- Planned vs. actual budget (by category)
- Planned vs. delivered scope (which features were shipped, which were deferred)

**What you receive:**

A `plan-fact-report.md` with variance tables across all three dimensions and brief explanatory comments for each significant deviation.

---

### 9.2 Generate the Project Closure Report

The closure report aggregates everything: charter, plan-fact comparison, realized risks, and lessons learned.

**How to activate:**

```
Generate a project closure report
```

The plugin reads all available project artifacts automatically. You will be asked to add the lessons learned section in your own words.

**What you receive:**

A `closure-report.md` — a comprehensive document suitable for archiving and sharing with sponsors or future project teams.

---

## 10. Slash Commands Reference

Slash commands are shortcuts for common actions. Type them at the start of a message.

### `/init-project [name]`

Initializes a new project. Creates folder structure, `CLAUDE.md`, `project-state.md`, and starts Phase 1.

**Example:** `/init-project crm-upgrade`

---

### `/status`

Shows the current state of the active project: phase, completed artifacts, and next recommended steps. Use this at the start of any session to orient yourself.

**Example:** `/status`

---

### `/next-step`

Recommends the single next action based on what has been completed and what dependencies have been met. Useful when you're unsure what to do next.

**Example:** `/next-step`

---

### `/sprint-report`

Generates a sprint progress report. The plugin asks for current sprint data, or pulls from Jira if connected.

**Example:** `/sprint-report`

---

### `/deviation-check`

Checks for schedule and budget deviations against the project plan. Flags issues and drafts alerts if thresholds are exceeded.

**Example:** `/deviation-check`

---

### `/risk-update`

Reviews the risk register: asks if any new risks have emerged, if any mitigation actions have been completed, and updates risk scores accordingly.

**Example:** `/risk-update`

---

### `/sync-check`

Synchronizes parallel workstreams during Phase 5. Shows status of all streams and critical dependencies.

**Example:** `/sync-check`

---

### `/remind-executors`

Sends reminders to team members with overdue tasks. The plugin reads the project plan to identify overdue items and drafts reminder emails.

**Example:** `/remind-executors`

---

## 11. Email Notifications

The plugin can send emails on your behalf through Gmail (if connected). All emails use a three-level autonomy system — you choose how much control you want.

### Autonomy Levels

**Level 1 — Automatic:** the plugin sends the email immediately. Used for routine, low-stakes notifications (e.g., weekly status reports to the team).

**Level 2 — Auto-send with PM copy:** the plugin sends the email and copies you. Used for deviation alerts and reminder notifications.

**Level 3 — Draft for approval:** the plugin creates a draft and shows it to you before sending. You review, edit if needed, and confirm. Used for approval requests, stakeholder reports, and anything going to clients.

### How to Change the Autonomy Level

When a skill proposes sending an email, it will tell you the default autonomy level. To change it, simply say:

```
Use autonomy level 3 for this email
```

or

```
Don't send automatically — show me the draft first
```

### If Gmail Is Not Connected

The plugin creates an `.md` file with the email draft content instead. You can copy the text and send it manually from your email client.

---

## 12. Scheduled Automatic Checks

The plugin can run routine checks automatically on a schedule. These are set up during `/init-project` and become active during Phases 3–5.

| Task | Schedule | Purpose |
|------|----------|---------|
| Weekly Status Report | Every Monday at 9:00 AM | Summary of project progress for stakeholders |
| Daily Deviation Check | Mon–Fri at 9:00 AM | Flags schedule and budget issues before they escalate |
| Risk Register Review | Every Monday (per sprint) | Updates risk scores based on current project state |
| Cross-stream Sync | Every Monday at 9:00 AM (Phase 5 only) | Checks parallel workstream alignment |
| Executor Reminders | Mon–Fri at 10:00 AM | Sends reminders for overdue tasks |

All scheduled tasks can also be triggered manually at any time using slash commands.

**To pause a scheduled task:**

```
Pause the daily deviation check
```

**To resume:**

```
Resume the daily deviation check
```

---

## 13. Working Without External Integrations

The plugin is fully functional without Jira, Gmail, or Google Calendar. Here's what changes in file-only mode:

| Feature | With integrations | Without integrations |
|---------|-------------------|----------------------|
| Sprint reports | Pulls task data from Jira automatically | You provide task data in chat |
| Deviation checks | Reads Jira statuses automatically | You confirm current status manually |
| Email notifications | Sends via Gmail | Saves draft to `.md` file for manual sending |
| Meeting scheduling | Creates Calendar event automatically | Provides event details for manual creation |

For most users, file-only mode is perfectly sufficient. Add integrations later if you want more automation.

---

## 14. Tips for Best Results

**Start each session with `/status`**
The plugin picks up where you left off. Running `/status` first shows you the current state and prevents accidentally duplicating work.

**Put your source data in `input/` before running skills**
The more context the plugin has, the better the output. A filled-in questionnaire or a brief document in `input/` is worth more than answering questions one by one in chat.

**Review and approve before moving on**
Each skill asks for your approval before marking an artifact as complete. Take a moment to read the output — corrections are much easier at this stage than after dependent documents have been generated.

**Use `/next-step` when unsure**
Rather than guessing what to do next, ask the plugin. It knows the dependency map and will suggest the right action based on what's been completed.

**Keep one session per phase**
Long sessions with many context switches can occasionally confuse the plugin about which project is active. Starting a fresh session for each major phase keeps things clean.

**Describe problems in plain language**
You don't need to know the name of the skill. Saying "I need to check if we're behind schedule" or "help me prepare for the client demo" is enough — the plugin will identify the right skill.

---

## 15. Frequently Asked Questions

**Q: Can the plugin manage multiple projects at the same time?**

A: Yes. Each project has its own folder and `CLAUDE.md` file. At the start of a session, tell the plugin which project you're working on: "Switch to the mobile-app project." The plugin reads the relevant `CLAUDE.md` and activates that project's context.

---

**Q: I accidentally ran `/init-project` twice. Now I have duplicate folders. What should I do?**

A: Delete the duplicate folder manually (keep the one with the content you want). Then run `/status` to confirm the plugin is reading the correct folder.

---

**Q: The plugin generated a document but I made manual edits to it. Will it overwrite my changes?**

A: No. The plugin only creates new files — it never overwrites files that already exist in the project folder. If you need to regenerate a document (e.g., to update it after the plan changed), tell the plugin explicitly: "Regenerate the risk register based on the updated project plan."

---

**Q: Can I use the plugin without running `/init-project` first?**

A: Individual skills (like generating a charter or meeting protocol) can be used without initializing a full project. However, skills that depend on other artifacts (e.g., the communication plan needs the stakeholder map) work best within a properly initialized project.

---

**Q: What happens if the plugin generates a document I don't like?**

A: Tell it what to change: "The risk register is missing the vendor dependency risk — please add it." or "Rewrite the charter's scope section — the exclusions list is too vague." The plugin will update the specific section without regenerating the whole document.

---

**Q: Does the plugin store any of my project data on external servers?**

A: No. All project files are stored locally on your computer in the folder you selected during setup. The plugin runs entirely within Claude Cowork on your machine. MCP integrations (Jira, Gmail, Calendar) connect to those external services directly — no intermediate storage.

---

**Q: The scheduled tasks aren't running. Why?**

A: Scheduled tasks only run while the Claude desktop app is open. If the app is closed, tasks will run at the next scheduled time after you open the app again. Check that the tasks are enabled by running `/status`.

---

**Q: Can I use the plugin in Russian?**

A: Yes. The plugin detects your language automatically from your input and responds in the same language. All 21 skills and 8 commands support both English and Russian. You can switch languages within a session at any time.

---

## 16. Glossary

**Artifact** — a document created by the plugin and saved to the project folder (charter, plan, risk register, etc.).

**Autonomy level** — how independently the plugin acts for a given action. Level 1: fully automatic. Level 3: requires your approval before proceeding.

**Command** — a shortcut starting with `/` that triggers a specific plugin action.

**Communication Plan** — a document specifying who receives what information, how often, and through which channel.

**Deviation** — a measurable difference between the planned and actual state of the project (schedule slippage, budget overrun).

**Gantt chart** — a timeline visualization showing when tasks start and end, represented in the plugin as a text-format table.

**MCP (Model Context Protocol)** — the standard that allows Claude plugins to connect to external services like Jira, Gmail, and Google Calendar.

**Phase** — one of the six stages of the project lifecycle: Initiation, Planning, Prototyping, Development, Launch, Closure.

**PMBoK** — Project Management Body of Knowledge. The international standard for project management methodology published by PMI. This plugin is based on PMBoK 8 + Agile hybrid approach.

**project-state.md** — the plugin's internal registry of all created artifacts and their approval status.

**Risk Register** — a structured list of identified risks with probability, impact, and mitigation plans.

**Skill** — a specialized capability of the plugin that handles one specific task (e.g., generating a charter, running a deviation check).

**Stakeholder** — anyone with an interest in the project: client, sponsor, team members, end users.

**WBS (Work Breakdown Structure)** — a hierarchical breakdown of all project deliverables and tasks into manageable components.

**WP-XXX** — the task numbering system used across all project documents to link related items.

---

[← Installation Guide](INSTALL-COWORK.md) | [Русская версия](USER-GUIDE.ru.md)

---

**Keywords:** Claude Cowork plugin user guide, AI project manager tutorial, IT project management automation, PMBoK AI agent, project charter generator Claude, risk register automation Cowork, project management AI tool, automated project documentation, sprint reporting AI, stakeholder communication automation
