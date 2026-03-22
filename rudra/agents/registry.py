"""
AgentRegistry   discovers, parses, and indexes all agent definitions.

Scans the Rudra_Agents/ directory for .md files, extracts YAML frontmatter
and the Markdown body (used as the system prompt), then builds an AgentSpec
for each agent.  Also enriches specs with routing metadata from the
hard-coded AGENT_CATALOG.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import yaml

from rudra.agents.base import BaseAgent
from rudra.config import RudraConfig, get_config
from rudra.models import AgentDomain, AgentSpec, ToolPermission

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Agent catalog   enriches parsed .md specs with routing / domain metadata
# ---------------------------------------------------------------------------

AGENT_CATALOG: dict[str, dict] = {
    "rudra": {
        "domain": AgentDomain.PROGRAM_MANAGEMENT,
        "capabilities": ["sales", "program_management", "delivery", "ERP_SI", "executive_advisory"],
        "embedding_tags": [
            "program management", "proposal", "sales", "ERP implementation",
            "governance", "steering committee", "executive",
        ],
        "confidence_threshold": 0.30,
        "model": "default",
        "downstream_agents": [
            "coa-designer", "accounting-hub-architect", "rapid-prototyper",
            "si-finance-process-lead", "si-functional-lead", "si-data-architect",
            "si-integration-lead", "si-security-controls-lead",
            "si-change-management-lead", "si-data-analytics-lead",
            "apqc-researcher", "creative-designer", "fact-check-agent",
        ],
        "tools": [
            ToolPermission(name="read_file", description="Read project files"),
            ToolPermission(name="write_file", description="Write deliverables"),
            ToolPermission(name="spawn_agent", description="Spawn sub-agents", required=True),
            ToolPermission(name="search_standards", description="Search accounting standards"),
            ToolPermission(name="get_apqc_benchmark", description="Retrieve APQC benchmarks"),
        ],
    },
    "accounting-policy-engine": {
        "domain": AgentDomain.TECHNICAL_ACCOUNTING,
        "capabilities": ["IFRS", "US_GAAP", "journal_entries", "policies", "disclosures", "standards_analysis"],
        "embedding_tags": [
            "revenue recognition", "lease accounting", "financial instruments",
            "tax accounting", "consolidation", "business combinations",
            "impairment", "provisions", "employee benefits", "foreign currency",
        ],
        "confidence_threshold": 0.35,
        "model": "reasoning",
        "upstream_agents": ["rudra", "revenue-recognition-agent", "lease-accounting-agent",
                           "ma-due-diligence-agent", "tax-accounting-agent"],
        "tools": [
            ToolPermission(name="search_standards", description="Search IFRS/US GAAP standards", required=True),
            ToolPermission(name="get_apqc_benchmark", description="Retrieve benchmarks"),
        ],
    },
    "revenue-recognition-agent": {
        "domain": AgentDomain.TECHNICAL_ACCOUNTING,
        "capabilities": ["IFRS_15", "ASC_606", "5_step_model", "variable_consideration", "licenses", "SaaS_revenue"],
        "embedding_tags": [
            "revenue", "contract", "performance obligation", "SaaS", "license",
            "variable consideration", "principal agent", "contract modification",
        ],
        "confidence_threshold": 0.40,
        "model": "reasoning",
        "downstream_agents": ["accounting-policy-engine"],
        "tools": [
            ToolPermission(name="search_standards", description="Search revenue standards", required=True),
        ],
    },
    "lease-accounting-agent": {
        "domain": AgentDomain.TECHNICAL_ACCOUNTING,
        "capabilities": ["IFRS_16", "ASC_842", "ROU_asset", "lease_liability", "sale_leaseback"],
        "embedding_tags": [
            "lease", "rental", "right of use", "operating lease",
            "finance lease", "sale leaseback", "lessee", "lessor",
        ],
        "confidence_threshold": 0.40,
        "model": "reasoning",
        "downstream_agents": ["accounting-policy-engine"],
        "tools": [
            ToolPermission(name="search_standards", description="Search lease standards", required=True),
        ],
    },
    "tax-accounting-agent": {
        "domain": AgentDomain.TAX,
        "capabilities": ["IAS_12", "ASC_740", "deferred_tax", "transfer_pricing", "Pillar_Two", "VAT"],
        "embedding_tags": [
            "tax provision", "deferred tax", "uncertain tax", "transfer pricing",
            "Pillar Two", "GloBE", "VAT", "GST", "tax planning",
        ],
        "confidence_threshold": 0.35,
        "model": "reasoning",
        "downstream_agents": ["accounting-policy-engine"],
        "tools": [
            ToolPermission(name="search_standards", description="Search tax standards", required=True),
        ],
    },
    "ma-due-diligence-agent": {
        "domain": AgentDomain.DEALS_ADVISORY,
        "capabilities": ["QoE", "PPA", "IFRS_3", "ASC_805", "acquisition_accounting", "earn_outs"],
        "embedding_tags": [
            "M&A", "acquisition", "due diligence", "purchase price allocation",
            "goodwill", "quality of earnings", "earn-out", "deal", "target company",
        ],
        "confidence_threshold": 0.38,
        "model": "reasoning",
        "downstream_agents": ["accounting-policy-engine", "financial-modeling-agent"],
        "tools": [
            ToolPermission(name="search_standards", description="Search M&A standards", required=True),
            ToolPermission(name="run_financial_model", description="Execute financial models"),
        ],
    },
    "financial-modeling-agent": {
        "domain": AgentDomain.DEALS_ADVISORY,
        "capabilities": ["DCF", "LBO", "three_statement_model", "WACC", "scenario_analysis"],
        "embedding_tags": [
            "model", "valuation", "DCF", "LBO", "WACC", "EBITDA",
            "IRR", "accretion dilution", "financial projection",
        ],
        "confidence_threshold": 0.35,
        "model": "reasoning",
        "tools": [
            ToolPermission(name="run_financial_model", description="Execute financial models", required=True),
            ToolPermission(name="write_file", description="Write model outputs"),
        ],
    },
    "treasury-management-agent": {
        "domain": AgentDomain.TREASURY,
        "capabilities": ["hedge_accounting", "IFRS_9", "ASC_815", "FX_risk", "liquidity", "debt_management"],
        "embedding_tags": [
            "treasury", "hedging", "FX", "foreign exchange", "cash management",
            "liquidity", "debt", "interest rate", "derivatives", "cash pool",
        ],
        "confidence_threshold": 0.35,
        "model": "reasoning",
        "downstream_agents": ["accounting-policy-engine"],
        "tools": [
            ToolPermission(name="search_standards", description="Search treasury standards", required=True),
        ],
    },
    "esg-reporting-agent": {
        "domain": AgentDomain.SUSTAINABILITY,
        "capabilities": ["ISSB", "CSRD", "TCFD", "GHG_accounting", "carbon_credits", "double_materiality"],
        "embedding_tags": [
            "ESG", "sustainability", "climate", "carbon", "Scope 1 2 3",
            "CSRD", "ISSB", "TCFD", "net zero", "GHG", "emissions",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="search_standards", description="Search ESG standards", required=True),
        ],
    },
    "internal-audit-agent": {
        "domain": AgentDomain.RISK_ASSURANCE,
        "capabilities": ["SOX_404", "IIA_standards", "COSO", "fraud_risk", "audit_planning", "controls_testing"],
        "embedding_tags": [
            "internal audit", "SOX", "ICFR", "controls", "fraud",
            "risk assessment", "audit committee", "compliance", "segregation of duties",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="search_standards", description="Search audit standards", required=True),
        ],
    },
    "consolidation-reporting-agent": {
        "domain": AgentDomain.REPORTING,
        "capabilities": ["IFRS_10", "ASC_810", "IC_eliminations", "FX_translation", "NCI", "group_close"],
        "embedding_tags": [
            "consolidation", "intercompany", "group accounts", "NCI",
            "non-controlling interest", "translation", "CTA", "group close", "elimination",
        ],
        "confidence_threshold": 0.38,
        "model": "default",
        "downstream_agents": ["accounting-policy-engine"],
        "tools": [
            ToolPermission(name="search_standards", description="Search consolidation standards", required=True),
            ToolPermission(name="run_analytics", description="Run close analytics"),
        ],
    },
    "coa-designer": {
        "domain": AgentDomain.SYSTEMS,
        "capabilities": ["COA_design", "segment_architecture", "GL_structure", "hierarchy_design"],
        "embedding_tags": [
            "chart of accounts", "COA", "account structure", "segments",
            "GL design", "natural account", "cost center",
        ],
        "confidence_threshold": 0.40,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write COA designs", required=True),
            ToolPermission(name="read_file", description="Read existing COA structures"),
        ],
    },
    "accounting-hub-architect": {
        "domain": AgentDomain.SYSTEMS,
        "capabilities": ["hub_architecture", "multi_ERP", "Oracle_AHCS", "SAP_Central_Finance"],
        "embedding_tags": [
            "accounting hub", "multi-ERP", "centralized accounting",
            "hub spoke", "subledger", "journal aggregation",
        ],
        "confidence_threshold": 0.38,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write architecture docs", required=True),
        ],
    },
    "openclaw-orchestrator": {
        "domain": AgentDomain.AI_ORCHESTRATION,
        "capabilities": ["agent_orchestration", "LangGraph", "RAG", "tool_use", "multi_model"],
        "embedding_tags": [
            "orchestration", "agent workflow", "LangGraph", "RAG",
            "retrieval", "tool use", "multi-model", "AI pipeline",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="spawn_agent", description="Spawn sub-agents", required=True),
        ],
    },
    "vector-search-router": {
        "domain": AgentDomain.AI_ORCHESTRATION,
        "capabilities": ["semantic_routing", "vector_search", "agent_selection"],
        "embedding_tags": [
            "routing", "semantic search", "agent selection", "query classification",
        ],
        "confidence_threshold": 0.35,
        "model": "fast",
        "tools": [],
    },
    "databricks-pipeline-agent": {
        "domain": AgentDomain.DATA_ENGINEERING,
        "capabilities": ["Databricks", "Delta_Lake", "MLflow", "streaming", "finance_analytics"],
        "embedding_tags": [
            "Databricks", "Delta Lake", "Spark", "MLflow",
            "pipeline", "lakehouse", "streaming", "feature engineering",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="run_analytics", description="Run Databricks SQL", required=True),
            ToolPermission(name="write_file", description="Write pipeline code"),
        ],
    },
    "apqc-researcher": {
        "domain": AgentDomain.BENCHMARKING,
        "capabilities": ["APQC", "PCF", "benchmarks", "target_setting"],
        "embedding_tags": [
            "benchmark", "APQC", "PCF", "best practice",
            "performance metrics", "industry comparison",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="get_apqc_benchmark", description="Retrieve APQC benchmarks", required=True),
        ],
    },
    "fact-check-agent": {
        "domain": AgentDomain.QUALITY_ASSURANCE,
        "capabilities": ["citation_audit", "provenance", "model_attribution", "website_verification"],
        "embedding_tags": [
            "fact check", "citation", "source", "verify", "provenance",
            "audit", "reference", "accuracy",
        ],
        "confidence_threshold": 0.35,
        "model": "fast",
        "tools": [
            ToolPermission(name="web_search", description="Search public URLs for verification"),
            ToolPermission(name="read_file", description="Read session transcripts"),
        ],
    },
    "creative-designer": {
        "domain": AgentDomain.CREATIVE,
        "capabilities": ["visual_design", "dashboard_design", "presentation_design", "GUI_design"],
        "embedding_tags": [
            "design", "dashboard", "presentation", "visual", "GUI",
            "interface", "UX", "executive dashboard",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write design artifacts", required=True),
            ToolPermission(name="generate_html", description="Generate HTML/CSS prototypes"),
        ],
    },
    "rapid-prototyper": {
        "domain": AgentDomain.CREATIVE,
        "capabilities": ["prototyping", "demos", "calculators", "dashboards"],
        "embedding_tags": [
            "prototype", "demo", "mockup", "calculator",
            "dashboard", "quick build", "proof of concept",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write prototype code", required=True),
            ToolPermission(name="generate_html", description="Generate HTML prototypes"),
        ],
    },
    "si-finance-process-lead": {
        "domain": AgentDomain.PROCESS_CONSULTING,
        "capabilities": ["R2R", "O2C", "P2P", "planning", "process_design"],
        "embedding_tags": [
            "record to report", "order to cash", "procure to pay",
            "finance process", "month end close", "process design",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write process designs"),
            ToolPermission(name="get_apqc_benchmark", description="Get process benchmarks"),
        ],
    },
    "si-functional-lead": {
        "domain": AgentDomain.SYSTEMS,
        "capabilities": ["ERP_configuration", "Oracle", "SAP", "Workday", "OneStream", "Anaplan"],
        "embedding_tags": [
            "ERP", "configuration", "Oracle Cloud", "SAP S/4HANA",
            "Workday", "OneStream", "Anaplan", "functional design",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write config workbooks"),
            ToolPermission(name="read_file", description="Read requirements"),
        ],
    },
    "si-data-architect": {
        "domain": AgentDomain.DATA_ENGINEERING,
        "capabilities": ["data_migration", "MDM", "data_governance", "ETL"],
        "embedding_tags": [
            "data migration", "master data", "MDM", "data quality",
            "ETL", "data lake", "data warehouse", "data governance",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write migration plans"),
            ToolPermission(name="run_analytics", description="Run data quality checks"),
        ],
    },
    "si-integration-lead": {
        "domain": AgentDomain.SYSTEMS,
        "capabilities": ["APIs", "middleware", "B2B_EDI", "MuleSoft", "Boomi", "OIC"],
        "embedding_tags": [
            "integration", "API", "middleware", "MuleSoft", "Boomi",
            "OIC", "B2B", "EDI", "interface", "REST", "SOAP",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write integration specs"),
        ],
    },
    "si-security-controls-lead": {
        "domain": AgentDomain.RISK_ASSURANCE,
        "capabilities": ["SOD", "SOX", "RBAC", "access_management", "compliance"],
        "embedding_tags": [
            "security", "SOD", "segregation of duties", "SOX",
            "access control", "RBAC", "compliance", "controls",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write security designs"),
        ],
    },
    "si-change-management-lead": {
        "domain": AgentDomain.PROCESS_CONSULTING,
        "capabilities": ["OCM", "training", "adoption", "ADKAR", "stakeholder_management"],
        "embedding_tags": [
            "change management", "OCM", "training", "adoption",
            "ADKAR", "stakeholder", "business readiness",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write change plans"),
        ],
    },
    "si-data-analytics-lead": {
        "domain": AgentDomain.DATA_ENGINEERING,
        "capabilities": ["BI", "reporting", "dashboards", "Power_BI", "Tableau"],
        "embedding_tags": [
            "business intelligence", "BI", "reporting", "dashboard",
            "Power BI", "Tableau", "analytics", "data visualization",
        ],
        "confidence_threshold": 0.35,
        "model": "default",
        "tools": [
            ToolPermission(name="write_file", description="Write reporting specs"),
            ToolPermission(name="run_analytics", description="Run analytics queries"),
        ],
    },
}


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_md_file(path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_markdown) from an agent .md file."""
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    fm_raw = match.group(1)
    body = text[match.end():]

    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        logger.warning("Failed to parse YAML frontmatter in %s", path)
        fm = {}

    return fm, body


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class AgentRegistry:
    """
    Discovers and manages all Rudra agent definitions.

    Usage::

        registry = AgentRegistry.from_directory(Path("Rudra_Agents"))
        agent = registry.get("accounting-policy-engine")
    """

    def __init__(self) -> None:
        self._specs: dict[str, AgentSpec] = {}
        self._agents: dict[str, BaseAgent] = {}

    # -- Discovery ----------------------------------------------------------

    @classmethod
    def from_directory(cls, agents_dir: Optional[Path] = None) -> "AgentRegistry":
        config = get_config()
        agents_dir = agents_dir or config.agents_dir
        registry = cls()

        if not agents_dir.is_dir():
            logger.warning("Agents directory does not exist: %s", agents_dir)
            return registry

        for md_path in sorted(agents_dir.glob("*.md")):
            if md_path.name.startswith("ARCHITECTURE") or md_path.name.startswith("FT_"):
                continue
            try:
                spec = registry._load_spec(md_path)
                if spec:
                    registry._specs[spec.id] = spec
                    registry._agents[spec.id] = BaseAgent(spec)
                    logger.debug("Loaded agent: %s", spec.id)
            except Exception:
                logger.exception("Failed to load agent from %s", md_path)

        logger.info("Loaded %d agents from %s", len(registry._specs), agents_dir)
        return registry

    def _load_spec(self, path: Path) -> Optional[AgentSpec]:
        fm, body = _parse_md_file(path)
        if not fm or "name" not in fm:
            return None

        agent_id = fm["name"]
        catalog_entry = AGENT_CATALOG.get(agent_id, {})

        return AgentSpec(
            id=agent_id,
            name=agent_id.replace("-", " ").title(),
            description=fm.get("description", ""),
            domain=catalog_entry.get("domain", AgentDomain.PROGRAM_MANAGEMENT),
            system_prompt=body.strip(),
            capabilities=catalog_entry.get("capabilities", []),
            embedding_tags=catalog_entry.get("embedding_tags", []),
            confidence_threshold=catalog_entry.get("confidence_threshold", 0.72),
            model=catalog_entry.get("model", fm.get("model", "default")),
            color=fm.get("color", "gray"),
            tools=catalog_entry.get("tools", []),
            max_tokens=catalog_entry.get("max_tokens", 8096),
            timeout_seconds=catalog_entry.get("timeout_seconds", 120),
            upstream_agents=catalog_entry.get("upstream_agents", []),
            downstream_agents=catalog_entry.get("downstream_agents", []),
        )

    # -- Access -------------------------------------------------------------

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def get_spec(self, agent_id: str) -> Optional[AgentSpec]:
        return self._specs.get(agent_id)

    def list_agents(self) -> list[AgentSpec]:
        return list(self._specs.values())

    def list_ids(self) -> list[str]:
        return list(self._specs.keys())

    def by_domain(self, domain: AgentDomain) -> list[AgentSpec]:
        return [s for s in self._specs.values() if s.domain == domain]

    def __len__(self) -> int:
        return len(self._specs)

    def __contains__(self, agent_id: str) -> bool:
        return agent_id in self._specs

    def __repr__(self) -> str:
        return f"<AgentRegistry agents={len(self._specs)}>"
