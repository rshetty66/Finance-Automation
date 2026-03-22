"""
Golden test cases for the accounting policy engine.

Each test case provides a scenario and checks that the agent's response
contains expected elements (standards referenced, conclusions, JE patterns).
"""

ACCOUNTING_POLICY_TEST_CASES: list[dict] = [
    {
        "id": "acct_01",
        "query": (
            "A company sells headquarters ($180M book value, $240M sale price) "
            "and leases back for 15 years at $15M/year. Analyze the accounting "
            "treatment under both IFRS 16 and ASC 842."
        ),
        "expected_standards": ["IFRS 16", "ASC 842"],
        "expected_contains": [
            "sale-leaseback",
            "right-of-use",
            "ROU",
            "lease liability",
        ],
        "expected_je_elements": ["DR", "CR"],
        "category": "leases",
    },
    {
        "id": "acct_02",
        "query": (
            "Analyze revenue recognition for a SaaS contract: $2M annual license, "
            "$300K implementation, 3-year term, customer can cancel after Year 1. "
            "Analyze under IFRS 15 and ASC 606."
        ),
        "expected_standards": ["IFRS 15", "ASC 606"],
        "expected_contains": [
            "performance obligation",
            "variable consideration",
            "SSP",
            "over time",
        ],
        "category": "revenue",
    },
    {
        "id": "acct_03",
        "query": (
            "Target company has $450M goodwill from a 2019 acquisition. CGU cash "
            "flows have declined 25% due to market disruption. Assess impairment "
            "under IAS 36 and ASC 350."
        ),
        "expected_standards": ["IAS 36", "ASC 350"],
        "expected_contains": [
            "recoverable amount",
            "impairment",
            "CGU",
            "goodwill",
        ],
        "category": "impairment",
    },
    {
        "id": "acct_04",
        "query": (
            "Draft an accounting policy for expected credit losses on trade "
            "receivables under IFRS 9, with a $500K materiality threshold."
        ),
        "expected_standards": ["IFRS 9"],
        "expected_contains": [
            "expected credit loss",
            "ECL",
            "simplified approach",
            "provision matrix",
        ],
        "category": "financial_instruments",
    },
    {
        "id": "acct_05",
        "query": (
            "A multinational is restructuring its European operations. "
            "Estimated cost is EUR 50M including severance, lease terminations, "
            "and asset write-downs. Analyze provision recognition under IAS 37 "
            "and ASC 420/ASC 450."
        ),
        "expected_standards": ["IAS 37", "ASC 420", "ASC 450"],
        "expected_contains": [
            "provision",
            "present obligation",
            "restructuring",
            "constructive obligation",
        ],
        "category": "provisions",
    },
]
