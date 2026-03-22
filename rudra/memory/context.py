"""
ContextManager   manages token budgets and context windows for agents.

Ensures no single agent or multi-agent pipeline exceeds the configured
token budget.  Tracks conversation history, extracted facts, and
routing history for the current session.
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Optional

from rudra.config import get_config

logger = logging.getLogger(__name__)


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English."""
    return max(1, len(text) // 4)


@dataclass
class ConversationTurn:
    role: str
    content: str
    agent_id: Optional[str] = None
    tokens: int = 0

    def __post_init__(self):
        if self.tokens == 0:
            self.tokens = _estimate_tokens(self.content)


@dataclass
class SessionContext:
    """All context for a single session."""
    session_id: str
    conversation: deque = field(default_factory=lambda: deque(maxlen=50))
    active_facts: dict[str, Any] = field(default_factory=dict)
    routing_history: list[dict] = field(default_factory=list)
    key_decisions: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    total_tokens_used: int = 0


class ContextManager:
    """
    Manages context budgets and conversation history.

    Usage::

        ctx = ContextManager()
        session = ctx.get_or_create("session-123")
        ctx.add_turn(session, "user", "Analyze this lease...")
        budget = ctx.get_budget_for_agent(session, "lease-accounting-agent")
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionContext] = {}
        config = get_config()
        self.max_context_tokens = config.memory.max_context_tokens
        self.max_agent_tokens = config.memory.max_agent_tokens

    def get_or_create(self, session_id: str) -> SessionContext:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionContext(session_id=session_id)
        return self._sessions[session_id]

    def add_turn(
        self,
        session: SessionContext,
        role: str,
        content: str,
        agent_id: Optional[str] = None,
    ) -> ConversationTurn:
        """Add a conversation turn and track token usage."""
        turn = ConversationTurn(role=role, content=content, agent_id=agent_id)
        session.conversation.append(turn)
        session.total_tokens_used += turn.tokens
        return turn

    def add_fact(self, session: SessionContext, key: str, value: Any) -> None:
        session.active_facts[key] = value

    def add_routing(self, session: SessionContext, routing_info: dict) -> None:
        session.routing_history.append(routing_info)

    def add_decision(self, session: SessionContext, decision: str) -> None:
        session.key_decisions.append(decision)

    def add_question(self, session: SessionContext, question: str) -> None:
        session.open_questions.append(question)

    def get_budget_for_agent(
        self,
        session: SessionContext,
        agent_id: str,
    ) -> int:
        """
        Calculate how many tokens an agent can use given current context.

        Reserves space for system prompt + conversation history, then
        allocates the remainder up to max_agent_tokens.
        """
        history_tokens = sum(t.tokens for t in session.conversation)
        facts_tokens = _estimate_tokens(str(session.active_facts))
        overhead = history_tokens + facts_tokens

        available = self.max_context_tokens - overhead
        return min(available, self.max_agent_tokens)

    def build_context_for_agent(
        self,
        session: SessionContext,
        agent_id: str,
        max_history_turns: int = 10,
    ) -> list[dict[str, str]]:
        """
        Build a message list for an agent, respecting the token budget.

        Includes recent conversation history and active facts.
        """
        budget = self.get_budget_for_agent(session, agent_id)
        messages: list[dict[str, str]] = []
        tokens_so_far = 0

        if session.active_facts:
            facts_str = f"**Active facts:**\n{session.active_facts}"
            facts_tokens = _estimate_tokens(facts_str)
            if tokens_so_far + facts_tokens < budget:
                messages.append({"role": "user", "content": facts_str})
                tokens_so_far += facts_tokens

        recent = list(session.conversation)[-max_history_turns:]
        for turn in recent:
            if tokens_so_far + turn.tokens > budget:
                break
            messages.append({"role": turn.role, "content": turn.content})
            tokens_so_far += turn.tokens

        return messages

    def get_session_summary(self, session: SessionContext) -> dict:
        return {
            "session_id": session.session_id,
            "turns": len(session.conversation),
            "total_tokens": session.total_tokens_used,
            "active_facts": len(session.active_facts),
            "decisions": len(session.key_decisions),
            "open_questions": len(session.open_questions),
            "routing_count": len(session.routing_history),
        }

    def clear_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
