"""
SkillRegistry – catalog of Claude Superpower Skills.

Each skill wraps a specific Claude API capability and exposes a uniform
interface: ``apply(client, params, base_request) -> dict``.  The dict is
merged into the kwargs sent to ``client.messages.create``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class SkillType(str, Enum):
    EXTENDED_THINKING = "extended_thinking"
    PROMPT_CACHING = "prompt_caching"
    VISION = "vision"
    STRUCTURED_OUTPUT = "structured_output"


@dataclass
class SkillDefinition:
    """Metadata + factory for a single superpower skill."""

    skill_type: SkillType
    name: str
    description: str
    default_params: dict[str, Any] = field(default_factory=dict)
    # factory returns an instance of the concrete skill class
    factory: Optional[Callable[[], Any]] = None

    def build(self) -> Any:
        if self.factory is None:
            raise ValueError(f"Skill '{self.name}' has no factory registered")
        return self.factory()


class SkillRegistry:
    """
    Central catalog of all registered superpower skills.

    Usage::

        registry = SkillRegistry.default()
        skill = registry.get(SkillType.EXTENDED_THINKING)
        extra_kwargs = skill.apply(params={"budget_tokens": 8000})
    """

    def __init__(self) -> None:
        self._skills: dict[SkillType, SkillDefinition] = {}

    def register(self, defn: SkillDefinition) -> None:
        self._skills[defn.skill_type] = defn
        logger.debug("Registered skill: %s", defn.name)

    def get(self, skill_type: SkillType) -> Optional[SkillDefinition]:
        return self._skills.get(skill_type)

    def list_skills(self) -> list[SkillDefinition]:
        return list(self._skills.values())

    def list_types(self) -> list[SkillType]:
        return list(self._skills.keys())

    @classmethod
    def default(cls) -> "SkillRegistry":
        """Return the default registry with all built-in superpower skills."""
        from rudra.skills.extended_thinking import ExtendedThinkingSkill
        from rudra.skills.prompt_caching import PromptCachingSkill
        from rudra.skills.vision import VisionSkill
        from rudra.skills.structured_output import StructuredOutputSkill

        registry = cls()

        registry.register(SkillDefinition(
            skill_type=SkillType.EXTENDED_THINKING,
            name="Extended Thinking",
            description=(
                "Activates Claude's visible chain-of-thought reasoning. "
                "The model emits <thinking> blocks before its final answer, "
                "enabling deep multi-step financial analysis."
            ),
            default_params={"budget_tokens": 10_000},
            factory=ExtendedThinkingSkill,
        ))

        registry.register(SkillDefinition(
            skill_type=SkillType.PROMPT_CACHING,
            name="Prompt Caching",
            description=(
                "Attaches cache_control headers to the system prompt so "
                "repeated calls reuse the cached KV state, cutting latency "
                "and token costs for large agent system prompts."
            ),
            default_params={"cache_type": "ephemeral"},
            factory=PromptCachingSkill,
        ))

        registry.register(SkillDefinition(
            skill_type=SkillType.VISION,
            name="Vision Analysis",
            description=(
                "Enables multimodal image and PDF analysis. Agents can pass "
                "base64-encoded financial documents, charts, or screenshots "
                "for Claude to reason over alongside text."
            ),
            default_params={"media_type": "image/png"},
            factory=VisionSkill,
        ))

        registry.register(SkillDefinition(
            skill_type=SkillType.STRUCTURED_OUTPUT,
            name="Structured Output",
            description=(
                "Forces Claude to return a typed JSON payload by pinning "
                "tool_use to a caller-supplied JSON schema. Guarantees "
                "machine-readable outputs for downstream finance systems."
            ),
            default_params={"tool_choice": "any"},
            factory=StructuredOutputSkill,
        ))

        return registry
