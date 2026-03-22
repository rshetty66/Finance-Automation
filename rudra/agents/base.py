"""
Base agent class that all Rudra agents inherit from.

Each agent wraps an AgentSpec (its contract) and exposes an `invoke()` method
that the orchestrator calls.  The base class handles token budgeting, timeout,
retry logic, and result packaging   subclasses only need to override
`build_messages()` if they want to customise the prompt assembly.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from rudra.models import (
    AgentRequest,
    AgentResult,
    AgentSpec,
    InvocationStatus,
)

logger = logging.getLogger(__name__)


class BaseAgent:
    """Runtime wrapper around an AgentSpec."""

    def __init__(self, spec: AgentSpec) -> None:
        self.spec = spec
        self._invoker: Optional[Any] = None  # set by orchestrator

    @property
    def id(self) -> str:
        return self.spec.id

    @property
    def name(self) -> str:
        return self.spec.name

    def bind_invoker(self, invoker: Any) -> None:
        self._invoker = invoker

    def build_messages(self, request: AgentRequest) -> list[dict[str, str]]:
        """
        Assemble the message list sent to the LLM.

        Override in subclasses for custom prompt engineering (e.g. RAG
        augmentation, multi-turn history injection).
        """
        user_content_parts: list[str] = []

        if request.facts:
            user_content_parts.append(f"**Facts:**\n{request.facts}\n")

        user_content_parts.append(request.query)

        if request.context:
            import json
            user_content_parts.append(f"\n**Additional context:**\n```json\n{json.dumps(request.context, indent=2)}\n```")

        return [{"role": "user", "content": "\n\n".join(user_content_parts)}]

    async def invoke(self, request: AgentRequest) -> AgentResult:
        """
        Invoke the agent with the given request.

        Handles retry logic, timeout, and result packaging.
        """
        if self._invoker is None:
            raise RuntimeError(f"Agent '{self.id}' has no invoker bound. Call bind_invoker() first.")

        start = time.monotonic()
        last_error: Optional[str] = None

        for attempt in range(1, self.spec.max_retries + 1):
            try:
                messages = self.build_messages(request)
                result = await self._invoker.call_llm(
                    agent_spec=self.spec,
                    messages=messages,
                    request=request,
                )
                result.duration_ms = int((time.monotonic() - start) * 1000)
                return result

            except Exception as exc:
                last_error = f"Attempt {attempt}/{self.spec.max_retries} failed: {exc}"
                logger.warning(last_error)
                if attempt < self.spec.max_retries:
                    await _sleep(2 ** attempt)

        return AgentResult(
            agent_id=self.id,
            status=InvocationStatus.FAILED,
            error=last_error or "Unknown error",
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    def __repr__(self) -> str:
        return f"<Agent {self.id} domain={self.spec.domain}>"


async def _sleep(seconds: float) -> None:
    import asyncio
    await asyncio.sleep(seconds)
