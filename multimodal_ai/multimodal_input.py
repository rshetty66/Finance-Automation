"""
Multimodal Input Processor — Qwen2-VL for Finance Document Vision.

Pipes visual finance documents through Qwen2-VL to extract structured text,
then routes to Rudra agents via Claude intent router.

Handles:
- Excel screenshots and spreadsheet photos
- Oracle EPM / SAP dashboard images
- PDF page extracts (when rendered as images)
- Whiteboard photos from design sessions
- Scanned finance documents (COA diagrams, process flows)
"""

import base64
import os
from pathlib import Path

import anthropic

from .intent_router import route_to_agent

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Finance-specific vision prompt templates by document type
VISION_PROMPTS = {
    "excel": """This is a finance Excel spreadsheet screenshot.
Extract ALL of the following:
- Column headers and row labels (exact text)
- All numerical values with their labels/context
- Formula results if visible
- Chart or graph data if present
- Any highlighted cells or color-coded regions (note what they indicate)
- Sheet tab names if visible
Format as structured JSON with sections for: headers, data_rows, totals, notes.""",

    "dashboard": """This is a finance system dashboard (Oracle EPM, SAP, Workday, or similar).
Extract ALL of the following:
- Dashboard title and date/period shown
- All KPI tiles: label, value, trend direction, comparison period
- Chart data: type, axes labels, data series names and values
- Any filters or dimension selectors active
- Alert indicators, RAG status, or threshold breaches
- Navigation elements visible (modules, tabs)
Format as structured JSON with sections for: period, kpis, charts, alerts, system_info.""",

    "pdf_page": """This is a page from a finance report, audit document, or requirements PDF.
Extract ALL of the following:
- Page title and section headers
- All body text (preserve paragraph structure)
- Tables: headers + all rows + footers
- Footnotes and references
- Figure captions and descriptions
- Any highlighted or annotated text
Preserve the logical document structure in your extraction.""",

    "process_flow": """This is a finance process flow diagram or whiteboard photo.
Extract ALL of the following:
- Process step names (in order)
- Decision diamonds and their conditions/branches
- System/role swim lanes
- Data flows and inputs/outputs between steps
- Start and end points
- Any annotations or notes written on the diagram
Output as: ordered list of steps, decision points, and a description of the overall flow.""",

    "coa": """This is a Chart of Accounts structure, GL account listing, or financial hierarchy diagram.
Extract ALL of the following:
- Account segment names and their positions/order
- Account codes/numbers (full range if shown)
- Account descriptions/names
- Account types (asset, liability, equity, revenue, expense)
- Hierarchy levels and parent-child relationships
- Any mapping or crosswalk tables
Format as hierarchical JSON preserving the COA structure.""",

    "general": """This is a finance or business document image.
Extract ALL visible text, numbers, tables, charts, and diagrams.
Preserve structure where possible. Note the document type at the start.
Flag any financial figures, KPIs, dates, or account codes found.""",
}


def _encode_image(image_path: str) -> tuple[str, str]:
    """Encode image to base64 and detect media type."""
    path = Path(image_path)
    suffix = path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_types.get(suffix, "image/png")

    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    return data, media_type


def process_finance_document(
    image_path: str,
    doc_type: str = "general",
    additional_context: str = None,
) -> str:
    """
    Process a finance document image using Claude's vision capabilities.
    Extracts structured data for downstream Rudra agent routing.

    This replaces Qwen2-VL for document understanding while using the
    same Claude infrastructure (no separate model deployment needed).

    Args:
        image_path: Path to the image file
        doc_type: One of: excel, dashboard, pdf_page, process_flow, coa, general
        additional_context: Optional text context to provide alongside the image

    Returns:
        Structured text extraction of the document contents
    """
    vision_prompt = VISION_PROMPTS.get(doc_type, VISION_PROMPTS["general"])
    if additional_context:
        vision_prompt += f"\n\nAdditional context: {additional_context}"

    image_data, media_type = _encode_image(image_path)

    content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data,
            },
        },
        {"type": "text", "text": vision_prompt},
    ]

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": content}],
    )

    return next(b.text for b in response.content if b.type == "text")


def process_finance_document_url(
    image_url: str,
    doc_type: str = "general",
    additional_context: str = None,
) -> str:
    """
    Process a finance document image from a URL.
    Useful for Oracle EPM screenshots, SAP dashboard exports, etc.

    Args:
        image_url: URL of the image
        doc_type: One of: excel, dashboard, pdf_page, process_flow, coa, general
        additional_context: Optional text context

    Returns:
        Structured text extraction
    """
    vision_prompt = VISION_PROMPTS.get(doc_type, VISION_PROMPTS["general"])
    if additional_context:
        vision_prompt += f"\n\nAdditional context: {additional_context}"

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "url", "url": image_url},
                    },
                    {"type": "text", "text": vision_prompt},
                ],
            }
        ],
    )

    return next(b.text for b in response.content if b.type == "text")


def process_and_route(
    image_path: str = None,
    image_url: str = None,
    doc_type: str = "general",
    additional_context: str = None,
) -> dict:
    """
    Full pipeline: vision extraction → Claude intent routing → Rudra agent selection.

    Accepts either a local file path or a URL.

    Returns:
        dict with keys:
          - extraction: str (structured document content from vision)
          - routing: dict (agents list, parallel flag, reasoning from intent router)

    Example:
        result = process_and_route(
            image_path="/tmp/oracle_epm_dashboard.png",
            doc_type="dashboard",
        )
        # result["routing"]["agents"] → ["si-data-analytics-lead", "apqc-researcher"]
        # result["routing"]["parallel"] → True
    """
    if image_path:
        extracted = process_finance_document(image_path, doc_type, additional_context)
        source_meta = {"source": "vision_file", "doc_type": doc_type, "path": image_path}
    elif image_url:
        extracted = process_finance_document_url(image_url, doc_type, additional_context)
        source_meta = {"source": "vision_url", "doc_type": doc_type, "url": image_url}
    else:
        raise ValueError("Provide either image_path or image_url")

    routing = route_to_agent(extracted, modality_context=source_meta)

    return {
        "extraction": extracted,
        "routing": routing,
        "doc_type": doc_type,
    }


def batch_process_documents(documents: list[dict]) -> list[dict]:
    """
    Process multiple finance documents in sequence.
    For parallel processing, wrap in asyncio.

    Args:
        documents: List of dicts with keys: image_path or image_url, doc_type, context

    Returns:
        List of extraction + routing results
    """
    results = []
    for doc in documents:
        result = process_and_route(
            image_path=doc.get("image_path"),
            image_url=doc.get("image_url"),
            doc_type=doc.get("doc_type", "general"),
            additional_context=doc.get("context"),
        )
        results.append(result)
    return results
