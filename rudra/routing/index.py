"""
AgentCapabilityIndex - pre-computed vector index of agent capabilities.

Builds a dense embedding for each agent by concatenating its capabilities
and embedding_tags into a focused text block. The master agent (rudra) is
excluded from primary routing unless no specialist matches; it serves as
the fallback.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from rudra.models import AgentSpec
from rudra.routing.embeddings import embed_text, embed_texts, cosine_similarities

logger = logging.getLogger(__name__)


@dataclass
class IndexEntry:
    agent_id: str
    domain: str
    capabilities: list[str]
    embedding_text: str
    confidence_threshold: float
    is_catch_all: bool = False
    embedding: Optional[np.ndarray] = field(default=None, repr=False)


class AgentCapabilityIndex:
    """
    In-memory vector index over agent capabilities.

    Usage::

        index = AgentCapabilityIndex.from_specs(registry.list_agents())
        results = index.search("Analyze a lease under IFRS 16", top_k=3)
    """

    def __init__(self) -> None:
        self._entries: list[IndexEntry] = []
        self._matrix: Optional[np.ndarray] = None

    @classmethod
    def from_specs(cls, specs: list[AgentSpec]) -> "AgentCapabilityIndex":
        index = cls()

        texts: list[str] = []
        for spec in specs:
            is_catch_all = spec.id in ("rudra", "openclaw-orchestrator", "vector-search-router")
            embedding_text = cls._build_embedding_text(spec, is_catch_all)
            entry = IndexEntry(
                agent_id=spec.id,
                domain=spec.domain,
                capabilities=spec.capabilities,
                embedding_text=embedding_text,
                confidence_threshold=spec.confidence_threshold,
                is_catch_all=is_catch_all,
            )
            index._entries.append(entry)
            texts.append(embedding_text)

        if texts:
            embeddings = embed_texts(texts)
            for i, entry in enumerate(index._entries):
                entry.embedding = embeddings[i]
            index._matrix = embeddings
            logger.info("Built capability index with %d agents", len(index._entries))

        return index

    @staticmethod
    def _build_embedding_text(spec: AgentSpec, is_catch_all: bool = False) -> str:
        """
        Build embedding text from agent metadata.

        For catch-all agents (rudra), use ONLY the embedding_tags
        to prevent their broad descriptions from dominating similarity.
        For specialists, include name + capabilities + tags (no description,
        which is also often too broad).
        """
        if is_catch_all:
            return " ".join(spec.embedding_tags)

        parts = [
            spec.name,
            " ".join(spec.capabilities),
            " ".join(spec.embedding_tags),
        ]
        return " | ".join(p for p in parts if p)

    def search(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None,
    ) -> list[tuple[IndexEntry, float]]:
        """
        Search the index for the best-matching agents.

        Specialists are preferred over catch-all agents. The catch-all
        (rudra) only appears as primary if no specialist exceeds its
        confidence threshold.
        """
        if self._matrix is None or len(self._entries) == 0:
            return []

        query_embedding = embed_text(query)
        scores = cosine_similarities(query_embedding, self._matrix)

        specialists: list[tuple[IndexEntry, float]] = []
        catch_alls: list[tuple[IndexEntry, float]] = []

        for i, entry in enumerate(self._entries):
            score = float(scores[i])
            if domain_filter and entry.domain != domain_filter:
                continue

            if entry.is_catch_all:
                catch_alls.append((entry, score))
            elif score >= entry.confidence_threshold:
                specialists.append((entry, score))

        specialists.sort(key=lambda x: x[1], reverse=True)
        catch_alls.sort(key=lambda x: x[1], reverse=True)

        if specialists:
            return specialists[:top_k]

        if catch_alls:
            return catch_alls[:1]

        all_results = [(entry, float(scores[i])) for i, entry in enumerate(self._entries)]
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:top_k]

    def search_all(self, query: str) -> list[tuple[IndexEntry, float]]:
        if self._matrix is None:
            return []

        query_embedding = embed_text(query)
        scores = cosine_similarities(query_embedding, self._matrix)

        results = [(entry, float(scores[i])) for i, entry in enumerate(self._entries)]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def get_entry(self, agent_id: str) -> Optional[IndexEntry]:
        for entry in self._entries:
            if entry.agent_id == agent_id:
                return entry
        return None

    def __len__(self) -> int:
        return len(self._entries)
