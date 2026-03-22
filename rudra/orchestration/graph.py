"""
RudraGraph - the main LangGraph state machine.

Wires together routing, agent execution, HITL checkpoints, and synthesis
into a single executable graph. Supports all 27 agents through a
dynamic routing pattern (rather than hard-coding one node per agent).
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from rudra.agents.invoker import AgentInvoker
from rudra.agents.registry import AgentRegistry
from rudra.orchestration.nodes import NodeFunctions
from rudra.orchestration.state import GraphState, initial_state
from rudra.routing.router import VectorSearchRouter

logger = logging.getLogger(__name__)


class RudraGraph:
    """
    Main orchestration graph for the Rudra framework.

    Builds a LangGraph StateGraph that routes queries to the best agent(s),
    executes them, optionally gates through HITL review, and synthesizes
    a final response.

    Usage::

        graph = RudraGraph.build(registry, router, invoker)
        result = await graph.run("Analyze our lease portfolio under IFRS 16")
    """

    def __init__(self, compiled_graph: Any, nodes: NodeFunctions) -> None:
        self._graph = compiled_graph
        self._nodes = nodes

    @classmethod
    def build(
        cls,
        registry: AgentRegistry,
        router: VectorSearchRouter,
        invoker: AgentInvoker,
    ) -> "RudraGraph":
        """Construct and compile the LangGraph state machine."""
        try:
            from langgraph.graph import StateGraph, END
        except ImportError:
            raise ImportError(
                "langgraph is required for orchestration. "
                "Install with: pip install langgraph"
            )

        nodes = NodeFunctions(registry, router, invoker)

        graph = StateGraph(dict)

        graph.add_node("router", nodes.router_node)
        graph.add_node("primary_agent", nodes.agent_node)
        graph.add_node("secondary_agents", nodes.secondary_agents_node)
        graph.add_node("hitl_checkpoint", nodes.hitl_checkpoint)
        graph.add_node("synthesizer", nodes.synthesizer_node)

        graph.set_entry_point("router")

        graph.add_edge("router", "primary_agent")

        def _should_run_secondary(state: dict) -> str:
            if state.get("secondary_agents"):
                return "secondary_agents"
            return "hitl_checkpoint"

        graph.add_conditional_edges(
            "primary_agent",
            _should_run_secondary,
            {
                "secondary_agents": "secondary_agents",
                "hitl_checkpoint": "hitl_checkpoint",
            },
        )

        graph.add_edge("secondary_agents", "hitl_checkpoint")

        def _hitl_decision(state: dict) -> str:
            return "synthesizer"

        graph.add_conditional_edges(
            "hitl_checkpoint",
            _hitl_decision,
            {"synthesizer": "synthesizer"},
        )

        graph.add_edge("synthesizer", END)

        compiled = graph.compile()
        logger.info("Rudra orchestration graph compiled successfully")

        return cls(compiled, nodes)

    async def run(
        self,
        query: str,
        reporting_basis: str = "BOTH",
        output_format: str = "narrative",
        audience: str = "controller",
        session_id: str = "",
    ) -> dict[str, Any]:
        """Execute the full orchestration pipeline."""
        import uuid

        state = initial_state(
            query=query,
            reporting_basis=reporting_basis,
            output_format=output_format,
            audience=audience,
            session_id=session_id or str(uuid.uuid4()),
        )

        final_state = await self._graph.ainvoke(state)
        return final_state

    async def stream(
        self,
        query: str,
        reporting_basis: str = "BOTH",
        output_format: str = "narrative",
        audience: str = "controller",
        session_id: str = "",
    ):
        """Stream the orchestration execution, yielding state updates."""
        import uuid

        state = initial_state(
            query=query,
            reporting_basis=reporting_basis,
            output_format=output_format,
            audience=audience,
            session_id=session_id or str(uuid.uuid4()),
        )

        async for chunk in self._graph.astream(state):
            yield chunk
