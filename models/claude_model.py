"""Anthropic Claude integration — primary reasoning model for complex ERP/EPM analysis."""

import os
from typing import Any

import anthropic

from .base_model import BaseModel, ModelResponse


class ClaudeModel(BaseModel):
    """Claude Opus 4.6 with adaptive thinking for deep accounting/ERP reasoning."""

    def __init__(
        self,
        model_id: str = "claude-opus-4-6",
        max_tokens: int = 16000,
        thinking: dict | None = None,
        output_config: dict | None = None,
    ):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.thinking = thinking or {"type": "adaptive"}
        self.output_config = output_config or {"effort": "high"}
        self._client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

    def complete(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ModelResponse:
        """Send a request to Claude and return a unified ModelResponse."""
        params: dict[str, Any] = {
            "model": self.model_id,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": messages,
            "thinking": self.thinking,
            "output_config": self.output_config,
        }
        if system:
            params["system"] = system
        if tools:
            params["tools"] = tools

        if stream:
            return self._stream(params)

        response = self._client.messages.create(**params)
        return self._parse_response(response)

    def _stream(self, params: dict) -> ModelResponse:
        """Stream response and collect full message."""
        with self._client.messages.stream(**params) as stream:
            full_response = stream.get_final_message()
        return self._parse_response(full_response)

    def _parse_response(self, response: anthropic.types.Message) -> "ModelResponse":
        text_blocks = []
        thinking_blocks = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_blocks.append(block.text)
            elif block.type == "thinking":
                thinking_blocks.append(block.thinking)
            elif block.type == "tool_use":
                tool_calls.append(
                    {"id": block.id, "name": block.name, "input": block.input}
                )

        return ModelResponse(
            text="\n".join(text_blocks),
            thinking="\n".join(thinking_blocks) if thinking_blocks else None,
            tool_calls=tool_calls or None,
            stop_reason=response.stop_reason,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            raw=response,
        )

    @property
    def provider(self) -> str:
        return "anthropic"
