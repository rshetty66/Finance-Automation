"""
Central configuration for the Rudra framework.

Reads from environment variables with sensible defaults. All config is
gathered into a single frozen dataclass so the rest of the codebase
never touches os.environ directly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ModelConfig:
    """LLM provider settings."""

    provider: str = "anthropic"
    default_model: str = "claude-sonnet-4-20250514"
    fast_model: str = "claude-haiku-4-5-20250514"
    reasoning_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 8096
    temperature: float = 0.2


@dataclass(frozen=True)
class EmbeddingConfig:
    """Embedding model settings for the vector-search router."""

    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    device: str = "cpu"


@dataclass(frozen=True)
class MemoryConfig:
    """Context and memory budget settings."""

    max_context_tokens: int = 100_000
    max_agent_tokens: int = 16_000
    session_dir: str = ".rudra/sessions"


@dataclass(frozen=True)
class RudraConfig:
    """Root configuration object."""

    agents_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "Rudra_Agents")
    models: ModelConfig = field(default_factory=ModelConfig)
    embeddings: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY"))
    log_level: str = field(default_factory=lambda: os.environ.get("RUDRA_LOG_LEVEL", "INFO"))

    @classmethod
    def from_env(cls) -> "RudraConfig":
        return cls(
            agents_dir=Path(os.environ.get("RUDRA_AGENTS_DIR", cls.agents_dir.fget())),  # type: ignore[arg-type]
            models=ModelConfig(
                default_model=os.environ.get("RUDRA_DEFAULT_MODEL", ModelConfig.default_model),
                fast_model=os.environ.get("RUDRA_FAST_MODEL", ModelConfig.fast_model),
            ),
            embeddings=EmbeddingConfig(
                model_name=os.environ.get("RUDRA_EMBEDDING_MODEL", EmbeddingConfig.model_name),
            ),
        )


_config: Optional[RudraConfig] = None


def get_config() -> RudraConfig:
    global _config
    if _config is None:
        _config = RudraConfig()
    return _config


def set_config(config: RudraConfig) -> None:
    global _config
    _config = config
