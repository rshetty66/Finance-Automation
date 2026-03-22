"""OpenClaw model — OpenAI-compatible interface for orchestration & routing.

'OpenClaw' uses the OpenAI SDK with a swappable backend:
  • Default: OpenAI GPT-4o
  • Self-hosted: any OpenAI-compatible endpoint (LM Studio, Ollama, vLLM)
  • Cloud: Together AI, Groq, Mistral, etc.
"""

import os
from typing import Any

import openai

from .base_model import BaseModel, ModelResponse


class OpenClawModel(BaseModel):
    """OpenAI-compatible model used for orchestration, routing and fast inference."""

    def __init__(
        self,
        model_id: str = "gpt-4o",
        base_url: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 8000,
    ):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self._client = openai.OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY", ""),
            base_url=base_url,  # None = OpenAI default
        )

    def complete(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ModelResponse:
        """Call OpenAI-compatible API and return unified ModelResponse."""
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
            # Convert Anthropic-style tools to OpenAI function format
            params["tools"] = [self._convert_tool(t) for t in tools]
            params["tool_choice"] = "auto"

        response = self._client.chat.completions.create(**params)
        return self._parse_response(response)

    def _convert_tool(self, tool: dict) -> dict:
        """Convert Anthropic-style tool schema to OpenAI function format."""
        return {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
            },
        }

    def _parse_response(self, response: Any) -> ModelResponse:
        choice = response.choices[0]
        message = choice.message
        text = message.content or ""

        tool_calls = None
        if message.tool_calls:
            import json

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
        return "openai"
