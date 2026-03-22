"""Base model interface — all model integrations implement this contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelResponse:
    """Unified response object returned by every model provider."""

    text: str
    model: str
    usage: dict[str, int]
    stop_reason: str = "end_turn"
    thinking: str | None = None
    tool_calls: list[dict] | None = None
    raw: Any = field(default=None, repr=False)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)

    def __str__(self) -> str:
        return self.text


class BaseModel(ABC):
    """Abstract base — all model integrations must implement complete()."""

    @abstractmethod
    def complete(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ModelResponse:
        ...

    @property
    @abstractmethod
    def provider(self) -> str:
        ...

    def user_message(self, content: str) -> dict:
        return {"role": "user", "content": content}

    def assistant_message(self, content: str) -> dict:
        return {"role": "assistant", "content": content}
