"""OpenClaw Orchestrator — LangGraph-compatible state machine for multi-agent workflows.

OpenClaw implements the open-source orchestration layer using:
  • OpenAI-compatible API (GPT-4o or self-hosted models)
  • LangGraph state machine design
  • Semantic routing via vector similarity
  • Memory management (short-term, long-term, episodic)
  • Human-in-the-loop checkpoints

State graph:
  [START] → classify_task → route_agent → execute_agent → synthesize → [END]
                                ↑                ↓
                          vector_search ← tool_execution
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from .base_agent import AgentContext, AgentResult, BaseAgent


# ─── Workflow State ────────────────────────────────────────────────────────────

@dataclass
class WorkflowState:
    """LangGraph-compatible state for the OpenClaw workflow."""

    task: str
    facts: str
    client_name: str = ""
    reporting_basis: str = "IFRS"
    audience: str = "controller"
    output_format: str = "narrative"

    # Routing
    primary_agent: str = ""
    secondary_agents: list[str] = field(default_factory=list)
    task_category: str = ""

    # Execution
    retrieved_standards: list[dict] = field(default_factory=list)
    agent_outputs: dict[str, str] = field(default_factory=dict)
    tool_results: list[dict] = field(default_factory=list)

    # Memory
    short_term_memory: list[dict] = field(default_factory=list)
    episodic_memory: list[dict] = field(default_factory=list)

    # Control
    interrupt_requested: bool = False
    human_feedback: str | None = None
    final_output: str = ""
    error: str | None = None
    iteration: int = 0
    max_iterations: int = 5


OPENCLAW_SYSTEM_PROMPT = """You are OpenClaw, an open-source AI orchestration engine for finance transformation.

Your role is to:
1. Classify incoming tasks by type (accounting, ERP, EPM, M&A, reporting, etc.)
2. Route to the most appropriate specialist agent
3. Coordinate multi-agent workflows
4. Synthesize outputs from multiple agents into coherent deliverables
5. Manage human-in-the-loop checkpoints for high-stakes decisions

You have access to the Rudra agent network:
  • AccountingPolicyAgent    → IFRS/GAAP policy analysis
  • RevenueRecognitionAgent  → IFRS 15 / ASC 606
  • LeaseAccountingAgent     → IFRS 16 / ASC 842
  • TaxAccountingAgent       → IAS 12 / ASC 740
  • MADueDiligenceAgent      → M&A QoE and PPA
  • FinancialModelingAgent   → EPM budgeting and forecasting
  • CreativeDesignerAgent    → Visual deliverables and Canva designs
  • DatabricksPipelineAgent  → Data engineering and ML pipelines

When routing, output structured JSON like:
{
  "primary_agent": "RevenueRecognitionAgent",
  "secondary_agents": ["AccountingPolicyAgent"],
  "task_category": "revenue_recognition",
  "rationale": "Task involves SaaS revenue allocation under IFRS 15"
}"""


class OpenClawOrchestrator(BaseAgent):
    """State machine orchestrator using OpenClaw (OpenAI-compatible model)."""

    name = "openclaw_orchestrator"
    description = "LangGraph-compatible multi-agent workflow orchestrator"

    def __init__(self, model_router=None):
        super().__init__(model_router)
        self._agent_registry: dict[str, BaseAgent] = {}
        self._hooks: dict[str, list[Callable]] = {
            "pre_execute": [],
            "post_execute": [],
            "on_interrupt": [],
        }

    def register_agent(self, agent: BaseAgent) -> None:
        self._agent_registry[agent.name] = agent

    def add_hook(self, event: str, callback: Callable) -> None:
        if event in self._hooks:
            self._hooks[event].append(callback)

    def run(self, context: AgentContext) -> AgentResult:
        """Execute the full OpenClaw workflow state machine."""
        t0 = time.time()
        state = WorkflowState(
            task=context.task,
            facts=context.facts,
            client_name=context.client_name,
            reporting_basis=context.reporting_basis,
            audience=context.audience,
            output_format=context.output_format,
        )

        # State machine execution
        state = self._step_classify(state)
        state = self._step_route(state)
        state = self._step_execute(state)
        state = self._step_synthesize(state)

        return AgentResult(
            agent_name=self.name,
            task=context.task,
            output=state.final_output,
            tool_calls_made=state.tool_results,
            model_used="openclaw/gpt-4o",
            elapsed_seconds=time.time() - t0,
        )

    def orchestrate(
        self,
        tasks: list[AgentContext],
        parallel: bool = False,
    ) -> list[AgentResult]:
        """Orchestrate multiple tasks — optionally in parallel."""
        if parallel:
            return self._run_parallel(tasks)
        return [self.run(task) for task in tasks]

    # ─── State Machine Steps ──────────────────────────────────────────────────

    def _step_classify(self, state: WorkflowState) -> WorkflowState:
        """Classify the task type using OpenClaw model."""
        model = self._get_openclaw_model()
        if model is None:
            state.task_category = self._rule_based_classify(state.task)
            return state

        prompt = f"""Classify this consulting task into a category.

