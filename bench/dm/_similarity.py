"""CDSFL Dynamic Management — Shared Similarity Backend.

Provides a unified similarity function for both the ConvergenceDetector
and the DynamicManager. Supports two backends:

1. **Embedding** (default when sentence-transformers is installed):
   Sentence-transformer cosine similarity with flaw-class bonus.
   Model: all-MiniLM-L6-v2 (~80MB, lazy-loaded singleton).

2. **Lexical** (fallback):
   Unigram/bigram Jaccard with flaw-class bonus.

Both backends produce bounded output in [0, 1] via a convex combination:

    s(f1, f2) = (1 - beta) * content_sim + beta * b_class

where content_sim in [0, 1] (cosine01 or combined Jaccard) and
b_class = CLASS_BONUS if flaw_class matches, else 0.

Created: 12 April 2026 (Phase 2 — Embedding Similarity).
"""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, Optional, Tuple

from bench.dm._types import Finding

logger = logging.getLogger("cdsfl.similarity")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLASS_BONUS: float = 0.3  # Flaw-class match bonus
BETA: float = 0.2  # Weight for class bonus in convex combination
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Stopwords and tokenisation (shared with lexical backend)
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "and", "but", "or",
    "nor", "not", "no", "so", "if", "then", "than", "that", "this", "these",
    "those", "it", "its", "of", "in", "on", "at", "to", "for", "with",
    "by", "from", "as", "into", "through", "during", "before", "after",
    "above", "below", "between", "out", "up", "down", "about", "each",
    "all", "any", "both", "such", "when", "where", "which", "who", "whom",
    "what", "how", "there", "here", "very", "just", "also", "only", "more",
    "most", "other", "some", "over", "under", "again", "further", "once",
})


def _tokenize(text: str) -> list[str]:
    """Lowercase, split, strip stopwords and short tokens."""
    return [w for w in text.lower().split() if w not in _STOPWORDS and len(w) > 2]


def _bigrams(tokens: list[str]) -> set[tuple[str, str]]:
    """Generate bigram set from token list."""
    return {(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)}


# ---------------------------------------------------------------------------
# Lexical backend (Jaccard)
# ---------------------------------------------------------------------------

def jaccard_similarity(f1: Finding, f2: Finding) -> float:
    """Combined unigram/bigram Jaccard with flaw-class bonus.

    Score = (1 - BETA) * combined_jaccard + BETA * b_class
    where combined_jaccard = 0.6 * unigram_jaccard + 0.4 * bigram_jaccard.

    Returns similarity in [0, 1].
    """
    class_match = f1.flaw_class == f2.flaw_class
    b_class = CLASS_BONUS if class_match else 0.0

    tokens1 = _tokenize(f1.description)
    tokens2 = _tokenize(f2.description)

    if not tokens1 and not tokens2:
        return (1 - BETA) * 0.5 + BETA * b_class
    if not tokens1 or not tokens2:
        return (1 - BETA) * 0.1 + BETA * b_class

    # Unigram Jaccard
    words1, words2 = set(tokens1), set(tokens2)
    uni_union = len(words1 | words2)
    uni_jaccard = len(words1 & words2) / uni_union if uni_union else 0.0

    # Bigram Jaccard
    bg1, bg2 = _bigrams(tokens1), _bigrams(tokens2)
    if bg1 or bg2:
        bg_union = len(bg1 | bg2)
        bg_jaccard = len(bg1 & bg2) / bg_union if bg_union else 0.0
    else:
        bg_jaccard = uni_jaccard

    combined = 0.6 * uni_jaccard + 0.4 * bg_jaccard
    return (1 - BETA) * combined + BETA * b_class


# ---------------------------------------------------------------------------
# Embedding backend (sentence-transformer cosine)
# ---------------------------------------------------------------------------

_EMBEDDING_MODEL: Optional[object] = None
_EMBEDDING_CACHE: Dict[str, object] = {}


def _get_embedding_model():
    """Lazy-load the sentence-transformer model (singleton)."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Loaded embedding model: %s", EMBEDDING_MODEL_NAME)
        except (ImportError, Exception) as exc:
            logger.warning(
                "sentence-transformers unavailable (%s); "
                "falling back to lexical similarity",
                exc,
            )
            _EMBEDDING_MODEL = False  # sentinel: tried and failed
    return _EMBEDDING_MODEL if _EMBEDDING_MODEL is not False else None


def _cache_key(text: str) -> str:
    """Stable hash key for embedding cache."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _get_embedding(text: str):
    """Get or compute embedding for text, using cache."""
    import numpy as np

    key = _cache_key(text)
    if key not in _EMBEDDING_CACHE:
        model = _get_embedding_model()
        if model is None:
            return None
        emb = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        _EMBEDDING_CACHE[key] = emb
    return _EMBEDDING_CACHE[key]


def embedding_similarity(f1: Finding, f2: Finding) -> float:
    """Sentence-transformer cosine similarity with flaw-class bonus.

    Score = (1 - BETA) * cos01 + BETA * b_class
    where cos01 = (cosine_similarity + 1) / 2   (mapped from [-1,1] to [0,1]).

    Returns similarity in [0, 1].
    """
    import numpy as np

    class_match = f1.flaw_class == f2.flaw_class
    b_class = CLASS_BONUS if class_match else 0.0

    emb1 = _get_embedding(f1.description)
    emb2 = _get_embedding(f2.description)

    if emb1 is None or emb2 is None:
        # Fallback to lexical if embedding failed
        return jaccard_similarity(f1, f2)

    # Cosine similarity in [-1, 1]
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    if norm1 < 1e-10 or norm2 < 1e-10:
        cos_sim = 0.0
    else:
        cos_sim = float(np.dot(emb1, emb2) / (norm1 * norm2))

    # Map to [0, 1]
    cos01 = (cos_sim + 1.0) / 2.0

    return (1 - BETA) * cos01 + BETA * b_class


# ---------------------------------------------------------------------------
# Unified interface
# ---------------------------------------------------------------------------

def finding_similarity(f1: Finding, f2: Finding) -> float:
    """Compute similarity between two findings using the best available backend.

    Tries embedding backend first; falls back to lexical if sentence-transformers
    is not installed or model loading fails.

    Returns similarity in [0, 1].
    """
    model = _get_embedding_model()
    if model is not None:
        return embedding_similarity(f1, f2)
    return jaccard_similarity(f1, f2)


def clear_cache() -> None:
    """Clear the embedding cache (useful for testing)."""
    _EMBEDDING_CACHE.clear()
