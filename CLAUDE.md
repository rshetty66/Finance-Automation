# CLAUDE.md — Finance-Automation

Project memory for Claude Code and Cowork sessions. Loaded automatically at the
start of every session in this repository.

## Standing operating instructions

All consulting, finance transformation, ERP/EPM, and deliverable work in this
project follows the reusable prompt framework in
[`prompts/consulting-master.md`](prompts/consulting-master.md) — a Spec →
Verifier → Environment structure adapted from Andrej Karpathy's method.

@prompts/consulting-master.md

## How I want you to apply it

- **Spec before execution.** If the ask is fuzzy, run the Discovery Prompt
  (Section 1) and get my approval on a one-paragraph Spec before producing the
  deliverable.
- **One deliverable per prompt.** For multi-phase work, propose a phased plan
  and execute only the first phase unless I say otherwise.
- **Run the Verifier.** Before returning a consulting deliverable, self-check it
  against the criteria in the relevant section and fix anything that fails.
- **Cite or flag.** Every factual or quantitative claim is traceable to a stated
  source or explicitly marked as an assumption. Never invent data, citations, or
  client names.
- **Ask, don't assume.** On anything material to the outcome, ask a clarifying
  question instead of guessing.
- **Match the variant to the task.** Research synthesis → Section 3. Client memo
  or slide narrative → Section 4. Chart of accounts / ledger / data model review
  → Section 5. New agent or skill → Section 6.

## Project standing context

- Domain: finance transformation, ERP/EPM (Oracle EPM, SAP S/4HANA, Workday,
  OneStream, Anaplan), regulatory and capital reporting (BCAR/OSFI), agentic AI
  tooling.
- Audience for most outputs: CFO, steering committee, or client stakeholders —
  write to a Big 4 / boutique strategy deliverable standard.
- Standing preferences: structured over prose, tables over paragraphs, cite
  everything, declarative and specific, no hedging unless genuinely uncertain
  (and then say why), no filler.

## Reusing this outside the repo

To make the framework standing context for **all** projects rather than just this
one, copy the same import line into the user-level memory file:

```bash
mkdir -p ~/.claude
echo "@$(pwd)/prompts/consulting-master.md" >> ~/.claude/CLAUDE.md
```

Cowork picks up this `CLAUDE.md` from the project directory the same way Claude
Code does.
