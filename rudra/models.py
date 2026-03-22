"""
Core Pydantic models for the Rudra framework.

Every agent has a formal spec (AgentSpec), every invocation produces an
AgentResult, and the orchestration state is captured in RudraState.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AgentDomain(str, Enum):
    TECHNICAL_ACCOUNTING = "technical_accounting"
    DEALS_ADVISORY = "deals_advisory"
    TAX = "tax"
    TREASURY = "treasury"
    SUSTAINABILITY = "sustainability"
    RISK_ASSURANCE = "risk_assurance"
    REPORTING = "reporting"
    SYSTEMS = "systems"
    PROCESS_CONSULTING = "process_consulting"
    DATA_ENGINEERING = "data_engineering"
    AI_ORCHESTRATION = "ai_orchestration"
    PROGRAM_MANAGEMENT = "program_management"
    BENCHMARKING = "benchmarking"
    CREATIVE = "creative"
    QUALITY_ASSURANCE = "quality_assurance"


class PipelineMode(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"


class ReportingBasis(str, Enum):
    IFRS = "IFRS"
    US_GAAP = "US_GAAP"
    BOTH = "BOTH"


class OutputFormat(str, Enum):
    NARRATIVE = "narrative"
    JSON = "json"
    TABLE = "table"
    HTML = "html"


class Audience(str, Enum):
    CONTROLLER = "controller"
    AUDITOR = "auditor"
    FPA = "fpa"
    BOARD = "board"
    SYSTEM = "system"


class InvocationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


# ---------------------------------------------------------------------------
# Agent specification
# ---------------------------------------------------------------------------

class ToolPermission(BaseModel):
    name: str
    description: str = ""
    required: bool = False


class AgentSpec(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field("", description="What the agent does")
    domain: AgentDomain = Field(..., description="Primary domain")
    system_prompt: str = Field("", description="Full system prompt from .md body")

    capabilities: list[str] = Field(default_factory=list)
    embedding_tags: list[str] = Field(default_factory=list)
    confidence_threshold: float = Field(0.72, ge=0.0, le=1.0)

    model: str = Field("default")
    color: str = Field("gray")

    tools: list[ToolPermission] = Field(default_factory=list)

    max_tokens: int = Field(8096)
    timeout_seconds: int = Field(120)
    max_retries: int = Field(2)

    upstream_agents: list[str] = Field(default_factory=list)
    downstream_agents: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Invocation request / result
# ---------------------------------------------------------------------------

class AgentRequest(BaseModel):
    agent_id: str
    query: str
    facts: str = ""
    reporting_basis: ReportingBasis = ReportingBasis.BOTH
    output_format: OutputFormat = OutputFormat.NARRATIVE
    audience: Audience = Audience.CONTROLLER
    context: dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    parent_agent_id: Optional[str] = None


class AgentResult(BaseModel):
    agent_id: str
    status: InvocationStatus = InvocationStatus.COMPLETED
    response: str = ""
    structured_output: dict[str, Any] = Field(default_factory=dict)
    citations: list[str] = Field(default_factory=list)
    tokens_used: int = 0
    model_used: str = ""
    duration_ms: int = 0
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def succeeded(self) -> bool:
        return self.status == InvocationStatus.COMPLETED


# ---------------------------------------------------------------------------
# Routing decision
# ---------------------------------------------------------------------------

class AgentMatch(BaseModel):
    agent_id: str
    confidence: float
    reason: str = ""
    role: str = ""


class RoutingDecision(BaseModel):
    query: str
    intent: str = ""
    primary_agent: AgentMatch
    secondary_agents: list[AgentMatch] = Field(default_factory=list)
    pipeline_mode: PipelineMode = PipelineMode.SEQUENTIAL
    context_for_agent: str = ""
    requires_disambiguation: bool = False
    disambiguation_questions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Orchestration state
# ---------------------------------------------------------------------------

class RudraState(BaseModel):
    query: str = ""
    reporting_basis: ReportingBasis = ReportingBasis.BOTH
    output_format: OutputFormat = OutputFormat.NARRATIVE
    audience: Audience = Audience.CONTROLLER

    routing_decision: Optional[RoutingDecision] = None

    normalized_facts: dict[str, Any] = Field(default_factory=dict)
    agent_outputs: dict[str, AgentResult] = Field(default_factory=dict)

    requires_human_review: bool = False
    human_feedback: str = ""
    iteration_count: int = 0
    current_step: str = ""
    error: Optional[str] = None

    final_response: str = ""
    citations: list[str] = Field(default_factory=list)

    session_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
