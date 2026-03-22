"""
APQC benchmark data tool.

Provides built-in APQC benchmark data for finance function metrics.
In production, this would pull from a live APQC data feed or
a Databricks Delta table.
"""

from __future__ import annotations

from typing import Optional

# Built-in APQC benchmark data
_BENCHMARKS: dict[str, dict] = {
    "total_cost_finance_pct_revenue": {
        "metric": "Total Cost to Perform Finance Function (% of Revenue)",
        "pcf_reference": "9.0",
        "top_25": 0.6,
        "median": 1.0,
        "bottom_25": 1.8,
        "unit": "percent",
        "source": "APQC Open Standards Benchmarking",
    },
    "finance_ftes_per_billion": {
        "metric": "Finance FTEs per $1 Billion Revenue",
        "pcf_reference": "9.0",
        "top_25": 40,
        "median": 70,
        "bottom_25": 120,
        "unit": "FTEs",
        "source": "APQC Open Standards Benchmarking",
    },
    "days_to_close": {
        "metric": "Days to Close the Books",
        "pcf_reference": "9.3",
        "top_25": 4,
        "median": 6.5,
        "bottom_25": 10,
        "unit": "days",
        "source": "APQC Open Standards Benchmarking",
    },
    "cost_per_invoice_ap": {
        "metric": "Cost to Process a Single Invoice (AP)",
        "pcf_reference": "9.6",
        "top_25": 2,
        "median": 8,
        "bottom_25": 15,
        "unit": "USD",
        "variants": {
            "manual_no_po": {"low": 15, "high": 20},
            "fully_automated": {"low": 2, "high": 4},
            "best_in_class": {"low": 0.5, "high": 1.0},
        },
        "source": "APQC Open Standards Benchmarking",
    },
    "dso": {
        "metric": "Days Sales Outstanding (DSO)",
        "pcf_reference": "9.2",
        "top_25": 30,
        "median": 40,
        "bottom_25": 55,
        "unit": "days",
        "source": "APQC Open Standards Benchmarking",
    },
    "dpo": {
        "metric": "Days Payable Outstanding (DPO)",
        "pcf_reference": "9.6",
        "top_25": 35,
        "median": 45,
        "bottom_25": 60,
        "unit": "days",
        "source": "APQC Open Standards Benchmarking",
    },
    "journal_entries_per_fte": {
        "metric": "Journal Entries Processed per FTE",
        "pcf_reference": "9.3",
        "top_25": 3500,
        "median": 2000,
        "bottom_25": 1200,
        "unit": "entries/FTE",
        "source": "APQC Open Standards Benchmarking",
    },
    "accounts_payable_cost_pct_revenue": {
        "metric": "AP Cost as % of Revenue",
        "pcf_reference": "9.6",
        "top_25": 0.03,
        "median": 0.07,
        "bottom_25": 0.15,
        "unit": "percent",
        "source": "APQC Open Standards Benchmarking",
    },
    "budget_accuracy": {
        "metric": "Budget Accuracy (Variance %)",
        "pcf_reference": "9.1",
        "top_25": 3,
        "median": 7,
        "bottom_25": 15,
        "unit": "percent_variance",
        "source": "APQC Open Standards Benchmarking",
    },
    "finance_cost_per_employee": {
        "metric": "Total Finance Cost per Employee",
        "pcf_reference": "9.0",
        "top_25": 800,
        "median": 1500,
        "bottom_25": 2800,
        "unit": "USD",
        "source": "APQC Open Standards Benchmarking",
    },
    "accounts_receivable_cost_pct_revenue": {
        "metric": "AR Cost as % of Revenue",
        "pcf_reference": "9.2",
        "top_25": 0.02,
        "median": 0.05,
        "bottom_25": 0.12,
        "unit": "percent",
        "source": "APQC Open Standards Benchmarking",
    },
    "intercompany_transactions_pct_automated": {
        "metric": "Intercompany Transactions % Automated",
        "pcf_reference": "9.11",
        "top_25": 90,
        "median": 60,
        "bottom_25": 30,
        "unit": "percent",
        "source": "APQC Open Standards Benchmarking",
    },
}

# PCF 9.0 taxonomy
_PCF_CATEGORIES: dict[str, str] = {
    "9.1": "Perform Planning and Management Accounting",
    "9.2": "Perform Revenue Accounting",
    "9.3": "Perform General Accounting and Reporting",
    "9.4": "Manage Fixed Asset Project Accounting",
    "9.5": "Process Payroll",
    "9.6": "Process Accounts Payable and Expense Reimbursements",
    "9.7": "Manage Treasury",
    "9.8": "Manage Internal Controls",
    "9.9": "Manage Taxes",
    "9.10": "Manage International Funds/Compliance",
    "9.11": "Perform Intercompany Accounting",
}


def get_apqc_benchmark(
    metric: str,
    industry: Optional[str] = None,
    percentile: Optional[str] = None,
) -> dict:
    """
    Retrieve APQC benchmark data.

    Args:
        metric: Metric key or search term
        industry: Industry filter (not yet implemented for built-in data)
        percentile: Specific percentile to return (top_25, median, bottom_25)

    Returns:
        Benchmark data dict with metric values and metadata
    """
    metric_lower = metric.lower().replace(" ", "_")

    if metric_lower in _BENCHMARKS:
        data = _BENCHMARKS[metric_lower].copy()
    else:
        matches = [
            (k, v) for k, v in _BENCHMARKS.items()
            if metric.lower() in v["metric"].lower() or metric.lower() in k
        ]
        if not matches:
            return {
                "error": f"Metric '{metric}' not found",
                "available_metrics": list(_BENCHMARKS.keys()),
            }
        data = matches[0][1].copy()

    if percentile and percentile in data:
        data["requested_percentile"] = {
            "percentile": percentile,
            "value": data[percentile],
            "unit": data.get("unit", ""),
        }

    if industry:
        data["industry_note"] = (
            f"Industry-specific data for '{industry}' is not available in the "
            "built-in dataset. Use the Databricks integration for industry-filtered benchmarks."
        )

    return data


def get_pcf_category(code: str) -> Optional[str]:
    """Look up a PCF category description by code."""
    return _PCF_CATEGORIES.get(code)


def list_benchmarks() -> list[dict]:
    """List all available benchmark metrics."""
    return [
        {"key": k, "metric": v["metric"], "pcf": v.get("pcf_reference", "")}
        for k, v in _BENCHMARKS.items()
    ]
