"""ModelRouter — selects the best model for each task type.

Routing logic:
  Claude  → Deep accounting reasoning, ERP/EPM design, M&A, audit
  OpenClaw → Orchestration, routing, summarization, structured extraction
  Qwen     → Multilingual reports, financial data extraction, code generation
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import yaml

from .base_model import BaseModel, ModelResponse
from .claude_model import ClaudeModel
from .openai_model import OpenClawModel
from .qwen_model import QwenModel

if TYPE_CHECKING:
    pass


# Task categories and their preferred model
TASK_MODEL_MAP: dict[str, str] = {
    # Claude — complex reasoning tasks
    "accounting_policy": "claude",
    "revenue_recognition": "claude",
    "lease_accounting": "claude",
    "tax_accounting": "claude",
    "ma_due_diligence": "claude",
    "consolidation": "claude",
    "epm_modeling": "claude",
    "erp_design": "claude",
    "audit": "claude",
    "financial_modeling": "claude",
    "coa_design": "claude",
    "treasury": "claude",
    "esg": "claude",
    # OpenClaw — orchestration and fast structured tasks
    "orchestration": "openclaw",
    "agent_routing": "openclaw",
    "summarization": "openclaw",
    "structured_extraction": "openclaw",
    "classification": "openclaw",
    # Qwen — multilingual and code
    "multilingual_report": "qwen",
    "financial_data_extraction": "qwen",
    "code_generation": "qwen",
    "data_pipeline": "qwen",
}


class ModelRouter:
    """Instantiates and routes requests to the appropriate model."""

    def __init__(self, config_path: str | None = None):
        cfg = self._load_config(config_path)
        models_cfg = cfg.get("models", {})

        self._models: dict[str, BaseModel] = {
            "claude": ClaudeModel(
                model_id=models_cfg.get("claude", {}).get("model_id", "claude-opus-4-6"),
                max_tokens=models_cfg.get("claude", {}).get("max_tokens", 16000),
                thinking=models_cfg.get("claude", {}).get("thinking", {"type": "adaptive"}),
                output_config=models_cfg.get("claude", {}).get("output_config", {"effort": "high"}),
            ),
            "openclaw": OpenClawModel(
                model_id=models_cfg.get("openclaw", {}).get("model_id", "gpt-4o"),
                base_url=models_cfg.get("openclaw", {}).get("base_url"),
                max_tokens=models_cfg.get("openclaw", {}).get("max_tokens", 8000),
            ),
            "qwen": QwenModel(
                model_id=models_cfg.get("qwen", {}).get("model_id", "qwen-max"),
                max_tokens=models_cfg.get("qwen", {}).get("max_tokens", 8000),
            ),
        }

        routing_cfg = cfg.get("routing", {})
        self._task_map = {**TASK_MODEL_MAP, **routing_cfg.get("task_model_map", {})}
        self._default = routing_cfg.get("default_model", "claude")

    def _load_config(self, path: str | None) -> dict:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        try:
            with open(path) as f:
                raw = yaml.safe_load(f)
            # Resolve ${ENV_VAR} placeholders
            import re

            def resolve(obj: object) -> object:
                if isinstance(obj, str):
                    return re.sub(
                        r"\$\{([^}]+)\}",
                        lambda m: os.environ.get(m.group(1), m.group(0)),
                        obj,
                    )
                if isinstance(obj, dict):
                    return {k: resolve(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [resolve(i) for i in obj]
                return obj

            return resolve(raw)  # type: ignore[return-value]
        except FileNotFoundError:
            return {}

    def get_model(self, task: str | None = None) -> BaseModel:
        """Return the best model for the given task."""
        key = self._task_map.get(task or "", self._default)
        return self._models[key]

    def complete(
        self,
        messages: list[dict],
        task: str | None = None,
        system: str | None = None,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> ModelResponse:
        """Route and execute — returns a unified ModelResponse."""
        model = self.get_model(task)
        return model.complete(messages, system=system, tools=tools, **kwargs)

    @property
    def models(self) -> dict[str, BaseModel]:
        return self._models
