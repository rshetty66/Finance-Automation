"""
FastAPI application for the Rudra Agent Framework.

Provides REST API endpoints and serves the interactive web UI.
"""

from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Rudra Agent Framework",
    description="Skills-based multi-agent platform for finance transformation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# Lazy-loaded singletons
# ---------------------------------------------------------------------------
_registry = None
_router = None
_index = None


def _get_registry():
    global _registry
    if _registry is None:
        from rudra.agents.registry import AgentRegistry
        _registry = AgentRegistry.from_directory()
    return _registry


def _get_router():
    global _router, _index
    if _router is None:
        from rudra.routing.router import VectorSearchRouter
        from rudra.routing.index import AgentCapabilityIndex
        registry = _get_registry()
        _index = AgentCapabilityIndex.from_specs(registry.list_agents())
        _router = VectorSearchRouter(registry, _index)
    return _router


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class RouteRequest(BaseModel):
    query: str
    top_k: int = 5


class ChatRequest(BaseModel):
    query: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    reporting_basis: str = "BOTH"
    output_format: str = "narrative"
    audience: str = "controller"


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Rudra Agent Framework</h1><p>Static files not found.</p>")


# ---------------------------------------------------------------------------
# Agent endpoints
# ---------------------------------------------------------------------------

@app.get("/api/agents")
async def list_agents():
    registry = _get_registry()
    agents = []
    for spec in registry.list_agents():
        agents.append({
            "id": spec.id,
            "name": spec.name,
            "domain": spec.domain,
            "description": spec.description[:200] + "..." if len(spec.description) > 200 else spec.description,
            "model": spec.model,
            "color": spec.color,
            "capabilities": spec.capabilities,
            "embedding_tags": spec.embedding_tags,
            "tools": [{"name": t.name, "required": t.required} for t in spec.tools],
            "confidence_threshold": spec.confidence_threshold,
            "upstream_agents": spec.upstream_agents,
            "downstream_agents": spec.downstream_agents,
        })
    return {"agents": agents, "total": len(agents)}


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    registry = _get_registry()
    spec = registry.get_spec(agent_id)
    if spec is None:
        raise HTTPException(404, f"Agent '{agent_id}' not found")
    return {
        "id": spec.id,
        "name": spec.name,
        "domain": spec.domain,
        "description": spec.description,
        "system_prompt": spec.system_prompt[:2000] + "..." if len(spec.system_prompt) > 2000 else spec.system_prompt,
        "model": spec.model,
        "color": spec.color,
        "capabilities": spec.capabilities,
        "embedding_tags": spec.embedding_tags,
        "tools": [{"name": t.name, "description": t.description, "required": t.required} for t in spec.tools],
        "max_tokens": spec.max_tokens,
        "timeout_seconds": spec.timeout_seconds,
        "upstream_agents": spec.upstream_agents,
        "downstream_agents": spec.downstream_agents,
    }


@app.get("/api/agents/domain/{domain}")
async def get_agents_by_domain(domain: str):
    registry = _get_registry()
    from rudra.models import AgentDomain
    try:
        d = AgentDomain(domain)
    except ValueError:
        raise HTTPException(400, f"Invalid domain: {domain}")
    agents = registry.by_domain(d)
    return {"domain": domain, "agents": [{"id": a.id, "name": a.name} for a in agents]}


# ---------------------------------------------------------------------------
# Routing endpoints
# ---------------------------------------------------------------------------

@app.post("/api/route")
async def route_query(req: RouteRequest):
    router = _get_router()
    start = time.monotonic()
    decision = router.route(req.query, top_k=req.top_k)
    duration_ms = int((time.monotonic() - start) * 1000)

    return {
        "query": decision.query,
        "intent": decision.intent,
        "primary_agent": decision.primary_agent.model_dump(),
        "secondary_agents": [a.model_dump() for a in decision.secondary_agents],
        "pipeline_mode": decision.pipeline_mode,
        "requires_disambiguation": decision.requires_disambiguation,
        "disambiguation_questions": decision.disambiguation_questions,
        "duration_ms": duration_ms,
    }


@app.get("/api/route/all-scores")
async def route_all_scores(query: str = Query(...)):
    router = _get_router()
    results = router.index.search_all(query)
    return {
        "query": query,
        "scores": [
            {
                "agent_id": entry.agent_id,
                "domain": entry.domain,
                "score": round(score, 4),
                "threshold": entry.confidence_threshold,
                "above_threshold": score >= entry.confidence_threshold,
                "is_catch_all": entry.is_catch_all,
            }
            for entry, score in results
        ],
    }


# ---------------------------------------------------------------------------
# Tools endpoints
# ---------------------------------------------------------------------------

@app.get("/api/benchmarks")
async def list_benchmarks():
    from rudra.tools.benchmarks import list_benchmarks
    return {"benchmarks": list_benchmarks()}


@app.get("/api/benchmarks/{metric}")
async def get_benchmark(metric: str, percentile: Optional[str] = None, industry: Optional[str] = None):
    from rudra.tools.benchmarks import get_apqc_benchmark
    result = get_apqc_benchmark(metric, industry=industry, percentile=percentile)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@app.get("/api/standards/search")
async def search_standards(query: str = Query(...), category: Optional[str] = None, k: int = 5):
    from rudra.tools.standards import search_standards
    results = search_standards(query, category=category, k=k)
    return {"query": query, "results": results, "total": len(results)}


@app.get("/api/analytics/templates")
async def list_analytics():
    from rudra.tools.analytics import list_query_types
    return {"query_types": list_query_types()}


@app.get("/api/analytics/{query_type}")
async def get_analytics(query_type: str, entity_id: str = "", period: str = ""):
    from rudra.tools.analytics import run_analytics_query
    result = run_analytics_query(query_type, entity_id=entity_id, period=period)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


# ---------------------------------------------------------------------------
# Evaluation endpoints
# ---------------------------------------------------------------------------

@app.get("/api/eval/routing")
async def eval_routing():
    from rudra.eval.harness import EvaluationHarness
    harness = EvaluationHarness()
    metrics = harness.eval_routing()
    return {
        "summary": metrics.summary(),
        "results": metrics.results,
    }


@app.get("/api/eval/tools")
async def eval_tools():
    from rudra.eval.harness import EvaluationHarness
    harness = EvaluationHarness()
    metrics = harness.eval_tools()
    return {
        "summary": metrics.summary(),
        "results": metrics.results,
    }


# ---------------------------------------------------------------------------
# PCF taxonomy
# ---------------------------------------------------------------------------

@app.get("/api/pcf")
async def get_pcf():
    from rudra.tools.benchmarks import _PCF_CATEGORIES
    return {"categories": [{"code": k, "description": v} for k, v in _PCF_CATEGORIES.items()]}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    registry = _get_registry()
    return {
        "status": "healthy",
        "agents_loaded": len(registry),
        "version": "0.1.0",
    }


def start():
    """Entry point for `rudra serve` command."""
    import uvicorn
    uvicorn.run("rudra.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
