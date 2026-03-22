"""
AgentInvoker   handles LLM calls for agent invocations.

Supports Anthropic as the primary provider with model routing based on
the agent spec's model field.  Wraps streaming, token counting, and
error handling.
"""

from __future__ import annotations

import logging
import time
from typing import Any, AsyncIterator, Optional

from rudra.config import RudraConfig, get_config
from rudra.models import (
    AgentRequest,
    AgentResult,
    AgentSpec,
    InvocationStatus,
)

logger = logging.getLogger(__name__)


class AgentInvoker:
    """
    Thin wrapper over the Anthropic Messages API.

    Resolves model aliases ('default', 'fast', 'reasoning') to concrete
    model identifiers using the RudraConfig.
    """

    def __init__(self, config: Optional[RudraConfig] = None) -> None:
        self.config = config or get_config()
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(
                    api_key=self.config.anthropic_api_key
                )
            except ImportError:
                raise ImportError(
                    "anthropic package is required. Install with: pip install anthropic"
                )
        return self._client

    def resolve_model(self, spec: AgentSpec) -> str:
        """Map model aliases to concrete model identifiers."""
        alias = spec.model
        mapping = {
            "default": self.config.models.default_model,
            "fast": self.config.models.fast_model,
            "reasoning": self.config.models.reasoning_model,
            "inherit": self.config.models.default_model,
        }
        return mapping.get(alias, alias)

    async def call_llm(
        self,
        agent_spec: AgentSpec,
        messages: list[dict[str, str]],
        request: AgentRequest,
    ) -> AgentResult:
        """
        Send messages to the LLM and return a structured AgentResult.
        """
        model = self.resolve_model(agent_spec)
        client = self._get_client()
        start = time.monotonic()

        try:
            response = await client.messages.create(
                model=model,
                max_tokens=agent_spec.max_tokens,
                temperature=self.config.models.temperature,
                system=agent_spec.system_prompt,
                messages=messages,
            )

            content = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0

            return AgentResult(
                agent_id=agent_spec.id,
                status=InvocationStatus.COMPLETED,
                response=content,
                tokens_used=input_tokens + output_tokens,
                model_used=model,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        except Exception as exc:
            logger.error("LLM call failed for agent %s: %s", agent_spec.id, exc)
            return AgentResult(
                agent_id=agent_spec.id,
                status=InvocationStatus.FAILED,
                error=str(exc),
                model_used=model,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    async def call_llm_streaming(
        self,
        agent_spec: AgentSpec,
        messages: list[dict[str, str]],
        request: AgentRequest,
    ) -> AsyncIterator[str]:
        """
        Stream LLM response tokens for real-time display.
        """
        model = self.resolve_model(agent_spec)
        client = self._get_client()

        async with client.messages.stream(
            model=model,
            max_tokens=agent_spec.max_tokens,
            temperature=self.config.models.temperature,
            system=agent_spec.system_prompt,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
