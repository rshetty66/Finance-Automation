"""
Tests for Claude Superpower Skills.

These tests cover the skills module logic without making live API calls.
All Anthropic client interactions are mocked.
"""

from __future__ import annotations

import base64
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rudra.skills.registry import SkillRegistry, SkillType, SkillDefinition
from rudra.skills.extended_thinking import ExtendedThinkingSkill, ThinkingResult
from rudra.skills.prompt_caching import PromptCachingSkill
from rudra.skills.vision import VisionSkill, DocumentSource
from rudra.skills.structured_output import StructuredOutputSkill


# ---------------------------------------------------------------------------
# SkillRegistry
# ---------------------------------------------------------------------------

class TestSkillRegistry:
    def test_default_registry_has_all_four_skills(self):
        registry = SkillRegistry.default()
        types = registry.list_types()
        assert SkillType.EXTENDED_THINKING in types
        assert SkillType.PROMPT_CACHING in types
        assert SkillType.VISION in types
        assert SkillType.STRUCTURED_OUTPUT in types

    def test_get_returns_correct_skill(self):
        registry = SkillRegistry.default()
        defn = registry.get(SkillType.EXTENDED_THINKING)
        assert defn is not None
        assert defn.skill_type == SkillType.EXTENDED_THINKING
        assert defn.name == "Extended Thinking"

    def test_get_unknown_returns_none(self):
        registry = SkillRegistry()
        assert registry.get(SkillType.VISION) is None

    def test_register_and_list(self):
        registry = SkillRegistry()
        defn = SkillDefinition(
            skill_type=SkillType.VISION,
            name="Test Vision",
            description="test",
        )
        registry.register(defn)
        assert len(registry.list_skills()) == 1
        assert registry.list_types() == [SkillType.VISION]

    def test_build_raises_without_factory(self):
        defn = SkillDefinition(
            skill_type=SkillType.VISION,
            name="No Factory",
            description="test",
            factory=None,
        )
        with pytest.raises(ValueError, match="no factory"):
            defn.build()

    def test_build_with_factory(self):
        defn = SkillDefinition(
            skill_type=SkillType.EXTENDED_THINKING,
            name="Thinking",
            description="test",
            factory=ExtendedThinkingSkill,
        )
        instance = defn.build()
        assert isinstance(instance, ExtendedThinkingSkill)


# ---------------------------------------------------------------------------
# ExtendedThinkingSkill
# ---------------------------------------------------------------------------

class TestExtendedThinkingSkill:
    def test_build_api_kwargs_contains_thinking_and_temperature(self):
        skill = ExtendedThinkingSkill(budget_tokens=5_000)
        kwargs = skill.build_api_kwargs()
        assert kwargs["thinking"] == {"type": "enabled", "budget_tokens": 5_000}
        assert kwargs["temperature"] == 1

    def test_default_budget_is_10000(self):
        skill = ExtendedThinkingSkill()
        assert skill.budget_tokens == 10_000

    def test_raises_for_budget_below_minimum(self):
        with pytest.raises(ValueError, match="budget_tokens"):
            ExtendedThinkingSkill(budget_tokens=500)

    def test_parse_response_extracts_thinking_and_text(self):
        thinking_block = SimpleNamespace(type="thinking", thinking="step 1: consider X")
        text_block = SimpleNamespace(type="text", text="The answer is Y")
        usage = SimpleNamespace(input_tokens=100, output_tokens=200)
        response = SimpleNamespace(content=[thinking_block, text_block], usage=usage)

        result = ExtendedThinkingSkill.parse_response(response)
        assert isinstance(result, ThinkingResult)
        assert result.thinking_text == "step 1: consider X"
        assert result.answer_text == "The answer is Y"
        assert result.input_tokens == 100
        assert result.output_tokens == 200

    def test_parse_response_no_thinking_blocks(self):
        text_block = SimpleNamespace(type="text", text="Plain answer")
        usage = SimpleNamespace(input_tokens=10, output_tokens=20)
        response = SimpleNamespace(content=[text_block], usage=usage)

        result = ExtendedThinkingSkill.parse_response(response)
        assert result.thinking_text == ""
        assert result.answer_text == "Plain answer"

    def test_full_response_includes_thinking_wrapper(self):
        result = ThinkingResult(thinking_text="my thoughts", answer_text="my answer")
        assert "<thinking>" in result.full_response
        assert "my thoughts" in result.full_response
        assert "my answer" in result.full_response

    def test_full_response_no_thinking_returns_answer_only(self):
        result = ThinkingResult(thinking_text="", answer_text="just the answer")
        assert result.full_response == "just the answer"


