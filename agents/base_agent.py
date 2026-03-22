"""Base agent class — all Rudra specialist agents extend this."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentContext:
    """Shared context passed between agents in a workflow."""

    task: str
    facts: str
    reporting_basis: str = "IFRS"
    output_format: str = "narrative"
    audience: str = "controller"
    client_name: str = ""
    metadata: dict = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)


@dataclass
class AgentResult:
    """Structured result returned by any agent."""

    agent_name: str
    task: str
    output: str
    structured_data: dict | None = None
    tool_calls_made: list[dict] = field(default_factory=list)
    model_used: str = ""
    tokens_used: dict = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "agent": self.agent_name,
            "task": self.task,
            "output": self.output,
            "structured_data": self.structured_data,
            "model": self.model_used,
            "tokens": self.tokens_used,
            "elapsed": self.elapsed_seconds,
            "created_at": self.created_at,
        }

    def __str__(self) -> str:
        return self.output


class BaseAgent(ABC):
    """Foundation for all Rudra specialist agents."""

    name: str = "base_agent"
    description: str = "Base agent"

    def __init__(self, model_router=None):
        self._router = model_router
        self._tool_registry: dict[str, Any] = {}

    def register_tool(self, name: str, callable_: Any) -> None:
        self._tool_registry[name] = callable_

    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent's primary task."""
        ...

    def _build_messages(self, prompt: str, context: AgentContext) -> list[dict]:
        messages = []
        # Include conversation history if available
        for h in context.history[-4:]:  # last 4 turns
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a registered tool and return the result as a string."""
        if tool_name not in self._tool_registry:
            return f"Tool '{tool_name}' not found in registry"
        try:
            result = self._tool_registry[tool_name](**tool_input)
            if isinstance(result, (dict, list)):
                return json.dumps(result, indent=2, default=str)
            return str(result)
        except Exception as exc:
            return f"Tool error: {exc}"

    def _run_tool_loop(
        self,
        model,
        messages: list[dict],
        system: str,
        tools: list[dict],
        max_iterations: int = 5,
    ) -> tuple[str, list[dict]]:
        """Standard agentic tool-use loop compatible with Claude and OpenClaw."""
        import time

        tool_calls_made = []
        final_text = ""

        for _ in range(max_iterations):
            response = model.complete(messages, system=system, tools=tools)
            final_text = response.text

            if not response.has_tool_calls:
                break

            # Process tool calls
            tool_results_content = []
            for tc in response.tool_calls:
                result = self._execute_tool(tc["name"], tc.get("input", {}))
                tool_calls_made.append({"tool": tc["name"], "input": tc["input"], "result": result[:200]})
                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": result,
                })

            # Append assistant response + tool results
            if hasattr(response.raw, "content"):
                # Claude format
                messages.append({"role": "assistant", "content": response.raw.content})
            else:
                messages.append({"role": "assistant", "content": response.text})

            messages.append({"role": "user", "content": tool_results_content})

        return final_text, tool_calls_made
