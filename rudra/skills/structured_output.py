"""
Structured Output Skill.

Forces Claude to return a typed JSON payload by pinning ``tool_use`` to a
caller-supplied JSON Schema.  This guarantees machine-readable outputs for
downstream finance systems, ERP integrations, and automated workflows.

How it works:
  1. The caller defines a JSON Schema describing the expected output shape.
  2. The skill registers this schema as a single tool named ``emit_result``.
  3. ``tool_choice`` is set to ``{"type": "tool", "name": "emit_result"}``
     so Claude is *required* to call the tool (no free-text fallback).
  4. The tool-call arguments are the structured JSON output.

This approach works with all Claude models that support tool use and avoids
brittle regex / JSON extraction from free-text responses.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# The synthetic tool name used to capture structured output
_EMIT_TOOL_NAME = "emit_result"


class StructuredOutputSkill:
    """
    Superpower Skill: Structured Output.

    Usage::

        schema = {
            "type": "object",
            "properties": {
                "journal_entries": {"type": "array", ...},
                "ifrs_standard":   {"type": "string"},
                "confidence":      {"type": "number"},
            },
            "required": ["journal_entries", "ifrs_standard"],
        }

        skill = StructuredOutputSkill(output_schema=schema)
        extra_kwargs = skill.build_api_kwargs(description="Produce journal entries")
        response = await client.messages.create(**base_kwargs, **extra_kwargs)
        result = StructuredOutputSkill.parse_response(response)
        # result is a plain Python dict matching the schema
    """

    def __init__(
        self,
        output_schema: dict[str, Any],
        tool_name: str = _EMIT_TOOL_NAME,
    ) -> None:
        self.output_schema = output_schema
        self.tool_name = tool_name

    def build_api_kwargs(
        self,
        description: str = "Emit the structured result",
    ) -> dict[str, Any]:
        """
        Return extra kwargs to merge into ``client.messages.create``.

        Sets ``tools`` (single emit tool) and ``tool_choice`` so Claude
        is forced to populate the schema before returning.
        """
        return {
            "tools": [
                {
                    "name": self.tool_name,
                    "description": description,
                    "input_schema": self.output_schema,
                }
            ],
            "tool_choice": {"type": "tool", "name": self.tool_name},
        }

    @staticmethod
    def parse_response(
        response: Any,
        tool_name: str = _EMIT_TOOL_NAME,
    ) -> Optional[dict[str, Any]]:
        """
        Extract the structured JSON from a tool-use response block.

        Returns the parsed dict, or ``None`` if no matching tool call found.
        """
        for block in response.content:
            if getattr(block, "type", None) == "tool_use" and block.name == tool_name:
                raw = getattr(block, "input", None)
                if isinstance(raw, dict):
                    return raw
                if isinstance(raw, str):
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError as exc:
                        logger.warning("Failed to parse tool input as JSON: %s", exc)
        return None

    # ------------------------------------------------------------------
    # Common finance schemas (convenience constructors)
    # ------------------------------------------------------------------

    @classmethod
    def journal_entry_schema(cls) -> "StructuredOutputSkill":
        """Pre-built schema for journal entry output."""
        schema = {
            "type": "object",
            "properties": {
                "entries": {
                    "type": "array",
                    "description": "List of journal entry lines",
                    "items": {
                        "type": "object",
                        "properties": {
                            "account_code": {"type": "string"},
                            "account_name": {"type": "string"},
                            "debit": {"type": "number"},
                            "credit": {"type": "number"},
                            "description": {"type": "string"},
                            "ifrs_reference": {"type": "string"},
                        },
                        "required": ["account_code", "account_name", "debit", "credit"],
                    },
                },
                "narrative": {
                    "type": "string",
                    "description": "Accounting rationale and standard references",
                },
                "standards_applied": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of IFRS/US GAAP standards applied",
                },
                "reporting_basis": {
                    "type": "string",
                    "enum": ["IFRS", "US_GAAP", "BOTH"],
                },
            },
            "required": ["entries", "narrative", "reporting_basis"],
        }
        return cls(output_schema=schema)

    @classmethod
    def risk_assessment_schema(cls) -> "StructuredOutputSkill":
        """Pre-built schema for financial risk assessment output."""
        schema = {
            "type": "object",
            "properties": {
                "risk_rating": {
                    "type": "string",
                    "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                },
                "risk_factors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "factor": {"type": "string"},
                            "impact": {"type": "string"},
                            "likelihood": {"type": "string"},
                            "mitigant": {"type": "string"},
                        },
                        "required": ["factor", "impact"],
                    },
                },
                "recommended_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                },
                "narrative": {"type": "string"},
            },
            "required": ["risk_rating", "risk_factors", "narrative"],
        }
        return cls(output_schema=schema)

    @classmethod
    def financial_metrics_schema(cls) -> "StructuredOutputSkill":
        """Pre-built schema for extracted financial metrics."""
        schema = {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "Reporting period (e.g. 2024-Q4)"},
                "entity": {"type": "string"},
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {"type": "number"},
                            "unit": {"type": "string"},
                            "benchmark": {"type": "number"},
                            "variance_pct": {"type": "number"},
                        },
                        "required": ["name", "value"],
                    },
                },
                "currency": {"type": "string"},
                "data_quality": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW"],
                },
            },
            "required": ["metrics", "currency"],
        }
        return cls(output_schema=schema)

    def __repr__(self) -> str:
        top_level_keys = list(self.output_schema.get("properties", {}).keys())
        return f"<StructuredOutputSkill fields={top_level_keys}>"