# ---------------------------------------------------------------------------
# PromptCachingSkill
# ---------------------------------------------------------------------------

class TestPromptCachingSkill:
    def test_build_api_kwargs_returns_structured_system(self):
        skill = PromptCachingSkill()
        kwargs = skill.build_api_kwargs(system_prompt="You are an expert.")
        system = kwargs["system"]
        assert isinstance(system, list)
        assert len(system) == 1
        block = system[0]
        assert block["type"] == "text"
        assert block["text"] == "You are an expert."
        assert block["cache_control"] == {"type": "ephemeral"}

    def test_empty_system_prompt_returns_empty_dict(self):
        skill = PromptCachingSkill()
        kwargs = skill.build_api_kwargs(system_prompt="")
        assert kwargs == {}

    def test_custom_cache_type(self):
        skill = PromptCachingSkill(cache_type="persistent")
        kwargs = skill.build_api_kwargs("hello")
        assert kwargs["system"][0]["cache_control"]["type"] == "persistent"

    def test_estimate_savings_single_call_is_zero(self):
        result = PromptCachingSkill.estimate_savings(prompt_tokens=5_000, call_count=1)
        assert result["tokens_saved"] == 0
        assert result["pct_saved"] == 0.0

    def test_estimate_savings_multiple_calls(self):
        # With 5000 tokens and 10 calls, we should save a significant fraction
        result = PromptCachingSkill.estimate_savings(prompt_tokens=5_000, call_count=10)
        assert result["tokens_saved"] > 0
        assert result["pct_saved"] > 50  # Should be well over 50% savings
        assert result["uncached_tokens"] == 50_000

    def test_estimate_savings_keys_present(self):
        result = PromptCachingSkill.estimate_savings(prompt_tokens=2_000, call_count=5)
        assert "uncached_tokens" in result
        assert "cached_tokens" in result
        assert "tokens_saved" in result
        assert "pct_saved" in result


# ---------------------------------------------------------------------------
# VisionSkill
# ---------------------------------------------------------------------------

class TestVisionSkill:
    def _make_source(self, media_type: str = "image/png") -> DocumentSource:
        return DocumentSource(
            data=base64.standard_b64encode(b"fake_image_bytes").decode(),
            media_type=media_type,
            label="test.png",
        )

    def test_build_content_image_structure(self):
        skill = VisionSkill()
        source = self._make_source("image/png")
        content = skill.build_content(text_query="What is this?", documents=[source])

        assert len(content) == 2
        assert content[0]["type"] == "image"
        assert content[0]["source"]["type"] == "base64"
        assert content[0]["source"]["media_type"] == "image/png"
        assert content[1]["type"] == "text"
        assert content[1]["text"] == "What is this?"

    def test_build_content_pdf_uses_document_type(self):
        skill = VisionSkill()
        source = DocumentSource(
            data=base64.standard_b64encode(b"%PDF-1.4").decode(),
            media_type="application/pdf",
            label="report.pdf",
        )
        content = skill.build_content(text_query="Summarize", documents=[source])
        assert content[0]["type"] == "document"

    def test_build_content_unsupported_type_raises(self):
        skill = VisionSkill()
        source = DocumentSource(data="abc", media_type="audio/mp3")
        with pytest.raises(ValueError, match="Unsupported media type"):
            skill.build_content("query", [source])

    def test_build_content_too_many_documents_raises(self):
        skill = VisionSkill(max_documents=2)
        sources = [self._make_source() for _ in range(3)]
        with pytest.raises(ValueError, match="Too many documents"):
            skill.build_content("query", sources)

    def test_from_bytes_encodes_correctly(self):
        raw = b"\x89PNG\r\n"
        source = VisionSkill.from_bytes(raw, media_type="image/png", label="chart")
        decoded = base64.standard_b64decode(source.data)
        assert decoded == raw
        assert source.media_type == "image/png"
        assert source.label == "chart"

    def test_load_file_infers_media_type(self, tmp_path):
        png_file = tmp_path / "test.png"
        png_file.write_bytes(b"\x89PNG\r\n\x1a\n")
        source = VisionSkill.load_file(str(png_file))
        assert source.media_type == "image/png"
        assert source.label == "test.png"

    def test_load_file_unknown_extension_raises(self, tmp_path):
        weird_file = tmp_path / "test.xyz"
        weird_file.write_bytes(b"data")
        with pytest.raises(ValueError, match="Cannot infer media type"):
            VisionSkill.load_file(str(weird_file))