Task: {state.task}
Facts: {state.facts[:500]}

Categories: accounting_policy, revenue_recognition, lease_accounting, tax_accounting,
ma_due_diligence, financial_modeling, erp_design, epm_requirements, coa_design,
project_plan, executive_presentation, dashboard, video_animation, data_pipeline, general

Respond with ONLY the category name."""

        try:
            response = model.complete([{"role": "user", "content": prompt}])
            state.task_category = response.text.strip().lower().replace(" ", "_")
        except Exception:
            state.task_category = self._rule_based_classify(state.task)

        return state

    def _step_route(self, state: WorkflowState) -> WorkflowState:
        """Route to the primary and secondary specialist agents."""
        model = self._get_openclaw_model()
        if model is None:
            state.primary_agent = self._rule_based_route(state.task_category)
            return state

        agent_list = list(self._agent_registry.keys()) or [
            "AccountingPolicyAgent", "RevenueRecognitionAgent", "LeaseAccountingAgent",
            "TaxAccountingAgent", "MADueDiligenceAgent", "FinancialModelingAgent",
            "CreativeDesignerAgent", "DatabricksPipelineAgent",
        ]

        prompt = f"""Route this task to the appropriate specialist agent(s).

Task: {state.task}
Category: {state.task_category}
Available agents: {', '.join(agent_list)}

Output JSON:
{{
  "primary_agent": "<agent_name>",
  "secondary_agents": ["<agent_name>"],
  "rationale": "<brief reason>"
}}"""

        try:
            response = model.complete([{"role": "user", "content": prompt}])
            data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            state.primary_agent = data.get("primary_agent", "rudra")
            state.secondary_agents = data.get("secondary_agents", [])
        except Exception:
            state.primary_agent = self._rule_based_route(state.task_category)

        return state

    def _step_execute(self, state: WorkflowState) -> WorkflowState:
        """Execute the primary agent and any secondary agents."""
        for hook in self._hooks["pre_execute"]:
            hook(state)

        # Run primary agent
        primary = self._agent_registry.get(state.primary_agent)
        if primary:
            ctx = AgentContext(
                task=state.task,
                facts=state.facts,
                reporting_basis=state.reporting_basis,
                audience=state.audience,
                output_format=state.output_format,
                client_name=state.client_name,
            )
            result = primary.run(ctx)
            state.agent_outputs[state.primary_agent] = result.output
            state.tool_results.extend(result.tool_calls_made)

        # Check for human-in-the-loop interrupt
        if state.interrupt_requested:
            for hook in self._hooks["on_interrupt"]:
                hook(state)

        # Run secondary agents if needed
        for agent_name in state.secondary_agents[:2]:  # limit parallel work
            agent = self._agent_registry.get(agent_name)
            if agent:
                ctx = AgentContext(
                    task=state.task,
                    facts=state.facts + f"\nContext from {state.primary_agent}: " + state.agent_outputs.get(state.primary_agent, ""),
                    reporting_basis=state.reporting_basis,
                    audience=state.audience,
                    client_name=state.client_name,
                )
                result = agent.run(ctx)
                state.agent_outputs[agent_name] = result.output

        for hook in self._hooks["post_execute"]:
            hook(state)

        return state

    def _step_synthesize(self, state: WorkflowState) -> WorkflowState:
        """Synthesize outputs from multiple agents using OpenClaw."""
        if not state.agent_outputs:
            state.final_output = f"[OpenClaw] No agent output generated for task: {state.task}"
            return state

        if len(state.agent_outputs) == 1:
            state.final_output = next(iter(state.agent_outputs.values()))
            return state

        # Multi-agent synthesis
        model = self._get_openclaw_model()
        if model is None:
            state.final_output = "\n\n---\n\n".join(
                f"**{agent}:**\n{output}" for agent, output in state.agent_outputs.items()
            )
            return state

        agents_text = "\n\n".join(
            f"=== {agent} Output ===\n{output[:1000]}"
            for agent, output in state.agent_outputs.items()
        )

        prompt = f"""Synthesize these specialist agent outputs into a single, coherent consulting deliverable.

