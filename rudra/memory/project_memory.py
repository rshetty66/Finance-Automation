"""
ProjectMemory   durable memory shared by every agentic project.

``ContextManager`` holds one conversation; ``ProjectMemory`` is what survives
between conversations and across engagements (BCAR, Sprott ERP, PCC
diagnostics, EPM WFP, ...).  One SQLite file holds:

* projects   the engagement portfolio
* memories   facts, decisions, lessons, preferences, open questions;
             scoped to one project or global (``project_id`` NULL)
* sessions   who worked on what, and the end-of-session summary
* decisions  typed Choice / Noul / Score records (see ``decisions.py``)

Two Score decisions sit on top of it:

* ``recall``   which memories to read: rank by relevance + importance +
               recency and return only the top few within a token budget,
               rather than loading everything.
* ``compact``  keep or drop: keep survivors verbatim and delete the tail,
               rather than summarising everything into a lossy paragraph.

The store is stdlib-only.  ``export_jsonl`` / ``import_jsonl`` give a
git-friendly copy so memory can travel with the repo.

Usage::

    mem = ProjectMemory()
    mem.register_project("bcar", "BCAR Capital Intelligence", client="D-SIB")
    sid = mem.start_session("bcar", agent_id="gl-capital-recon")
    mem.remember("CET1 deductions mapped from GL 1950-1999", project="bcar",
                 kind="fact", tags=["bcar", "cet1"])
    hits = mem.recall("CET1 deduction mapping", project="bcar")
    print(mem.brief("bcar", query="capital reconciliation"))
    mem.end_session(sid, "Mapped CET1 deductions; OSFI template pending")
"""

from __future__ import annotations

import json
import math
import os
import re
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from rudra.config import get_config
from rudra.memory.context import SessionContext, _estimate_tokens
from rudra.memory.decisions import DecisionType, TypedDecision

MEMORY_KINDS = ("fact", "decision", "lesson", "preference", "question", "summary")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT DEFAULT '',
    description TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL,
    last_active TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '[]',
    importance REAL DEFAULT 0.5,
    pinned INTEGER DEFAULT 0,
    source TEXT DEFAULT '',
    session_id TEXT,
    created_at TEXT NOT NULL,
    last_used TEXT,
    use_count INTEGER DEFAULT 0,
    UNIQUE(project_id, kind, content)
);
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    agent_id TEXT DEFAULT '',
    started_at TEXT NOT NULL,
    ended_at TEXT,
    summary TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    session_id TEXT,
    decision_type TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    options TEXT DEFAULT '[]',
    rationale TEXT DEFAULT '',
    resolved_by TEXT DEFAULT 'rule',
    cost_usd REAL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mem_project ON memories(project_id);
