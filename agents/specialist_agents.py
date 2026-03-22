"""Specialist agents — each an expert in a specific finance/ERP/EPM domain.

Agents:
  AccountingPolicyAgent     → IFRS/GAAP policy drafting (Claude)
  RevenueRecognitionAgent   → IFRS 15 / ASC 606 (Claude)
  LeaseAccountingAgent      → IFRS 16 / ASC 842 (Claude)
  TaxAccountingAgent        → IAS 12 / ASC 740 / Pillar Two (Claude)
  MADueDiligenceAgent       → M&A QoE, PPA, IFRS 3 (Claude)
  FinancialModelingAgent    → EPM budgeting/forecasting (Claude)
  CreativeDesignerAgent     → Visual deliverables via Canva (Claude + Canva)
  DatabricksPipelineAgent   → Data pipelines and lakehouse (Qwen + Databricks)
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .base_agent import AgentContext, AgentResult, BaseAgent

if TYPE_CHECKING:
    pass


# ─── Accounting Policy Agent ──────────────────────────────────────────────────

class AccountingPolicyAgent(BaseAgent):
    """IFRS and US GAAP accounting policy engine — Big-4 quality analysis."""

    name = "accounting_policy_agent"
    description = "IFRS/GAAP accounting policy analysis and drafting"

    SYSTEM = """You are a Big-4 Technical Accounting Partner specializing in IFRS and US GAAP.

Follow this 8-step analytical workflow:
1. Normalize the facts and identify the reporting entity's framework
2. Scope relevant standards (IFRS/GAAP/both)
3. Identify the specific sections of each standard that apply
4. Analyze how the standard(s) apply to the given facts
5. Identify any significant differences between IFRS and US GAAP
6. Draft journal entry patterns (debit/credit format)
7. Draft disclosure requirements
8. Assess system/process impacts

Always cite specific standard references (e.g., IFRS 15.31, ASC 606-10-25-27).
Format journal entries clearly. Note any judgment areas or elections available."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        model = self._router.get_model("accounting_policy") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        prompt = self._build_prompt(context)
        tools = self._get_tools()
        messages = self._build_messages(prompt, context)

        if tools:
            final_text, tool_calls = self._run_tool_loop(model, messages, self.SYSTEM, tools)
        else:
            response = model.complete(messages, system=self.SYSTEM)
            final_text = response.text
            tool_calls = []

        return AgentResult(
            agent_name=self.name, task=context.task, output=final_text,
            tool_calls_made=tool_calls, model_used="claude-opus-4-6",
            elapsed_seconds=time.time() - t0,
        )

    def _build_prompt(self, context: AgentContext) -> str:
        return f"""
Accounting Policy Analysis Request:
  Reporting Basis: {context.reporting_basis}
  Audience: {context.audience}
  Output Format: {context.output_format}

Facts:
{context.facts}

Please provide a comprehensive accounting policy analysis following the 8-step workflow.
""".strip()

    def _get_tools(self) -> list[dict]:
        return list(self._tool_registry.keys()) and [
            {
                "name": name,
                "description": f"Tool: {name}",
                "input_schema": {"type": "object", "properties": {}},
            }
            for name in self._tool_registry
        ] or []

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(
            agent_name=self.name, task=context.task,
            output=f"[Demo] Accounting policy analysis for: {context.facts[:100]}...\nSet ANTHROPIC_API_KEY to enable full analysis.",
            model_used="demo", elapsed_seconds=time.time() - t0,
        )


# ─── Revenue Recognition Agent ────────────────────────────────────────────────

class RevenueRecognitionAgent(BaseAgent):
    """IFRS 15 / ASC 606 — Five-step model and SaaS revenue specialization."""

    name = "revenue_recognition_agent"
    description = "IFRS 15 / ASC 606 revenue recognition specialist"

    SYSTEM = """You are a revenue recognition specialist with deep expertise in IFRS 15 and ASC 606.

Apply the Five-Step Model rigorously:
  Step 1: Identify the contract(s) with a customer
  Step 2: Identify the performance obligations in the contract
  Step 3: Determine the transaction price
  Step 4: Allocate the transaction price to performance obligations (SSP basis)
  Step 5: Recognize revenue when (or as) each performance obligation is satisfied

Key judgment areas to address:
  • Variable consideration (IFRS 15.50-59 / ASC 606-10-32-5)
  • Standalone selling price allocation
  • Contract modifications
  • Principal vs agent considerations (IFRS 15.B34-B38)
  • Licensing (IFRS 15.B52-B63)
  • Contract costs (IFRS 15.91-104)

For SaaS contracts: address bundled licenses, implementation fees, and usage-based fees.
Always provide ASC 606 differences when IFRS 15 is the primary basis."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        model = self._router.get_model("revenue_recognition") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        prompt = f"""
Revenue Recognition Analysis:
  Basis: {context.reporting_basis}
  Audience: {context.audience}

