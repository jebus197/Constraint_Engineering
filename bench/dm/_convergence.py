"""CDSFL Dynamic Management — Convergence Detection (Area 4).

Three-metric conservative convergence detection with severity veto.
Extracted from ``bench/dynamic_management.py``.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

from bench.dm._types import (
    DynamicManagementConfig,
    Finding,
    FindingEquivalenceClass,
)


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


def _tokenize_for_similarity(text: str) -> list[str]:
    """Tokenize text for similarity comparison: lowercase, strip stopwords."""
    words = text.lower().split()
    return [w for w in words if w not in _STOPWORDS and len(w) > 2]


def _bigrams(tokens: list[str]) -> set[tuple[str, str]]:
    """Generate bigram set from token list."""
    return {(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)}


def _finding_similarity(f1: Finding, f2: Finding) -> float:
    """Compute similarity between two findings.

    Uses flaw-class match + combined unigram/bigram Jaccard on description
    words (stopwords removed). Bigrams capture phrase-level semantic overlap
    that raw word sets miss — "race condition" and "condition race" are
    different bigrams, but "race condition" and "race condition" match.

    The combined score weights unigrams 0.6 and bigrams 0.4. This provides
    a middle ground between the original raw Jaccard (too strict for
    semantic duplicates) and embedding-based similarity (too complex for
    the current infrastructure).

    When flaw classes differ, the combined Jaccard alone determines the score
    (no class bonus). This prevents models that assign different integer
    labels to the same concept from appearing maximally novel.

    Self-healing note: if this function fails to detect convergence (kappa
    stuck at 0.0 for consecutive rounds), the DetectorHealthMonitor will
    flag the pathology. See §immune_response below.

    Args:
        f1, f2: Findings to compare.

    Returns:
        Similarity in [0, 1].
    """
    class_match = f1.flaw_class == f2.flaw_class

    # Tokenize with stopword removal
    tokens1 = _tokenize_for_similarity(f1.description)
    tokens2 = _tokenize_for_similarity(f2.description)

    # Handle empty descriptions
    if not tokens1 and not tokens2:
        return 0.8 if class_match else 0.2
    if not tokens1 or not tokens2:
        return 0.3 if class_match else 0.1

    # Unigram Jaccard (on content words only)
    words1 = set(tokens1)
    words2 = set(tokens2)
    uni_inter = len(words1 & words2)
    uni_union = len(words1 | words2)
    uni_jaccard = uni_inter / uni_union if uni_union else 0.0

    # Bigram Jaccard (phrase-level overlap)
    bg1 = _bigrams(tokens1)
    bg2 = _bigrams(tokens2)
    if bg1 or bg2:
        bg_inter = len(bg1 & bg2)
        bg_union = len(bg1 | bg2)
        bg_jaccard = bg_inter / bg_union if bg_union else 0.0
    else:
        bg_jaccard = uni_jaccard  # single-word descriptions: fall back to unigram

    # Combined similarity: 60% unigram + 40% bigram
    combined = 0.6 * uni_jaccard + 0.4 * bg_jaccard

    if class_match:
        # 0.3 base from class match + 0.7 from combined Jaccard
        return 0.3 + 0.7 * combined
    else:
        # No class match bonus — combined Jaccard only.
        # Confer consensus: raw Jaccard at tau_sim=0.8 was too strict.
        # Stopword removal + bigrams increase similarity for genuine
        # duplicates while maintaining discrimination.
        return combined


class ConvergenceDetector:
    """Three-metric conservative convergence detection.

    Implements the merged formulation from §5 of the converged plan:
    - Finding aggregation via equivalence relation ≈
    - Three metrics: kappa_set, kappa_rate, kappa_adopt
    - Combined via min (conservative)
    - Severity veto clause (ChatGPT contribution)
    - tau_kappa SEPARATE from gamma (founder decision)

    Example::

        cd = ConvergenceDetector(DynamicManagementConfig())
        cd.add_round_findings(0, [finding1, finding2])
        cd.add_round_findings(1, [finding3])
        print(cd.kappa(1))  # convergence metric
        print(cd.converged(1))  # boolean predicate
    """

    def __init__(
        self,
        config: DynamicManagementConfig,
        similarity_fn: Optional[Callable[[Finding, Finding], float]] = None,
    ) -> None:
        self.config = config
        self.similarity_fn = similarity_fn or _finding_similarity
        # Per-round raw findings
        self._round_findings: Dict[int, List[Finding]] = {}
        # Per-round equivalence classes (computed lazily)
        self._round_classes: Dict[int, List[FindingEquivalenceClass]] = {}
        # Cumulative equivalence classes
        self._cumulative_classes: Dict[int, List[FindingEquivalenceClass]] = {}
        # Round durations (for rate-based metric)
        self._round_durations: Dict[int, float] = {}
        # Adoption deltas (from external source)
        self._adoption_deltas: Dict[int, float] = {}

    def add_round_findings(
        self,
        round_idx: int,
        findings: Sequence[Finding],
        duration: float = 1.0,
        adoption_delta: float = 0.0,
    ) -> None:
        """Register findings for a round.

        Args:
            round_idx: Round index r.
            findings: All findings from all models in this round.
            duration: Wall-clock duration of the round (for rate metric).
            adoption_delta: Delta_r from existing schema (for adopt metric).
        """
        self._round_findings[round_idx] = list(findings)
        self._round_durations[round_idx] = duration
        self._adoption_deltas[round_idx] = adoption_delta
        # Invalidate cached classes
        self._round_classes.pop(round_idx, None)
        # Recompute cumulative for this and all subsequent rounds
        for r in list(self._cumulative_classes.keys()):
            if r >= round_idx:
                self._cumulative_classes.pop(r, None)

    def _compute_equivalence_classes(
        self, findings: Sequence[Finding]
    ) -> List[FindingEquivalenceClass]:
        """Cluster findings into equivalence classes using the ≈ relation.

        Uses single-linkage clustering with tau_sim threshold.
        """
        if not findings:
            return []

        n = len(findings)
        # Union-Find for clustering
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x: int, y: int) -> None:
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for i in range(n):
            for j in range(i + 1, n):
                if self.similarity_fn(findings[i], findings[j]) >= self.config.tau_sim:
                    union(i, j)

        # Group by root
        clusters: Dict[int, List[int]] = {}
        for i in range(n):
            root = find(i)
            clusters.setdefault(root, []).append(i)

        classes = []
        for idx, (root, members_idx) in enumerate(clusters.items()):
            members = [findings[i] for i in members_idx]
            # Aggregated severity: max severity in class (conservative proxy for S_v)
            agg_sev = max(f.severity for f in members)
            flaw_class = members[0].flaw_class
            classes.append(
                FindingEquivalenceClass(
                    class_id=f"ec_{idx}",
                    flaw_class=flaw_class,
                    members=members,
                    aggregated_severity=agg_sev,
                )
            )
        return classes

    def get_round_classes(self, round_idx: int) -> List[FindingEquivalenceClass]:
        """Get equivalence classes for a specific round F^(r)."""
        if round_idx not in self._round_classes:
            findings = self._round_findings.get(round_idx, [])
            self._round_classes[round_idx] = self._compute_equivalence_classes(findings)
        return self._round_classes[round_idx]

    def get_cumulative_classes(self, round_idx: int) -> List[FindingEquivalenceClass]:
        """Get cumulative equivalence classes F^(<=r).

        Aggregates all findings from round 0 through round_idx, then
        computes equivalence classes over the union.
        """
        if round_idx not in self._cumulative_classes:
            all_findings: List[Finding] = []
            for r in range(round_idx + 1):
                all_findings.extend(self._round_findings.get(r, []))
            self._cumulative_classes[round_idx] = self._compute_equivalence_classes(
                all_findings
            )
        return self._cumulative_classes[round_idx]

    def _novel_classes(
        self, round_idx: int
    ) -> List[FindingEquivalenceClass]:
        """Find equivalence classes in F^(r) that are novel (not in F^(<=r-1)).

        A class is novel if none of its members are similar to any member
        of any class in the cumulative set from the previous round.
        """
        if round_idx <= 0:
            return self.get_round_classes(round_idx)

        current_classes = self.get_round_classes(round_idx)
        prev_cumulative = self.get_cumulative_classes(round_idx - 1)

        if not prev_cumulative:
            return current_classes

        prev_findings = []
        for ec in prev_cumulative:
            prev_findings.extend(ec.members)

        novel = []
        for ec in current_classes:
            is_novel = True
            for member in ec.members:
                for prev_f in prev_findings:
                    if self.similarity_fn(member, prev_f) >= self.config.tau_sim:
                        is_novel = False
                        break
                if not is_novel:
                    break
            if is_novel:
                novel.append(ec)
        return novel

    def kappa_set(self, round_idx: int) -> float:
        """Set-theoretic stability (severity-weighted novelty).

        kappa_set(r) = 1 - sum(Sev_agg of novel classes) / (sum(Sev_agg of all cumulative) + eps)

        Returns value in [0, 1]. Higher = more converged.
        """
        novel = self._novel_classes(round_idx)
        cumulative = self.get_cumulative_classes(round_idx)

        novel_sev = sum(ec.aggregated_severity for ec in novel)
        total_sev = sum(ec.aggregated_severity for ec in cumulative) + self.config.epsilon_conv

        return 1.0 - (novel_sev / total_sev)

    def kappa_rate(self, round_idx: int) -> float:
        """Rate-based stability (Duane connection).

        kappa_rate(r) = 1 - lambda_hat(r) / (lambda_hat(1) + eps)

        where lambda_hat(r) = |F^(r)| / delta_t_r.

        Returns value in (-inf, 1]. Clamped to [0, 1] in combined metric.
        """
        if round_idx < 1:
            return 0.0

        def _rate(r: int) -> float:
            classes = self.get_round_classes(r)
            dt = self._round_durations.get(r, 1.0)
            return len(classes) / max(dt, 1e-10)

        rate_r = _rate(round_idx)
        rate_1 = _rate(1) if 1 in self._round_findings else _rate(0)

        # MM_F006 + GEM_FFF_002: When rate_1 is near zero (no baseline
        # established), check if rate_r is also near zero. If both are
        # near zero, return 0.0 (no data). If rate_r > 0 with rate_1 ≈ 0,
        # the system is diverging — return -1.0 (bounded minimum).
        if rate_1 < self.config.epsilon_conv:
            if rate_r < self.config.epsilon_conv:
                return 0.0  # No baseline, no current activity
            return -1.0  # Diverging: new findings with no baseline
        result = 1.0 - (rate_r / (rate_1 + self.config.epsilon_conv))
        return max(-1.0, min(1.0, result))

    def kappa_adopt(self, round_idx: int) -> float:
        """Adoption stabilisation metric.

        kappa_adopt(r) = clamp(1 - Delta_r, 0, 1)

        where Delta_r is the adoption delta from the existing schema.
        Returns value in [0, 1].  Clamped to prevent negative kappa or
        values > 1 when adoption_delta is outside [0, 1] (Exp14 fix:
        ChatGPT F005, sev 0.90).
        """
        delta = self._adoption_deltas.get(round_idx, 0.0)
        return max(0.0, min(1.0, 1.0 - delta))

    def kappa(self, round_idx: int) -> float:
        """Combined convergence metric.

        kappa(r) = min(kappa_set(r), max(0, kappa_rate(r)), kappa_adopt(r))

        Conservative combination (3/4 model majority).
        Returns value in [0, 1].
        """
        ks = self.kappa_set(round_idx)
        kr = max(0.0, self.kappa_rate(round_idx))
        ka = self.kappa_adopt(round_idx)
        return min(ks, kr, ka)

    def _veto(self, round_idx: int) -> bool:
        """Severity veto: a single new high-severity finding blocks convergence.

        veto(r) iff exists [f] in novel classes with Sev_agg >= eta_veto.
        (ChatGPT contribution, adopted.)
        """
        novel = self._novel_classes(round_idx)
        return any(ec.aggregated_severity >= self.config.eta_veto for ec in novel)

    def converged(self, round_idx: int) -> bool:
        """Convergence predicate.

        converged(r) iff kappa(r) >= tau_kappa AND r >= min_rounds AND NOT veto(r)

        Note: tau_kappa is SEPARATE from gamma (founder decision §9.2).
        """
        if round_idx < self.config.min_rounds_for_convergence:
            return False
        if self._veto(round_idx):
            return False
        return self.kappa(round_idx) >= self.config.tau_kappa

    def conv_metric(self, round_idx: int) -> float:
        """Alias for kappa(r) — the continuous convergence measure."""
        return self.kappa(round_idx)

    def estimate_gamma(self, round_idx: int) -> float:
        """Estimate Duane convergence parameter gamma_hat.

        MM_F014: Corrected formula. Duane model: N(t) = (t/η)^β, so
        β = (log(N(r)) - log(N(1))) / log(r). Then γ = 1 - β:
          γ > 0: reliability growth (finding rate decreasing)
          γ < 0: degradation (finding rate increasing)

        This is a DIAGNOSTIC, not the convergence threshold (founder decision).
        """
        if round_idx < 2:
            return 0.0

        cum_r = len(self.get_cumulative_classes(round_idx))
        cum_1 = len(self.get_cumulative_classes(1)) if 1 in self._round_findings else len(
            self.get_cumulative_classes(0)
        )

        # CX refinement of GEM_FFF_001: return 1.0 only when cum_1 > 0.
        # When cum_r == cum_1 == 0, there's no data — return 0.0 not "converged".
        if cum_1 <= 0:
            return 0.0
        if cum_r <= cum_1:
            return 1.0 if cum_r == cum_1 else 0.0

        log_r = math.log(round_idx)
        if abs(log_r) < 1e-10:
            return float("inf")

        beta = (math.log(cum_r) - math.log(cum_1)) / log_r
        return 1.0 - beta

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(config: DynamicManagementConfig) -> bool:
        """K=1: Trivial aggregation. kappa measures single model's finding exhaustion."""
        cd = ConvergenceDetector(config)
        # Round 0: many findings
        findings_r0 = [
            Finding(f"f{i}", "m1", 0, i % 3, 0.5 + 0.1 * i, 0.5, f"finding {i}")
            for i in range(5)
        ]
        cd.add_round_findings(0, findings_r0)
        # Round 1: same findings (no novelty)
        findings_r1 = [
            Finding(f"f{i}_r1", "m1", 1, i % 3, 0.5 + 0.1 * i, 0.5, f"finding {i}")
            for i in range(5)
        ]
        cd.add_round_findings(1, findings_r1)
        # Round 2: same again
        findings_r2 = [
            Finding(f"f{i}_r2", "m1", 2, i % 3, 0.5 + 0.1 * i, 0.5, f"finding {i}")
            for i in range(5)
        ]
        cd.add_round_findings(2, findings_r2)
        # Should show high convergence
        return cd.kappa_set(2) > 0.8

    @staticmethod
    def validate_no_findings(config: DynamicManagementConfig) -> bool:
        """Edge case: F^(<=r) = empty. Convention: not converged unless null_expected."""
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [])
        cd.add_round_findings(1, [])
        cd.add_round_findings(2, [])
        # kappa_set with no findings: 1 - 0/(0+eps) = 1.0
        # But we require r >= min_rounds, so check that
        return cd.kappa_set(2) == 1.0
