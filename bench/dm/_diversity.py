"""Cross-model diversity metric for compliance-theatre detection.

Item 1E.7 from Exp 40 execution plan. The 5-panel round-1 review on
15 April 2026 identified compliance theatre as the dominant §18 risk:
nu_k rises nominally while semantic novelty stagnates because models
converge on formulaic template alternatives.

This module computes a defensive instrument: mean pairwise Jaccard
across all divergence alternatives across all models per round. Trend
to 1.0 signals template collapse. Logging-only, non-invasive.

Two functions:

* ``compute_cross_model_diversity`` — pairwise Jaccard over a sequence
  of alternative strings (already tokenised externally or raw text).

* ``diversity_signal_from_round`` — convenience: accept a list of
  ``(model_id, alternative_text)`` pairs and produce a diversity
  summary suitable for round JSON logging.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple


_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "should", "could", "may", "might", "must",
    "to", "of", "in", "on", "at", "by", "for", "with", "from",
    "this", "that", "these", "those", "it", "its", "as", "not", "no",
})


def _tokenise(text: str) -> set:
    if not text:
        return set()
    # Simple tokenisation matching _divergence.py Jaccard convention.
    tokens = {
        t.strip(".,;:!?()[]{}\"'`")
        for t in text.lower().split()
    }
    return {t for t in tokens if t and t not in _STOPWORDS}


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union > 0 else 0.0


def compute_cross_model_diversity(alternatives: Sequence[str]) -> Dict[str, float]:
    """Compute pairwise Jaccard statistics over a list of alternative texts.

    Args:
        alternatives: Sequence of alternative strings (one per
            model-finding pair).  Fewer than 2 means diversity is
            undefined — returns neutral 1.0 values (treated as
            "maximally diverse" to avoid false-positive theatre flags
            with thin data).

    Returns:
        Dict with:
          * ``count``: number of alternatives
          * ``pairs``: number of pairs compared
          * ``mean_pairwise_jaccard``: mean similarity (0 = diverse, 1 = identical)
          * ``max_pairwise_jaccard``: most-similar pair's similarity
          * ``template_collapse_risk``: ratio in [0, 1] interpreting the
            mean; ≥ 0.85 is the alarm threshold matching §18 isomorphism.
    """
    n = len(alternatives)
    if n < 2:
        return {
            "count": float(n),
            "pairs": 0.0,
            "mean_pairwise_jaccard": 0.0,
            "max_pairwise_jaccard": 0.0,
            "template_collapse_risk": 0.0,
        }

    token_sets = [_tokenise(a) for a in alternatives]
    pair_count = 0
    jaccard_sum = 0.0
    jaccard_max = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            j_ij = _jaccard(token_sets[i], token_sets[j])
            jaccard_sum += j_ij
            if j_ij > jaccard_max:
                jaccard_max = j_ij
            pair_count += 1

    mean_j = jaccard_sum / pair_count if pair_count > 0 else 0.0
    # Risk interpretation: mean >= 0.85 matches the §18 isomorphism threshold.
    # Linearly map [0.5, 1.0] onto [0.0, 1.0] for interpretable signal.
    risk = max(0.0, (mean_j - 0.5) / 0.5) if mean_j > 0.5 else 0.0
    risk = min(1.0, risk)

    return {
        "count": float(n),
        "pairs": float(pair_count),
        "mean_pairwise_jaccard": round(mean_j, 4),
        "max_pairwise_jaccard": round(jaccard_max, 4),
        "template_collapse_risk": round(risk, 4),
    }


def diversity_signal_from_round(
    per_model_alternatives: Iterable[Tuple[str, str]],
) -> Dict[str, object]:
    """Build a round-level diversity signal.

    Args:
        per_model_alternatives: Iterable of ``(model_id, alternative_text)``
            tuples.  Pass every §18 alternative produced in the round; if
            one model emitted three alternatives, pass three tuples for
            that model.

    Returns:
        Dict suitable for inclusion in round JSON under
        ``cross_model_diversity``. Keys:
          * ``per_model_count``: Dict[model_id, count of alternatives]
          * ``stats``: output of ``compute_cross_model_diversity`` on all
            alternatives pooled
          * ``cross_model_only``: same stats but restricted to the
            first alternative per model, for a cleaner "template across
            models" signal
    """
    all_alts: List[str] = []
    per_model: Dict[str, List[str]] = {}
    for model_id, alt in per_model_alternatives:
        all_alts.append(alt)
        per_model.setdefault(model_id, []).append(alt)

    per_model_count = {mid: len(alts) for mid, alts in per_model.items()}
    stats = compute_cross_model_diversity(all_alts)

    first_per_model = [alts[0] for alts in per_model.values() if alts]
    cross_only = compute_cross_model_diversity(first_per_model)

    return {
        "per_model_count": per_model_count,
        "stats": stats,
        "cross_model_only": cross_only,
    }
