"""
Finance analytics query tool.

Provides built-in analytics patterns that agents can invoke.
In production, these would execute against Databricks SQL or
a connected data warehouse.
"""

from __future__ import annotations

from typing import Any, Optional


# SQL templates for common finance analytics
_QUERY_TEMPLATES: dict[str, str] = {
    "close_metrics": """
        SELECT
            entity_id,
            period_key,
            MIN(accounting_date) AS first_posting,
            MAX(accounting_date) AS last_posting,
            DATEDIFF(MAX(accounting_date), DATE_TRUNC('MONTH', MAX(accounting_date))) + 1 AS days_to_close,
            COUNT(DISTINCT journal_id) AS total_journals,
            SUM(CASE WHEN journal_category = 'ACCRUAL' THEN 1 ELSE 0 END) AS accrual_count,
            SUM(CASE WHEN journal_category = 'RECLASS' THEN 1 ELSE 0 END) AS reclass_count
        FROM rudra_finance.silver.gl_transactions
        WHERE entity_id = '{entity_id}'
          AND period_key = '{period}'
        GROUP BY entity_id, period_key
    """,

    "ar_aging": """
        SELECT
            entity_id,
            customer_id,
            invoice_date,
            due_date,
            amount_outstanding,
            DATEDIFF(CURRENT_DATE, due_date) AS days_past_due,
            CASE
                WHEN DATEDIFF(CURRENT_DATE, due_date) <= 0 THEN 'Current'
                WHEN DATEDIFF(CURRENT_DATE, due_date) BETWEEN 1 AND 30 THEN '1-30'
                WHEN DATEDIFF(CURRENT_DATE, due_date) BETWEEN 31 AND 60 THEN '31-60'
                WHEN DATEDIFF(CURRENT_DATE, due_date) BETWEEN 61 AND 90 THEN '61-90'
                ELSE '90+'
            END AS aging_bucket
        FROM rudra_finance.silver.ar_open_items
        WHERE entity_id = '{entity_id}'
        ORDER BY days_past_due DESC
    """,

    "variance": """
        SELECT
            a.entity_id,
            a.account_code,
            a.period_key,
            a.amount AS actual,
            b.amount AS budget,
            (a.amount - b.amount) AS variance,
            ROUND((a.amount - b.amount) / NULLIF(b.amount, 0) * 100, 2) AS variance_pct
        FROM rudra_finance.gold.actuals a
        LEFT JOIN rudra_finance.gold.budget b
            ON a.entity_id = b.entity_id
            AND a.account_code = b.account_code
            AND a.period_key = b.period_key
        WHERE a.entity_id = '{entity_id}'
          AND a.period_key = '{period}'
        ORDER BY ABS(a.amount - b.amount) DESC
    """,

    "ic_matching": """
        SELECT
            a.entity_id AS entity_a,
            b.entity_id AS entity_b,
            a.period_key,
            a.amount_functional AS entity_a_balance,
            b.amount_functional AS entity_b_balance,
            ABS(a.amount_functional + b.amount_functional) AS matching_difference,
            CASE
                WHEN ABS(a.amount_functional + b.amount_functional) > 50000 THEN 'MATERIAL'
                ELSE 'IMMATERIAL'
            END AS materiality
        FROM rudra_finance.silver.gl_transactions a
        JOIN rudra_finance.silver.gl_transactions b
            ON a.intercompany_id = b.entity_id
            AND b.intercompany_id = a.entity_id
            AND a.period_key = b.period_key
        WHERE a.entity_id = '{entity_id}'
        ORDER BY matching_difference DESC
    """,
}


def run_analytics_query(
    query_type: str,
    entity_id: str = "",
    period: str = "",
) -> dict[str, Any]:
    """
    Generate or execute a finance analytics query.

    In the built-in mode, returns the SQL template with parameters filled in.
    In production mode (with Databricks), executes against the warehouse.
    """
    template = _QUERY_TEMPLATES.get(query_type)
    if template is None:
        return {
            "error": f"Unknown query type: {query_type}",
            "available_types": list(_QUERY_TEMPLATES.keys()),
        }

    sql = template.format(
        entity_id=entity_id or "ALL",
        period=period or "CURRENT",
    )

    return {
        "query_type": query_type,
        "sql": sql.strip(),
        "parameters": {"entity_id": entity_id, "period": period},
        "execution_mode": "template_only",
        "note": "Connect to Databricks to execute this query against live data.",
    }


def list_query_types() -> list[str]:
    """List available analytics query types."""
    return list(_QUERY_TEMPLATES.keys())
