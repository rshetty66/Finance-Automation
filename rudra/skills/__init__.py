"""
Claude Superpower Skills for the Rudra framework.

Superpower Skills expose advanced Claude API capabilities as first-class
primitives that any agent can opt into:

  extended_thinking  – visible chain-of-thought reasoning blocks
  prompt_caching     – cache_control headers for hot system-prompt paths
  vision             – multimodal image/PDF financial document analysis
  structured_output  – JSON schema enforcement via tool_use pinning
"""

from rudra.skills.registry import SkillRegistry, SkillDefinition, SkillType
from rudra.skills.extended_thinking import ExtendedThinkingSkill
from rudra.skills.prompt_caching import PromptCachingSkill
from rudra.skills.vision import VisionSkill
from rudra.skills.structured_output import StructuredOutputSkill

__all__ = [
    "SkillRegistry",
    "SkillDefinition",
    "SkillType",
    "ExtendedThinkingSkill",
    "PromptCachingSkill",
    "VisionSkill",
    "StructuredOutputSkill",
]