Contract Facts:
{context.facts}

Apply the five-step model. Identify all performance obligations and provide the recognition pattern.
Include journal entries and disclosure requirements.
""".strip()

        response = model.complete(self._build_messages(prompt, context), system=self.SYSTEM)
        return AgentResult(
            agent_name=self.name, task=context.task, output=response.text,
            model_used="claude-opus-4-6", elapsed_seconds=time.time() - t0,
        )

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(agent_name=self.name, task=context.task,
            output="[Demo] Revenue recognition analysis. Set ANTHROPIC_API_KEY to enable.",
            model_used="demo", elapsed_seconds=time.time() - t0)


# ─── Lease Accounting Agent ───────────────────────────────────────────────────

class LeaseAccountingAgent(BaseAgent):
    """IFRS 16 / ASC 842 — ROU asset, lease liability, and sale-leaseback."""

    name = "lease_accounting_agent"
    description = "IFRS 16 / ASC 842 lease accounting specialist"

    SYSTEM = """You are a lease accounting specialist with expertise in IFRS 16 and ASC 842.

For every lease analysis:
1. Determine whether the contract is or contains a lease (IFRS 16.9-11)
2. Apply lessee practical expedients (if applicable)
3. Calculate the lease liability (PV of future lease payments)
4. Calculate the right-of-use (ROU) asset
5. Determine the discount rate (IBR methodology if implicit rate unavailable)
6. Prepare the amortization schedule
7. Draft journal entries (initial recognition and subsequent measurement)
8. Identify IFRS 16 vs ASC 842 differences (operating/finance classification)

For sale-and-leaseback: assess whether the transfer qualifies as a sale under IFRS 15."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        model = self._router.get_model("lease_accounting") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        prompt = f"""
Lease Accounting Analysis:
  Standard: {context.reporting_basis}
  Lessee Facts: {context.facts}

Provide: lease classification, ROU asset/liability calculation, amortization schedule, journal entries.
""".strip()

        response = model.complete(self._build_messages(prompt, context), system=self.SYSTEM)
        return AgentResult(agent_name=self.name, task=context.task, output=response.text,
            model_used="claude-opus-4-6", elapsed_seconds=time.time() - t0)

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(agent_name=self.name, task=context.task,
            output="[Demo] Lease accounting analysis. Set ANTHROPIC_API_KEY to enable.",
            model_used="demo", elapsed_seconds=time.time() - t0)


# ─── Tax Accounting Agent ─────────────────────────────────────────────────────

class TaxAccountingAgent(BaseAgent):
    """IAS 12 / ASC 740 — Deferred tax, transfer pricing, Pillar Two."""

    name = "tax_accounting_agent"
    description = "IAS 12 / ASC 740 tax accounting and Pillar Two compliance"

    SYSTEM = """You are a tax accounting specialist with expertise in IAS 12, ASC 740, and Pillar Two (GloBE rules).

For tax accounting analyses:
1. Identify temporary differences and their tax effects
2. Calculate deferred tax assets and liabilities
3. Assess recoverability (valuation allowance / DTA recognition)
4. Analyze uncertain tax positions (IAS 12.29 / ASC 740-10-30)
5. Address Pillar Two top-up tax where applicable (OECD Model Rules)
6. Draft tax footnote disclosures
7. Compute effective tax rate reconciliation

Always distinguish between current and deferred tax. Flag any significant judgment areas."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        model = self._router.get_model("tax_accounting") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        prompt = f"""
Tax Accounting Analysis:
  Standard: {context.reporting_basis}
  Facts: {context.facts}