# ---------------------------------------------------------------------------
# StructuredOutputSkill
# ---------------------------------------------------------------------------

class TestStructuredOutputSkill:
    def _simple_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {"value": {"type": "number"}},
            "required": ["value"],
        }

    def test_build_api_kwargs_sets_tool_and_tool_choice(self):
        skill = StructuredOutputSkill(output_schema=self._simple_schema())
        kwargs = skill.build_api_kwargs("Extract the value")
        assert "tools" in kwargs
        assert len(kwargs["tools"]) == 1
        tool = kwargs["tools"][0]
        assert tool["name"] == "emit_result"
        assert tool["description"] == "Extract the value"
        assert "tool_choice" in kwargs
        assert kwargs["tool_choice"]["type"] == "tool"

    def test_parse_response_extracts_dict(self):
        block = SimpleNamespace(
            type="tool_use",
            name="emit_result",
            input={"value": 42},
        )
        response = SimpleNamespace(content=[block])
        result = StructuredOutputSkill.parse_response(response)
        assert result == {"value": 42}

    def test_parse_response_json_string_input(self):
        block = SimpleNamespace(
            type="tool_use",
            name="emit_result",
            input='{"value": 99}',
        )
        response = SimpleNamespace(content=[block])
        result = StructuredOutputSkill.parse_response(response)
        assert result == {"value": 99}

    def test_parse_response_no_matching_block_returns_none(self):
        text_block = SimpleNamespace(type="text", text="hello")
        response = SimpleNamespace(content=[text_block])
        result = StructuredOutputSkill.parse_response(response)
        assert result is None

    def test_journal_entry_schema_factory(self):
        skill = StructuredOutputSkill.journal_entry_schema()
        schema = skill.output_schema
        assert "entries" in schema["properties"]
        assert "narrative" in schema["properties"]
        assert "reporting_basis" in schema["properties"]

    def test_risk_assessment_schema_factory(self):
        skill = StructuredOutputSkill.risk_assessment_schema()
        schema = skill.output_schema
        assert "risk_rating" in schema["properties"]
        assert "risk_factors" in schema["properties"]

    def test_financial_metrics_schema_factory(self):
        skill = StructuredOutputSkill.financial_metrics_schema()
        schema = skill.output_schema
        assert "metrics" in schema["properties"]
        assert "currency" in schema["properties"]

    def test_custom_tool_name(self):
        skill = StructuredOutputSkill(
            output_schema=self._simple_schema(),
            tool_name="my_custom_tool",
        )
        kwargs = skill.build_api_kwargs()
        assert kwargs["tools"][0]["name"] == "my_custom_tool"
        assert kwargs["tool_choice"]["name"] == "my_custom_tool"


# ---------------------------------------------------------------------------
# Config: SkillsConfig
# ---------------------------------------------------------------------------

class TestSkillsConfig:
    def test_skills_config_defaults(self):
        from rudra.config import SkillsConfig
        cfg = SkillsConfig()
        assert cfg.thinking_budget_tokens == 10_000
        assert cfg.cache_type == "ephemeral"
        assert cfg.vision_max_documents == 5
        assert cfg.enabled is True

    def test_rudra_config_includes_skills(self):
        from rudra.config import RudraConfig
        cfg = RudraConfig()
        assert hasattr(cfg, "skills")
        from rudra.config import SkillsConfig
        assert isinstance(cfg.skills, SkillsConfig)


# ---------------------------------------------------------------------------
# Models: SkillType, SkillInvocation
# ---------------------------------------------------------------------------

try:
    import pydantic as _pydantic
    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False

_skip_no_pydantic = pytest.mark.skipif(not _HAS_PYDANTIC, reason="pydantic not installed")


@_skip_no_pydantic
class TestSkillModels:
    def test_skill_type_values(self):
        from rudra.models import SkillType
        assert SkillType.EXTENDED_THINKING == "extended_thinking"
        assert SkillType.PROMPT_CACHING == "prompt_caching"
        assert SkillType.VISION == "vision"
        assert SkillType.STRUCTURED_OUTPUT == "structured_output"

    def test_skill_invocation_model(self):
        from rudra.models import SkillInvocation, SkillType
        inv = SkillInvocation(
            skill_type=SkillType.EXTENDED_THINKING,
            agent_id="extended-thinking-analyst",
            params={"budget_tokens": 8000},
            result_summary="Analysis complete",
            tokens_used=1500,
            duration_ms=3200,
        )
        assert inv.succeeded is True
        assert inv.skill_type == SkillType.EXTENDED_THINKING
        assert inv.tokens_used == 1500
