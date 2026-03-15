"""
Multimodal Agentic AI — Finance Automation
Replaces keyword-trigger-based skill activation with intent-driven,
parallel-agent orchestration using Claude, Qwen, Databricks, and Kimi PARL.
"""

from .intent_router import route_to_agent
from .kimi_orchestrator import parallel_rudra_execution, run_month_end_close
from .multimodal_input import process_finance_document, process_and_route
from .databricks_backend import RudraDataBrain

__all__ = [
    "route_to_agent",
    "parallel_rudra_execution",
    "run_month_end_close",
    "process_finance_document",
    "process_and_route",
    "RudraDataBrain",
]