Provide deferred tax analysis, ETR reconciliation, and Pillar Two assessment if applicable.
""".strip()

        response = model.complete(self._build_messages(prompt, context), system=self.SYSTEM)
        return AgentResult(agent_name=self.name, task=context.task, output=response.text,
            model_used="claude-opus-4-6", elapsed_seconds=time.time() - t0)

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(agent_name=self.name, task=context.task,
            output="[Demo] Tax accounting analysis. Set ANTHROPIC_API_KEY to enable.",
            model_used="demo", elapsed_seconds=time.time() - t0)


# ─── M&A Due Diligence Agent ──────────────────────────────────────────────────

class MADueDiligenceAgent(BaseAgent):
    """M&A Quality of Earnings, Purchase Price Allocation, IFRS 3 / ASC 805."""

    name = "ma_due_diligence_agent"
    description = "M&A QoE, PPA, IFRS 3 / ASC 805 due diligence specialist"

    SYSTEM = """You are an M&A due diligence specialist with Big-4 transaction advisory expertise.

For every M&A analysis:
1. Quality of Earnings (QoE):
   - Identify one-time / non-recurring items
   - Normalize EBITDA
   - Assess revenue quality and concentration risk
   - Review working capital trends (NWC peg)

2. Purchase Price Allocation (PPA):
   - Identify and value intangible assets (customer relationships, technology, brands)
   - Assess fair value of contingent consideration (earn-outs)
   - Calculate goodwill (IFRS 3 / ASC 805)
   - Prepare deferred tax on PPA adjustments

3. Integration Considerations:
   - Accounting policy harmonization
   - Chart of accounts integration
   - Consolidation model adjustments

Always cite IFRS 3 and ASC 805 paragraphs as applicable."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        model = self._router.get_model("ma_due_diligence") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        prompt = f"""
M&A Due Diligence Analysis:
  Basis: {context.reporting_basis}
  Transaction Facts: {context.facts}
  Audience: {context.audience}

Provide QoE analysis, PPA framework, goodwill calculation, and integration roadmap.
""".strip()

        response = model.complete(self._build_messages(prompt, context), system=self.SYSTEM)
        return AgentResult(agent_name=self.name, task=context.task, output=response.text,
            model_used="claude-opus-4-6", elapsed_seconds=time.time() - t0)

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(agent_name=self.name, task=context.task,
            output="[Demo] M&A due diligence analysis. Set ANTHROPIC_API_KEY to enable.",
            model_used="demo", elapsed_seconds=time.time() - t0)


# ─── Financial Modeling Agent ─────────────────────────────────────────────────

class FinancialModelingAgent(BaseAgent):
    """EPM financial modeling — budgeting, forecasting, scenario analysis."""

    name = "financial_modeling_agent"
    description = "EPM budgeting, forecasting and scenario analysis"

    SYSTEM = """You are an EPM (Enterprise Performance Management) expert specializing in:
- Driver-based planning models
- Rolling forecast design
- Budget process optimization
- Scenario and sensitivity analysis
- Variance analysis frameworks
- Management reporting hierarchies

Design models for Oracle EPM Cloud, OneStream, Anaplan and Hyperion.
Always specify dimension structure, calculation rules, and data integration requirements."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        model = self._router.get_model("epm_modeling") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        prompt = f"""
EPM Financial Modeling Request:
  Client: {context.client_name}
  Facts: {context.facts}
  Output: {context.output_format}

Design the EPM model architecture including dimensions, calculations, and reporting hierarchy.
""".strip()

        response = model.complete(self._build_messages(prompt, context), system=self.SYSTEM)
        return AgentResult(agent_name=self.name, task=context.task, output=response.text,
            model_used="claude-opus-4-6", elapsed_seconds=time.time() - t0)

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(agent_name=self.name, task=context.task,
            output="[Demo] Financial modeling analysis. Set ANTHROPIC_API_KEY to enable.",
            model_used="demo", elapsed_seconds=time.time() - t0)


# ─── Creative Designer Agent ──────────────────────────────────────────────────

class CreativeDesignerAgent(BaseAgent):
    """Visual design — executive presentations, CFO dashboards via Canva."""

    name = "creative_designer_agent"
    description = "Visual deliverables: executive presentations, CFO dashboards via Canva"

    SYSTEM = """You are a creative design director with expertise in finance consulting visuals.

