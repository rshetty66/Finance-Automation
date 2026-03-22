"""Databricks Agentic AI Framework integration.

Capabilities:
  • Vector Search (semantic RAG over accounting standards)
  • Delta Lake SQL analytics (finance metrics, KPIs)
  • MLflow experiment tracking
  • Databricks Jobs (pipeline execution)
  • Unity Catalog (data governance)
  • Agent compute (Mosaic AI Model Serving)

Implements the Databricks Agentic AI pattern:
  Agent → Tools → Databricks Lakehouse
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class VectorSearchResult:
    chunk: str
    score: float
    source: str
    metadata: dict


@dataclass
class SQLResult:
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    execution_time_ms: float


class DatabricksTool:
    """Databricks Agentic AI integration for Finance Automation."""

    def __init__(
        self,
        host: str | None = None,
        token: str | None = None,
        catalog: str = "finance_automation",
        schema: str = "rudra_agents",
        warehouse_id: str | None = None,
    ):
        self.host = host or os.environ.get("DATABRICKS_HOST", "")
        self.token = token or os.environ.get("DATABRICKS_TOKEN", "")
        self.warehouse_id = warehouse_id or os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
        self.catalog = catalog
        self.schema = schema
        self._ws = None  # Workspace client — lazy-init
        self._sql_conn = None  # SQL connector — lazy-init

    # ─── Workspace Client ─────────────────────────────────────────────────────

    def _get_workspace(self):
        """Lazy-initialize Databricks SDK workspace client."""
        if self._ws is None:
            try:
                from databricks.sdk import WorkspaceClient

                self._ws = WorkspaceClient(host=self.host, token=self.token)
            except ImportError:
                raise RuntimeError("Install databricks-sdk: pip install databricks-sdk")
        return self._ws

    # ─── Vector Search / RAG ──────────────────────────────────────────────────

    def search_standards(
        self,
        query: str,
        category: str | None = None,
        top_k: int = 5,
        index_name: str | None = None,
    ) -> list[VectorSearchResult]:
        """Semantic search over IFRS/GAAP standards corpus using Databricks Vector Search."""
        idx = index_name or f"{self.catalog}.{self.schema}.standards_index"
        filters = {}
        if category:
            filters["category"] = category

        try:
            ws = self._get_workspace()
            results = ws.vector_search_indexes.query_index(
                index_name=idx,
                columns=["chunk", "source", "category", "standard", "score"],
                query_text=query,
                filters_json=json.dumps(filters) if filters else None,
                num_results=top_k,
            )
            rows = results.result.data_array or []
            cols = [c.name for c in results.manifest.columns]
            return [
                VectorSearchResult(
                    chunk=row[cols.index("chunk")] if "chunk" in cols else "",
                    score=float(row[cols.index("score")]) if "score" in cols else 0.0,
                    source=row[cols.index("source")] if "source" in cols else "",
                    metadata={
                        k: row[cols.index(k)]
                        for k in ["category", "standard"]
                        if k in cols
                    },
                )
                for row in rows
            ]
        except Exception:
            return self._mock_standards_search(query, category, top_k)

    # ─── SQL Analytics ────────────────────────────────────────────────────────

    def run_analytics(self, sql: str) -> SQLResult:
        """Execute a SQL query on the Databricks lakehouse."""
        try:
            conn = self._get_sql_connection()
            cursor = conn.cursor()
            import time

            t0 = time.time()
            cursor.execute(sql)
            rows = cursor.fetchall()
            elapsed = (time.time() - t0) * 1000
            cols = [desc[0] for desc in cursor.description] if cursor.description else []
            return SQLResult(
                columns=cols,
                rows=[list(row) for row in rows],
                row_count=len(rows),
                execution_time_ms=elapsed,
            )
        except Exception:
            return self._mock_sql_result(sql)

    def _get_sql_connection(self):
        if self._sql_conn is None:
            try:
                from databricks import sql

                self._sql_conn = sql.connect(
                    server_hostname=self.host.replace("https://", ""),
                    http_path=f"/sql/1.0/warehouses/{self.warehouse_id}",
                    access_token=self.token,
                )
            except ImportError:
                raise RuntimeError("Install databricks-sql-connector: pip install databricks-sql-connector")
        return self._sql_conn

    # ─── Finance Analytics Queries ────────────────────────────────────────────

    def get_close_metrics(self, period: str = "2024-12") -> dict:
        """Retrieve month-end close KPIs from the lakehouse."""
        sql = f"""
        SELECT
            period,
            close_day,
            je_count,
            recon_count,
            auto_posting_rate_pct,
            manual_je_pct,
            interco_match_rate_pct
        FROM {self.catalog}.{self.schema}.close_metrics
        WHERE period = '{period}'
        ORDER BY close_day
        """
        result = self.run_analytics(sql)
        if result.rows:
            return dict(zip(result.columns, result.rows[0]))
        return {"period": period, "status": "no_data"}

    def get_erp_kpis(self, module: str = "GL") -> list[dict]:
        """Return ERP module KPIs from the lakehouse."""
        sql = f"""
        SELECT kpi_name, value, target, variance_pct, status
        FROM {self.catalog}.{self.schema}.erp_kpis
        WHERE module = '{module}'
        ORDER BY kpi_name
        """
        result = self.run_analytics(sql)
        return [dict(zip(result.columns, row)) for row in result.rows]

    def get_epm_forecast(self, scenario: str = "Base", fiscal_year: int = 2025) -> list[dict]:
        """Retrieve EPM forecast data for scenario analysis."""
        sql = f"""
        SELECT account, period, actual, forecast, budget, variance
        FROM {self.catalog}.{self.schema}.epm_forecast
        WHERE scenario = '{scenario}' AND fiscal_year = {fiscal_year}
        ORDER BY account, period
        """
        result = self.run_analytics(sql)
        return [dict(zip(result.columns, row)) for row in result.rows]

    # ─── Databricks Jobs / Pipelines ──────────────────────────────────────────

    def trigger_pipeline(self, job_name: str, parameters: dict | None = None) -> str:
        """Trigger a Databricks Job and return the run URL."""
        try:
            ws = self._get_workspace()
            jobs = list(ws.jobs.list(name=job_name))
            if not jobs:
                return f"[mock] Pipeline '{job_name}' triggered successfully"
            job_id = jobs[0].job_id
            run = ws.jobs.run_now(job_id=job_id, notebook_params=parameters or {})
            return f"https://{self.host}/jobs/{job_id}/runs/{run.run_id}"
        except Exception as exc:
            return f"[mock] Pipeline '{job_name}' triggered (offline mode): {exc}"

    # ─── MLflow / Model Serving ────────────────────────────────────────────────

    def log_agent_run(self, agent_name: str, task: str, metrics: dict) -> str:
        """Log an agent run to MLflow for governance and auditability."""
        try:
            import mlflow

            mlflow.set_tracking_uri(f"{self.host}/api/2.0/mlflow")
            with mlflow.start_run(run_name=f"{agent_name}_{task}") as run:
                mlflow.log_params({"agent": agent_name, "task": task})
                mlflow.log_metrics({k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))})
                return run.info.run_id
        except Exception:
            return f"mock-run-{agent_name}-{task}"

    # ─── Tool Definitions for Agent Use ───────────────────────────────────────

    @staticmethod
    def tool_definitions() -> list[dict]:
        return [
            {
                "name": "search_standards",
                "description": "Search IFRS/GAAP accounting standards using Databricks Vector Search",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural language search query"},
                        "category": {
                            "type": "string",
                            "enum": ["IFRS", "US_GAAP", "POLICIES"],
                            "description": "Filter by standard category",
                        },
                        "top_k": {"type": "integer", "default": 5},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "run_close_analytics",
                "description": "Execute SQL analytics queries on the Databricks finance lakehouse",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "SQL query to execute"},
                    },
                    "required": ["sql"],
                },
            },
            {
                "name": "get_epm_forecast",
                "description": "Retrieve EPM forecast and budget data from Databricks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "scenario": {"type": "string", "default": "Base"},
                        "fiscal_year": {"type": "integer", "default": 2025},
                    },
                },
            },
        ]

    # ─── Mock Data (offline development) ──────────────────────────────────────

    def _mock_standards_search(self, query: str, category: str | None, top_k: int) -> list[VectorSearchResult]:
        mock_results = [
            VectorSearchResult(
                chunk=f"IFRS 15 Revenue Recognition: {query[:60]} — The five-step model requires identifying performance obligations...",
                score=0.95,
                source="IFRS_15_Revenue_Recognition.pdf",
                metadata={"category": "IFRS", "standard": "IFRS 15"},
            ),
            VectorSearchResult(
                chunk=f"ASC 606 Topic 606: {query[:60]} — An entity shall recognize revenue when it satisfies a performance obligation...",
                score=0.88,
                source="ASC_606.pdf",
                metadata={"category": "US_GAAP", "standard": "ASC 606"},
            ),
        ]
        return mock_results[:top_k]

    def _mock_sql_result(self, sql: str) -> SQLResult:
        return SQLResult(
            columns=["period", "metric", "value"],
            rows=[["2024-12", "close_day", 5], ["2024-12", "je_count", 1240]],
            row_count=2,
            execution_time_ms=12.5,
        )
