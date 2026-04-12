"""
ToolRegistry   centralized catalog of tools available to Rudra agents.

Each tool has a name, description, parameter schema, and an implementation
function.  The registry enforces agent-level permissions: an agent can only
invoke tools listed in its AgentSpec.tools.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """A single tool in the registry."""
    name: str
    description: str
    parameters: dict[str, Any]
    function: Optional[Callable] = None
    is_async: bool = False


class ToolRegistry:
    """
    Central tool catalog.

    Usage::

        registry = ToolRegistry.default()
        result = await registry.invoke("search_standards", query="IFRS 16")
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s", tool.name)

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def get_tools_for_agent(self, agent_tool_names: list[str]) -> list[ToolDefinition]:
        """Return only the tools an agent is permitted to use."""
        return [self._tools[name] for name in agent_tool_names if name in self._tools]

    async def invoke(self, tool_name: str, **kwargs: Any) -> Any:
        tool = self._tools.get(tool_name)
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        if tool.function is None:
            raise ValueError(f"Tool '{tool_name}' has no implementation")

        if tool.is_async:
            return await tool.function(**kwargs)
        return tool.function(**kwargs)

    def to_anthropic_tools(self, tool_names: Optional[list[str]] = None) -> list[dict]:
        """Convert tools to Anthropic tool_use format for LLM calls."""
        tools = self._tools.values() if tool_names is None else self.get_tools_for_agent(tool_names)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": {
                    "type": "object",
                    "properties": tool.parameters,
                },
            }
            for tool in tools
        ]

    @classmethod
    def default(cls) -> "ToolRegistry":
        """Create the default tool registry with all built-in tools."""
        registry = cls()

        from rudra.tools.standards import search_standards
        from rudra.tools.benchmarks import get_apqc_benchmark
        from rudra.tools.analytics import run_analytics_query

        registry.register(ToolDefinition(
            name="search_standards",
            description="Search IFRS and US GAAP accounting standards passages",
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "category": {"type": "string", "description": "IFRS | US_GAAP | POLICIES"},
                "k": {"type": "integer", "description": "Number of results"},
            },
            function=search_standards,
        ))

        registry.register(ToolDefinition(
            name="get_apqc_benchmark",
            description="Retrieve APQC benchmark data for a finance process metric",
            parameters={
                "metric": {"type": "string", "description": "Metric name"},
                "industry": {"type": "string", "description": "Industry filter"},
                "percentile": {"type": "string", "description": "top_25 | median | bottom_25"},
            },
            function=get_apqc_benchmark,
        ))

        registry.register(ToolDefinition(
            name="run_analytics",
            description="Run a finance analytics query",
            parameters={
                "query_type": {"type": "string", "description": "close_metrics | ar_aging | variance"},
                "entity_id": {"type": "string", "description": "Entity identifier"},
                "period": {"type": "string", "description": "Period (yyyy-MM)"},
            },
            function=run_analytics_query,
        ))

        registry.register(ToolDefinition(
            name="read_file",
            description="Read a file from the workspace",
            parameters={
                "path": {"type": "string", "description": "File path"},
            },
            function=_read_file,
        ))

        registry.register(ToolDefinition(
            name="write_file",
            description="Write content to a file",
            parameters={
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "File content"},
            },
            function=_write_file,
        ))

        registry.register(ToolDefinition(
            name="spawn_agent",
            description="Spawn a sub-agent for a focused task",
            parameters={
                "agent_id": {"type": "string", "description": "Agent to spawn"},
                "task": {"type": "string", "description": "Task description"},
                "context": {"type": "string", "description": "Context to pass"},
            },
        ))

        registry.register(ToolDefinition(
            name="web_search",
            description="Search public URLs for verification",
            parameters={
                "query": {"type": "string", "description": "Search query"},
            },
        ))

        registry.register(ToolDefinition(
            name="generate_html",
            description="Generate HTML/CSS prototypes",
            parameters={
                "spec": {"type": "string", "description": "Design specification"},
            },
        ))

        registry.register(ToolDefinition(
            name="run_financial_model",
            description="Execute a financial model (DCF, LBO, etc.)",
            parameters={
                "model_type": {"type": "string", "description": "DCF | LBO | three_statement"},
                "assumptions": {"type": "object", "description": "Model assumptions"},
            },
        ))

        # ------------------------------------------------------------------
        # Claude Superpower Skill tools
        # ------------------------------------------------------------------

        registry.register(ToolDefinition(
            name="invoke_extended_thinking",
            description=(
                "Invoke Claude's extended thinking skill for deep multi-step "
                "financial reasoning. Returns both the chain-of-thought and "
                "the final answer. Use for complex IFRS/US GAAP analysis, "
                "M&A accounting, ECL modelling, or multi-entity consolidation."
            ),
            parameters={
                "query": {"type": "string", "description": "The analytical question or scenario"},
                "agent_id": {"type": "string", "description": "Agent to invoke (defaults to extended-thinking-analyst)"},
                "budget_tokens": {"type": "integer", "description": "Thinking token budget (1000-32000, default 10000)"},
            },
            function=_invoke_extended_thinking_tool,
            is_async=True,
        ))

        registry.register(ToolDefinition(
            name="analyze_financial_document",
            description=(
                "Analyze a financial document or image using Claude's vision "
                "skill. Accepts a local file path (PNG, JPEG, PDF) and a "
                "text query. Returns extracted data, key figures, and insights."
            ),
            parameters={
                "file_path": {"type": "string", "description": "Path to image or PDF file"},
                "query": {"type": "string", "description": "What to extract or analyze"},
                "agent_id": {"type": "string", "description": "Agent to use (defaults to document-vision-agent)"},
            },
            function=_analyze_financial_document_tool,
            is_async=True,
        ))

        registry.register(ToolDefinition(
            name="extract_structured_financials",
            description=(
                "Extract structured financial data from free-form text using "
                "Claude's structured output skill. Returns a typed JSON "
                "payload guaranteed to match the requested schema: "
                "journal_entry | risk_assessment | financial_metrics."
            ),
            parameters={
                "text": {"type": "string", "description": "Source text to extract from"},
                "schema_type": {
                    "type": "string",
                    "description": "journal_entry | risk_assessment | financial_metrics",
                },
                "agent_id": {"type": "string", "description": "Agent to use (defaults to accounting-policy-engine)"},
            },
            function=_extract_structured_financials_tool,
            is_async=True,
        ))

        return registry


