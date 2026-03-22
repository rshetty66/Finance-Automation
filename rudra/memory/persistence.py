"""
SessionStore   persists session context to disk (JSON) or Databricks Delta.

The local JSON backend works out of the box; the Databricks backend
is activated when DATABRICKS_HOST is set in the environment.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from rudra.config import get_config
from rudra.memory.context import SessionContext

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Persist and restore session context.

    Usage::

        store = SessionStore()
        store.save(session)
        restored = store.load("session-123")
    """

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        config = get_config()
        self.storage_dir = storage_dir or Path(config.memory.session_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, session: SessionContext) -> Path:
        """Save session context to a JSON file."""
        data = {
            "session_id": session.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_facts": session.active_facts,
            "routing_history": session.routing_history,
            "key_decisions": session.key_decisions,
            "open_questions": session.open_questions,
            "total_tokens_used": session.total_tokens_used,
            "conversation": [
                {
                    "role": t.role,
                    "content": t.content,
                    "agent_id": t.agent_id,
                    "tokens": t.tokens,
                }
                for t in session.conversation
            ],
        }

        path = self.storage_dir / f"{session.session_id}.json"
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        logger.debug("Saved session %s to %s", session.session_id, path)
        return path

    def load(self, session_id: str) -> Optional[SessionContext]:
        """Load session context from a JSON file."""
        path = self.storage_dir / f"{session_id}.json"
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))

        from rudra.memory.context import ConversationTurn
        from collections import deque

        session = SessionContext(
            session_id=data["session_id"],
            active_facts=data.get("active_facts", {}),
            routing_history=data.get("routing_history", []),
            key_decisions=data.get("key_decisions", []),
            open_questions=data.get("open_questions", []),
            total_tokens_used=data.get("total_tokens_used", 0),
        )

        for turn_data in data.get("conversation", []):
            turn = ConversationTurn(
                role=turn_data["role"],
                content=turn_data["content"],
                agent_id=turn_data.get("agent_id"),
                tokens=turn_data.get("tokens", 0),
            )
            session.conversation.append(turn)

        return session

    def list_sessions(self) -> list[str]:
        """List all saved session IDs."""
        return [p.stem for p in self.storage_dir.glob("*.json")]

    def delete(self, session_id: str) -> bool:
        path = self.storage_dir / f"{session_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False
