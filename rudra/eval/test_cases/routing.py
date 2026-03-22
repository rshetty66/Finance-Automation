"""
Golden test cases for the vector-search router.

Each test case specifies a query and the expected primary agent.
The evaluation harness checks whether the router selects the
correct agent.
"""

ROUTING_TEST_CASES: list[dict] = [
    # Technical accounting
    {
        "id": "route_01",
        "query": "Analyze our lease portfolio under IFRS 16",
        "expected_primary": "lease-accounting-agent",
        "expected_secondary_contains": ["accounting-policy-engine"],
        "category": "technical_accounting",
    },
    {
        "id": "route_02",
        "query": "Build a DCF model for the target company acquisition",
        "expected_primary": "financial-modeling-agent",
        "category": "deals",
    },
    {
        "id": "route_03",
        "query": "What are our Scope 3 emissions reporting obligations under CSRD?",
        "expected_primary": "esg-reporting-agent",
        "category": "sustainability",
    },
    {
        "id": "route_04",
        "query": "Design a chart of accounts for our new Oracle Cloud instance",
        "expected_primary": "coa-designer",
        "category": "systems",
    },
    {
        "id": "route_05",
        "query": "Review our SOX 404 control gaps and recommend remediation",
        "expected_primary": "internal-audit-agent",
        "category": "risk_assurance",
    },
    {
        "id": "route_06",
        "query": "Our monthly close is taking 12 days, help us optimize",
        "expected_primary": "si-finance-process-lead",
        "category": "process",
    },
    {
        "id": "route_07",
        "query": "Set up a Databricks pipeline for AP analytics and close monitoring",
        "expected_primary": "databricks-pipeline-agent",
        "category": "data_engineering",
    },
    {
        "id": "route_08",
        "query": "What is APQC best practice cost per invoice for AP automation?",
        "expected_primary": "apqc-researcher",
        "category": "benchmarking",
    },
    {
        "id": "route_09",
        "query": "Analyze a SaaS contract with $2M annual fee and usage-based overage under IFRS 15 and ASC 606",
        "expected_primary": "revenue-recognition-agent",
        "expected_secondary_contains": ["accounting-policy-engine"],
        "category": "technical_accounting",
    },
    {
        "id": "route_10",
        "query": "We're acquiring a company for $500M, assess goodwill and do purchase price allocation",
        "expected_primary": "ma-due-diligence-agent",
        "category": "deals",
    },
    {
        "id": "route_11",
        "query": "Configure SAP S/4HANA FI module for our global rollout",
        "expected_primary": "si-functional-lead",
        "category": "systems",
    },
    {
        "id": "route_12",
        "query": "Design a data migration strategy for our Oracle ERP Cloud implementation",
        "expected_primary": "si-data-architect",
        "category": "data_engineering",
    },
    {
        "id": "route_13",
        "query": "Design MuleSoft API-led integration architecture for our ERP",
        "expected_primary": "si-integration-lead",
        "category": "systems",
    },
    {
        "id": "route_14",
        "query": "Help me prepare a steering committee deck for the CFO",
        "expected_primary": "rudra",
        "category": "program_management",
    },
    {
        "id": "route_15",
        "query": "Create an executive dashboard design for our CFO that shows financial KPIs",
        "expected_primary": "creative-designer",
        "category": "creative",
    },
    {
        "id": "route_16",
        "query": "Determine the deferred tax impact of our international restructuring under IAS 12 and ASC 740",
        "expected_primary": "tax-accounting-agent",
        "category": "tax",
    },
    {
        "id": "route_17",
        "query": "Help us set up hedge accounting for our FX forward contracts under IFRS 9",
        "expected_primary": "treasury-management-agent",
        "category": "treasury",
    },
    {
        "id": "route_18",
        "query": "Design a change management and training plan for our SAP rollout",
        "expected_primary": "si-change-management-lead",
        "category": "process",
    },
    {
        "id": "route_19",
        "query": "Build Power BI dashboards for our finance reporting",
        "expected_primary": "si-data-analytics-lead",
        "category": "analytics",
    },
    {
        "id": "route_20",
        "query": "Fact-check the benchmark analysis before sending to the CFO",
        "expected_primary": "fact-check-agent",
        "category": "quality",
    },
]
