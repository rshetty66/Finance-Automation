"""
Intent Router — replaces the static keyword trigger table in rudra.md:547-565.

Instead of matching keywords like "GL, COA" → modern-finance-gl,
Claude reads ANY input (text, image description, document summary, voice
transcript) and dynamically selects which Rudra sub-agents to spawn.

No trigger tables. No hardcoded keyword maps. Pure intent understanding.
"""

import json
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# All available Rudra sub-agents from Rudra_Agents/
RUDRA_AGENTS = [
    "coa-designer",
    "accounting-hub-architect",
    "rapid-prototyper",
    "si-finance-process-lead",
    "si-functional-lead",
    "si-data-architect",
    "si-integration-lead",
    "si-security-controls-lead",
    "si-change-management-lead",
    "si-data-analytics-lead",
    "apqc-researcher",
    "creative-designer",
    "fact-check-agent",
]

ROUTER_SYSTEM_PROMPT = f"""You are Rudra's intent router for a finance transformation consulting platform.

Given user input in ANY modality (text, image description, document extract, voice transcript),
select which specialist sub-agents to spawn to best address the request.

Available agents:
{json.dumps(RUDRA_AGENTS, indent=2)}

Agent capabilities (for routing decisions):
- coa-designer: Chart of Accounts design, multi-entity COA, redesign, rationalization
- accounting-hub-architect: Multi-ERP consolidation, Accounting Hub implementation
- rapid-prototyper: 15-minute demos, dashboard mockups, ROI calculators
- si-finance-process-lead: R2R, O2C, P2P, Planning process design and optimization
- si-functional-lead: Oracle, SAP, Workday, OneStream, Anaplan configuration
- si-data-architect: Data migration, MDM, data governance
- si-integration-lead: APIs, middleware, B2B/EDI architecture
- si-security-controls-lead: SOD, SOX, compliance, access management
- si-change-management-lead: OCM, training, adoption frameworks
- si-data-analytics-lead: Power BI, Tableau, reporting strategy, dashboards
- apqc-researcher: APQC benchmarking, PCF mapping, target setting
- creative-designer: Visual design, executive GUIs, presentations
- fact-check-agent: Citation audit, model attribution, provenance verification

Rules:
1. Return ONLY agents needed for the specific task — do not over-spawn
2. Multiple agents = parallel execution (return them all if independent tasks)
3. Use deep intent understanding, NOT keyword matching
4. Consider multimodal context when provided (image = visual output needed)
5. Always include fact-check-agent when financial benchmarks are cited

Return ONLY valid JSON in this exact format:
{{"agents": ["agent1", "agent2"], "parallel": true, "reasoning": "brief explanation"}}"""


def route_to_agent(
    user_input: str,
    modality_context: dict = None,
    stream: bool = False,
) -> dict:
    """
    Route user input to the appropriate Rudra sub-agents via Claude intent understanding.

    Args:
        user_input: The user's request in any form (text, extracted doc content, etc.)
        modality_context: Optional dict describing the input modality and metadata.
                          e.g. {"source": "qwen_vision", "doc_type": "excel_screenshot"}
        stream: Whether to stream the routing decision (useful for large inputs).

    Returns:
        dict with keys: agents (list), parallel (bool), reasoning (str)
    """
    context_str = json.dumps(modality_context or {})

    messages = [
        {
            "role": "user",
            "content": f"User Input:\n{user_input}\n\nModality Context:\n{context_str}",
        }
    ]

    if stream:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=512,
            thinking={"type": "adaptive"},
            system=ROUTER_SYSTEM_PROMPT,
            messages=messages,
        ) as s:
            raw = s.get_final_message()
            text = next(b.text for b in raw.content if b.type == "text")
    else:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=512,
            thinking={"type": "adaptive"},
            system=ROUTER_SYSTEM_PROMPT,
            messages=messages,
        )
        text = next(b.text for b in response.content if b.type == "text")

    # Parse and validate
    result = json.loads(text)
    result["agents"] = [a for a in result.get("agents", []) if a in RUDRA_AGENTS]
    return result


def route_multimodal(
    text_input: str = None,
    image_description: str = None,
    document_extract: str = None,
    voice_transcript: str = None,
    doc_type: str = None,
) -> dict:
    """
    Convenience wrapper for multimodal routing. Combines all available
    input signals into a unified intent understanding call.
    """
    parts = []
    if text_input:
        parts.append(f"Text: {text_input}")
    if image_description:
        parts.append(f"Visual content (from Qwen vision): {image_description}")
    if document_extract:
        parts.append(f"Document extract: {document_extract}")
    if voice_transcript:
        parts.append(f"Voice transcript: {voice_transcript}")

    combined = "\n\n".join(parts)
    context = {"source": "multimodal", "doc_type": doc_type or "unknown"}

    return route_to_agent(combined, modality_context=context)
