"""Tests for memory and context management."""

import pytest
import tempfile
from pathlib import Path

from rudra.memory.context import ContextManager, SessionContext, ConversationTurn
from rudra.memory.persistence import SessionStore


class TestContextManager:
    def test_create_session(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")
        assert session.session_id == "test-session"
        assert len(session.conversation) == 0

    def test_add_turn(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")
        turn = ctx.add_turn(session, "user", "Analyze this lease under IFRS 16")
        assert turn.role == "user"
        assert turn.tokens > 0
        assert len(session.conversation) == 1

    def test_add_fact(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")
        ctx.add_fact(session, "reporting_basis", "IFRS")
        assert session.active_facts["reporting_basis"] == "IFRS"

    def test_add_decision(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")
        ctx.add_decision(session, "Classify as finance lease under IFRS 16")
        assert len(session.key_decisions) == 1

    def test_token_budget(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")
        budget = ctx.get_budget_for_agent(session, "test-agent")
        assert budget > 0
        assert budget <= ctx.max_agent_tokens

    def test_budget_decreases_with_large_history(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")

        # Add enough content to exceed the agent token budget
        for i in range(20):
            ctx.add_turn(session, "user", "x" * 20000)
        budget_with_history = ctx.get_budget_for_agent(session, "test-agent")
        assert budget_with_history < ctx.max_agent_tokens

    def test_build_context(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")
        ctx.add_turn(session, "user", "Hello")
        ctx.add_turn(session, "assistant", "Hi there")
        messages = ctx.build_context_for_agent(session, "test-agent")
        assert len(messages) >= 2

    def test_session_summary(self):
        ctx = ContextManager()
        session = ctx.get_or_create("test-session")
        ctx.add_turn(session, "user", "test")
        ctx.add_fact(session, "key", "value")
        summary = ctx.get_session_summary(session)
        assert summary["turns"] == 1
        assert summary["active_facts"] == 1

    def test_clear_session(self):
        ctx = ContextManager()
        ctx.get_or_create("test-session")
        ctx.clear_session("test-session")
        session = ctx.get_or_create("test-session")
        assert len(session.conversation) == 0


class TestSessionStore:
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SessionStore(storage_dir=Path(tmpdir))
            session = SessionContext(session_id="test-123")
            session.active_facts = {"basis": "IFRS"}
            session.key_decisions = ["Use ROU model"]
            session.conversation.append(
                ConversationTurn(role="user", content="Analyze lease")
            )

            store.save(session)
            loaded = store.load("test-123")
            assert loaded is not None
            assert loaded.session_id == "test-123"
            assert loaded.active_facts["basis"] == "IFRS"
            assert len(loaded.conversation) == 1

    def test_load_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SessionStore(storage_dir=Path(tmpdir))
            assert store.load("nonexistent") is None

    def test_list_sessions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SessionStore(storage_dir=Path(tmpdir))
            store.save(SessionContext(session_id="s1"))
            store.save(SessionContext(session_id="s2"))
            sessions = store.list_sessions()
            assert set(sessions) == {"s1", "s2"}

    def test_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SessionStore(storage_dir=Path(tmpdir))
            store.save(SessionContext(session_id="to-delete"))
            assert store.delete("to-delete") is True
            assert store.load("to-delete") is None
            assert store.delete("nonexistent") is False
