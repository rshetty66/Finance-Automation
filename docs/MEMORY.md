# Cross-project agent memory

`rudra.memory.ProjectMemory` is one memory store for every agentic project in this
portfolio: Rudra, F-VOLT, BCAR, BMO, PCC, Sprott ERP, EPM WFP and the intake register.
`ContextManager` holds a single conversation. `ProjectMemory` holds what should
carry over between sessions and between engagements.

## Model

| Table | Holds |
|---|---|
| `projects` | The engagement portfolio (id, client, status, last active) |
| `memories` | `fact`, `decision`, `lesson`, `preference`, `question`, `summary`. Scoped to a project, or global when `project` is omitted |
| `sessions` | Who worked on which project, and the summary they left at the end |
| `decisions` | Typed Choice / Noul / Score records, with the resolver (`rule`, `cheap`, `mid`, `frontier`, `human`) and cost |

The design follows the "typed decisions around the loop" idea. Most agent turns make a
small decision instead of producing a deliverable, so the store handles those decisions
cheaply:

- **Which memories?** (Score): `recall()` ranks memories by lexical match, importance, recency and project scope. It returns the top *k* that fit a token budget, instead of loading everything. Pinned memories always come back.
- **Keep or drop?** (Score): `compact()` keeps the top *N* memories word for word and deletes the rest. It does not rewrite the rest into a lossy summary. Pinned memories are never dropped.
- **Which model? Safe to run? Done?** (Choice / Noul): `decisions.py` has rule resolvers (`choose_tier`, `is_irreversible`, `is_done`). `record_decision()` logs every decision, and `decision_cost()` shows how much work stayed off the frontier model.

## CLI

```bash
rudra memory projects
rudra memory project bcar "BCAR Capital Intelligence" --client "Bank" --tags osfi,capital
rudra memory start bcar --agent gl-capital-recon --query "CET1 deductions"   # prints a brief + session id
rudra memory add "CET1 deductions mapped from GL 1950-1999" --project bcar --kind fact
rudra memory add "Exec summary first, sources cited" --kind preference --pin  # global
rudra memory recall "intercompany eliminations" --project sprott-erp
rudra memory end <session-id> "Mapped CET1; OSFI template pending"
rudra memory compact --project bcar --keep 200 --dry-run
rudra memory decisions --project bcar
rudra memory export memory/portfolio.jsonl     # git-tracked copy
```

## Python

```python
from rudra.memory import ContextManager, ProjectMemory
from rudra.memory.decisions import choose_tier, is_irreversible

mem = ProjectMemory()
sid = mem.start_session("sprott-erp", agent_id="si-functional-lead")

ctx = ContextManager()
session = ctx.get_or_create(sid)
mem.hydrate(session, "sprott-erp", query="AP invoice approval workflow")

mem.record_decision(choose_tier("draft intercompany design memo"), project="sprott-erp", session_id=sid)
gate = is_irreversible("post journal entries to GL")   # answer == "yes" -> ask a human

mem.absorb(session, "sprott-erp")          # saves the session's decisions, questions and facts
mem.end_session(sid, "IC design drafted; tax rules open")
```

## Storage

- The working store is SQLite at `RUDRA_MEMORY_DB`, or `~/.rudra/memory.db` if that is not set. It uses only the standard library.
- `memory/portfolio.jsonl` is the copy tracked in git. Run `rudra memory export memory/portfolio.jsonl` and commit the file so memory carries over to new machines and cloud sessions.
- The Claude Code `SessionStart` hook in `.claude/settings.json` runs `rudra memory session-start`. If the DB is empty, it first loads the JSONL seed. It then prints the portfolio brief, so every session starts with that context.
- Keep client-confidential details out of the JSONL file if the repo is shared.
