"""Rudra — Principal Multi-Model Consulting Agent.

Rudra is the orchestrating principal with 25+ years of Big-4 consulting expertise.
It routes tasks to the right specialist agents, coordinates multi-agent workflows,
and delivers ERP/EPM consulting outcomes in 1 week.

Model Strategy:
  • Claude Opus 4.6  — Deep reasoning (accounting, ERP design, M&A)
  • OpenClaw (GPT-4o) — Orchestration, routing, extraction
  • Qwen 2.5         — Multilingual reports, data pipelines, code
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .base_agent import AgentContext, AgentResult, BaseAgent

if TYPE_CHECKING:
    from models.router import ModelRouter


RUDRA_SYSTEM_PROMPT = """You are Rudra, a Principal-level consulting partner with 25+ years of Big-4 experience in:
- Finance Transformation (ERP, EPM, CFO Advisory)
- Technical Accounting (IFRS, US GAAP, M&A)
- Systems Integration (Oracle ERP Cloud, SAP S/4HANA, Workday, OneStream, Anaplan)
- Databricks Agentic AI and modern data architecture
- Creative deliverable design (executive presentations, CFO dashboards)

You lead a team of specialist agents and coordinate multi-model workflows:
  → Claude Opus 4.6  : Complex reasoning, accounting standards, ERP/EPM design
  → OpenClaw        : Orchestration, routing, structured extraction
  → Qwen 2.5        : Multilingual analysis, data pipelines, code generation
  → Canva MCP       : Visual deliverables, executive presentations
  → Databricks      : Vector search, lakehouse analytics, ML pipelines
  → Video Animation : Animated roadmaps, KPI dashboards, process flows

Your deliverables are always:
  • Board-ready and Big-4 quality
  • Grounded in accounting standards (cite IFRS/GAAP references)
  • Actionable with clear recommendations
  • Completed in the defined timeline (1 week for kickoff packages)

When given a client engagement request:
1. Identify the primary task (ERP, EPM, accounting, M&A, etc.)
2. Determine which specialist agents and tools are needed
3. Coordinate the workflow and synthesize outputs
4. Deliver a structured, client-ready result

