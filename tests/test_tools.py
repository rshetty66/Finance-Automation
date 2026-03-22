"""Tests for the built-in tools."""

import pytest

from rudra.tools.standards import search_standards
from rudra.tools.benchmarks import get_apqc_benchmark, list_benchmarks, get_pcf_category
from rudra.tools.analytics import run_analytics_query, list_query_types


class TestStandardsSearch:
    def test_search_ifrs16(self):
        results = search_standards("lease IFRS 16 right of use")
        assert len(results) > 0
        standards = [r["standard"] for r in results]
        assert "IFRS 16" in standards

    def test_search_revenue(self):
        results = search_standards("revenue recognition contract performance obligation")
        assert len(results) > 0

    def test_search_with_category(self):
        results = search_standards("revenue", category="US_GAAP")
        assert all(r["category"] == "US_GAAP" for r in results)

    def test_search_no_results(self):
        results = search_standards("xyznonexistent123")
        assert len(results) == 0

    def test_search_k_limit(self):
        results = search_standards("accounting", k=3)
        assert len(results) <= 3


class TestBenchmarks:
    def test_get_days_to_close(self):
        result = get_apqc_benchmark("days_to_close")
        assert result["median"] == 6.5
        assert result["top_25"] == 4
        assert result["unit"] == "days"

    def test_get_dso(self):
        result = get_apqc_benchmark("dso")
        assert result["median"] == 40
        assert result["top_25"] == 30

    def test_get_with_percentile(self):
        result = get_apqc_benchmark("days_to_close", percentile="top_25")
        assert "requested_percentile" in result
        assert result["requested_percentile"]["value"] == 4

    def test_get_with_industry(self):
        result = get_apqc_benchmark("days_to_close", industry="manufacturing")
        assert "industry_note" in result

    def test_not_found(self):
        result = get_apqc_benchmark("nonexistent_metric")
        assert "error" in result
        assert "available_metrics" in result

    def test_search_by_name(self):
        result = get_apqc_benchmark("Days Sales Outstanding")
        assert "median" in result

    def test_list_benchmarks(self):
        benchmarks = list_benchmarks()
        assert len(benchmarks) >= 10
        assert all("key" in b and "metric" in b for b in benchmarks)

    def test_pcf_category(self):
        assert get_pcf_category("9.3") == "Perform General Accounting and Reporting"
        assert get_pcf_category("9.7") == "Manage Treasury"
        assert get_pcf_category("99.99") is None


class TestAnalytics:
    def test_close_metrics(self):
        result = run_analytics_query("close_metrics", entity_id="CORP001", period="2026-03")
        assert "sql" in result
        assert "CORP001" in result["sql"]
        assert result["query_type"] == "close_metrics"

    def test_ar_aging(self):
        result = run_analytics_query("ar_aging", entity_id="CORP001")
        assert "sql" in result
        assert "aging_bucket" in result["sql"]

    def test_variance(self):
        result = run_analytics_query("variance", entity_id="CORP001", period="2026-03")
        assert "sql" in result
        assert "variance_pct" in result["sql"]

    def test_unknown_query_type(self):
        result = run_analytics_query("nonexistent")
        assert "error" in result
        assert "available_types" in result

    def test_list_query_types(self):
        types = list_query_types()
        assert "close_metrics" in types
        assert "ar_aging" in types
        assert "variance" in types
