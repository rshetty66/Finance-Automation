"""Tests for cross-project memory and typed decisions."""

import tempfile
from pathlib import Path

import pytest

from rudra.memory.context import ContextManager
from rudra.memory.decisions import (
    DecisionType,
    Resolver,
    TypedDecision,
    choose_tier,
    is_done,
    is_irreversible,
)
from rudra.memory.project_memory import ProjectMemory


@pytest.fixture
def mem():
    m = ProjectMemory(":memory:")
    m.register_project("bcar", "BCAR Capital Intelligence", client="Bank")
    m.register_project("sprott-erp", "Sprott Oracle ERP")
    yield m
    m.close()


class TestProjects:
    def test_register_is_idempotent(self, mem):
        mem.register_project("bcar", "BCAR renamed")
        assert mem.get_project("bcar")["name"] == "BCAR renamed"
        assert len(mem.list_projects()) == 2

    def test_unknown_project_rejected(self, mem):
        with pytest.raises(KeyError):
            mem.remember("x", project="nope")


class TestRemember:
    def test_dedupes_and_bumps_importance(self, mem):
        a = mem.remember("CET1 floor is 4.5%", project="bcar", importance=0.3)
        b = mem.remember("CET1 floor is 4.5%", project="bcar", importance=0.9)
        assert a == b
        assert mem.list_memories("bcar")[0].importance == 0.9

    def test_global_dedupes(self, mem):
        assert mem.remember("Exec summary first") == mem.remember("Exec summary first")

    def test_invalid_kind(self, mem):
        with pytest.raises(ValueError):
            mem.remember("x", kind="gossip")


class TestRecall:
    def test_project_scoping_includes_global(self, mem):
        mem.remember("CET1 deductions mapped from GL", project="bcar")
        mem.remember("Intercompany eliminations automated", project="sprott-erp")
        mem.remember("Cite sources in every deliverable")
        hits = mem.recall("", project="bcar", k=10)
        contents = {h.content for h in hits}
        assert "CET1 deductions mapped from GL" in contents
        assert "Cite sources in every deliverable" in contents
        assert "Intercompany eliminations automated" not in contents

    def test_relevance_ranking(self, mem):
        mem.remember("Lease portfolio classified under IFRS 16", project="bcar")
        mem.remember("CET1 deductions mapped from GL accounts", project="bcar")
        hits = mem.recall("cet1 deduction mapping", project="bcar", k=1)
        assert hits[0].content.startswith("CET1")

    def test_pinned_always_first(self, mem):
        mem.remember("unrelated pinned rule", pinned=True)
        mem.remember("CET1 deductions", project="bcar")
        assert mem.recall("cet1", project="bcar")[0].pinned

    def test_token_budget(self, mem):
        for i in range(10):
            mem.remember(f"capital note {i} " + "x" * 400, project="bcar")
        hits = mem.recall("capital", project="bcar", k=10, token_budget=250)
        assert sum(h.tokens for h in hits) <= 250
        assert len(hits) < 10

    def test_recall_updates_usage(self, mem):
        mid = mem.remember("CET1", project="bcar")
        mem.recall("cet1", project="bcar")
        m = [m for m in mem.list_memories("bcar") if m.id == mid][0]
        assert m.use_count == 1 and m.last_used


class TestCompact:
    def test_keeps_top_and_pinned(self, mem):
        pinned = mem.remember("keep me", project="bcar", importance=0.0, pinned=True)
        for i in range(5):
            mem.remember(f"note {i}", project="bcar", importance=i / 10)
        dropped = mem.compact("bcar", keep=3)
        remaining = {m.id for m in mem.list_memories("bcar", include_global=False)}
        assert pinned in remaining
        assert len(remaining) == 3
        assert len(dropped) == 3

    def test_dry_run(self, mem):
        for i in range(4):
            mem.remember(f"note {i}", project="bcar")
        dropped = mem.compact("bcar", keep=1, dry_run=True)
        assert len(dropped) == 3
        assert len(mem.list_memories("bcar", include_global=False)) == 4


class TestSessions:
    def test_end_session_stores_summary(self, mem):
        sid = mem.start_session("bcar", agent_id="gl-capital-recon")
        mem.end_session(sid, "Mapped CET1; OSFI template pending")
        assert mem.list_sessions("bcar")[0]["summary"].startswith("Mapped")
        assert any(m.kind == "summary" for m in mem.list_memories("bcar"))
        assert "Last session" in mem.brief("bcar")

    def test_hydrate_and_absorb(self, mem):
        mem.remember("Reporting basis is IFRS", project="bcar")
        ctx = ContextManager()
        session = ctx.get_or_create("s1")
        hits = mem.hydrate(session, "bcar", query="reporting basis")
        assert hits and session.active_facts["memory"]

        ctx.add_decision(session, "Classify as finance lease")
        ctx.add_question(session, "Confirm discount rate with treasury")
        ctx.add_fact(session, "entity", "BankCo")
        assert mem.absorb(session, "bcar") == 3
        kinds = {m.kind for m in mem.list_memories("bcar", include_global=False)}
        assert {"decision", "question", "fact"} <= kinds


class TestDecisions:
    def test_record_and_cost(self, mem):
        mem.record_decision(choose_tier("rename column headers"), project="bcar")
        mem.record_decision(TypedDecision(DecisionType.NOUL, "done?", "yes",
                                          resolved_by=Resolver.CHEAP, cost_usd=0.0017), project="bcar")
        assert len(mem.list_decisions("bcar")) == 2
        assert len(mem.list_decisions("bcar", "noul")) == 1
        cost = mem.decision_cost("bcar")
        assert cost["rule"]["count"] == 1
        assert cost["cheap"]["cost_usd"] == 0.0017

    def test_choice_validation(self):
        with pytest.raises(ValueError):
            TypedDecision(DecisionType.CHOICE, "tier?", "huge", options=["cheap", "mid"])
        with pytest.raises(ValueError):
            TypedDecision(DecisionType.NOUL, "ok?", "maybe")

    def test_rule_resolvers(self):
        assert choose_tier("rename a file").answer == "cheap"
        assert choose_tier("draft OSFI BCAR capital memo").answer == "frontier"
        assert choose_tier("anything", brief_clear=False).answer == "ask"
        assert is_irreversible("post journal entries to GL").answer == "yes"
        assert is_irreversible("git push --force-push origin").answer == "yes"
        assert is_irreversible("read the trial balance").answer == "no"
        assert is_done("12 passed in 0.4s").answer == "yes"
        assert is_done("1 failed, 11 passed").answer == "no"
        assert is_done(None).answer == "no"


class TestExportImport:
    def test_roundtrip(self, mem):
        mem.remember("CET1", project="bcar", tags=["osfi"], pinned=True)
        mem.remember("Exec summary first", kind="preference")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mem.jsonl"
            assert mem.export_jsonl(path) == 4
            other = ProjectMemory(Path(tmp) / "other.db")
            other.import_jsonl(path)
            other.import_jsonl(path)  # idempotent
            assert len(other.list_projects()) == 2
            assert len(other.list_memories()) == 2
            assert other.list_memories("bcar", include_global=False)[0].pinned
            other.close()

    def test_seed_file_loads(self):
        seed = Path(__file__).resolve().parent.parent / "memory" / "portfolio.jsonl"
        m = ProjectMemory(":memory:")
        assert m.import_jsonl(seed) > 0
        assert m.get_project("rudra") is not None
        m.close()
