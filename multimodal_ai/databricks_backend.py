"""
Databricks Backend — Rudra's Intelligence Layer.

Connects the Rudra agentic system to a Databricks Lakehouse for:
- Live APQC benchmark queries (replaces static tables in rudra.md:401-435)
- Agent execution audit trail via MLflow
- Finance ML models (forecasting, anomaly detection, close prediction)
- Persistent state management for long-running engagements

From rudra.md:38: Data platforms include Databricks, AWS, Snowflake, Azure.
This module makes Databricks the primary intelligence and persistence layer.
"""

import json
import os
import time
from typing import Any

try:
    from databricks import sql as databricks_sql
    import mlflow
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False
    print("[Databricks] SDK not installed. Using mock mode for development.")


class RudraDataBrain:
    """
    Databricks Lakehouse as Rudra's persistent knowledge and ML layer.

    Replaces:
    - Static benchmark tables (rudra.md:401) → live APQC queries
    - Manual audit trails → MLflow experiment tracking
    - Excel-based client data → Delta Lake tables
    - Static reporting → live BI-ready data marts
    """

    def __init__(
        self,
        server_hostname: str = None,
        http_path: str = None,
        token: str = None,
    ):
        self.server_hostname = server_hostname or os.environ.get("DATABRICKS_HOST", "")
        self.http_path = http_path or os.environ.get("DATABRICKS_HTTP_PATH", "")
        self.token = token or os.environ.get("DATABRICKS_TOKEN", "")
        self._conn = None

        if DATABRICKS_AVAILABLE and self.server_hostname and self.token:
            self._connect()

    def _connect(self):
        """Establish Databricks SQL connection."""
        self._conn = databricks_sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=self.token,
        )
        print(f"[Databricks] Connected to {self.server_hostname}")

    def _query(self, sql: str, params: dict = None) -> list[dict]:
        """Execute SQL and return results as list of dicts."""
        if not self._conn:
            print(f"[Databricks] Mock query: {sql[:80]}...")
            return self._mock_query(sql)

        cursor = self._conn.cursor()
        cursor.execute(sql, parameters=params or {})
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def _mock_query(self, sql: str) -> list[dict]:
        """Return mock data for development/testing without Databricks."""
        if "apqc" in sql.lower():
            return [
                {"metric_name": "days_to_close", "top25": 4.0, "median": 6.5, "bottom25": 10.0, "unit": "days"},
                {"metric_name": "ftes_per_1b_revenue", "top25": 40.0, "median": 70.0, "bottom25": 120.0, "unit": "FTEs"},
                {"metric_name": "cost_pct_revenue", "top25": 0.6, "median": 1.0, "bottom25": 1.8, "unit": "%"},
            ]
        if "engagement" in sql.lower():
            return [{"engagement_id": "mock-001", "client": "Test Client", "status": "active"}]
        return []

    # ─── APQC Benchmarks (Live) ─────────────────────────────────────────

    def get_apqc_benchmarks(
        self,
        process: str,
        industry: str = "cross_industry",
        metric: str = None,
    ) -> list[dict]:
        """
        Live APQC benchmarks — replaces the static table at rudra.md:401-435.

        Args:
            process: APQC PCF process code (e.g., "9.3", "R2R", "O2C")
            industry: Industry filter (default cross-industry)
            metric: Optional specific metric filter

        Returns:
            List of benchmark records with top25/median/bottom25 percentiles
        """
        metric_filter = "AND metric_name = :metric" if metric else ""
        sql = f"""
            SELECT
                metric_name,
                percentile_25 AS top25,
                median,
                percentile_75 AS bottom25,
                unit,
                source_year,
                industry
            FROM finance_benchmarks.apqc_pcf
            WHERE pcf_process LIKE :process
              AND industry IN (:industry, 'cross_industry')
              {metric_filter}
            ORDER BY metric_name
        """
        params = {"process": f"%{process}%", "industry": industry}
        if metric:
            params["metric"] = metric

        return self._query(sql, params)

    def get_benchmark_gap(
        self,
        client_metrics: dict[str, float],
        process: str,
        industry: str = "cross_industry",
    ) -> dict[str, Any]:
        """
        Calculate gaps between client's current metrics and APQC benchmarks.
        Used by apqc-researcher agent for business case development.

        Args:
            client_metrics: dict of {metric_name: current_value}
            process: APQC process code
            industry: Industry comparison group

        Returns:
            dict with gap analysis per metric
        """
        benchmarks = self.get_apqc_benchmarks(process, industry)
        gaps = {}

        for bm in benchmarks:
            metric = bm["metric_name"]
            if metric not in client_metrics:
                continue

            current = client_metrics[metric]
            top25 = bm["top25"]
            median = bm["median"]

            gap_to_top25 = current - top25
            gap_to_median = current - median

            gaps[metric] = {
                "current": current,
                "top25": top25,
                "median": median,
                "bottom25": bm["bottom25"],
                "unit": bm["unit"],
                "gap_to_top25": gap_to_top25,
                "gap_to_median": gap_to_median,
                "percentile_position": "top25" if current <= top25
                    else "top50" if current <= median
                    else "bottom50",
            }

        return gaps

    # ─── Agent Execution Audit (MLflow) ─────────────────────────────────

    def log_agent_execution(
        self,
        agent_name: str,
        task: str,
        output: str,
        model_used: str = "claude-opus-4-6",
        metadata: dict = None,
        experiment_name: str = "rudra-agents",
    ) -> str:
        """
        Log every Rudra agent execution to MLflow for audit trail.
        Powers the fact-check-agent's model attribution tracking.

        Returns:
            MLflow run_id for reference
        """
        if not DATABRICKS_AVAILABLE:
            print(f"[MLflow] Mock log: agent={agent_name}, model={model_used}")
            return f"mock-run-{int(time.time())}"

        mlflow.set_experiment(experiment_name)
        with mlflow.start_run() as run:
            mlflow.log_param("agent", agent_name)
            mlflow.log_param("model_used", model_used)
            mlflow.log_param("task_summary", task[:200])

            mlflow.log_metric("output_length", len(output))
            mlflow.log_metric("timestamp", time.time())

            mlflow.log_text(task, "task.txt")
            mlflow.log_text(output, "agent_output.txt")

            if metadata:
                mlflow.log_dict(metadata, "metadata.json")

            return run.info.run_id

    def get_agent_run_history(
        self,
        agent_name: str = None,
        limit: int = 50,
        experiment_name: str = "rudra-agents",
    ) -> list[dict]:
        """
        Retrieve agent execution history for fact-checking and audit.
        Used by fact-check-agent to trace model → output provenance.
        """
        if not DATABRICKS_AVAILABLE:
            return [{"agent": agent_name or "all", "runs": 0, "mock": True}]

        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)
        if not experiment:
            return []

        filter_str = f"params.agent = '{agent_name}'" if agent_name else ""
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=filter_str,
            max_results=limit,
            order_by=["start_time DESC"],
        )

        return [
            {
                "run_id": r.info.run_id,
                "agent": r.data.params.get("agent"),
                "model": r.data.params.get("model_used"),
                "task": r.data.params.get("task_summary"),
                "start_time": r.info.start_time,
                "status": r.info.status,
            }
            for r in runs
        ]

    # ─── Engagement State (Delta Lake) ──────────────────────────────────

    def save_engagement_state(self, engagement_id: str, state: dict) -> bool:
        """
        Persist engagement state to Delta Lake for cross-session continuity.
        Enables resuming long-running ERP implementations across multiple sessions.
        """
        sql = """
            MERGE INTO engagements.state AS target
            USING (SELECT :engagement_id AS id, :state AS state_json, current_timestamp() AS updated_at) AS source
            ON target.id = source.id
            WHEN MATCHED THEN UPDATE SET state_json = source.state_json, updated_at = source.updated_at
            WHEN NOT MATCHED THEN INSERT (id, state_json, updated_at) VALUES (source.id, source.state_json, source.updated_at)
        """
        try:
            self._query(sql, {
                "engagement_id": engagement_id,
                "state": json.dumps(state),
            })
            return True
        except Exception as e:
            print(f"[Databricks] State save failed: {e}")
            return False

    def load_engagement_state(self, engagement_id: str) -> dict:
        """Load previously saved engagement state."""
        sql = """
            SELECT state_json, updated_at
            FROM engagements.state
            WHERE id = :engagement_id
            ORDER BY updated_at DESC
            LIMIT 1
        """
        rows = self._query(sql, {"engagement_id": engagement_id})
        if not rows:
            return {}
        return json.loads(rows[0]["state_json"])

    # ─── Finance ML Models ──────────────────────────────────────────────

    def run_close_prediction(self, current_period_data: dict) -> dict:
        """
        Predict financial close completion date using MLflow-registered model.
        Input: current open items, reconciliation status, IC matching progress.
        Output: predicted close date, confidence interval, bottleneck forecast.
        """
        if not DATABRICKS_AVAILABLE:
            return {
                "predicted_close_day": 5.5,
                "confidence": 0.82,
                "bottleneck": "intercompany_matching",
                "mock": True,
            }

        model = mlflow.pyfunc.load_model("models:/close-predictor/Production")
        return model.predict(current_period_data)

    def run_anomaly_detection(self, journal_entries: list[dict]) -> list[dict]:
        """
        Detect anomalous journal entries using Databricks ML model.
        Flags unusual amounts, off-cycle postings, unsupported accounts.
        """
        if not DATABRICKS_AVAILABLE:
            return [{"entry_id": "mock", "anomaly_score": 0.12, "mock": True}]

        model = mlflow.pyfunc.load_model("models:/je-anomaly-detector/Production")
        return model.predict(journal_entries)

    def run_cash_forecast(self, historical_data: dict) -> dict:
        """
        13-week rolling cash flow forecast using Databricks ML.
        Integrates AR aging, AP schedule, and treasury position.
        """
        if not DATABRICKS_AVAILABLE:
            return {"forecast_weeks": 13, "net_cash_position": 0, "mock": True}

        model = mlflow.pyfunc.load_model("models:/cash-forecaster/Production")
        return model.predict(historical_data)

    def close(self):
        """Close the Databricks connection."""
        if self._conn:
            self._conn.close()
            print("[Databricks] Connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