# ---------------------------------------------------------------------------
# Superpower Skill tool implementations
# ---------------------------------------------------------------------------

async def _invoke_extended_thinking_tool(
    query: str,
    agent_id: str = "extended-thinking-analyst",
    budget_tokens: int = 10_000,
) -> dict:
    """Tool implementation: invoke the extended thinking skill."""
    from rudra.agents.invoker import AgentInvoker
    from rudra.agents.registry import AgentRegistry

    registry = AgentRegistry.from_default_dir()
    agent = registry.get(agent_id)
    if agent is None:
        # Fall back to first available agent if the specialist isn't loaded
        agents = registry.list_agents()
        if not agents:
            return {"error": f"Agent '{agent_id}' not found and no agents available"}
        agent = agents[0]

    invoker = AgentInvoker()
    from rudra.models import AgentRequest
    request = AgentRequest(agent_id=agent.spec.id, query=query)
    messages = [{"role": "user", "content": query}]

    result = await invoker.call_llm_with_skill(
        agent_spec=agent.spec,
        messages=messages,
        request=request,
        skill_type="extended_thinking",
        skill_params={"budget_tokens": budget_tokens},
    )
    return {
        "answer": result.response,
        "thinking_summary": result.structured_output.get("thinking", "")[:500],
        "tokens_used": result.tokens_used,
        "model": result.model_used,
    }


async def _analyze_financial_document_tool(
    file_path: str,
    query: str,
    agent_id: str = "document-vision-agent",
) -> dict:
    """Tool implementation: analyze a financial document with vision."""
    from rudra.skills.vision import VisionSkill
    from rudra.agents.invoker import AgentInvoker
    from rudra.agents.registry import AgentRegistry
    from rudra.models import AgentRequest

    registry = AgentRegistry.from_default_dir()
    agent = registry.get(agent_id)
    if agent is None:
        agents = registry.list_agents()
        if not agents:
            return {"error": f"Agent '{agent_id}' not found"}
        agent = agents[0]

    try:
        source = VisionSkill.load_file(file_path)
    except (ValueError, FileNotFoundError) as exc:
        return {"error": str(exc)}

    skill = VisionSkill()
    content = skill.build_content(text_query=query, documents=[source])
    messages = [{"role": "user", "content": content}]

    invoker = AgentInvoker()
    request = AgentRequest(agent_id=agent.spec.id, query=query)

    result = await invoker.call_llm_with_skill(
        agent_spec=agent.spec,
        messages=messages,
        request=request,
        skill_type="vision",
    )
    return {
        "analysis": result.response,
        "tokens_used": result.tokens_used,
        "model": result.model_used,
    }


async def _extract_structured_financials_tool(
    text: str,
    schema_type: str,
    agent_id: str = "accounting-policy-engine",
) -> dict:
    """Tool implementation: extract structured financial data."""
    from rudra.skills.structured_output import StructuredOutputSkill
    from rudra.agents.invoker import AgentInvoker
    from rudra.agents.registry import AgentRegistry
    from rudra.models import AgentRequest

    schema_map = {
        "journal_entry": StructuredOutputSkill.journal_entry_schema,
        "risk_assessment": StructuredOutputSkill.risk_assessment_schema,
        "financial_metrics": StructuredOutputSkill.financial_metrics_schema,
    }
    factory = schema_map.get(schema_type)
    if factory is None:
        return {
            "error": f"Unknown schema_type '{schema_type}'. "
                     f"Valid values: {list(schema_map.keys())}"
        }

    skill = factory()

    registry = AgentRegistry.from_default_dir()
    agent = registry.get(agent_id)
    if agent is None:
        agents = registry.list_agents()
        if not agents:
            return {"error": f"Agent '{agent_id}' not found"}
        agent = agents[0]

    invoker = AgentInvoker()
    request = AgentRequest(agent_id=agent.spec.id, query=text)
    messages = [{"role": "user", "content": text}]

    result = await invoker.call_llm_with_skill(
        agent_spec=agent.spec,
        messages=messages,
        request=request,
        skill_type="structured_output",
        skill_params={
            "output_schema": skill.output_schema,
            "description": f"Extract {schema_type} data from the provided text.",
        },
    )
    return result.structured_output


def _read_file(path: str) -> str:
    from pathlib import Path
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return f"File not found: {path}"


def _write_file(path: str, content: str) -> str:
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {path}"
