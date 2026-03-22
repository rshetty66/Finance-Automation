"""Qwen 2.5 integration via Alibaba DashScope (OpenAI-compatible API).

Qwen 2.5 models available:
  qwen-max       — Most capable, best for financial reasoning
  qwen-plus      — Balanced performance/cost
  qwen-turbo     — Fastest, lowest cost
  qwen2.5-72b-instruct — Open-source via HuggingFace Inference API

DashScope API is OpenAI-compatible, so we use the openai SDK with a custom base_url.
"""

import os
from typing import Any

import openai

from .base_model import BaseModel, ModelResponse


DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class QwenModel(BaseModel):
    """Qwen 2.5 — multilingual financial data analysis and code generation."""

    def __init__(
        self,
        model_id: str = "qwen-max",
        api_key: str | None = None,
        max_tokens: int = 8000,
    ):
        self.model_id = model_id
        self.max_tokens = max_tokens
        resolved_key = api_key or os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY", "")
        self._client = openai.OpenAI(
            api_key=resolved_key,
            base_url=DASHSCOPE_BASE_URL,
        )

    def complete(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ModelResponse:
        """Call Qwen 2.5 via DashScope and return unified ModelResponse."""
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        params: dict[str, Any] = {
            "model": self.model_id,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": all_messages,
        }
        if tools:
            params["tools"] = [self._convert_tool(t) for t in tools]
            params["tool_choice"] = "auto"

        if stream:
            return self._stream(params)

        response = self._client.chat.completions.create(**params)
        return self._parse_response(response)

    def _stream(self, params: dict) -> ModelResponse:
        params["stream"] = True
        stream = self._client.chat.completions.create(**params)
        chunks = []
        model_name = self.model_id
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                chunks.append(chunk.choices[0].delta.content)
            if chunk.model:
                model_name = chunk.model
        return ModelResponse(
            text="".join(chunks),
            model=model_name,
            usage={"input_tokens": 0, "output_tokens": len(chunks)},
            stop_reason="end_turn",
        )

    def _convert_tool(self, tool: dict) -> dict:
        return {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
            },
        }

    def _parse_response(self, response: Any) -> ModelResponse:
        import json

        choice = response.choices[0]
        message = choice.message
        text = message.content or ""
        tool_calls = None
        if getattr(message, "tool_calls", None):
            tool_calls = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": json.loads(tc.function.arguments),
                }
                for tc in message.tool_calls
            ]
        return ModelResponse(
            text=text,
            model=response.model,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            },
            stop_reason=choice.finish_reason or "end_turn",
            tool_calls=tool_calls,
            raw=response,
        )

    @property
    def provider(self) -> str:
        return "qwen"
