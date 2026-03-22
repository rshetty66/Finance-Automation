"""AgentFramework — top-level assembly wiring all components together.

This is the entry point for the Rudra Multi-Model Agent Framework:

  Models:    Claude Opus 4.6  (Anthropic)
             OpenClaw/GPT-4o  (OpenAI-compatible)
             Qwen 2.5         (Alibaba DashScope)

  Tools:     Canva            (visual deliverables)
             Databricks       (vector search, analytics, pipelines)
             Video Animation  (matplotlib + Luma AI)
             ERP/EPM Tools    (consulting deliverables)

  Agents:    Rudra            (principal orchestrator)
             OpenClaw         (state machine orchestrator)
             8 Specialist     (accounting, ERP, EPM, design, data)

Usage:
    from framework import AgentFramework

    fw = AgentFramework()
    result = fw.run_engagement(
        client_name="Acme Corp",
        task="Design Oracle ERP Cloud implementation for O2C process",
        reporting_basis="IFRS",
    )
    print(result.output)
"""

from __future__ import annotations

import os
from pathlib import Path

from agents.base_agent import AgentContext, AgentResult
from agents.openclaw_orchestrator import OpenClawOrchestrator
from agents.rudra_agent import RudraAgent
from agents.specialist_agents import (
    AccountingPolicyAgent,
    CreativeDesignerAgent,
    DatabricksPipelineAgent,
    FinancialModelingAgent,
    LeaseAccountingAgent,
    MADueDiligenceAgent,
    RevenueRecognitionAgent,
    TaxAccountingAgent,
)
from models.router import ModelRouter
from tools.canva_tool import CanvaTool
from tools.databricks_tool import DatabricksTool
from tools.erp_epm_tools import ERPEPMTool
from tools.video_animation_tool import VideoAnimationTool


