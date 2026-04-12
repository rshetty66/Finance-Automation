"""
Extended Thinking Skill.

Activates Claude's visible chain-of-thought reasoning blocks.  When enabled,
the model emits a ``thinking`` block before its final answer, performing deep
multi-step reasoning that is especially valuable for complex financial analysis
(e.g. IFRS 9 ECL models, multi-entity consolidation, M&A PPA).

API surface:
  ``messages.create(..., thinking={"type": "enabled", "budget_tokens": N})``
  Temperature must be 1.0 when thinking is enabled (API requirement).

The skill also parses the response to extract and surface both the thinking
summary and the final answer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Minimum budget Claude needs to actually produce thinking blocks
_MIN_BUDGET_TOKENS = 1_000
# Default budget balances depth vs. cost for finance analysis
_DEFAULT_BUDGET_TOKENS = 10_000


@dataclass
class ThinkingResult:
    """Parsed output from an extended-thinking LLM response."""

    thinking_text: str = ""
    answer_text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def full_response(self) -> str:
        """Combine thinking + answer for logging / audit trails."""
        if self.thinking_text:
            return f"<thinking>\n{self.thinking_text}\n</thinking>\n\n{self.answer_text}"
        return self.answer_text


class ExtendedThinkingSkill:
    """
    Superpower Skill: Extended Thinking.

    Usage::

        skill = ExtendedThinkingSkill(budget_tokens=16_000)
        extra_kwargs = skill.build_api_kwargs()
        # merge into client.messages.create(**base_kwargs, **extra_kwargs)

        result = ExtendedThinkingSkill.parse_response(response)
        print(result.thinking_text)
        print(result.answer_text)
    """

    def __init__(self, budget_tokens: int = _DEFAULT_BUDGET_TOKENS) -> None:
        if budget_tokens < _MIN_BUDGET_TOKENS:
            raise ValueError(
                f"budget_tokens must be >= {_MIN_BUDGET_TOKENS}, got {budget_tokens}"
            )
        self.budget_tokens = budget_tokens

    def build_api_kwargs(self) -> dict[str, Any]:
        """
        Return the extra kwargs to merge into ``client.messages.create``.

        Extended thinking requires temperature=1 (API constraint).
        """
        return {
            "thinking": {
                "type": "enabled",
                "budget_tokens": self.budget_tokens,
            },
            # Extended thinking requires temperature = 1
            "temperature": 1,
        }

    @staticmethod
    def parse_response(response: Any) -> ThinkingResult:
        """
        Parse an Anthropic Messages response that may contain thinking blocks.

        Returns a ``ThinkingResult`` with separate thinking text and answer.
        """
        thinking_parts: list[str] = []
        answer_parts: list[str] = []

        for block in response.content:
            block_type = getattr(block, "type", None)
            if block_type == "thinking":
                thinking_parts.append(getattr(block, "thinking", ""))
            elif block_type == "text":
                answer_parts.append(getattr(block, "text", ""))

        input_tokens = getattr(response.usage, "input_tokens", 0) if response.usage else 0
        output_tokens = getattr(response.usage, "output_tokens", 0) if response.usage else 0

        return ThinkingResult(
            thinking_text="\n\n".join(thinking_parts),
            answer_text="\n\n".join(answer_parts),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    def __repr__(self) -> str:
        return f"<ExtendedThinkingSkill budget_tokens={self.budget_tokens}>"
