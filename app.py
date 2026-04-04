"""
Rudra Finance Automation - Streamlit App

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the local rudra package importable without installation
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

st.set_page_config(
    page_title="Rudra Finance Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

PAGES = [
    "🏠 Home",
    "🤖 Agent Browser",
    "🔀 Query Router",
    "📐 Standards Search",
    "📊 APQC Benchmarks",
]

st.sidebar.title("Rudra")
st.sidebar.caption("Finance Automation Framework")
page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.markdown(
    "**Domains**\n"
    "- Technical Accounting\n"
    "- Deals Advisory\n"
    "- Tax & Treasury\n"
    "- ESG / Sustainability\n"
    "- Systems & Data\n"
    "- Process Consulting\n"
)


# ---------------------------------------------------------------------------
# Shared loader (cached)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading agent registry…")
def load_registry():
    from rudra.agents.registry import AgentRegistry
    return AgentRegistry.from_directory()


# ---------------------------------------------------------------------------
# Page: Home
# ---------------------------------------------------------------------------

if page == "🏠 Home":
    st.title("Rudra Finance Automation")
    st.subheader("Skills-based multi-agent framework for finance transformation")

    col1, col2, col3, col4 = st.columns(4)
    registry = load_registry()
    agents = registry.list_agents()

    from rudra.models import AgentDomain
    domains = {a.domain for a in agents}

    col1.metric("Agents Loaded", len(agents))
    col2.metric("Domains Covered", len(domains))

    from rudra.tools.benchmarks import list_benchmarks
    col3.metric("APQC Benchmarks", len(list_benchmarks()))

    from rudra.tools.standards import _STANDARDS_KB
    total_standards = sum(len(v) for v in _STANDARDS_KB.values())
    col4.metric("Standards Entries", total_standards)

    st.divider()

    st.markdown(
        """
        ### What is Rudra?

        Rudra is a **skills-based multi-agent framework** built for finance transformation consulting.
        It routes natural-language queries to the right specialist agent — from technical accounting
        and IFRS/US GAAP analysis to ERP system design, ESG reporting, and M&A due diligence.

        ### How to use this app

        | Page | Description |
        |------|-------------|
        | **Agent Browser** | Explore all available agents, their domains, capabilities, and system prompts |
        | **Query Router** | Enter a finance query and see which agent(s) it would be routed to |
        | **Standards Search** | Search the built-in IFRS / US GAAP knowledge base |
        | **APQC Benchmarks** | Browse and compare finance function benchmarks from APQC |
        """
    )

    st.divider()
    st.markdown("### Agent Domain Breakdown")

    from collections import Counter
    domain_counts = Counter(a.domain for a in agents)
    import pandas as pd
    df = pd.DataFrame(
        [(d.replace("_", " ").title(), c) for d, c in sorted(domain_counts.items(), key=lambda x: -x[1])],
        columns=["Domain", "Count"],
    )
    st.bar_chart(df.set_index("Domain"))


# ---------------------------------------------------------------------------
# Page: Agent Browser
# ---------------------------------------------------------------------------

elif page == "🤖 Agent Browser":
    st.title("Agent Browser")
    registry = load_registry()
    agents = registry.list_agents()

    from rudra.models import AgentDomain
    all_domains = sorted({a.domain for a in agents})
    domain_filter = st.selectbox(
        "Filter by domain",
        ["All"] + [d.replace("_", " ").title() for d in all_domains],
    )

    search = st.text_input("Search agents", placeholder="e.g. lease, ESG, treasury…")

    filtered = agents
    if domain_filter != "All":
        raw_domain = domain_filter.lower().replace(" ", "_")
        filtered = [a for a in filtered if a.domain == raw_domain]
    if search:
        s = search.lower()
        filtered = [
            a for a in filtered
            if s in a.id or s in a.description.lower()
            or any(s in cap for cap in a.capabilities)
            or any(s in tag for tag in a.embedding_tags)
        ]

    st.caption(f"Showing {len(filtered)} of {len(agents)} agents")

    for spec in filtered:
        with st.expander(f"**{spec.id}** — {spec.domain.replace('_', ' ').title()}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Description:** {spec.description or '—'}")
                if spec.capabilities:
                    st.markdown("**Capabilities:** " + " · ".join(f"`{c}`" for c in spec.capabilities))
                if spec.embedding_tags:
                    st.markdown("**Routing tags:** " + ", ".join(spec.embedding_tags))
            with col2:
                st.markdown(f"**Model:** `{spec.model}`")
                st.markdown(f"**Confidence threshold:** `{spec.confidence_threshold}`")
                if spec.tools:
                    st.markdown("**Tools:**")
                    for t in spec.tools:
                        req = " *(required)*" if t.required else ""
                        st.markdown(f"- `{t.name}`{req}")
                if spec.downstream_agents:
                    st.markdown("**Downstream agents:**")
                    for a in spec.downstream_agents:
                        st.markdown(f"- `{a}`")

            if spec.system_prompt:
                with st.expander("System prompt"):
                    st.markdown(spec.system_prompt[:3000] + ("…" if len(spec.system_prompt) > 3000 else ""))


# ---------------------------------------------------------------------------
# Page: Query Router
# ---------------------------------------------------------------------------

elif page == "🔀 Query Router":
    st.title("Query Router")
    st.markdown(
        "Enter a finance query to see how Rudra's vector-search router would route it "
        "across the available agents."
    )

    query = st.text_area(
        "Finance query",
        placeholder="e.g. 'Analyze our lease portfolio under IFRS 16' or 'Help design a COA for a multi-entity structure'",
        height=100,
    )
    top_k = st.slider("Top K results", 1, 10, 5)

    if st.button("Route query", type="primary", disabled=not query.strip()):
        registry = load_registry()
        try:
            from rudra.routing.router import VectorSearchRouter
            with st.spinner("Running semantic routing…"):
                router = VectorSearchRouter(registry)
                decision = router.route(query.strip(), top_k=top_k)

            st.success("Routing complete")

            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("Primary Agent")
                primary = decision.primary_agent
                st.markdown(f"### `{primary.agent_id}`")
                st.metric("Confidence", f"{primary.confidence:.1%}")
                if primary.reason:
                    st.markdown(f"**Reason:** {primary.reason}")
                spec = registry.get_spec(primary.agent_id)
                if spec:
                    st.markdown(f"**Domain:** {spec.domain.replace('_', ' ').title()}")
                    if spec.capabilities:
                        st.markdown("**Capabilities:** " + ", ".join(spec.capabilities[:5]))

            with col2:
                st.subheader("Secondary Agents")
                if decision.secondary_agents:
                    import pandas as pd
                    rows = []
                    for m in decision.secondary_agents:
                        s = registry.get_spec(m.agent_id)
                        rows.append({
                            "Agent": m.agent_id,
                            "Confidence": f"{m.confidence:.1%}",
                            "Domain": s.domain.replace("_", " ").title() if s else "—",
                            "Role": m.role or "—",
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.info("No secondary agents matched.")

            st.divider()
            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"**Pipeline mode:** `{decision.pipeline_mode}`")
                st.markdown(f"**Requires disambiguation:** `{decision.requires_disambiguation}`")
            with col4:
                if decision.disambiguation_questions:
                    st.markdown("**Disambiguation questions:**")
                    for q in decision.disambiguation_questions:
                        st.markdown(f"- {q}")
                if decision.context_for_agent:
                    st.markdown(f"**Context hint:** {decision.context_for_agent}")

        except ImportError as e:
            st.warning(
                f"Vector routing requires optional dependencies: `{e}`\n\n"
                "Install with: `pip install sentence-transformers torch`\n\n"
                "Falling back to keyword-based routing preview."
            )
            # Keyword fallback
            registry = load_registry()
            q_lower = query.lower()
            matches = []
            for spec in registry.list_agents():
                score = sum(1 for tag in spec.embedding_tags if tag.lower() in q_lower)
                score += sum(0.5 for cap in spec.capabilities if cap.lower().replace("_", " ") in q_lower)
                if score > 0:
                    matches.append((spec, score))
            matches.sort(key=lambda x: -x[1])

            if matches:
                st.subheader("Keyword-based matches (fallback)")
                import pandas as pd
                rows = [
                    {"Agent": s.id, "Score": sc, "Domain": s.domain.replace("_", " ").title()}
                    for s, sc in matches[:top_k]
                ]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No keyword matches found. Try different terms.")

        except Exception as e:
            st.error(f"Routing error: {e}")


# ---------------------------------------------------------------------------
# Page: Standards Search
# ---------------------------------------------------------------------------

elif page == "📐 Standards Search":
    st.title("Accounting Standards Search")
    st.markdown("Search the built-in IFRS / US GAAP knowledge base.")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        query = st.text_input("Search query", placeholder="e.g. lease, revenue recognition, impairment…")
    with col2:
        category = st.selectbox("Framework", ["Both", "IFRS", "US_GAAP"])
    with col3:
        k = st.number_input("Max results", min_value=1, max_value=20, value=5)

    if query.strip():
        from rudra.tools.standards import search_standards
        cat_arg = None if category == "Both" else category
        results = search_standards(query.strip(), category=cat_arg, k=int(k))

        if results:
            st.caption(f"{len(results)} result(s)")
            for r in results:
                badge = "🟦 IFRS" if r["category"] == "IFRS" else "🟥 US GAAP"
                with st.expander(f"{badge} **{r['standard']}** — {r['topic']}"):
                    st.markdown(r["key_rules"])
        else:
            st.info("No matching standards found. Try broader search terms.")
    else:
        # Show all standards
        from rudra.tools.standards import _STANDARDS_KB
        st.markdown("### All Standards")
        for cat, entries in _STANDARDS_KB.items():
            with st.expander(f"**{cat}** ({len(entries)} standards)"):
                import pandas as pd
                rows = [{"Standard": e["standard"], "Topic": e["topic"]} for e in entries]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Page: APQC Benchmarks
# ---------------------------------------------------------------------------

elif page == "📊 APQC Benchmarks":
    st.title("APQC Finance Benchmarks")
    st.markdown(
        "Built-in APQC Open Standards Benchmarking data for finance function metrics. "
        "Enter your actual value to see where you stand."
    )

    from rudra.tools.benchmarks import list_benchmarks, get_apqc_benchmark
    benchmarks = list_benchmarks()

    import pandas as pd

    # Summary table
    st.subheader("All Benchmarks")
    rows = []
    for b in benchmarks:
        data = get_apqc_benchmark(b["key"])
        rows.append({
            "Metric": data["metric"],
            "Top 25%": data.get("top_25", "—"),
            "Median": data.get("median", "—"),
            "Bottom 25%": data.get("bottom_25", "—"),
            "Unit": data.get("unit", ""),
            "PCF": data.get("pcf_reference", ""),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Compare Your Performance")

    metric_labels = {b["key"]: b["metric"] for b in benchmarks}
    selected_key = st.selectbox(
        "Select metric",
        options=list(metric_labels.keys()),
        format_func=lambda k: metric_labels[k],
    )

    data = get_apqc_benchmark(selected_key)
    top25 = data.get("top_25")
    median = data.get("median")
    bottom25 = data.get("bottom_25")
    unit = data.get("unit", "")

    col1, col2, col3 = st.columns(3)
    col1.metric("Top 25%", f"{top25} {unit}" if top25 is not None else "—")
    col2.metric("Median", f"{median} {unit}" if median is not None else "—")
    col3.metric("Bottom 25%", f"{bottom25} {unit}" if bottom25 is not None else "—")

    your_value = st.number_input(
        f"Your actual value ({unit})",
        min_value=0.0,
        step=0.1,
        value=float(median) if median is not None else 0.0,
    )

    if top25 is not None and median is not None and bottom25 is not None:
        # Determine direction: lower is better for cost/days metrics, higher for automation %
        lower_is_better_units = {"days", "USD", "percent_variance", "percent"}
        lower_is_better = unit in lower_is_better_units and "automated" not in selected_key

        if lower_is_better:
            if your_value <= top25:
                tier, color = "Top 25% (Best in class)", "success"
            elif your_value <= median:
                tier, color = "Between Top 25% and Median", "info"
            elif your_value <= bottom25:
                tier, color = "Between Median and Bottom 25%", "warning"
            else:
                tier, color = "Below Bottom 25%", "error"
        else:
            if your_value >= top25:
                tier, color = "Top 25% (Best in class)", "success"
            elif your_value >= median:
                tier, color = "Between Median and Top 25%", "info"
            elif your_value >= bottom25:
                tier, color = "Between Median and Bottom 25%", "warning"
            else:
                tier, color = "Below Bottom 25%", "error"

        getattr(st, color)(f"**Performance tier:** {tier}")

        # Simple bar chart
        chart_data = pd.DataFrame({
            "Percentile": ["Top 25%", "Median", "Bottom 25%", "Your Value"],
            unit or "Value": [top25, median, bottom25, your_value],
        })
        st.bar_chart(chart_data.set_index("Percentile"))

    if "variants" in data:
        st.markdown("**Process variants:**")
        for variant, vals in data["variants"].items():
            st.markdown(f"- **{variant.replace('_', ' ').title()}**: {vals['low']}–{vals['high']} {unit}")