Always end with a clear "Next Steps" section."""


DELIVERABLE_TASK_ROUTING = {
    "revenue_recognition": "RevenueRecognitionAgent",
    "lease_accounting": "LeaseAccountingAgent",
    "tax_accounting": "TaxAccountingAgent",
    "ma_due_diligence": "MADueDiligenceAgent",
    "accounting_policy": "AccountingPolicyAgent",
    "financial_modeling": "FinancialModelingAgent",
    "erp_design": "ERPEPMTool",
    "epm_requirements": "ERPEPMTool",
    "coa_design": "ERPEPMTool",
    "project_plan": "ERPEPMTool",
    "executive_presentation": "CreativeDesignerAgent",
    "dashboard": "CreativeDesignerAgent",
    "video_animation": "VideoAnimationTool",
    "data_pipeline": "DatabricksPipelineAgent",
}


class RudraAgent(BaseAgent):
    """Principal orchestrator — routes to specialists, synthesizes outputs."""

    name = "rudra"
    description = "Principal consulting partner — 25+ years Big-4 expertise"

    def __init__(self, model_router: "ModelRouter | None" = None):
        super().__init__(model_router)
        self._sub_agents: dict[str, BaseAgent] = {}
        self._tools_attached: dict = {}

    def attach_tools(
        self,
        canva_tool=None,
        databricks_tool=None,
        video_tool=None,
        erp_epm_tool=None,
    ) -> None:
        """Attach external tool instances for use in agent workflows."""
        if canva_tool:
            self._tools_attached["canva"] = canva_tool
            for td in canva_tool.tool_definitions():
                self.register_tool(td["name"], self._make_canva_executor(canva_tool, td["name"]))
        if databricks_tool:
            self._tools_attached["databricks"] = databricks_tool
            for td in databricks_tool.tool_definitions():
                self.register_tool(td["name"], self._make_databricks_executor(databricks_tool, td["name"]))
        if video_tool:
            self._tools_attached["video"] = video_tool
            for td in video_tool.tool_definitions():
                self.register_tool(td["name"], self._make_video_executor(video_tool, td["name"]))
        if erp_epm_tool:
            self._tools_attached["erp_epm"] = erp_epm_tool
            for td in erp_epm_tool.tool_definitions():
                self.register_tool(td["name"], self._make_erpepm_executor(erp_epm_tool, td["name"]))

    def register_specialist(self, agent: BaseAgent) -> None:
        self._sub_agents[agent.name] = agent

    def run(self, context: AgentContext) -> AgentResult:
        """Orchestrate a full consulting workflow."""
        t0 = time.time()
        model = self._router.get_model("accounting_policy") if self._router else None

        if model is None:
            return self._run_without_model(context, t0)

        # Build tool definitions list for Claude
        all_tools = self._build_tool_definitions()

        # Build the engagement prompt
        prompt = self._build_engagement_prompt(context)
        messages = self._build_messages(prompt, context)

        # Run Claude with tools
        final_text, tool_calls = self._run_tool_loop(
            model, messages, RUDRA_SYSTEM_PROMPT, all_tools, max_iterations=8
        )

        elapsed = time.time() - t0
        return AgentResult(
            agent_name=self.name,
            task=context.task,
            output=final_text,
            tool_calls_made=tool_calls,
            model_used="claude-opus-4-6",
            elapsed_seconds=elapsed,
        )

    def run_week1_engagement(
        self,
        client_name: str,
        project_name: str,
        erp_system: str = "Oracle ERP Cloud",
        epm_system: str = "Oracle EPM Cloud",
        include_video: bool = True,
        include_canva: bool = True,
    ) -> dict:
        """Full 1-week engagement: generate all ERP/EPM consulting deliverables.

        Coordinates Claude + OpenClaw + Qwen + Canva + Databricks + Video.
        """
        results = {}

        # 1. Generate ERP/EPM deliverables package
        if "erp_epm" in self._tools_attached:
            tool = self._tools_attached["erp_epm"]
            deliverables = tool.generate_week1_package(client_name, project_name, erp_system, epm_system)
            results["deliverables"] = [d.to_dict() if hasattr(d, "to_dict") else d.__dict__ for d in deliverables]

        # 2. Generate Canva executive presentation
        if include_canva and "canva" in self._tools_attached:
            canva = self._tools_attached["canva"]
            deck = canva.create_executive_deck(
                title=f"{client_name} — {erp_system} Transformation",
                slides=[
                    {"title": "Executive Summary"},
                    {"title": "Current State Assessment"},
                    {"title": "Future State Vision"},
                    {"title": "Transformation Roadmap"},
                    {"title": "Financial Business Case"},
                    {"title": "Risk & Mitigation"},
                    {"title": "Next Steps"},
                ],
                client_name=client_name,
            )
            results["executive_deck"] = deck

        # 3. Generate animated roadmap video
        if include_video and "video" in self._tools_attached:
            video = self._tools_attached["video"]
            phases = [
                {"name": "Assess & Design", "start_week": 0, "end_week": 1},
                {"name": "Build & Configure", "start_week": 1, "end_week": 2},
                {"name": "Test", "start_week": 2, "end_week": 3},
                {"name": "Train & Deploy", "start_week": 3, "end_week": 4},
                {"name": "Stabilize", "start_week": 4, "end_week": 5},
            ]
            video_result = video.animate_erp_roadmap(
                project_name=project_name,
                phases=phases,
                duration=20.0,
            )
            results["roadmap_video"] = video_result.__dict__

        # 4. Use Rudra (Claude) to write the executive summary
        if self._router:
            context = AgentContext(
                task="executive_summary",
                facts=f"Client: {client_name}, Project: {project_name}, ERP: {erp_system}, EPM: {epm_system}",
                client_name=client_name,
                output_format="narrative",
                audience="board",
            )
            summary_result = self.run(context)
            results["executive_summary"] = summary_result.output

        results["metadata"] = {
            "client": client_name,
            "project": project_name,
            "erp": erp_system,
            "epm": epm_system,
            "generated_by": "Rudra Multi-Model Agent Framework",
            "models_used": ["claude-opus-4-6", "gpt-4o (OpenClaw)", "qwen-max"],
        }

        return results

    def _build_engagement_prompt(self, context: AgentContext) -> str:
        return f"""
