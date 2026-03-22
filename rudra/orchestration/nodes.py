"""
Graph node functions for the Rudra LangGraph orchestration.

Each function takes a GraphState dict and returns a partial state update.
The orchestrator wires these into a StateGraph with conditional edges.
"""

from __future__ import annotations

import logging
from typing import Any

from rudra.models import AgentRequest, ReportingBasis, OutputFormat, Audience

logger = logging.getLogger(__name__)


class NodeFunctions:
    """
    Stateful node function container.

    Holds references to the registry, router, and invoker so node functions
    can access them without globals.
    """

    def __init__(self, registry, router, invoker) -> None:
        self.registry = registry
        self.router = router
        self.invoker = invoker

    def router_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """Semantic routing   select the best agent(s) for the query."""
        decision = self.router.route(state["query"])

        return {
            "primary_agent": decision.primary_agent.agent_id,
            "secondary_agents": [a.agent_id for a in decision.secondary_agents],
            "routing_confidence": decision.primary_agent.confidence,
            "routing_intent": decision.intent,
            "current_step": "routed",
        }

    async def agent_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke the primary agent with the user query.

        This is the generic agent execution node. The graph's conditional
        edges route to this node after the router selects an agent.
        """
        agent_id = state.get("active_agent") or state.get("primary_agent", "rudra")
        agent = self.registry.get(agent_id)

        if agent is None:
            logger.error("Agent '%s' not found in registry", agent_id)
            return {
                "error": f"Agent '{agent_id}' not found",
                "current_step": "error",
            }

        agent.bind_invoker(self.invoker)

        request = AgentRequest(
            agent_id=agent_id,
            query=state["query"],
            facts=str(state.get("normalized_facts", {})),
            reporting_basis=ReportingBasis(state.get("reporting_basis", "BOTH")),
            output_format=OutputFormat(state.get("output_format", "narrative")),
            audience=Audience(state.get("audience", "controller")),
            context={
                "prior_outputs": {
                    k: v.get("response", "")[:2000] if isinstance(v, dict) else str(v)[:2000]
                    for k, v in state.get("agent_outputs", {}).items()
                }
            },
            session_id=state.get("session_id", ""),
        )

        result = await agent.invoke(request)

        needs_review = _check_needs_review(agent_id, result.response)

        return {
            "agent_outputs": {agent_id: result.model_dump()},
            "citations": result.citations,
            "requires_human_review": needs_review,
            "current_step": f"completed_{agent_id}",
        }

    async def secondary_agents_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke secondary agents (if any) after the primary agent completes.
        Runs them sequentially for now; parallel execution is a future enhancement.
        """
        import asyncio

        secondary_ids = state.get("secondary_agents", [])
        if not secondary_ids:
            return {"current_step": "no_secondary"}

        outputs: dict[str, Any] = {}
        all_citations: list[str] = []

        for agent_id in secondary_ids[:3]:  # cap at 3 to control costs
            agent = self.registry.get(agent_id)
            if agent is None:
                continue

            agent.bind_invoker(self.invoker)
            request = AgentRequest(
                agent_id=agent_id,
                query=state["query"],
                facts=str(state.get("normalized_facts", {})),
                context={"primary_output": state.get("agent_outputs", {})},
                session_id=state.get("session_id", ""),
            )

            result = await agent.invoke(request)
            outputs[agent_id] = result.model_dump()
            all_citations.extend(result.citations)

        return {
            "agent_outputs": outputs,
            "citations": all_citations,
            "current_step": "secondary_complete",
        }

    def hitl_checkpoint(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Human-in-the-loop checkpoint.

        In a real deployment, this would interrupt the graph and wait
        for human feedback.  For now, it passes through with a flag.
        """
        if state.get("requires_human_review"):
            logger.info("HITL checkpoint reached   human review required")
            return {
                "current_step": "awaiting_human_review",
            }
        return {"current_step": "hitl_passed"}

    async def synthesizer_node(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Synthesize outputs from all agents into a final response.

        Uses the primary Rudra agent to synthesize if multiple agents
        contributed, or passes through single-agent output directly.
        """
        outputs = state.get("agent_outputs", {})

        if len(outputs) <= 1:
            for agent_id, output in outputs.items():
                response = output.get("response", "") if isinstance(output, dict) else str(output)
                return {
                    "final_response": response,
                    "current_step": "complete",
                }
            return {"final_response": "", "current_step": "complete"}

        synthesis_prompt = "Synthesize the following agent outputs into a coherent response:\n\n"
        for agent_id, output in outputs.items():
            response = output.get("response", "")[:3000] if isinstance(output, dict) else str(output)[:3000]
            synthesis_prompt += f"### {agent_id}\n{response}\n\n"

        synth_agent = self.registry.get("rudra")
        if synth_agent:
            synth_agent.bind_invoker(self.invoker)
            request = AgentRequest(
                agent_id="rudra",
                query=synthesis_prompt,
                session_id=state.get("session_id", ""),
            )
            result = await synth_agent.invoke(request)
            return {
                "final_response": result.response,
                "current_step": "complete",
            }

        combined = "\n\n---\n\n".join(
            f"**{aid}:**\n{o.get('response', '')}" if isinstance(o, dict) else f"**{aid}:**\n{o}"
            for aid, o in outputs.items()
        )
        return {"final_response": combined, "current_step": "complete"}


def _check_needs_review(agent_id: str, response: str) -> bool:
    """Determine if the output should go through HITL review."""
    high_stakes_agents = {
        "accounting-policy-engine",
        "revenue-recognition-agent",
        "ma-due-diligence-agent",
        "tax-accounting-agent",
        "internal-audit-agent",
    }
    if agent_id in high_stakes_agents:
        risk_phrases = [
            "material misstatement",
            "significant judgment",
            "high uncertainty",
            "alternative treatment",
            "consult your auditor",
        ]
        return any(phrase in response.lower() for phrase in risk_phrases)
    return False