You design:
- Executive presentation decks (C-suite ready, 10-15 slides)
- CFO dashboards (KPI tiles, sparklines, traffic lights)
- Process flow diagrams (BPMN-style swim lanes)
- ERP transformation roadmaps (Gantt-style timelines)
- One-pagers and executive summaries

Design principles:
- Dark professional color scheme (#1a1a2e, #3498db, accent colors)
- Data-ink ratio: maximize content, minimize decoration
- Clear hierarchy: headline → supporting data → source
- Always include a 'So What?' interpretation for every chart

When creating with Canva tools, specify slide-by-slide content structure."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        model = self._router.get_model("erp_design") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        tools = [
            td for name, tool_inst in self._tool_registry.items()
        ] if self._tool_registry else []

        canva_tools = []
        if "canva_generate_design" in self._tool_registry:
            from tools.canva_tool import CanvaTool
            canva_tools = CanvaTool.tool_definitions()

        prompt = f"""
Design Request:
  Client: {context.client_name}
  Deliverable: {context.task}
  Facts: {context.facts}
  Audience: {context.audience}

Create the design specification and generate the Canva deliverable if tools are available.
""".strip()

        messages = self._build_messages(prompt, context)
        if canva_tools:
            final_text, tool_calls = self._run_tool_loop(model, messages, self.SYSTEM, canva_tools)
        else:
            response = model.complete(messages, system=self.SYSTEM)
            final_text = response.text
            tool_calls = []

        return AgentResult(agent_name=self.name, task=context.task, output=final_text,
            tool_calls_made=tool_calls, model_used="claude-opus-4-6",
            elapsed_seconds=time.time() - t0)

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(agent_name=self.name, task=context.task,
            output="[Demo] Creative design analysis. Set ANTHROPIC_API_KEY to enable.",
            model_used="demo", elapsed_seconds=time.time() - t0)


# ─── Databricks Pipeline Agent ────────────────────────────────────────────────

class DatabricksPipelineAgent(BaseAgent):
    """Databricks lakehouse and ML pipelines — uses Qwen 2.5 for code generation."""

    name = "databricks_pipeline_agent"
    description = "Databricks data engineering, lakehouse design and ML pipeline agent"

    SYSTEM = """You are a Databricks data engineering expert specializing in:
- Delta Lake architecture and optimization
- Databricks Agentic AI framework
- Finance data pipelines (close, consolidation, planning)
- Vector Search for RAG applications
- MLflow experiment tracking
- Unity Catalog data governance
- Databricks SQL analytics
- Auto-ML for forecasting models

Generate production-ready Python/PySpark code with proper error handling.
Follow the Medallion Architecture: Bronze (raw) → Silver (cleansed) → Gold (analytics).
Always include data quality checks and schema validation."""

    def run(self, context: AgentContext) -> AgentResult:
        t0 = time.time()
        # Qwen handles data pipeline and code generation tasks
        model = self._router.get_model("data_pipeline") if self._router else None
        if model is None:
            return self._demo_result(context, t0)

        databricks_tools = []
        if self._tool_registry:
            from tools.databricks_tool import DatabricksTool
            databricks_tools = DatabricksTool.tool_definitions()

        prompt = f"""
Databricks Pipeline Request:
  Task: {context.task}
  Facts: {context.facts}
  Client: {context.client_name}

Design and implement the Databricks pipeline. Include:
1. Architecture diagram (text-based)
2. PySpark/Python code
3. Delta Lake table design
4. Data quality rules
5. Scheduling and monitoring approach
""".strip()

        messages = self._build_messages(prompt, context)
        if databricks_tools:
            final_text, tool_calls = self._run_tool_loop(model, messages, self.SYSTEM, databricks_tools)
        else:
            response = model.complete(messages, system=self.SYSTEM)
            final_text = response.text
            tool_calls = []

        return AgentResult(agent_name=self.name, task=context.task, output=final_text,
            tool_calls_made=tool_calls, model_used="qwen-max",
            elapsed_seconds=time.time() - t0)

    def _demo_result(self, context: AgentContext, t0: float) -> AgentResult:
        return AgentResult(agent_name=self.name, task=context.task,
            output="[Demo] Databricks pipeline analysis. Set DASHSCOPE_API_KEY to enable Qwen 2.5.",
            model_used="demo", elapsed_seconds=time.time() - t0)
