"""
Accounting standards search tool.

Provides a built-in knowledge base of IFRS and US GAAP standards
for agents to query.  In production, this would be backed by a
vector-indexed RAG pipeline over full standards documents.
"""

from __future__ import annotations

from typing import Optional

# Built-in standards reference (subset for immediate use)
_STANDARDS_KB: dict[str, list[dict]] = {
    "IFRS": [
        {"standard": "IFRS 3", "topic": "Business Combinations", "key_rules": "Acquisition method. Identify acquirer. Recognition and measurement at fair value. Goodwill = consideration transferred - net identifiable assets. No amortization of goodwill."},
        {"standard": "IFRS 9", "topic": "Financial Instruments", "key_rules": "Classification: amortized cost, FVOCI, FVTPL based on business model + SPPI test. ECL model: 3-stage (12-month vs lifetime). Hedge accounting: qualifying criteria, effectiveness testing."},
        {"standard": "IFRS 10", "topic": "Consolidated Financial Statements", "key_rules": "Control = power + exposure to variable returns + ability to use power. Consolidation required when control exists. NCI measured at fair value or proportionate share."},
        {"standard": "IFRS 15", "topic": "Revenue from Contracts with Customers", "key_rules": "5-step model: identify contract, identify POs, determine TP, allocate TP, recognize revenue. Variable consideration constraint: highly probable. Over-time vs point-in-time."},
        {"standard": "IFRS 16", "topic": "Leases", "key_rules": "Single lessee model: ROU asset + lease liability for all leases >12 months. Short-term and low-value exemptions. Depreciation + interest expense pattern. Sale-leaseback: partial gain if transfer of control."},
        {"standard": "IFRS 17", "topic": "Insurance Contracts", "key_rules": "General measurement model (GMM), premium allocation approach (PAA), variable fee approach (VFA). CSM represents unearned profit."},
        {"standard": "IAS 12", "topic": "Income Taxes", "key_rules": "Deferred tax on temporary differences. Deferred tax asset recognized when probable taxable profit available. No discounting. Initial recognition exemption."},
        {"standard": "IAS 16", "topic": "Property, Plant and Equipment", "key_rules": "Cost model or revaluation model. Componentization. Depreciation over useful life. Impairment under IAS 36."},
        {"standard": "IAS 19", "topic": "Employee Benefits", "key_rules": "Defined benefit: PBO, plan assets, net defined benefit liability. Remeasurements in OCI. Current service cost + net interest in P&L."},
        {"standard": "IAS 21", "topic": "Foreign Currency", "key_rules": "Functional currency determination. Monetary items at closing rate. Non-monetary at historical rate. Translation: assets/liabilities at closing, P&L at average, CTA in OCI."},
        {"standard": "IAS 36", "topic": "Impairment of Assets", "key_rules": "Recoverable amount = higher of VIU and FVLCTS. CGU level for goodwill. Impairment loss to P&L. No reversal for goodwill."},
        {"standard": "IAS 37", "topic": "Provisions", "key_rules": "Recognize when: present obligation, probable outflow, reliable estimate. Best estimate of expenditure. Onerous contracts. Contingent liabilities disclosed only."},
        {"standard": "IAS 38", "topic": "Intangible Assets", "key_rules": "Identifiable, controlled, future economic benefits. R&D: research expensed, development capitalized if criteria met. Amortize over useful life unless indefinite."},
    ],
    "US_GAAP": [
        {"standard": "ASC 606", "topic": "Revenue Recognition", "key_rules": "5-step model aligned with IFRS 15. VC constraint: probable (lower threshold than IFRS). Functional IP = point-in-time (right-to-use). Symbolic IP = over time."},
        {"standard": "ASC 326", "topic": "CECL - Credit Losses", "key_rules": "Lifetime expected credit losses from origination. Day-1 loss allowance required. Pools with similar risk characteristics. Forward-looking, including reasonable forecasts."},
        {"standard": "ASC 740", "topic": "Income Taxes", "key_rules": "Deferred tax on temporary differences. More-likely-than-not threshold for deferred tax assets. Two-step approach for uncertain tax positions: recognition then measurement."},
        {"standard": "ASC 805", "topic": "Business Combinations", "key_rules": "Acquisition method. Goodwill = consideration - net assets. Bargain purchase gain recognized. Qualitative impairment assessment option."},
        {"standard": "ASC 810", "topic": "Consolidation", "key_rules": "Voting interest model + VIE model. Primary beneficiary consolidates VIE. NCI presented in equity."},
        {"standard": "ASC 815", "topic": "Derivatives and Hedging", "key_rules": "All derivatives at fair value on BS. Hedge accounting: fair value, cash flow, net investment. Effectiveness testing required."},
        {"standard": "ASC 842", "topic": "Leases", "key_rules": "Dual model: operating vs finance lease. Operating: straight-line expense. Finance: interest + amortization. Short-term exemption <12 months. No low-value exemption."},
        {"standard": "ASC 350", "topic": "Goodwill and Intangibles", "key_rules": "Qualitative assessment option (Step 0). Quantitative: compare FV of reporting unit to carrying amount. Impairment = excess of carrying over FV, capped at goodwill."},
        {"standard": "ASC 718", "topic": "Stock Compensation", "key_rules": "Fair value at grant date. Service period expense. Forfeitures: estimate or recognize as they occur. Modification accounting."},
        {"standard": "ASC 820", "topic": "Fair Value Measurement", "key_rules": "Exit price. Three-level hierarchy: Level 1 (quoted), Level 2 (observable), Level 3 (unobservable). Market, income, cost approaches."},
        {"standard": "ASC 830", "topic": "Foreign Currency", "key_rules": "Functional currency determination. Remeasurement (temporal method) vs translation (current rate method). CTA in AOCI."},
        {"standard": "ASC 842", "topic": "Leases (Detail)", "key_rules": "Classification: finance if transfer of ownership, purchase option reasonably certain, major part of economic life, substantially all FV, or specialized asset. Else operating."},
    ],
}


def search_standards(
    query: str,
    category: Optional[str] = None,
    k: int = 5,
) -> list[dict]:
    """
    Search the built-in standards knowledge base.

    Returns the top-k matching standards entries based on keyword overlap.
    In production, this would use vector similarity search over full standards PDFs.
    """
    query_terms = set(query.lower().split())
    results: list[tuple[dict, float]] = []

    categories = [category] if category else list(_STANDARDS_KB.keys())

    for cat in categories:
        entries = _STANDARDS_KB.get(cat, [])
        for entry in entries:
            searchable = f"{entry['standard']} {entry['topic']} {entry['key_rules']}".lower()
            overlap = len(query_terms & set(searchable.split()))
            score = overlap / max(len(query_terms), 1)
            if score > 0:
                results.append(({**entry, "category": cat}, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in results[:k]]
