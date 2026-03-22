"""Tests for core Pydantic models."""

import pytest
from rudra.models import (
    AgentSpec,
    AgentRequest,
    AgentResult,
    AgentMatch,
    RoutingDecision,
    RudraState,
    AgentDomain,
    InvocationStatus,
    ReportingBasis,
    OutputFormat,
    Audience,
    PipelineMode,
    ToolPermission,
)


class TestAgentSpec:
    def test_create_minimal(self):
        spec = AgentSpec(
            id="test-agent",
            name="Test Agent",
            domain=AgentDomain.TECHNICAL_ACCOUNTING,
        )
        assert spec.id == "test-agent"
        assert spec.domain == "technical_accounting"
        assert spec.confidence_threshold == 0.72
        assert spec.max_tokens == 8096

    def test_create_full(self):
        spec = AgentSpec(
            id="accounting-policy-engine",
            name="Accounting Policy Engine",
            domain=AgentDomain.TECHNICAL_ACCOUNTING,
            capabilities=["IFRS", "US_GAAP"],
            embedding_tags=["revenue", "lease"],
            confidence_threshold=0.75,
            model="reasoning",
            tools=[ToolPermission(name="search_standards", required=True)],
            max_tokens=16000,
            upstream_agents=["rudra"],
        )
        assert len(spec.capabilities) == 2
        assert spec.tools[0].name == "search_standards"
        assert spec.tools[0].required is True

    def test_confidence_threshold_bounds(self):
        with pytest.raises(Exception):
            AgentSpec(id="x", name="x", domain=AgentDomain.TAX, confidence_threshold=1.5)


class TestAgentRequest:
    def test_defaults(self):
        req = AgentRequest(agent_id="test", query="hello")
        assert req.reporting_basis == ReportingBasis.BOTH
        assert req.output_format == OutputFormat.NARRATIVE
        assert req.audience == Audience.CONTROLLER

    def test_full(self):
        req = AgentRequest(
            agent_id="accounting-policy-engine",
            query="Analyze lease",
            facts="HQ sale-leaseback",
            reporting_basis=ReportingBasis.IFRS,
            output_format=OutputFormat.JSON,
            audience=Audience.AUDITOR,
            context={"entity": "Corp"},
        )
        assert req.facts == "HQ sale-leaseback"
        assert req.context["entity"] == "Corp"


class TestAgentResult:
    def test_success(self):
        result = AgentResult(
            agent_id="test",
            status=InvocationStatus.COMPLETED,
            response="Analysis complete",
            tokens_used=500,
        )
        assert result.succeeded is True

    def test_failure(self):
        result = AgentResult(
            agent_id="test",
            status=InvocationStatus.FAILED,
            error="Timeout",
        )
        assert result.succeeded is False


class TestRoutingDecision:
    def test_create(self):
        decision = RoutingDecision(
            query="test query",
            intent="analyze",
            primary_agent=AgentMatch(
                agent_id="lease-accounting-agent",
                confidence=0.89,
            ),
            secondary_agents=[
                AgentMatch(agent_id="accounting-policy-engine", confidence=0.82),
            ],
            pipeline_mode=PipelineMode.SEQUENTIAL,
        )
        assert decision.primary_agent.agent_id == "lease-accounting-agent"
        assert len(decision.secondary_agents) == 1


class TestRudraState:
    def test_defaults(self):
        state = RudraState()
        assert state.reporting_basis == ReportingBasis.BOTH
        assert state.iteration_count == 0
        assert state.agent_outputs == {}
