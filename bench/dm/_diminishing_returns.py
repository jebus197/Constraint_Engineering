"""CDSFL Dynamic Management — Diminishing Returns Detection (Area 5).

Marginal value/cost ratio with ascending abstraction guard and vocabulary
saturation tracking. Extracted from ``bench/dynamic_management.py``.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence, Set

import numpy as np

from bench.dm._types import (
    DynamicManagementConfig,
    Finding,
)
from bench.dm._convergence import _tokenize_for_similarity, _finding_similarity


class DiminishingReturnsDetector:
    """Marginal value/cost ratio with ascending abstraction guard.

    Implements the merged formulation from §6 of the converged plan:
    - mu(r) = Delta_Y / c_r (marginal cognitive yield per unit cost)
    - Y^(<=r) = |F^(<=r)| * H_bar^(<=r) (cumulative cognitive yield)
    - Ascending abstraction guard (CONJUNCTIVE — founder decision §9.1)
    - Smoothing window W (CC2 contribution)
    - stop(r) predicate with threshold tau_mu

    Example::

        drd = DiminishingReturnsDetector(DynamicManagementConfig())
        drd.add_round(0, yield_value=5.0, cost=1.0, mean_abstraction_new=0.7)
        drd.add_round(1, yield_value=7.0, cost=1.0, mean_abstraction_new=0.6)
        print(drd.marginal_value(1))  # mu(1)
        print(drd.stop(1))  # False (r < r_min)
    """

    def __init__(self, config: DynamicManagementConfig) -> None:
        self.config = config
        # Per-round data (system-level)
        self._cumulative_yields: Dict[int, float] = {}  # Y^(<=r)
        self._round_costs: Dict[int, float] = {}  # c_r
        self._mean_abstraction_new: Dict[int, float] = {}  # H_bar^(r)_new
        # Per-model data (Exp13a confer: per-model mu eliminates cost
        # distortion from model attrition.  CC2 approved as HARD.)
        self._per_model_yields: Dict[str, Dict[int, float]] = {}  # model → {round → cumulative_yield}
        self._per_model_costs: Dict[str, Dict[int, float]] = {}  # model → {round → cost}
        # Novelty rate tracking (cost-decoupled convergence signal)
        self._novelty_rates: Dict[int, float] = {}  # fraction of novel findings per round
        self._all_prior_findings: List[Finding] = []  # accumulated for novelty comparison
        # Vocabulary saturation tracking (similarity-independent stop signal)
        self._cumulative_vocab: Set[str] = set()  # all unique terms seen (global)
        self._vocab_sizes: Dict[int, int] = {}  # cumulative vocab size per round
        self._vocab_growth_rates: Dict[int, float] = {}  # growth rate per round
        # Phase D (Exp14): Per-area vocabulary tracking.
        # Eliminates the decomposed-dispatch × global-vocab interaction that
        # caused premature termination in Exp13b.  Each area maintains its own
        # cumulative vocabulary.  Stop fires when ALL active areas are saturated.
        self._area_vocab: Dict[str, Set[str]] = {}  # area_id → cumulative terms
        self._area_vocab_sizes: Dict[str, Dict[int, int]] = {}  # area → {round → size}
        self._area_vocab_growth: Dict[str, Dict[int, float]] = {}  # area → {round → rate}
        self._area_active_rounds: Dict[str, Set[int]] = {}  # area → rounds where it was reviewed

    def add_round(
        self,
        round_idx: int,
        yield_value: float,
        cost: float,
        mean_abstraction_new: float = 0.5,
    ) -> None:
        """Register a round's cumulative yield, cost, and new-finding abstraction.

        Args:
            round_idx: Round index r.
            yield_value: Cumulative cognitive yield Y^(<=r) = |F^(<=r)| * H_bar^(<=r).
            cost: Round cost c_r = sum_m c_m * load(m, A^(r)).
            mean_abstraction_new: Mean abstraction index of NEW findings in round r.
        """
        self._cumulative_yields[round_idx] = yield_value
        self._round_costs[round_idx] = cost
        self._mean_abstraction_new[round_idx] = mean_abstraction_new

    def add_round_from_findings(
        self,
        round_idx: int,
        cumulative_findings: Sequence[Finding],
        new_findings: Sequence[Finding],
        cost: float,
    ) -> None:
        """Convenience: compute yield from finding sequences.

        Args:
            round_idx: Round index r.
            cumulative_findings: All findings up to and including round r.
            new_findings: Findings new in round r (F^(r) \\ F^(<=r-1)).
            cost: Round cost c_r.
        """
        if cumulative_findings:
            h_bar = float(np.mean([f.abstraction_index for f in cumulative_findings]))
            y = len(cumulative_findings) * h_bar
        else:
            y = 0.0

        if new_findings:
            h_new = float(np.mean([f.abstraction_index for f in new_findings]))
        else:
            h_new = 0.0

        self.add_round(round_idx, y, cost, h_new)

        # Compute novelty rate: fraction of new findings with max similarity
        # < tau_novelty to ALL prior findings. Cost-decoupled convergence signal.
        # When all findings are rephrased duplicates, novelty_rate → 0.
        # When all findings are genuinely new, novelty_rate → 1.
        tau_novelty = self.config.tau_novelty  # lower than tau_sim (0.8) — "related" counts as non-novel
        if self._all_prior_findings and new_findings:
            novel_count = 0
            for f in new_findings:
                max_sim = max(
                    _finding_similarity(f, pf) for pf in self._all_prior_findings
                )
                if max_sim < tau_novelty:
                    novel_count += 1
            self._novelty_rates[round_idx] = novel_count / len(new_findings)
        elif not self._all_prior_findings and new_findings:
            # First round — everything is novel
            self._novelty_rates[round_idx] = 1.0
        else:
            self._novelty_rates[round_idx] = 0.0

        # Accumulate prior findings for next round's novelty comparison
        if new_findings:
            self._all_prior_findings.extend(new_findings)

        # Vocabulary saturation: count unique terms per round.
        # Uses the same tokenizer as the similarity function — stopwords removed,
        # minimum length 3.  This is similarity-independent: it measures how many
        # NEW words appear, not whether findings are "similar" to prior ones.
        prev_size = len(self._cumulative_vocab)
        for f in new_findings:
            tokens = _tokenize_for_similarity(f.description)
            self._cumulative_vocab.update(tokens)
        new_size = len(self._cumulative_vocab)
        self._vocab_sizes[round_idx] = new_size
        if prev_size > 0:
            self._vocab_growth_rates[round_idx] = (new_size - prev_size) / prev_size
        else:
            self._vocab_growth_rates[round_idx] = 1.0  # first round = 100% growth

        # Phase D (Exp14): Per-area vocabulary tracking.
        # Group findings by area (using flaw_class as area proxy) and track
        # vocabulary growth per area.  This eliminates the decomposed-dispatch
        # interaction: under decomposition, each model reviews one area per round,
        # so global vocab saturates fast even when individual areas still have
        # novelty.  The stop signal uses area-level saturation instead.
        area_findings: Dict[str, List[Finding]] = {}
        for f in new_findings:
            area_key = str(f.flaw_class)
            area_findings.setdefault(area_key, []).append(f)

        for area_key, a_findings in area_findings.items():
            if area_key not in self._area_vocab:
                self._area_vocab[area_key] = set()
                self._area_vocab_sizes[area_key] = {}
                self._area_vocab_growth[area_key] = {}
                self._area_active_rounds[area_key] = set()

            self._area_active_rounds[area_key].add(round_idx)
            prev_area_size = len(self._area_vocab[area_key])
            for f in a_findings:
                tokens = _tokenize_for_similarity(f.description)
                self._area_vocab[area_key].update(tokens)
            new_area_size = len(self._area_vocab[area_key])
            self._area_vocab_sizes[area_key][round_idx] = new_area_size
            if prev_area_size > 0:
                self._area_vocab_growth[area_key][round_idx] = (
                    (new_area_size - prev_area_size) / prev_area_size
                )
            else:
                self._area_vocab_growth[area_key][round_idx] = 1.0

    def marginal_value(self, round_idx: int) -> float:
        """Compute mu(r) = (Y^(<=r) - Y^(<=r-1)) / c_r.

        Returns:
            Marginal cognitive yield per unit cost. Can be negative if yield decreased.
            Returns inf if c_r = 0 (free information always worth having).
        """
        if round_idx not in self._cumulative_yields:
            raise ValueError(f"No data for round {round_idx}")

        y_r = self._cumulative_yields[round_idx]
        y_prev = self._cumulative_yields.get(round_idx - 1, 0.0)
        c_r = self._round_costs.get(round_idx, 0.0)

        delta_y = y_r - y_prev
        if c_r <= self.config.epsilon_cost:
            return float("inf") if delta_y > 0 else 0.0

        return delta_y / c_r

    def add_model_round(
        self,
        model_id: str,
        round_idx: int,
        findings: Sequence[Finding],
        cost: float,
    ) -> None:
        """Register per-model round data for per-model mu computation.

        Per-model mu eliminates the cost distortion from model attrition
        that broke system-level mu in Exp12 (CC2 confer, approved HARD).

        Args:
            model_id: Model identifier.
            round_idx: Round index r.
            findings: Findings produced by this model in round r.
            cost: Cost of dispatching this model in round r (1.0 per model).
        """
        if model_id not in self._per_model_yields:
            self._per_model_yields[model_id] = {}
            self._per_model_costs[model_id] = {}

        # Cumulative yield for this model
        prev_yield = 0.0
        if round_idx > 0:
            # Find the most recent round this model participated in
            for r in range(round_idx - 1, -1, -1):
                if r in self._per_model_yields[model_id]:
                    prev_yield = self._per_model_yields[model_id][r]
                    break

        if findings:
            h_bar = float(np.mean([f.abstraction_index for f in findings]))
            y = len(findings) * h_bar
        else:
            y = 0.0

        self._per_model_yields[model_id][round_idx] = prev_yield + y
        self._per_model_costs[model_id][round_idx] = cost

    def per_model_mu(self, model_id: str, round_idx: int) -> float:
        """Per-model marginal value: delta_Y_m / c_m.

        Independent of other models' costs, eliminating the attrition
        distortion that broke system-level mu in Exp12.
        """
        if model_id not in self._per_model_yields:
            return 0.0
        if round_idx not in self._per_model_yields[model_id]:
            return 0.0

        y_r = self._per_model_yields[model_id][round_idx]
        # Find previous yield for this model
        y_prev = 0.0
        for r in range(round_idx - 1, -1, -1):
            if r in self._per_model_yields[model_id]:
                y_prev = self._per_model_yields[model_id][r]
                break

        c_r = self._per_model_costs[model_id].get(round_idx, 0.0)
        delta_y = y_r - y_prev

        if c_r <= self.config.epsilon_cost:
            return float("inf") if delta_y > 0 else 0.0
        return delta_y / c_r

    def aggregate_per_model_mu(self, round_idx: int) -> float:
        """Aggregate per-model mu via maximum across active models.

        Max aggregation means the system continues as long as ANY single
        model is still delivering value.  This is the conservative (correct)
        bias: premature stopping is worse than one extra round.

        Returns system-level marginal value if no per-model data exists
        (backward compatibility).
        """
        if not self._per_model_yields:
            # Fallback to system-level mu
            if round_idx in self._cumulative_yields:
                return self.marginal_value(round_idx)
            return 0.0

        mus = []
        for model_id in self._per_model_yields:
            if round_idx in self._per_model_yields[model_id]:
                mu = self.per_model_mu(model_id, round_idx)
                if math.isfinite(mu):
                    mus.append(mu)
        return max(mus) if mus else 0.0

    def smoothed_marginal_value(self, round_idx: int) -> float:
        """Compute smoothed VCR over window W.

        Average mu(r) over the last W rounds to prevent premature stopping
        from a single noisy round. (CC2 contribution.)

        Uses per-model mu aggregation when per-model data is available,
        falling back to system-level mu for backward compatibility.
        """
        W = self.config.smoothing_window
        start = max(0, round_idx - W + 1)
        values = []
        for r in range(start, round_idx + 1):
            if self._per_model_yields:
                # Use per-model aggregation (Exp13a fix)
                mu = self.aggregate_per_model_mu(r)
            elif r in self._cumulative_yields:
                mu = self.marginal_value(r)
            else:
                continue
            if math.isfinite(mu):
                values.append(mu)
        if not values:
            return 0.0
        return float(np.mean(values))

    def novelty_rate(self, round_idx: int) -> float:
        """Fraction of genuinely novel findings in round r.

        Cost-decoupled convergence signal. Unlike mu (= delta_Y / c_r), this
        measures whether we're still finding NEW things, independent of how
        much we spent to find them. When a model is benched, cost drops but
        novelty rate is unaffected — preventing the mu-spike pathology.

        Returns:
            Float in [0, 1]. 1.0 = all findings novel. 0.0 = all duplicates.
        """
        return self._novelty_rates.get(round_idx, 1.0)

    def smoothed_novelty_rate(self, round_idx: int) -> float:
        """Smoothed novelty rate over window W (same as mu smoothing)."""
        W = self.config.smoothing_window
        start = max(0, round_idx - W + 1)
        values = []
        for r in range(start, round_idx + 1):
            if r in self._novelty_rates:
                values.append(self._novelty_rates[r])
        if not values:
            return 1.0
        return float(np.mean(values))

    def vocab_growth_rate(self, round_idx: int) -> float:
        """Vocabulary growth rate at round r.

        Returns the fractional increase in cumulative unique terms.
        1.0 = vocabulary doubled.  0.0 = no new terms.
        Similarity-independent: immune to the Jaccard problem.
        """
        return self._vocab_growth_rates.get(round_idx, 1.0)

    def vocab_saturated(self, round_idx: int) -> bool:
        """Check if vocabulary growth is below threshold for sustained window.

        Phase D (Exp14): When area-level tracking is available, uses per-area
        saturation.  Stop fires only when ALL areas that were active in the
        last W rounds have growth below threshold.  This eliminates the
        decomposed-dispatch × global-vocab interaction from Exp13b.

        Falls back to global vocab tracking when no area data exists (e.g.
        blind round where areas are not yet differentiated).

        NOTE (CC2 confer, Exp13a): The proportional growth rate
        (new - old) / old is a monotonically decreasing function of
        cumulative vocabulary size, even if the absolute number of new
        terms per round is constant.  This means the signal is biased
        toward firing in later rounds.  For 10-20 round experiments
        this is acceptable and even desirable (sublinear growth SHOULD
        trigger stop).  For experiments exceeding ~30 rounds on very
        large artifacts, consider switching to an absolute-count floor
        (e.g., min_new_terms=5) or log-scaled growth rate.
        """
        W = self.config.vocab_sustained_window
        tau = self.config.tau_vocab_growth
        if round_idx < W:
            return False

        # Phase D: Per-area saturation check (preferred).
        if self._area_vocab:
            # Find areas active in the last W rounds.
            recent_range = set(range(round_idx - W + 1, round_idx + 1))
            active_areas = [
                area for area, rounds in self._area_active_rounds.items()
                if rounds & recent_range  # intersection: area was active recently
            ]
            if active_areas:
                # MM_F010: Track whether any area was actually checked.
                # If all areas were skipped (insufficient data), return False.
                any_checked = False
                for area in active_areas:
                    # Check if this area has sustained low growth over its
                    # active rounds within the window.
                    area_rounds_in_window = sorted(
                        self._area_active_rounds[area] & recent_range
                    )
                    # Exp14 fix (CC2 F032, sev 0.70): Under 6-area rotation,
                    # each area appears every ~6 rounds.  W//2 (=2 for W=5)
                    # is unreachable with rotation.  Require at least 1 active
                    # round in the window — if even that one round showed low
                    # growth, the area is saturated from its perspective.
                    if len(area_rounds_in_window) < 1:
                        # Area wasn't active at all in window — skip, not block
                        continue
                    any_checked = True
                    for r in area_rounds_in_window:
                        if self._area_vocab_growth.get(area, {}).get(r, 1.0) >= tau:
                            return False  # This area still has novelty
                if not any_checked:
                    return False  # No area had data — not saturated
                return True  # All checked areas are saturated

        # Fallback: global vocab tracking (pre-Phase D behaviour).
        for r in range(round_idx - W + 1, round_idx + 1):
            if self._vocab_growth_rates.get(r, 1.0) >= tau:
                return False
        return True

    def _abstraction_dropping(self, round_idx: int) -> bool:
        """Check if mean abstraction of new findings is NOT ascending.

        H_bar^(r)_new <= H_bar^(r-1)_new

        Returns True when abstraction is flat or dropping (ok to stop).
        Returns False when abstraction is RISING (models finding higher-level
        issues — don't stop yet).

        This is used as a CONJUNCTIVE factor (founder decision), not a
        disjunctive veto.
        """
        if round_idx < 1:
            return False
        h_curr = self._mean_abstraction_new.get(round_idx, 0.5)
        h_prev = self._mean_abstraction_new.get(round_idx - 1, 0.5)
        return h_curr <= h_prev

    def stop(self, round_idx: int) -> bool:
        """Diminishing returns stop predicate.

        stop(r) iff ((smoothed_mu(r) < tau_mu)
                     OR (smoothed_novelty(r) < tau_novelty_stop)
                     OR vocab_saturated(r))
                    AND (r >= r_min)

        Three independent signals, any sufficient:
        1. Cost-normalized marginal value (mu) — catches efficiency decline
        2. Novelty rate — catches content exhaustion regardless of cost
        3. Vocabulary saturation — similarity-independent exhaustion signal

        Signal 3 was added after Experiment 12, where signals 1 and 2 both
        failed: mu was distorted by model attrition costs, and novelty_rate
        depended on the same Jaccard similarity that broke kappa.  Vocabulary
        saturation measures raw term growth rate, which is immune to both
        failure modes.

        The ascending abstraction guard is CONJUNCTIVE (founder decision §9.1):
        abstraction drop is one factor in the stop decision, not a unilateral veto.

        Note: veto logic (e.g., from convergence detector) is external to this
        predicate. The round progression FSM handles the interaction.
        """
        if round_idx < self.config.r_min:
            return False

        smoothed_mu = self.smoothed_marginal_value(round_idx)
        smoothed_novelty = self.smoothed_novelty_rate(round_idx)

        # Any exhaustion signal sufficient: cost efficiency exhausted OR
        # content exhausted OR vocabulary saturated
        exhaustion = (
            smoothed_mu < self.config.tau_mu
            or smoothed_novelty < self.config.tau_novelty_stop
            or self.vocab_saturated(round_idx)
        )

        # Ascending abstraction guard (CONJUNCTIVE, founder decision §9.1):
        # If abstraction is still rising, models may be finding higher-level
        # issues — don't stop yet even if exhaustion signals fire.
        # _abstraction_dropping returns True when H_bar is decreasing (ok to stop).
        # At round 0-1 the guard is permissive (not enough data to judge).
        abstraction_ok = round_idx <= 1 or self._abstraction_dropping(round_idx)

        return exhaustion and abstraction_ok

    def remaining_value_estimate(self, round_idx: int, remaining_rounds: int) -> float:
        """Estimate remaining value if we continue.

        Y_hat_remaining = sum_{r'=r+1}^{N} mu_hat(r') * c_hat(r')

        Uses exponential decay of mu as a simple forecast.
        """
        if round_idx < 1:
            return float("inf")

        mu_current = self.smoothed_marginal_value(round_idx)
        if not math.isfinite(mu_current) or mu_current <= 0:
            return 0.0

        # Assume mu decays by the ratio of last two rounds
        # MM_F012: Use absolute values for magnitude decay; if mu_prev is negative
        # (yield decreasing), ratio would be negative and produce wrong decay.
        mu_prev = self.smoothed_marginal_value(round_idx - 1) if round_idx >= 1 else mu_current
        if abs(mu_prev) > 1e-10 and math.isfinite(mu_prev):
            decay = abs(mu_current) / abs(mu_prev)
        else:
            decay = 0.5  # default decay

        decay = max(0.01, min(decay, 0.99))  # clamp

        avg_cost = float(np.mean(list(self._round_costs.values()))) if self._round_costs else 1.0

        total = 0.0
        mu = mu_current
        for _ in range(remaining_rounds):
            mu *= decay
            total += mu * avg_cost

        return total

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(config: DynamicManagementConfig) -> bool:
        """K=1: Single model's yield/cost ratio."""
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0, 0.7)
        drd.add_round(1, 7.0, 1.0, 0.6)
        drd.add_round(2, 7.5, 1.0, 0.5)
        # mu should be decreasing
        return drd.marginal_value(1) > drd.marginal_value(2)

    @staticmethod
    def validate_homogeneous(config: DynamicManagementConfig) -> bool:
        """Homogeneous: High overlap -> fast Delta_Y decline -> early stop."""
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 10.0, 3.0, 0.7)
        drd.add_round(1, 11.0, 3.0, 0.6)  # small increment (high overlap)
        drd.add_round(2, 11.2, 3.0, 0.5)  # even smaller
        # With tau_mu = 0.05, mu(2) = 0.2/3.0 ≈ 0.067 > 0.05
        # But the trend is clearly diminishing
        return drd.marginal_value(1) > drd.marginal_value(2)
