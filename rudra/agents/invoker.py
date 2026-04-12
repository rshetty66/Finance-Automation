"""
AgentInvoker   handles LLM calls for agent invocations.

Supports Anthropic as the primary provider with model routing based on
the agent spec's model field.  Wraps streaming, token counting, and
error handling.

Superpower Skills are opt-in capabilities layered on top of the base
call via ``call_llm_with_skill()``:

  - extended_thinking  : visible chain-of-thought reasoning blocks
  - prompt_caching     : cache_control headers for hot system-prompt paths
  - vision             : multimodal image / PDF document analysis
  - structured_output  : JSON schema enforcement via tool_use pinning
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

    async def call_llm_with_skill(
        self,
        agent_spec: AgentSpec,
        messages: list[dict],
        request: AgentRequest,
        skill_type: str,
        skill_params: Optional[dict[str, Any]] = None,
    ) -> AgentResult:
        """
        Invoke a Claude Superpower Skill alongside the standard LLM call.

        ``skill_type`` must be one of:
          - ``"extended_thinking"``  – deep chain-of-thought reasoning
          - ``"prompt_caching"``     – system-prompt KV caching
          - ``"vision"``             – multimodal document analysis
          - ``"structured_output"``  – JSON schema-enforced output

        ``skill_params`` is forwarded to the skill's ``build_api_kwargs``
        method; leave as ``None`` to use the skill's defaults.

        The ``AgentResult.structured_output`` field is populated with the
        parsed skill output where applicable (extended thinking summary,
        structured JSON).
        """
        from rudra.skills.registry import SkillRegistry, SkillType

        skill_params = skill_params or {}
        model = self.resolve_model(agent_spec)
        client = self._get_client()
        start = time.monotonic()

        registry = SkillRegistry.default()
        try:
            skill_enum = SkillType(skill_type)
        except ValueError:
            valid = [s.value for s in SkillType]
            return AgentResult(
                agent_id=agent_spec.id,
                status=InvocationStatus.FAILED,
                error=f"Unknown skill_type {skill_type!r}. Valid values: {valid}",
                model_used=model,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        skill_def = registry.get(skill_enum)
        if skill_def is None:
            return AgentResult(
                agent_id=agent_spec.id,
                status=InvocationStatus.FAILED,
                error=f"Skill '{skill_type}' not found in registry",
                model_used=model,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        try:
            return await self._dispatch_skill(
                skill_enum=skill_enum,
                skill_def=skill_def,
                skill_params=skill_params,
                agent_spec=agent_spec,
                messages=messages,
                model=model,
                client=client,
                start=start,
            )
        except Exception as exc:
            logger.error(
                "Skill call '%s' failed for agent %s: %s",
                skill_type, agent_spec.id, exc,
            )
            return AgentResult(
                agent_id=agent_spec.id,
                status=InvocationStatus.FAILED,
                error=str(exc),
                model_used=model,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    async def _dispatch_skill(
        self,
        skill_enum: Any,
        skill_def: Any,
        skill_params: dict[str, Any],
        agent_spec: AgentSpec,
        messages: list[dict],
        model: str,
        client: Any,
        start: float,
    ) -> AgentResult:
        """Route to the concrete skill handler."""
        from rudra.skills.registry import SkillType

        if skill_enum == SkillType.EXTENDED_THINKING:
            return await self._call_with_extended_thinking(
                agent_spec=agent_spec,
                messages=messages,
                model=model,
                client=client,
                start=start,
                params=skill_params,
            )
        elif skill_enum == SkillType.PROMPT_CACHING:
            return await self._call_with_prompt_caching(
                agent_spec=agent_spec,
                messages=messages,
                model=model,
                client=client,
                start=start,
                params=skill_params,
            )
        elif skill_enum == SkillType.VISION:
            return await self._call_with_vision(
                agent_spec=agent_spec,
                messages=messages,
                model=model,
                client=client,
                start=start,
                params=skill_params,
            )
        elif skill_enum == SkillType.STRUCTURED_OUTPUT:
            return await self._call_with_structured_output(
                agent_spec=agent_spec,
                messages=messages,
                model=model,
                client=client,
                start=start,
                params=skill_params,
            )
        else:
            raise ValueError(f"No dispatch handler for skill: {skill_enum}")

    async def _call_with_extended_thinking(
        self,
        agent_spec: AgentSpec,
        messages: list[dict],
        model: str,
        client: Any,
        start: float,
        params: dict[str, Any],
    ) -> AgentResult:
        from rudra.skills.extended_thinking import ExtendedThinkingSkill

        budget_tokens = params.get("budget_tokens", 10_000)
        skill = ExtendedThinkingSkill(budget_tokens=budget_tokens)
        extra = skill.build_api_kwargs()

        response = await client.messages.create(
            model=model,
            max_tokens=agent_spec.max_tokens,
            system=agent_spec.system_prompt,
            messages=messages,
            **extra,
        )

        result = ExtendedThinkingSkill.parse_response(response)
        input_tokens = result.input_tokens
        output_tokens = result.output_tokens

        return AgentResult(
            agent_id=agent_spec.id,
            status=InvocationStatus.COMPLETED,
            response=result.answer_text,
            structured_output={
                "thinking": result.thinking_text,
                "skill": "extended_thinking",
                "budget_tokens": budget_tokens,
            },
            tokens_used=input_tokens + output_tokens,
            model_used=model,
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    async def _call_with_prompt_caching(
        self,
        agent_spec: AgentSpec,
        messages: list[dict],
        model: str,
        client: Any,
        start: float,
        params: dict[str, Any],
    ) -> AgentResult:
        from rudra.skills.prompt_caching import PromptCachingSkill

        cache_type = params.get("cache_type", "ephemeral")
        skill = PromptCachingSkill(cache_type=cache_type)
        extra = skill.build_api_kwargs(system_prompt=agent_spec.system_prompt)

        create_kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": agent_spec.max_tokens,
            "temperature": self.config.models.temperature,
            "messages": messages,
        }
        create_kwargs.update(extra)

        response = await client.messages.create(**create_kwargs)

        content = response.content[0].text if response.content else ""
        input_tokens = response.usage.input_tokens if response.usage else 0
        output_tokens = response.usage.output_tokens if response.usage else 0
        cache_read = getattr(response.usage, "cache_read_input_tokens", 0) or 0
        cache_created = getattr(response.usage, "cache_creation_input_tokens", 0) or 0

        return AgentResult(
            agent_id=agent_spec.id,
            status=InvocationStatus.COMPLETED,
            response=content,
            structured_output={
                "skill": "prompt_caching",
                "cache_read_tokens": cache_read,
                "cache_creation_tokens": cache_created,
            },
            tokens_used=input_tokens + output_tokens,
            model_used=model,
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    async def _call_with_vision(
        self,
        agent_spec: AgentSpec,
        messages: list[dict],
        model: str,
        client: Any,
        start: float,
        params: dict[str, Any],
    ) -> AgentResult:
        """
        Vision calls expect the caller to have already built a multimodal
        content list via ``VisionSkill.build_content()``.  The messages list
        must contain at least one dict with a list-typed ``content`` field.
        """
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
            structured_output={"skill": "vision"},
            tokens_used=input_tokens + output_tokens,
            model_used=model,
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    async def _call_with_structured_output(
        self,
        agent_spec: AgentSpec,
        messages: list[dict],
        model: str,
        client: Any,
        start: float,
        params: dict[str, Any],
    ) -> AgentResult:
        from rudra.skills.structured_output import StructuredOutputSkill

        output_schema = params.get("output_schema")
        if not output_schema:
            raise ValueError(
                "structured_output skill requires 'output_schema' in skill_params"
            )

        description = params.get("description", "Emit the structured result")
        skill = StructuredOutputSkill(output_schema=output_schema)
        extra = skill.build_api_kwargs(description=description)

        response = await client.messages.create(
            model=model,
            max_tokens=agent_spec.max_tokens,
            temperature=self.config.models.temperature,
            system=agent_spec.system_prompt,
            messages=messages,
            **extra,
        )

        parsed = StructuredOutputSkill.parse_response(response)
        input_tokens = response.usage.input_tokens if response.usage else 0
        output_tokens = response.usage.output_tokens if response.usage else 0

        return AgentResult(
            agent_id=agent_spec.id,
            status=InvocationStatus.COMPLETED,
            response=str(parsed) if parsed else "",
            structured_output=parsed or {"skill": "structured_output", "error": "no tool call found"},
            tokens_used=input_tokens + output_tokens,
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
