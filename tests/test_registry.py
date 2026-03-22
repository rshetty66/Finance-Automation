"""Tests for the agent registry."""

import pytest
from pathlib import Path

from rudra.agents.registry import AgentRegistry, _parse_md_file, AGENT_CATALOG
from rudra.models import AgentDomain


AGENTS_DIR = Path(__file__).resolve().parent.parent / "Rudra_Agents"


class TestFrontmatterParser:
    def test_parse_rudra_md(self):
        path = AGENTS_DIR / "rudra.md"
        if not path.exists():
            pytest.skip("Rudra_Agents directory not found")

        fm, body = _parse_md_file(path)
        assert fm["name"] == "rudra"
        assert "model" in fm
        assert len(body) > 100

    def test_parse_accounting_policy(self):
        path = AGENTS_DIR / "accounting-policy-engine.md"
        if not path.exists():
            pytest.skip("Rudra_Agents directory not found")

        fm, body = _parse_md_file(path)
        assert fm["name"] == "accounting-policy-engine"
        assert "IFRS" in body


class TestAgentRegistry:
    def test_load_from_directory(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        assert len(registry) > 20

    def test_get_agent(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        agent = registry.get("rudra")
        assert agent is not None
        assert agent.id == "rudra"

    def test_get_spec(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        spec = registry.get_spec("accounting-policy-engine")
        assert spec is not None
        assert spec.domain == "technical_accounting"
        assert spec.model == "reasoning"

    def test_list_agents(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        agents = registry.list_agents()
        assert len(agents) > 0
        assert all(hasattr(a, "id") for a in agents)

    def test_by_domain(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        accounting_agents = registry.by_domain(AgentDomain.TECHNICAL_ACCOUNTING)
        assert len(accounting_agents) >= 3

    def test_contains(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        assert "rudra" in registry
        assert "nonexistent-agent" not in registry

    def test_agent_has_system_prompt(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        spec = registry.get_spec("accounting-policy-engine")
        assert spec is not None
        assert len(spec.system_prompt) > 500
        assert "Accounting Policy Reasoning Engine" in spec.system_prompt

    def test_agent_has_tools(self):
        if not AGENTS_DIR.is_dir():
            pytest.skip("Rudra_Agents directory not found")

        registry = AgentRegistry.from_directory(AGENTS_DIR)
        spec = registry.get_spec("rudra")
        assert spec is not None
        assert len(spec.tools) > 0
        tool_names = [t.name for t in spec.tools]
        assert "spawn_agent" in tool_names


class TestAgentCatalog:
    def test_all_agents_have_domains(self):
        for agent_id, entry in AGENT_CATALOG.items():
            assert "domain" in entry, f"{agent_id} missing domain"

    def test_all_agents_have_capabilities(self):
        for agent_id, entry in AGENT_CATALOG.items():
            assert "capabilities" in entry, f"{agent_id} missing capabilities"
            assert len(entry["capabilities"]) > 0, f"{agent_id} has empty capabilities"

    def test_all_agents_have_embedding_tags(self):
        for agent_id, entry in AGENT_CATALOG.items():
            assert "embedding_tags" in entry, f"{agent_id} missing embedding_tags"
            assert len(entry["embedding_tags"]) > 0, f"{agent_id} has empty embedding_tags"

    def test_catalog_matches_md_files(self):
        assert len(AGENT_CATALOG) == 27
