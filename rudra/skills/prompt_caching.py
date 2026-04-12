"""
Prompt Caching Skill.

Attaches ``cache_control`` breakpoints to the system prompt so that repeated
API calls reuse the cached KV state on Anthropic's servers.  This is
particularly valuable for Rudra agents whose system prompts are 4 000–20 000
tokens long (e.g. accounting-policy-engine, extended-thinking-analyst).

Caching rules (Anthropic):
  - Minimum cacheable prefix: 1 024 tokens (Sonnet/Opus), 2 048 (Haiku)
  - Cache lifetime: 5 minutes (ephemeral)
  - Cost savings: cached input tokens billed at 10% of normal input rate
  - Latency reduction: significant on second+ call for large prompts

The skill rewrites the ``system`` parameter from a plain string to the
structured list format required by the cache_control API.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Anthropic minimum token threshold to make caching worthwhile
_MIN_CACHE_TOKENS = 1_024


class PromptCachingSkill:
    """
    Superpower Skill: Prompt Caching.

    Converts a plain system-prompt string into the structured block format
    that carries ``cache_control`` metadata, enabling server-side KV caching.

    Usage::

        skill = PromptCachingSkill()
        extra_kwargs = skill.build_api_kwargs(system_prompt="You are ...")
        # The returned dict has "system" as a list[dict] with cache_control.
        # Pass as: client.messages.create(**base_kwargs, **extra_kwargs)
    """

    def __init__(self, cache_type: str = "ephemeral") -> None:
        self.cache_type = cache_type

    def build_api_kwargs(self, system_prompt: str) -> dict[str, Any]:
        """
        Return the extra kwargs to merge into ``client.messages.create``.

        Replaces the plain ``system`` string with a structured block list
        that includes the cache_control breakpoint.
        """
        if not system_prompt:
            return {}

        return {
            "system": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": self.cache_type},
                }
            ]
        }

    @staticmethod
    def estimate_savings(prompt_tokens: int, call_count: int) -> dict[str, Any]:
        """
        Estimate cost savings from caching over ``call_count`` API calls.

        Based on Anthropic's pricing model: cached tokens billed at 10% of
        normal input rate; cache write is 25% extra on the first call.

        Args:
            prompt_tokens: Number of tokens in the system prompt.
            call_count: Number of times the same prompt is used.

        Returns:
            Dict with uncached_tokens, cached_tokens, tokens_saved, pct_saved.
        """
        if call_count <= 1:
            return {"tokens_saved": 0, "pct_saved": 0.0}

        # First call: full tokens + 25% write overhead
        first_call_tokens = int(prompt_tokens * 1.25)
        # Subsequent calls: 10% of normal (cache hits)
        subsequent_tokens = int(prompt_tokens * 0.10) * (call_count - 1)
        cached_total = first_call_tokens + subsequent_tokens

        uncached_total = prompt_tokens * call_count
        tokens_saved = uncached_total - cached_total
        pct_saved = (tokens_saved / uncached_total * 100) if uncached_total > 0 else 0.0

        return {
            "uncached_tokens": uncached_total,
            "cached_tokens": cached_total,
            "tokens_saved": tokens_saved,
            "pct_saved": round(pct_saved, 1),
        }

    def __repr__(self) -> str:
        return f"<PromptCachingSkill cache_type={self.cache_type!r}>"