class AgentFramework:
    """Top-level framework — assembles all models, tools, and agents."""

    def __init__(
        self,
        config_path: str | None = None,
        output_dir: str = "./output",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # ── Models ──────────────────────────────────────────────────────────
        self.router = ModelRouter(config_path)

        # ── Tools ───────────────────────────────────────────────────────────
        self.canva = CanvaTool()
        self.databricks = DatabricksTool()
        self.video = VideoAnimationTool(output_dir=str(self.output_dir / "videos"))
        self.erp_epm = ERPEPMTool(output_dir=str(self.output_dir / "deliverables"))

        # ── Specialist Agents ────────────────────────────────────────────────
        self._specialists = {
            "accounting_policy_agent": AccountingPolicyAgent(self.router),
            "revenue_recognition_agent": RevenueRecognitionAgent(self.router),
            "lease_accounting_agent": LeaseAccountingAgent(self.router),
            "tax_accounting_agent": TaxAccountingAgent(self.router),
            "ma_due_diligence_agent": MADueDiligenceAgent(self.router),
            "financial_modeling_agent": FinancialModelingAgent(self.router),
            "creative_designer_agent": CreativeDesignerAgent(self.router),
            "databricks_pipeline_agent": DatabricksPipelineAgent(self.router),
        }

        # ── OpenClaw Orchestrator ─────────────────────────────────────────────
        self.openclaw = OpenClawOrchestrator(self.router)
        for agent in self._specialists.values():
            self.openclaw.register_agent(agent)

        # ── Rudra — Principal Agent ──────────────────────────────────────────
        self.rudra = RudraAgent(self.router)
        self.rudra.attach_tools(
            canva_tool=self.canva,
            databricks_tool=self.databricks,
            video_tool=self.video,
            erp_epm_tool=self.erp_epm,
        )
        for agent in self._specialists.values():
            self.rudra.register_specialist(agent)

    # ─── Public API ───────────────────────────────────────────────────────────

    def run_engagement(
        self,
        task: str,
        facts: str = "",
        client_name: str = "",
        reporting_basis: str = "IFRS",
        audience: str = "controller",
        output_format: str = "narrative",
    ) -> AgentResult:
        """Run a single consulting engagement task through the full agent stack."""
        context = AgentContext(
            task=task,
            facts=facts,
            client_name=client_name,
            reporting_basis=reporting_basis,
            audience=audience,
            output_format=output_format,
        )
        # OpenClaw classifies and routes; Rudra executes with tools
        return self.openclaw.run(context)

    def run_week1_package(
        self,
        client_name: str,
        project_name: str,
        erp_system: str = "Oracle ERP Cloud",
        epm_system: str = "Oracle EPM Cloud",
        include_video: bool = True,
        include_canva: bool = True,
    ) -> dict:
        """Generate the full 1-week ERP/EPM kickoff deliverable package."""
        return self.rudra.run_week1_engagement(
            client_name=client_name,
            project_name=project_name,
            erp_system=erp_system,
            epm_system=epm_system,
            include_video=include_video,
            include_canva=include_canva,
        )

    def run_accounting_analysis(
        self,
        facts: str,
        standard: str = "IFRS",
        task_type: str = "accounting_policy",
    ) -> AgentResult:
        """Route an accounting question to the appropriate specialist."""
        context = AgentContext(
            task=task_type,
            facts=facts,
            reporting_basis=standard,
        )
        agent = self._specialists.get(f"{task_type}_agent")
        if agent:
            return agent.run(context)
        return self.openclaw.run(context)

    def run_databricks_pipeline(
        self,
        pipeline_description: str,
        client_name: str = "",
    ) -> AgentResult:
        """Design and generate a Databricks finance data pipeline."""
        context = AgentContext(
            task="data_pipeline",
            facts=pipeline_description,
            client_name=client_name,
        )
        return self._specialists["databricks_pipeline_agent"].run(context)

    def generate_video_deliverable(
        self,
        deliverable_type: str,
        data: dict,
        project_name: str = "",
    ) -> dict:
        """Generate an animated video deliverable."""
        if deliverable_type == "roadmap":
            result = self.video.animate_erp_roadmap(
                project_name=project_name,
                phases=data.get("phases", []),
            )
        elif deliverable_type == "kpi_dashboard":
            result = self.video.animate_kpi_dashboard(
                kpis=data.get("kpis", []),
                title=data.get("title", "CFO Dashboard"),
            )
        elif deliverable_type == "process_flow":
            result = self.video.animate_process_flow(
                process_name=data.get("process_name", "Process"),
                steps=data.get("steps", []),
            )
        elif deliverable_type == "waterfall":
            result = self.video.animate_waterfall_chart(
                title=data.get("title", "Variance Analysis"),
                data=data,
            )
        else:
            result = self.video.generate_luma_video(prompt=data.get("prompt", ""))
        return result.__dict__

    def search_standards(self, query: str, category: str | None = None) -> list[dict]:
        """Search IFRS/GAAP standards using Databricks Vector Search."""
        results = self.databricks.search_standards(query, category)
        return [r.__dict__ for r in results]

    # ─── Status & Health ──────────────────────────────────────────────────────

    def status(self) -> dict:
        """Return framework status including API key configuration."""
        return {
            "framework": "Rudra Multi-Model Agent Framework v1.0",
            "models": {
                "claude": {
                    "configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
                    "model": "claude-opus-4-6",
                    "provider": "Anthropic",
                },
                "openclaw": {
                    "configured": bool(os.environ.get("OPENAI_API_KEY")),
                    "model": "gpt-4o",
                    "provider": "OpenAI-compatible",
                },
                "qwen": {
                    "configured": bool(os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY")),
                    "model": "qwen-max",
                    "provider": "Alibaba DashScope",
                },
            },
            "tools": {
                "canva": bool(os.environ.get("CANVA_ACCESS_TOKEN")),
                "databricks": bool(os.environ.get("DATABRICKS_HOST") and os.environ.get("DATABRICKS_TOKEN")),
                "video_animation": True,  # matplotlib is always available
                "luma_ai": bool(os.environ.get("LUMA_AI_KEY")),
                "erp_epm": True,  # No external API needed
            },
            "agents": list(self._specialists.keys()) + ["rudra", "openclaw_orchestrator"],
            "output_dir": str(self.output_dir),
        }