Client: {state.client_name}
Task: {state.task}
Audience: {state.audience}

Agent Outputs:
{agents_text}

Create a unified, Big-4 quality deliverable. Remove any redundancy. Preserve all key findings."""

        try:
            response = model.complete(
                [{"role": "user", "content": prompt}],
                system=OPENCLAW_SYSTEM_PROMPT,
            )
            state.final_output = response.text
        except Exception:
            state.final_output = "\n\n---\n\n".join(state.agent_outputs.values())

        return state

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _get_openclaw_model(self):
        if self._router:
            return self._router.get_model("orchestration")
        return None

    def _rule_based_classify(self, task: str) -> str:
        task_lower = task.lower()
        if any(k in task_lower for k in ["revenue", "asc 606", "ifrs 15"]):
            return "revenue_recognition"
        if any(k in task_lower for k in ["lease", "ifrs 16", "asc 842"]):
            return "lease_accounting"
        if any(k in task_lower for k in ["tax", "ias 12", "asc 740", "pillar"]):
            return "tax_accounting"
        if any(k in task_lower for k in ["m&a", "acquisition", "due diligence", "qoe"]):
            return "ma_due_diligence"
        if any(k in task_lower for k in ["erp", "oracle", "sap", "implementation"]):
            return "erp_design"
        if any(k in task_lower for k in ["epm", "budget", "forecast", "planning"]):
            return "epm_requirements"
        if any(k in task_lower for k in ["presentation", "deck", "dashboard", "canva"]):
            return "executive_presentation"
        if any(k in task_lower for k in ["video", "animation", "animated"]):
            return "video_animation"
        if any(k in task_lower for k in ["databricks", "pipeline", "delta lake"]):
            return "data_pipeline"
        return "accounting_policy"

    def _rule_based_route(self, category: str) -> str:
        route_map = {
            "revenue_recognition": "revenue_recognition_agent",
            "lease_accounting": "lease_accounting_agent",
            "tax_accounting": "tax_accounting_agent",
            "ma_due_diligence": "ma_due_diligence_agent",
            "accounting_policy": "accounting_policy_agent",
            "financial_modeling": "financial_modeling_agent",
            "executive_presentation": "creative_designer_agent",
            "data_pipeline": "databricks_pipeline_agent",
        }
        return route_map.get(category, "accounting_policy_agent")

    def _run_parallel(self, tasks: list[AgentContext]) -> list[AgentResult]:
        """Run tasks in parallel using threads (for I/O-bound API calls)."""
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.run, task): task for task in tasks}
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    task = futures[future]
                    results.append(AgentResult(
                        agent_name=self.name,
                        task=task.task,
                        output=f"Error: {exc}",
                        model_used="openclaw",
                    ))
        return results
