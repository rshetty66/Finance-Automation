"""
Embedding utilities for the vector-search router.

Uses sentence-transformers for local embeddings (no API dependency),
with a lazy-loaded singleton model to avoid re-loading on every call.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from rudra.config import get_config

logger = logging.getLogger(__name__)

_model: Optional[object] = None


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            config = get_config()
            _model = SentenceTransformer(
                config.embeddings.model_name,
                device=config.embeddings.device,
            )
            logger.info("Loaded embedding model: %s", config.embeddings.model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for routing. "
                "Install with: pip install sentence-transformers"
            )
    return _model


def embed_text(text: str) -> np.ndarray:
    """Embed a single text string, returning a 1-D float32 numpy array."""
    model = _get_model()
    return model.encode(text, convert_to_numpy=True, normalize_embeddings=True)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed multiple texts, returning a (N, D) float32 numpy array."""
    model = _get_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors (assumes normalized)."""
    return float(np.dot(a, b))


def cosine_similarities(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Cosine similarities between a query vector and a matrix of vectors."""
    return matrix @ query
