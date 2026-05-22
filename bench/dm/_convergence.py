"""CDSFL Dynamic Management — Convergence Detection (Area 4).

Three-metric conservative convergence detection with severity veto.
Extracted from ``bench/dynamic_management.py``.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence

from bench.dm._types import (
    DynamicManagementConfig,
    Finding,
    FindingEquivalenceClass,
)


from bench.dm._similarity import finding_similarity as _finding_similarity
from bench.dm._similarity import effective_tau_sim as _effective_tau_sim
# Backward-compat re-exports (used by dynamic_management.py shim and _diminishing_returns.py)
from bench.dm._similarity import _tokenize as _tokenize_for_similarity  # noqa: F401
from bench.dm._similarity import _bigrams  # noqa: F401
from bench.dm._similarity import _STOPWORDS  # noqa: F401


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

    def _tau_sim(self) -> float:
        """Equivalence-merge threshold matched to THIS detector's similarity
        function — not to global package state.

        For the default embedding-backed similarity (_finding_similarity), use
        the embedding-calibrated threshold (tau_sim_embed) when the embedding
        backend is active, else the lexical tau_sim — via effective_tau_sim().
        For a CUSTOM similarity_fn the caller owns its calibration, so use
        config.tau_sim directly.

        Confer condition (2026-05-22, 5-model fix-verification): bind the
        threshold to the function actually in use. A custom lexical
        similarity_fn run while sentence-transformers happens to be installed
        must NOT silently inherit the 0.55 embedding threshold (which would
        stop identical lexical findings from merging -> infinite false
        novelty -> non-convergence). This keeps threshold and similarity
        scale coupled.
        """
        if self.similarity_fn is _finding_similarity:
            return _effective_tau_sim(self.config)
        return self.config.tau_sim

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
                if self.similarity_fn(findings[i], findings[j]) >= self._tau_sim():
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
                    if self.similarity_fn(member, prev_f) >= self._tau_sim():
                        is_novel = False
                        break
                if not is_novel:
                    break
            if is_novel:
                novel.append(ec)
        return novel

    def _suppression_weight(
        self, finding: Finding, prior_findings: Sequence[Finding]
    ) -> float:
        """Compute suppression weight for a single finding.

        w(f) = max(exp(-λ_s · Σ_{g ∈ TopK(f)} sim(f, g)), w_floor)

        TopK(f) selects the k most similar prior findings regardless of
        arrival order, making this permutation-invariant by construction.
        This fixes the order-dependence bug from predecessor-product
        suppression (Error 2, 12 April 2026).

        Returns weight in [w_floor, 1.0].
        """
        if not prior_findings:
            return 1.0  # No priors → no suppression

        # Compute similarity to all prior findings
        sims = sorted(
            (self.similarity_fn(finding, g) for g in prior_findings),
            reverse=True,
        )

        # Sum top-k similarities
        k = self.config.suppression_k
        top_k_sum = sum(sims[:k])

        # Exponential decay, floored
        w = math.exp(-self.config.lambda_s * top_k_sum)
        return max(w, self.config.w_floor)

    def _weighted_novel_severity(
        self, novel_classes: List[FindingEquivalenceClass],
        prior_findings: Optional[Sequence[Finding]] = None,
    ) -> float:
        """Compute suppression-weighted severity for novel equivalence classes.

        w(f) = max(exp(-λ_s · Σ TopK sim), w_floor) per finding, then
        class weight = max member weight (conservative: least suppressed).

        CRITICAL CONSTRAINT (Confer 12 April 2026 — Corroboration Collapse):
        Suppression weights apply to kappa_set NUMERATOR ONLY. They must
        NEVER enter q_eff in the Bayesian update (q = η·d·p, no w(f)).
        The denominator uses raw (unweighted) aggregated_severity.
        """
        if prior_findings is None or not prior_findings:
            # No priors → identity weight (1.0)
            return sum(ec.aggregated_severity for ec in novel_classes)

        total = 0.0
        for ec in novel_classes:
            # Per-class weight: max of member weights (least suppressed)
            class_weight = max(
                self._suppression_weight(member, prior_findings)
                for member in ec.members
            ) if ec.members else 1.0
            total += class_weight * ec.aggregated_severity
        return total

    def kappa_set(self, round_idx: int) -> float:
        """Set-theoretic stability (severity-weighted novelty).

        kappa_set(r) = 1 - Σ(w·Sev_novel) / (Σ Sev_cumulative + ε)

        Numerator: suppression-weighted severity of novel classes.
        Denominator: raw (unweighted) severity of all cumulative classes.
        This asymmetry prevents the kappa overflow bug (Error 3, 12 April 2026)
        where weighting the denominator caused kappa to leave [0, 1].

        Returns value in [0, 1]. Higher = more converged.
        """
        novel = self._novel_classes(round_idx)
        cumulative = self.get_cumulative_classes(round_idx)

        # Collect prior findings for suppression weighting
        prior_findings: List[Finding] = []
        if round_idx > 0:
            for ec in self.get_cumulative_classes(round_idx - 1):
                prior_findings.extend(ec.members)

        # Numerator: suppression-weighted (w(f) applied here)
        novel_sev = self._weighted_novel_severity(novel, prior_findings)
        # Denominator: raw, unweighted — w(f) EXCLUDED (Corroboration Collapse fix)
        total_sev = sum(ec.aggregated_severity for ec in cumulative) + self.config.epsilon_conv

        return 1.0 - (novel_sev / total_sev)

    def kappa_rate(self, round_idx: int) -> float:
        """Rate-based stability (Duane connection).

        kappa_rate(r) = clamp(1 - lambda_novel(r) / lambda_peak, 0, 1)

        where lambda_novel(r) = |novel classes at r| / delta_t_r is the
        NOVEL discovery intensity (new equivalence classes per unit time),
        and lambda_peak is the maximum novel intensity over rounds 0..r
        (the initial discovery burst). As the novel rate decays from its
        peak the metric rises toward 1; a genuinely quiet state (no new
        discoveries) reads converged. When no novelty has ever appeared
        there is no decline signal, so the metric returns 1.0 and does
        not veto (kappa_set / kappa_adopt govern).

        2026-05-22 (Exp 41 materiality review, founder-approved fold of the
        three material kappa_rate findings; the other findings were
        non-material footnotes deferred to the iteration backlog):
        - C1 (DS_R7_001 etc.): count NOVEL classes, not all round classes,
          so repeated findings no longer register as ongoing discovery and
          wrongly block convergence. This is the Duane-correct quantity
          (new failures/discoveries per round), not raw round volume.
        - C2/C3 (kappa_rate baseline + quiet-state): use the PEAK novel
          rate as the baseline (robust to a quiet round 1) and treat a
          genuinely quiet state as converged, not 0.0/-1.0. Replaces the
          brittle "no-baseline" special case with one clear rule.

        Returns value in [0, 1]. Higher = more converged.
        """
        if round_idx < 1:
            return 0.0

        def _novel_rate(r: int) -> float:
            dt = self._round_durations.get(r, 1.0)
            return len(self._novel_classes(r)) / max(dt, 1e-10)

        rate_r = _novel_rate(round_idx)
        peak = max((_novel_rate(r) for r in range(round_idx + 1)), default=0.0)
        if peak < self.config.epsilon_conv:
            return 1.0  # no novelty ever -> no decline signal; do not veto
        return max(0.0, min(1.0, 1.0 - rate_r / (peak + self.config.epsilon_conv)))

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