Client Engagement Request:
  Client: {context.client_name or 'Not specified'}
  Task: {context.task}
  Reporting Basis: {context.reporting_basis}
  Audience: {context.audience}
  Output Format: {context.output_format}

Facts / Background:
{context.facts}

Please provide a comprehensive consulting response. Use the available tools to:
1. Search relevant accounting standards (Databricks Vector Search)
2. Generate required deliverables (ERP/EPM templates, COA, project plan)
3. Create visual assets if appropriate (Canva presentations, animated videos)
4. Run any required analytics (Databricks SQL)

Structure your response as a Big-4 quality deliverable with:
- Executive Summary
- Analysis and Findings
- Recommendations
- Implementation Roadmap
- Next Steps
""".strip()

    def _build_tool_definitions(self) -> list[dict]:
        """Combine tool definitions from all attached tools."""
        tools = []
        for tool_instance in self._tools_attached.values():
            if hasattr(tool_instance, "tool_definitions"):
                tools.extend(tool_instance.tool_definitions())
        return tools

    def _run_without_model(self, context: AgentContext, t0: float) -> AgentResult:
        """Graceful degradation when no model API key is configured."""
        output = f"""
[Rudra Agent — Demo Mode — No API Keys Configured]

Task: {context.task}
Client: {context.client_name}
Facts: {context.facts[:200]}...

To enable full AI-powered responses, set:
  ANTHROPIC_API_KEY    → Claude Opus 4.6  (primary reasoning)
  OPENAI_API_KEY       → OpenClaw/GPT-4o  (orchestration)
  DASHSCOPE_API_KEY    → Qwen 2.5          (multilingual/code)
  CANVA_ACCESS_TOKEN   → Canva design generation
  DATABRICKS_HOST/TOKEN → Vector search and analytics
  LUMA_AI_KEY          → Photorealistic video animation

Framework is fully configured and ready to run.
""".strip()
        return AgentResult(
            agent_name=self.name,
            task=context.task,
            output=output,
            model_used="demo",
            elapsed_seconds=time.time() - t0,
        )

    # ─── Tool executor factories ───────────────────────────────────────────────

    def _make_canva_executor(self, tool, method_name: str):
        def executor(**kwargs):
            if method_name == "canva_generate_design":
                return tool.generate_design(**kwargs).__dict__
            elif method_name == "canva_export_design":
                return tool.export_design(**kwargs)
            return str(tool)
        return executor

    def _make_databricks_executor(self, tool, method_name: str):
        def executor(**kwargs):
            if method_name == "search_standards":
                results = tool.search_standards(**kwargs)
                return [r.__dict__ for r in results]
            elif method_name == "run_close_analytics":
                result = tool.run_analytics(kwargs.get("sql", "SELECT 1"))
                return result.__dict__
            elif method_name == "get_epm_forecast":
                return tool.get_epm_forecast(**kwargs)
            return {}
        return executor

    def _make_video_executor(self, tool, method_name: str):
        def executor(**kwargs):
            if method_name == "animate_erp_roadmap":
                return tool.animate_erp_roadmap(**kwargs).__dict__
            elif method_name == "animate_kpi_dashboard":
                return tool.animate_kpi_dashboard(**kwargs).__dict__
            elif method_name == "generate_luma_video":
                return tool.generate_luma_video(**kwargs).__dict__
            return {}
        return executor

    def _make_erpepm_executor(self, tool, method_name: str):
        def executor(**kwargs):
            if method_name == "generate_erp_project_plan":
                d = tool.generate_project_plan(**kwargs)
                return d.__dict__
            elif method_name == "generate_week1_package":
                deliverables = tool.generate_week1_package(**kwargs)
                return [d.__dict__ for d in deliverables]
            elif method_name == "generate_epm_requirements":
                d = tool.generate_epm_requirements(**kwargs)
                return d.__dict__
            return {}
        return executor
