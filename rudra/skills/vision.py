"""
Vision Skill.

Enables multimodal financial document analysis using Claude's vision
capabilities.  Agents can pass base64-encoded images (PNG, JPEG, WEBP, GIF)
or PDFs alongside text queries to extract data from:

  - Financial statements (balance sheets, P&L, cash flow)
  - Audit workpapers and tick-mark schedules
  - Chart of accounts screenshots
  - Dashboard exports from BI tools
  - Signed contracts / lease schedules scanned as PDFs

The skill builds the structured ``content`` block list that the Anthropic
Messages API expects for multimodal inputs.
"""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Supported MIME types (Anthropic vision)
SUPPORTED_IMAGE_TYPES = {
    "image/png", "image/jpeg", "image/gif", "image/webp",
}
SUPPORTED_DOC_TYPES = {
    "application/pdf",
}
ALL_SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | SUPPORTED_DOC_TYPES


@dataclass
class DocumentSource:
    """A single document or image to analyse."""

    data: str             # base64-encoded content
    media_type: str       # e.g. "image/png", "application/pdf"
    label: Optional[str] = None   # optional human-readable label


class VisionSkill:
    """
    Superpower Skill: Vision / Document Analysis.

    Builds the multimodal message content list required by the Anthropic
    Messages API to analyse images and PDFs alongside text.

    Usage::

        skill = VisionSkill()
        source = VisionSkill.load_file("/path/to/balance_sheet.png")
        content = skill.build_content(
            text_query="Extract all line items from this balance sheet.",
            documents=[source],
        )
        response = await client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": content}],
            system=system_prompt,
        )
    """

    def __init__(self, max_documents: int = 5) -> None:
        self.max_documents = max_documents

    def build_content(
        self,
        text_query: str,
        documents: list[DocumentSource],
    ) -> list[dict[str, Any]]:
        """
        Build the ``content`` list for a multimodal user message.

        Documents are prepended before the text query so Claude sees the
        visual context first, then the instruction.
        """
        if len(documents) > self.max_documents:
            raise ValueError(
                f"Too many documents ({len(documents)}). "
                f"Max allowed: {self.max_documents}"
            )

        content: list[dict[str, Any]] = []

        for doc in documents:
            if doc.media_type not in ALL_SUPPORTED_TYPES:
                raise ValueError(
                    f"Unsupported media type: {doc.media_type!r}. "
                    f"Supported: {sorted(ALL_SUPPORTED_TYPES)}"
                )

            if doc.media_type in SUPPORTED_IMAGE_TYPES:
                block: dict[str, Any] = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": doc.media_type,
                        "data": doc.data,
                    },
                }
            else:
                # PDF – use document block type
                block = {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": doc.media_type,
                        "data": doc.data,
                    },
                }

            if doc.label:
                block["title"] = doc.label

            content.append(block)

        content.append({"type": "text", "text": text_query})
        return content

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @staticmethod
    def load_file(path: str | Path, label: Optional[str] = None) -> DocumentSource:
        """
        Load a local file and return a ``DocumentSource``.

        Infers the media type from the file extension.
        """
        p = Path(path)
        ext = p.suffix.lower()
        ext_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
        }
        media_type = ext_map.get(ext)
        if media_type is None:
            raise ValueError(
                f"Cannot infer media type for extension {ext!r}. "
                "Provide media_type explicitly via DocumentSource."
            )

        raw_bytes = p.read_bytes()
        encoded = base64.standard_b64encode(raw_bytes).decode("utf-8")
        return DocumentSource(
            data=encoded,
            media_type=media_type,
            label=label or p.name,
        )

    @staticmethod
    def from_bytes(
        data: bytes,
        media_type: str,
        label: Optional[str] = None,
    ) -> DocumentSource:
        """Create a ``DocumentSource`` directly from raw bytes."""
        encoded = base64.standard_b64encode(data).decode("utf-8")
        return DocumentSource(data=encoded, media_type=media_type, label=label)

    def __repr__(self) -> str:
        return f"<VisionSkill max_documents={self.max_documents}>"