CREATE INDEX IF NOT EXISTS idx_dec_project ON decisions(project_id);
"""

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_\-\.]*")
_STOP = frozenset(
    "a an and are as at be by for from has have in is it of on or that the this to was were will with".split()
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _stem(t: str) -> str:
    """Plural folding only: journals -> journal, entities -> entity."""
    if len(t) > 4 and t.endswith("ies"):
        return t[:-3] + "y"
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t


def _tokens(text: str) -> list[str]:
    return [_stem(t) for t in _TOKEN_RE.findall(text.lower()) if t not in _STOP]


def default_db_path() -> Path:
    """RUDRA_MEMORY_DB, else config.memory.memory_db, else ~/.rudra/memory.db."""
    env = os.environ.get("RUDRA_MEMORY_DB")
    if env:
        return Path(env).expanduser()
    return Path(get_config().memory.memory_db).expanduser()


@dataclass
class Memory:
    id: int
    project_id: Optional[str]
    kind: str
    content: str
    tags: list[str] = field(default_factory=list)
    importance: float = 0.5
    pinned: bool = False
    source: str = ""
    session_id: Optional[str] = None
    created_at: str = ""
    last_used: Optional[str] = None
    use_count: int = 0
    score: float = 0.0

    @property
    def tokens(self) -> int:
        return _estimate_tokens(self.content)


class ProjectMemory:
    """Cross-project memory store. Safe to open from many agents; one file per portfolio."""

    def __init__(self, db_path: Optional[Path | str] = None) -> None:
        self.db_path = Path(db_path) if db_path else default_db_path()
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "ProjectMemory":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def register_project(
        self,
        project_id: str,
        name: str,
        client: str = "",
        description: str = "",
        tags: Iterable[str] = (),
        status: str = "active",
    ) -> None:
        """Create or update a project. Idempotent."""
        now = _now()
        self._conn.execute(
            """INSERT INTO projects (id, name, client, description, tags, status, created_at, last_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET name=excluded.name, client=excluded.client,
                   description=excluded.description, tags=excluded.tags, status=excluded.status""",
            (project_id, name, client, description, json.dumps(list(tags)), status, now, now),
        )
        self._conn.commit()

    def get_project(self, project_id: str) -> Optional[dict]:
        row = self._conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return self._project_dict(row) if row else None

    def list_projects(self, status: Optional[str] = None) -> list[dict]:
        sql = "SELECT * FROM projects"
        args: tuple = ()
        if status:
            sql += " WHERE status = ?"
            args = (status,)
        sql += " ORDER BY last_active DESC"
        return [self._project_dict(r) for r in self._conn.execute(sql, args)]

    def _require_project(self, project_id: Optional[str]) -> None:
        if project_id is not None and self.get_project(project_id) is None:
            raise KeyError(f"Unknown project {project_id!r}; register_project() first")

    def _touch_project(self, project_id: Optional[str]) -> None:
        if project_id:
            self._conn.execute("UPDATE projects SET last_active = ? WHERE id = ?", (_now(), project_id))

    @staticmethod
    def _project_dict(row: sqlite3.Row) -> dict:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags") or "[]")
        return d

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def start_session(self, project_id: str, agent_id: str = "", session_id: Optional[str] = None) -> str:
        self._require_project(project_id)
        sid = session_id or f"{project_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}"
        self._conn.execute(
            "INSERT OR IGNORE INTO sessions (id, project_id, agent_id, started_at) VALUES (?, ?, ?, ?)",
            (sid, project_id, agent_id, _now()),
        )
        self._touch_project(project_id)
        self._conn.commit()
        return sid

    def end_session(self, session_id: str, summary: str = "") -> None:
        row = self._conn.execute("SELECT project_id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown session {session_id!r}")
        self._conn.execute(
            "UPDATE sessions SET ended_at = ?, summary = ? WHERE id = ?", (_now(), summary, session_id)
        )
        if summary:
            self.remember(summary, project=row["project_id"], kind="summary",
                          importance=0.6, session_id=session_id, source="end_session")
        self._touch_project(row["project_id"])
        self._conn.commit()

    def list_sessions(self, project_id: Optional[str] = None, limit: int = 20) -> list[dict]:
        sql = "SELECT * FROM sessions"
        args: list = []
        if project_id:
            sql += " WHERE project_id = ?"
            args.append(project_id)
        sql += " ORDER BY started_at DESC LIMIT ?"
        args.append(limit)
        return [dict(r) for r in self._conn.execute(sql, args)]

    # ------------------------------------------------------------------
    # Memories
    # ------------------------------------------------------------------

    def remember(
        self,
        content: str,
        project: Optional[str] = None,
        kind: str = "fact",
        tags: Iterable[str] = (),
        importance: float = 0.5,
        pinned: bool = False,
        source: str = "",
        session_id: Optional[str] = None,
    ) -> int:
        """Store a memory. ``project=None`` makes it global (visible to every project).

        Re-remembering identical content bumps importance instead of duplicating.
        """
        if kind not in MEMORY_KINDS:
            raise ValueError(f"kind must be one of {MEMORY_KINDS}, got {kind!r}")
        content = content.strip()
        if not content:
            raise ValueError("content is empty")
        self._require_project(project)
        importance = max(0.0, min(1.0, importance))

        existing = self._conn.execute(
            "SELECT id, importance FROM memories WHERE project_id IS ? AND kind = ? AND content = ?",
            (project, kind, content),
        ).fetchone()
        if existing:
            self._conn.execute(
                "UPDATE memories SET importance = ?, pinned = MAX(pinned, ?) WHERE id = ?",
                (max(existing["importance"], importance), int(pinned), existing["id"]),
            )
            self._conn.commit()
            return existing["id"]

        cur = self._conn.execute(
            """INSERT INTO memories (project_id, kind, content, tags, importance, pinned, source, session_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project, kind, content, json.dumps(sorted(set(tags))), importance, int(pinned),
             source, session_id, _now()),
        )
        self._touch_project(project)
        self._conn.commit()
        return int(cur.lastrowid)

    def forget(self, memory_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def pin(self, memory_id: int, pinned: bool = True) -> None:
        self._conn.execute("UPDATE memories SET pinned = ? WHERE id = ?", (int(pinned), memory_id))
        self._conn.commit()

    def list_memories(
        self,
        project: Optional[str] = None,
        kind: Optional[str] = None,
        include_global: bool = True,
    ) -> list[Memory]:
        return self._candidates(project, kind, include_global)

    def _candidates(self, project: Optional[str], kind: Optional[str], include_global: bool) -> list[Memory]:
        where, args = [], []
        if project is not None:
            where.append("(project_id = ? OR project_id IS NULL)" if include_global else "project_id = ?")
            args.append(project)
        if kind:
            where.append("kind = ?")
            args.append(kind)
        sql = "SELECT * FROM memories" + (" WHERE " + " AND ".join(where) if where else "")
        sql += " ORDER BY created_at DESC, id DESC"
        return [self._row_to_memory(r) for r in self._conn.execute(sql, args)]

    @staticmethod
    def _row_to_memory(row: sqlite3.Row) -> Memory:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags") or "[]")
        d["pinned"] = bool(d["pinned"])
        return Memory(**d)

    # ------------------------------------------------------------------
    # Score: which memories to read
    # ------------------------------------------------------------------

    def _score(self, memories: list[Memory], query: str, project: Optional[str]) -> None:
        """Assign ``score`` in place: BM25-style lexical match + importance + recency + scope."""
        q = _tokens(query)
        docs = [_tokens(m.content + " " + " ".join(m.tags)) for m in memories]
        n = len(docs) or 1
        avg_len = (sum(len(d) for d in docs) / n) or 1.0
        df = Counter(t for d in docs for t in set(d))
        now = datetime.now(timezone.utc)

        for m, d in zip(memories, docs):
            lexical = 0.0
            if q:
                tf = Counter(d)
                for t in set(q):
                    if t not in tf:
                        continue
                    idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                    f = tf[t]
                    lexical += idf * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * len(d) / avg_len))
                lexical = lexical / (lexical + 2.0)  # squash to 0..1
            try:
                age_days = (now - datetime.fromisoformat(m.last_used or m.created_at)).days
            except ValueError:
                age_days = 365
            recency = math.exp(-age_days / 90)
            scope = 0.1 if (project and m.project_id == project) else 0.0
            weight = 0.6 if q else 0.0
            m.score = (weight * lexical + 0.25 * m.importance + 0.1 * recency + scope
                       + (0.5 if m.pinned else 0.0))
            if q and lexical == 0 and not m.pinned:
                m.score *= 0.3

    def recall(
        self,
        query: str = "",
        project: Optional[str] = None,
        k: int = 8,
        token_budget: int = 2000,
        kinds: Optional[Iterable[str]] = None,
        include_global: bool = True,
        min_score: float = 0.0,
    ) -> list[Memory]:
        """Return the top-k memories for ``query`` that fit in ``token_budget``."""
        mems = self._candidates(project, None, include_global)
        if kinds:
            allowed = set(kinds)
            mems = [m for m in mems if m.kind in allowed]
        self._score(mems, query, project)
        mems.sort(key=lambda m: m.score, reverse=True)

        picked: list[Memory] = []
        used = 0
        for m in mems:
            if len(picked) >= k or m.score < min_score:
                break
            if used + m.tokens > token_budget:
                continue
            picked.append(m)
            used += m.tokens

        if picked:
            now = _now()
            self._conn.executemany(
                "UPDATE memories SET last_used = ?, use_count = use_count + 1 WHERE id = ?",
                [(now, m.id) for m in picked],
            )
            self._conn.commit()
        return picked

    # ------------------------------------------------------------------
    # Score: keep or drop
    # ------------------------------------------------------------------

    def compact(self, project: Optional[str], keep: int = 200, dry_run: bool = False) -> list[int]:
        """Keep the ``keep`` highest-value memories verbatim; drop the rest.

        Pinned memories are never dropped. Value = importance + usage + recency.
        Returns the ids dropped (or that would be dropped with ``dry_run``).
        """
        mems = self._candidates(project, None, include_global=False) if project else [
            m for m in self._candidates(None, None, True) if m.project_id is None
        ]
        self._score(mems, "", project)
        for m in mems:
            m.score += min(m.use_count, 20) / 40
        mems.sort(key=lambda m: m.score, reverse=True)
        droppable = [m for m in mems if not m.pinned]
        budget = max(0, keep - (len(mems) - len(droppable)))
        drop = [m.id for m in droppable[budget:]]
        if drop and not dry_run:
            self._conn.executemany("DELETE FROM memories WHERE id = ?", [(i,) for i in drop])
            self._conn.commit()
        return drop

    # ------------------------------------------------------------------
    # Typed decisions
    # ------------------------------------------------------------------

    def record_decision(
        self,
        decision: TypedDecision,
        project: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> int:
        self._require_project(project)
        cur = self._conn.execute(
            """INSERT INTO decisions (project_id, session_id, decision_type, question, answer, options,
                                      rationale, resolved_by, cost_usd, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project, session_id, decision.decision_type.value, decision.question, decision.answer,
             json.dumps(decision.options), decision.rationale, decision.resolved_by.value,
             decision.cost_usd, _now()),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def list_decisions(
        self, project: Optional[str] = None, decision_type: Optional[str] = None, limit: int = 50
    ) -> list[dict]:
        where, args = [], []
        if project:
            where.append("project_id = ?")
            args.append(project)
        if decision_type:
            where.append("decision_type = ?")
            args.append(DecisionType(decision_type).value)
        sql = "SELECT * FROM decisions" + (" WHERE " + " AND ".join(where) if where else "")
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        out = []
        for r in self._conn.execute(sql, args):
            d = dict(r)
            d["options"] = json.loads(d["options"] or "[]")
            out.append(d)
        return out

    def decision_cost(self, project: Optional[str] = None) -> dict[str, Any]:
        """Decisions and spend grouped by resolver, to show what stays off the frontier model."""
        sql = "SELECT resolved_by, COUNT(*) n, SUM(cost_usd) cost FROM decisions"
        args: tuple = ()
        if project:
            sql += " WHERE project_id = ?"
            args = (project,)
        sql += " GROUP BY resolved_by"
        return {r["resolved_by"]: {"count": r["n"], "cost_usd": round(r["cost"] or 0, 6)}
                for r in self._conn.execute(sql, args)}

    # ------------------------------------------------------------------
    # Bridge to the in-conversation ContextManager
    # ------------------------------------------------------------------

    def hydrate(self, session: SessionContext, project: str, query: str = "", k: int = 8) -> list[Memory]:
        """Load recalled memories into a live ``SessionContext`` at session start."""
        hits = self.recall(query, project=project, k=k)
        session.active_facts.setdefault("project", project)
        session.active_facts["memory"] = [f"[{m.kind}] {m.content}" for m in hits]
        return hits

    def absorb(self, session: SessionContext, project: str) -> int:
        """Persist a finished session's decisions, open questions and facts. Returns count stored."""
        n = 0
        for d in session.key_decisions:
            self.remember(d, project=project, kind="decision", importance=0.7,
                          session_id=session.session_id, source="absorb")
            n += 1
        for q in session.open_questions:
            self.remember(q, project=project, kind="question", importance=0.6,
                          session_id=session.session_id, source="absorb")
            n += 1
        for key, val in session.active_facts.items():
            if key in ("memory", "project"):
                continue
            self.remember(f"{key}: {val}", project=project, kind="fact",
                          session_id=session.session_id, source="absorb")
            n += 1
        return n

    # ------------------------------------------------------------------
    # Brief: the block an agent reads at session start
    # ------------------------------------------------------------------

    def brief(self, project: Optional[str] = None, query: str = "", k: int = 10, token_budget: int = 1500) -> str:
        lines: list[str] = []
        if project:
            p = self.get_project(project)
            if p is None:
                raise KeyError(f"Unknown project {project!r}")
            lines.append(f"# Project memory: {p['name']} ({p['id']})")
            if p["client"]:
                lines.append(f"Client: {p['client']}")
            if p["description"]:
                lines.append(p["description"])
            last = self.list_sessions(project, limit=1)
            if last and last[0]["summary"]:
                lines.append(f"\nLast session ({last[0]['started_at'][:10]}): {last[0]['summary']}")
        else:
            lines.append("# Agentic project portfolio")
            for p in self.list_projects():
                count = self._conn.execute(
                    "SELECT COUNT(*) FROM memories WHERE project_id = ?", (p["id"],)
                ).fetchone()[0]
                lines.append(f"- **{p['id']}**   {p['name']} [{p['status']}] · {count} memories"
                             f" · last active {p['last_active'][:10]}")

        hits = self.recall(query, project=project, k=k, token_budget=token_budget)
        if hits:
            lines.append("\n## Recalled memory")
            for m in hits:
                scope = m.project_id or "global"
                pin = " 📌" if m.pinned else ""
                lines.append(f"- [{m.kind} · {scope}]{pin} {m.content}")

        if project:
            qs = self._candidates(project, "question", include_global=False)[:5]
            if qs:
                lines.append("\n## Open questions")
                lines.extend(f"- {m.content}" for m in qs)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Export / import (git-friendly JSONL)
    # ------------------------------------------------------------------

    def export_jsonl(self, path: Path | str) -> int:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        with path.open("w", encoding="utf-8") as f:
            for p in self.list_projects():
                f.write(json.dumps({"type": "project", **p}, ensure_ascii=False) + "\n")
                n += 1
            for m in self._candidates(None, None, True):
                rec = asdict(m)
                rec.pop("score")
                f.write(json.dumps({"type": "memory", **rec}, ensure_ascii=False) + "\n")
                n += 1
        return n

    def import_jsonl(self, path: Path | str) -> int:
        """Merge a JSONL export. Projects upsert; memories dedupe on (project, kind, content)."""
        n = 0
        with Path(path).open(encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
        for r in records:
            if r.get("type") == "project":
                self.register_project(r["id"], r["name"], r.get("client", ""), r.get("description", ""),
                                      r.get("tags", []), r.get("status", "active"))
                n += 1
        for r in records:
            if r.get("type") == "memory":
                self.remember(r["content"], project=r.get("project_id"), kind=r.get("kind", "fact"),
                              tags=r.get("tags", []), importance=r.get("importance", 0.5),
                              pinned=bool(r.get("pinned")), source=r.get("source", "import"))
                n += 1
        return n

    def is_empty(self) -> bool:
        return self._conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0
