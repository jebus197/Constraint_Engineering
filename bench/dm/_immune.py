"""CDSFL Dynamic Management — Detector Health Monitor (Immune Layer).

Extracted from ``bench/dynamic_management.py``.  Contains the
``DetectorHealthMonitor`` class: the Level 2/3 immune response that monitors
convergence detectors for dysfunction and autonomously remediates.

Imports types from ``bench.dm._types``.
"""

from __future__ import annotations

from dataclasses import field
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)

import numpy as np

from bench.dm._types import (
    DetectorDiagnosis,
    DynamicManagementConfig,
)


class DetectorHealthMonitor:
    """Level 2 immune response: monitors convergence detectors for dysfunction.

    Watches kappa, mu, and novelty_rate trajectories. Detects:
    - kappa stuck at 0.0 for N consecutive rounds (similarity too strict)
    - mu increasing when finding count is stable/declining (cost distortion)
    - novelty_rate and mu disagreeing (one says converging, other doesn't)
    - model benching causing metric distortion
    - model failure patterns (consecutive timeouts/errors)
    - findings decline across all models (system exhaustion)
    - vocab saturation (low vocab_growth sustained)

    Autonomous remediation (Exp15): the monitor now tracks remediation outcomes
    and escalates through remediation chains when initial fixes don't work.
    Each pathology has a prioritised chain of fixes. After applying fix N,
    the monitor checks whether the target metric improved within a verification
    window. If not, it escalates to fix N+1. Full audit trail is maintained.

    This is the mathematical immune response the founder identified: the system
    monitors its own monitoring instruments and flags dysfunction.
    """

    def __init__(
        self,
        stuck_window: int = 3,
        mu_increase_window: int = 2,
        config: Optional["DynamicManagementConfig"] = None,
    ) -> None:
        self._config = config
        self._kappa_history: List[float] = []
        self._mu_history: List[float] = []
        self._novelty_history: List[float] = []
        self._finding_counts: List[int] = []
        self._active_model_counts: List[int] = []
        self._diagnoses: List[DetectorDiagnosis] = []
        self._stuck_window = stuck_window
        self._mu_increase_window = mu_increase_window

        # Adaptive immune response state.
        # Like biological adaptive immunity: initial exposure triggers slow
        # response with wide detection window. Repeated exposure to the SAME
        # pathology narrows the window and speeds response.
        # Conversely, if a diagnosis was acknowledged but the pathology resolved
        # naturally, widen the window (reduce sensitivity) to prevent false alarms.
        #
        # Formal:
        #   W_d(r) = W_d(0) · decay^(count_resolved_d)
        #            + growth · count_persistent_d
        #   where:
        #     decay ∈ (0,1) — shrinks window after false alarms
        #     growth > 0    — grows window after persistent true positives
        #     count_resolved_d = pathologies that appeared then disappeared
        #     count_persistent_d = pathologies present for > W rounds
        #
        # This makes the monitor more sensitive to known recurring pathologies
        # and less sensitive to transient fluctuations.
        self._pathology_counts: Dict[str, int] = {}  # detector → consecutive occurrences
        self._resolved_counts: Dict[str, int] = {}   # detector → resolved pathologies
        # Run 6 bug 4: resolution hysteresis counter. Tracks consecutive
        # non-pathological rounds per detector. Resolution only fires when
        # this counter reaches resolution_hysteresis threshold.
        self._resolution_counter: Dict[str, int] = {}
        self._sensitivity_decay: float = 0.8  # multiplicative decay per resolved pathology
        self._sensitivity_growth: float = 0.5  # multiplicative growth per persistent pathology

        # --- Autonomous remediation (Exp15) ---
        # Track per-model failure counts for failure pattern detection.
        self._model_failure_counts: Dict[str, int] = {}  # model → consecutive failures
        self._model_finding_history: Dict[str, List[int]] = {}  # model → per-round finding counts
        self._model_response_times: Dict[str, List[float]] = {}  # model → per-round response times
        self._model_response_chars: Dict[str, List[int]] = {}  # model → per-round response char counts
        self._vocab_growth_history: List[float] = []  # vocab growth rates per round

        # Remediation chain state: tracks which fix in the chain was last
        # applied for each pathology, and the metric value at application time.
        # Schema: {pathology_key: {"chain_idx": int, "applied_round": int,
        #          "metric_at_apply": float, "verification_window": int}}
        self._remediation_state: Dict[str, Dict[str, Any]] = {}

        # Full remediation audit log — never truncated, exported in reports.
        self._remediation_log: List[Dict[str, Any]] = []

        # --- Level 3: Self-adaptive immune layer (Exp15b) ---
        # The immune layer monitors its OWN performance and adjusts its own
        # parameters when it detects calibration failures. This is the second-
        # order feedback loop: detect → remediate → verify → self-assess →
        # self-adjust → repeat.
        #
        # Tracked metrics:
        #   - remediation_success_rate: fraction of applied fixes that improved
        #     their target metric (rolling window)
        #   - false_positive_rate: pathologies detected that resolved WITHOUT
        #     intervention (natural resolution ÷ total detections)
        #   - chain_exhaustion_rate: fraction of pathology encounters where the
        #     entire chain was exhausted without improvement
        #   - step_effectiveness: per-chain-step success counts, used to learn
        #     which steps to skip (simplest-sufficient preference)
        #
        # Self-diagnosis triggers:
        #   - If remediation_success_rate < 0.3 for 3+ rounds → detection is
        #     miscalibrated (too sensitive), widen detection windows
        #   - If false_positive_rate > 0.5 for 3+ rounds → reduce sensitivity
        #   - If chain_exhaustion_rate > 0.5 → chains need extension or
        #     pathology needs reclassification
        #
        # All self-adjustments are logged and P-passed (lightweight: predict
        # expected metric direction, verify after verification_window rounds).

        self._remediation_outcomes: List[Dict[str, Any]] = []  # {success: bool, ...}
        self._false_positive_history: List[Dict[str, Any]] = []  # natural resolutions
        self._chain_exhaustion_history: List[Dict[str, Any]] = []
        # Per chain-step effectiveness: {chain_key: {step_idx: {success: N, fail: N}}}
        self._step_effectiveness: Dict[str, Dict[int, Dict[str, int]]] = {}
        self._self_adjustment_log: List[Dict[str, Any]] = []
        self._self_diagnosis_history: List[Dict[str, Any]] = []
        # Track the original parameter values for bounded self-adjustment
        self._original_stuck_window = stuck_window
        self._original_mu_window = mu_increase_window
        # SY-2 fix (Run 7b): per-trigger-type damping dict, not a single int.
        # Prevents one trigger's adjustment from damping a different trigger.
        self._last_self_adjust_round: Dict[str, int] = {}

    def register_diagnoses(self, diagnoses: list) -> None:
        """Register externally-produced diagnoses (e.g. from record_model_round).

        DC-1/DC-2 fix (Run 5): encapsulates _diagnoses access so callers
        don't reach into the internal list directly. Call this BEFORE
        record_round() to ensure false_positive_rate sees consistent counts.
        """
        self._diagnoses.extend(diagnoses)

    def record_round(
        self,
        kappa: float,
        mu: float,
        novelty_rate: float,
        finding_count: int,
        active_models: int,
    ) -> List[DetectorDiagnosis]:
        """Record one round's detector outputs and check for pathologies.

        Args:
            kappa: Convergence metric from ConvergenceDetector.
            mu: Marginal value from DiminishingReturnsDetector.
            novelty_rate: Fraction of novel findings.
            finding_count: Number of findings this round.
            active_models: Number of active models.

        Returns:
            List of new diagnoses (may be empty if detectors are healthy).
        """
        self._kappa_history.append(kappa)
        self._mu_history.append(mu)
        self._novelty_history.append(novelty_rate)
        self._finding_counts.append(finding_count)
        self._active_model_counts.append(active_models)

        new_diagnoses: List[DetectorDiagnosis] = []

        # Adaptive sensitivity: compute effective window based on history
        # A pathology that has been seen and resolved means we should be
        # LESS sensitive (wider window). A pathology that persists means
        # we should be MORE sensitive (narrower window, but we've already
        # diagnosed it — increase severity instead).
        def effective_window(detector: str, base_window: int) -> int:
            resolved = self._resolved_counts.get(detector, 0)
            persistent = self._pathology_counts.get(detector, 0)
            # AW-1 fix (Run 5, SymPy-verified): decay direction was inverted.
            # resolved → WIDEN window (less sensitive): use decay^(-resolved)
            #   so more resolved issues → larger window.
            # persistent → NARROW window (more sensitive): divide by (1 + growth*persistent)
            #   so more persistent issues → smaller window.
            # AW-2 fix: cap at [2, 2 * base_window] to prevent unbounded growth.
            decay = self._sensitivity_decay
            growth = self._sensitivity_growth
            widen = decay ** (-resolved) if decay > 0 else 1.0  # >1 when resolved>0
            narrow = 1.0 / (1.0 + growth * persistent)          # <1 when persistent>0
            adjusted = int(base_window * widen * narrow)
            return max(2, min(2 * base_window, adjusted))

        # Check 1: kappa stuck at zero
        eff_kappa_window = effective_window("kappa", self._stuck_window)
        if len(self._kappa_history) >= eff_kappa_window:
            recent_kappa = self._kappa_history[-eff_kappa_window:]
            if all(k < 0.01 for k in recent_kappa):
                recent_findings = self._finding_counts[-eff_kappa_window:]
                if sum(recent_findings) > 0:
                    # Adaptive severity: first diagnosis = WARNING, persistent = CRITICAL
                    persistence = self._pathology_counts.get("kappa", 0)
                    self._pathology_counts["kappa"] = persistence + 1
                    self._resolution_counter["kappa"] = 0  # Reset hysteresis
                    severity = "CRITICAL" if persistence >= 1 else "WARNING"
                    # FFF-D: suppression gate — skip diagnosis if remediation active
                    if "kappa_stuck" not in self._remediation_state:
                        diag = DetectorDiagnosis(
                            detector="kappa",
                            pathology=f"kappa stuck at ~0 for {eff_kappa_window} consecutive "
                                      f"rounds despite {sum(recent_findings)} findings produced "
                                      f"(occurrence {persistence + 1})",
                            severity=severity,
                            recommended_action="Similarity function may be too strict for this "
                                               "domain. Consider lowering tau_sim or improving "
                                               "tokenization. Check _finding_similarity() output "
                                               "on actual finding pairs.",
                            evidence={
                                "kappa_values": recent_kappa,
                                "finding_counts": recent_findings,
                                "adaptive_window": eff_kappa_window,
                                "persistence": persistence + 1,
                            },
                            pathology_key="kappa_stuck",
                            round_idx=len(self._kappa_history) - 1,
                        )
                        new_diagnoses.append(diag)
            else:
                # Kappa no longer stuck — require resolution_hysteresis consecutive
                # non-pathological rounds before resolving (Run 6 bug 4 fix).
                if self._pathology_counts.get("kappa", 0) > 0:
                    self._resolution_counter["kappa"] = (
                        self._resolution_counter.get("kappa", 0) + 1
                    )
                    hysteresis = getattr(self._config, "resolution_hysteresis", 2)
                    if self._resolution_counter["kappa"] >= hysteresis:
                        self._resolved_counts["kappa"] = (
                            self._resolved_counts.get("kappa", 0) + 1
                        )
                        if "kappa_stuck" not in self._remediation_state:
                            self.record_natural_resolution("kappa")
                        self._pathology_counts["kappa"] = 0
                        self._resolution_counter["kappa"] = 0

        # Check 2: mu increasing while finding count stable/declining
        eff_mu_window = effective_window("mu", self._mu_increase_window)
        if len(self._mu_history) >= eff_mu_window + 1:
            recent_mu = self._mu_history[-(eff_mu_window + 1):]
            # Exp14 fix (CC2 F027, sev 0.75): multiplying a negative mu by 1.1
            # makes it MORE negative, not less — the comparison would be wrong.
            # Use absolute increase check instead.
            mu_increasing = all(
                recent_mu[i + 1] > recent_mu[i] + abs(recent_mu[i]) * 0.1
                for i in range(len(recent_mu) - 1)
            )
            recent_findings = self._finding_counts[-(eff_mu_window + 1):]
            findings_not_increasing = recent_findings[-1] <= max(recent_findings[:-1])

            if mu_increasing and findings_not_increasing:
                # Check if model count changed (benching distortion)
                recent_models = self._active_model_counts[-(eff_mu_window + 1):]
                model_count_changed = len(set(recent_models)) > 1

                # MU-1 fix (Run 5): increment pathology count (was missing)
                persistence = self._pathology_counts.get("mu", 0)
                self._pathology_counts["mu"] = persistence + 1
                self._resolution_counter["mu"] = 0  # Reset hysteresis

                # FFF-D: suppression gate — skip diagnosis if remediation active
                if "mu_distortion" not in self._remediation_state:
                    diag = DetectorDiagnosis(
                        detector="mu",
                        pathology=f"mu increasing ({recent_mu[0]:.1f} → {recent_mu[-1]:.1f}) "
                                  f"while findings stable/declining ({recent_findings})",
                        severity="WARNING" if not model_count_changed else "CRITICAL",
                        recommended_action=(
                            "Cost distortion from model benching/unbenching. mu = delta_Y / c_r "
                            "is unreliable when active model count changes. Use novelty_rate as "
                            "primary convergence signal."
                            if model_count_changed
                            else "mu may be unreliable — check cost calculation and yield function."
                        ),
                        evidence={
                            "mu_values": recent_mu,
                            "finding_counts": recent_findings,
                            "active_models": recent_models,
                            "model_count_changed": model_count_changed,
                            "persistence": persistence + 1,
                        },
                        # PK-1 fix (Run 5): was missing pathology_key
                        pathology_key="mu_distortion",
                        round_idx=len(self._kappa_history) - 1,
                    )
                    new_diagnoses.append(diag)
            else:
                # MU-3 fix (Run 5): resolve ONLY when mu stops increasing.
                # Run 6 bug 4: require resolution_hysteresis non-pathological rounds.
                if not mu_increasing and self._pathology_counts.get("mu", 0) > 0:
                    self._resolution_counter["mu"] = (
                        self._resolution_counter.get("mu", 0) + 1
                    )
                    hysteresis = getattr(self._config, "resolution_hysteresis", 2)
                    if self._resolution_counter["mu"] >= hysteresis:
                        self._resolved_counts["mu"] = (
                            self._resolved_counts.get("mu", 0) + 1
                        )
                        if "mu_distortion" not in self._remediation_state:
                            self.record_natural_resolution("mu")
                        self._pathology_counts["mu"] = 0
                        self._resolution_counter["mu"] = 0

        # Check 3: novelty_rate and mu disagreeing
        if len(self._novelty_history) >= 2 and len(self._mu_history) >= 2:
            novelty_declining = self._novelty_history[-1] < self._novelty_history[-2] * 0.8
            # MU-2 fix (Run 5): use directional test consistent with Check 2.
            # abs() comparison treated "more negative" as "increasing", which is
            # semantically wrong. Use signed comparison: mu increased if it grew
            # by more than 20% of its absolute value (same logic as Check 2).
            mu_increasing_now = (
                self._mu_history[-1] > self._mu_history[-2]
                + abs(self._mu_history[-2]) * 0.2
            )

            if novelty_declining and mu_increasing_now:
                # FFF-G: full lifecycle for Check 3 (mirroring checks 1, 2, 4, 5)
                persistence = self._pathology_counts.get("mu_novelty_disagree", 0)
                self._pathology_counts["mu_novelty_disagree"] = persistence + 1
                self._resolution_counter["mu_novelty_disagree"] = 0  # Reset hysteresis
                severity = "CRITICAL" if persistence >= 1 else "WARNING"
                # FFF-D: suppression gate — skip diagnosis if remediation active
                if "mu_novelty_disagree" not in self._remediation_state:
                    diag = DetectorDiagnosis(
                        detector="mu+novelty",
                        pathology=f"Novelty declining ({self._novelty_history[-2]:.2f} → "
                                  f"{self._novelty_history[-1]:.2f}) but mu increasing "
                                  f"({self._mu_history[-2]:.1f} → {self._mu_history[-1]:.1f})",
                        severity=severity,
                        recommended_action="Detectors disagree — novelty says converging, mu says "
                                           "not. Trust novelty_rate (cost-independent) over mu "
                                           "(cost-dependent). The stop predicate should use "
                                           "novelty_rate as primary signal.",
                        evidence={
                            "novelty_rate": self._novelty_history[-2:],
                            "mu": self._mu_history[-2:],
                            "persistence": persistence + 1,
                        },
                        pathology_key="mu_novelty_disagree",  # CX_FFF_004
                        round_idx=len(self._kappa_history) - 1,
                    )
                    new_diagnoses.append(diag)
            else:
                # FFF-G: resolution path for Check 3 with hysteresis
                if self._pathology_counts.get("mu_novelty_disagree", 0) > 0:
                    self._resolution_counter["mu_novelty_disagree"] = (
                        self._resolution_counter.get("mu_novelty_disagree", 0) + 1
                    )
                    hysteresis = getattr(self._config, "resolution_hysteresis", 2)
                    if self._resolution_counter["mu_novelty_disagree"] >= hysteresis:
                        self._resolved_counts["mu_novelty_disagree"] = (
                            self._resolved_counts.get("mu_novelty_disagree", 0) + 1
                        )
                        if "mu_novelty_disagree" not in self._remediation_state:
                            self.record_natural_resolution("mu_novelty_disagree")
                        self._pathology_counts["mu_novelty_disagree"] = 0
                        self._resolution_counter["mu_novelty_disagree"] = 0

        # --- Check 4 (Exp15): System-wide findings decline ---
        # If total findings have declined for 3+ consecutive rounds, the models
        # may be exhausting the artifact or getting stuck in unproductive areas.
        if len(self._finding_counts) >= 3:
            recent_3 = self._finding_counts[-3:]
            if all(recent_3[i] < recent_3[i - 1] for i in range(1, len(recent_3))):
                total_decline = recent_3[0] - recent_3[-1]
                # FD-1 fix (Run 5): relative threshold, not fixed constant.
                # At least 30% decline from window start, minimum 3 to filter noise.
                decline_threshold = max(3, int(0.3 * recent_3[0]))
                if total_decline >= decline_threshold:
                    persistence = self._pathology_counts.get("findings_decline", 0)
                    self._pathology_counts["findings_decline"] = persistence + 1
                    self._resolution_counter["findings_decline"] = 0  # Reset hysteresis
                    severity = "CRITICAL" if persistence >= 2 else "WARNING"
                    # FFF-D: suppression gate — skip diagnosis if remediation active
                    if "findings_decline" not in self._remediation_state:
                        diag = DetectorDiagnosis(
                            detector="findings_decline",
                            pathology=(
                                f"System-wide findings declining for 3 rounds "
                                f"({recent_3}), total drop={total_decline}"
                            ),
                            severity=severity,
                            recommended_action=(
                                "Models may be exhausting the current area rotation. "
                                "Consider shuffling area order, adjusting decomposition "
                                "boundaries, or adding cross-area synthesis prompts."
                            ),
                            evidence={
                                "finding_counts": recent_3,
                                "total_decline": total_decline,
                                "occurrence": persistence + 1,
                            },
                            pathology_key="findings_decline",
                            round_idx=len(self._kappa_history) - 1,
                        )
                        new_diagnoses.append(diag)
            else:
                # IM_F035 fix: require actual recovery (latest >= earliest),
                # not just non-decline. A plateau after a crash is not recovery.
                # Run 6 bug 4: require resolution_hysteresis non-pathological rounds.
                if (self._pathology_counts.get("findings_decline", 0) > 0
                        and recent_3[-1] >= recent_3[0]):
                    self._resolution_counter["findings_decline"] = (
                        self._resolution_counter.get("findings_decline", 0) + 1
                    )
                    hysteresis = getattr(self._config, "resolution_hysteresis", 2)
                    if self._resolution_counter["findings_decline"] >= hysteresis:
                        self._resolved_counts["findings_decline"] = (
                            self._resolved_counts.get("findings_decline", 0) + 1
                        )
                        if "findings_decline" not in self._remediation_state:
                            self.record_natural_resolution("findings_decline")
                        self._pathology_counts["findings_decline"] = 0
                        self._resolution_counter["findings_decline"] = 0

        # --- Check 5 (Exp15): Vocab saturation detection ---
        # Wire up the previously dead vocab_saturation handler: if vocab_growth
        # has been below tau_vocab_growth for 3+ consecutive rounds AND finding
        # counts are still positive, the models are using repetitive vocabulary
        # but still producing novel findings.
        # VS-1 fix (Run 5): use configured window, not hardcoded 3
        vs_window = self._config.vocab_sustained_window if self._config else 5
        if len(self._finding_counts) < vs_window:
            pass  # FFF-J: not enough finding_count entries for Check 5
        elif len(self._vocab_growth_history) >= vs_window:
            recent_vg = self._vocab_growth_history[-vs_window:]
            tau_vg = self._config.tau_vocab_growth if self._config else 0.04
            if all(vg < tau_vg for vg in recent_vg):
                recent_fc = self._finding_counts[-vs_window:]
                if sum(recent_fc) > 0:
                    persistence = self._pathology_counts.get("vocab_saturation", 0)
                    self._pathology_counts["vocab_saturation"] = persistence + 1
                    self._resolution_counter["vocab_saturation"] = 0  # Reset hysteresis
                    # FFF-D: suppression gate — skip diagnosis if remediation active
                    if "vocab_saturation" not in self._remediation_state:
                        diag = DetectorDiagnosis(
                            detector="vocab_saturation",
                            pathology=(
                                f"Premature vocab saturation: vocab_growth below "
                                f"{tau_vg:.0%} for {vs_window} rounds "
                                f"({[f'{v:.3f}' for v in recent_vg]}) "
                                f"but {sum(recent_fc)} findings still being produced"
                            ),
                            severity="WARNING",
                            recommended_action=(
                                "Lower tau_vocab_growth or reset vocab tracking window. "
                                "Models are still productive but the vocab growth signal "
                                "would falsely suggest saturation."
                            ),
                            evidence={
                                "vocab_growth_rates": recent_vg,
                                "finding_counts": recent_fc,
                                "occurrence": persistence + 1,
                            },
                            pathology_key="vocab_saturation",
                            round_idx=len(self._kappa_history) - 1,
                        )
                        new_diagnoses.append(diag)
            else:
                # VS-2 fix (Run 5): add resolution path (was missing entirely).
                # Run 6 bug 4: require resolution_hysteresis non-pathological rounds.
                if self._pathology_counts.get("vocab_saturation", 0) > 0:
                    self._resolution_counter["vocab_saturation"] = (
                        self._resolution_counter.get("vocab_saturation", 0) + 1
                    )
                    hysteresis = getattr(self._config, "resolution_hysteresis", 2)
                    if self._resolution_counter["vocab_saturation"] >= hysteresis:
                        self._resolved_counts["vocab_saturation"] = (
                            self._resolved_counts.get("vocab_saturation", 0) + 1
                        )
                        if "vocab_saturation" not in self._remediation_state:
                            self.record_natural_resolution("vocab_saturation")
                        self._pathology_counts["vocab_saturation"] = 0
                        self._resolution_counter["vocab_saturation"] = 0

        # --- Autonomous remediation outcome verification (Exp15) ---
        # After each round, check if previously applied remediations worked.
        verification_results = self._verify_remediation_outcomes()
        for vr in verification_results:
            new_diagnoses.append(vr)  # outcome reports as diagnoses

        # --- Level 3: Self-diagnosis (Exp15b) ---
        # Check the immune layer's own performance and self-adjust if needed.
        self_diags = self.self_diagnose()
        for sd in self_diags:
            new_diagnoses.append(sd)

        # IM_F005 fix: extend AFTER all diagnosis sources collected
        self._diagnoses.extend(new_diagnoses)

        return new_diagnoses

    def record_vocab_growth(self, vocab_growth_rate: float) -> None:
        """Record vocab growth rate for this round (called by manager)."""
        self._vocab_growth_history.append(vocab_growth_rate)

    def record_model_round(
        self,
        model_id: str,
        finding_count: int,
        failed: bool,
        response_time: float = 0.0,
        response_chars: int = 0,
    ) -> List[DetectorDiagnosis]:
        """Track per-model performance for failure pattern detection.

        Args:
            model_id: The model being tracked.
            finding_count: Findings produced this round (0 if failed/timeout).
            failed: Whether the model failed/timed out this round.
            response_time: Seconds taken to produce the response.
            response_chars: Number of characters in the raw response.

        Returns:
            List of DetectorDiagnosis (may be empty if no pathology detected).
        """
        if model_id not in self._model_finding_history:
            self._model_finding_history[model_id] = []
        self._model_finding_history[model_id].append(finding_count)

        if model_id not in self._model_response_times:
            self._model_response_times[model_id] = []
        self._model_response_times[model_id].append(response_time)

        if model_id not in self._model_response_chars:
            self._model_response_chars[model_id] = []
        self._model_response_chars[model_id].append(response_chars)

        results: List[DetectorDiagnosis] = []

        if failed:
            self._model_failure_counts[model_id] = (
                self._model_failure_counts.get(model_id, 0) + 1
            )
        else:
            self._model_failure_counts[model_id] = 0

        # --- Consecutive failure detection (existing) ---
        consecutive = self._model_failure_counts.get(model_id, 0)
        if consecutive >= 2:
            key = f"model_failure_{model_id}"
            persistence = self._pathology_counts.get(key, 0)
            self._pathology_counts[key] = persistence + 1
            severity = "CRITICAL" if consecutive >= 3 else "WARNING"
            diag = DetectorDiagnosis(
                detector="model_failure",
                pathology=(
                    f"{model_id} has failed {consecutive} consecutive rounds"
                ),
                severity=severity,
                recommended_action=(
                    f"Lower decomposition threshold for {model_id}, or "
                    f"increase timeout, or bench and reassign its workload."
                ),
                evidence={
                    "model_id": model_id,
                    "consecutive_failures": consecutive,
                    "occurrence": persistence + 1,
                },
                pathology_key=f"model_failure_{model_id}",
                round_idx=len(self._kappa_history),
            )
            # DC-1 fix (Run 5): do NOT append to self._diagnoses here.
            # The caller consolidates all diagnoses via record_round().
            results.append(diag)

        # --- Parser yield anomaly detection (Exp15 FM4) ---
        # Detects: large response but zero parsed findings → format divergence.
        # Formal: |raw_chars(i)| > τ_chars ∧ φ_i < τ_φ (§2 of appendix).
        tau_chars = 2000  # substantive response threshold
        if response_chars > tau_chars and finding_count == 0 and not failed:
            key = f"parser_yield_{model_id}"
            persistence = self._pathology_counts.get(key, 0)
            self._pathology_counts[key] = persistence + 1
            diag = DetectorDiagnosis(
                detector="parser_yield",
                pathology=(
                    f"{model_id}: {response_chars} chars produced but "
                    f"0 findings parsed (φ=0). Format divergence likely."
                ),
                severity="WARNING" if persistence < 1 else "CRITICAL",
                recommended_action=(
                    f"Re-extract findings from {model_id} response using "
                    f"format-adaptive parser. Check if model uses non-standard "
                    f"finding ID format (e.g. bold markdown vs FINDING_ID prefix)."
                ),
                evidence={
                    "model_id": model_id,
                    "response_chars": response_chars,
                    "finding_count": finding_count,
                    "format_yield": 0.0,
                    "occurrence": persistence + 1,
                },
                pathology_key=f"parser_yield_{model_id}",  # PK-2 fix (Run 5), FFF-B (Run 7b)
                round_idx=len(self._kappa_history),
            )
            results.append(diag)

        # --- Monotonic decline detection (Exp15 FM3) ---
        # Detects: model finding count declining for 3+ consecutive rounds.
        # Indicates the model is entering a low-productivity attractor.
        history = self._model_finding_history.get(model_id, [])
        if len(history) >= 3:
            recent_3 = history[-3:]
            if (recent_3[0] > recent_3[1] > recent_3[2]) and recent_3[0] > 0:
                total_decline = recent_3[0] - recent_3[2]
                if total_decline >= 3:  # not just noise (e.g. 7→5→3)
                    key = f"monotonic_decline_{model_id}"
                    persistence = self._pathology_counts.get(key, 0)
                    self._pathology_counts[key] = persistence + 1
                    self._resolution_counter[key] = 0  # Reset hysteresis
                    diag = DetectorDiagnosis(
                        detector="monotonic_decline",
                        pathology=(
                            f"{model_id}: findings declining monotonically "
                            f"for 3 rounds ({recent_3}), drop={total_decline}"
                        ),
                        severity="WARNING" if persistence < 2 else "CRITICAL",
                        recommended_action=(
                            f"Model {model_id} entering low-productivity attractor. "
                            f"Adjust prompt strategy, shuffle area order, or bench "
                            f"temporarily and reassign workload."
                        ),
                        evidence={
                            "model_id": model_id,
                            "finding_counts": recent_3,
                            "total_decline": total_decline,
                            "occurrence": persistence + 1,
                        },
                        pathology_key=f"monotonic_decline_{model_id}",  # PK-2 fix (Run 5), FFF-B (Run 7b)
                        round_idx=len(self._kappa_history),
                    )
                    results.append(diag)
            else:
                # Decline broken — resolve if previously pathological
                # Run 6 bug 4: require resolution_hysteresis non-pathological rounds.
                key = f"monotonic_decline_{model_id}"
                if self._pathology_counts.get(key, 0) > 0:
                    self._resolution_counter[key] = (
                        self._resolution_counter.get(key, 0) + 1
                    )
                    hysteresis = getattr(self._config, "resolution_hysteresis", 2)
                    if self._resolution_counter[key] >= hysteresis:
                        self._resolved_counts[key] = (
                            self._resolved_counts.get(key, 0) + 1
                        )
                        if key not in self._remediation_state:
                            self.record_natural_resolution(key)
                        self._pathology_counts[key] = 0
                        self._resolution_counter[key] = 0

        # --- Cost-per-finding spike detection (Exp15 FM5) ---
        # Detects: response_time / findings > 2σ of model's historical mean.
        # Indicates efficiency collapse (high compute, low yield).
        times = self._model_response_times.get(model_id, [])
        findings_hist = self._model_finding_history.get(model_id, [])
        if (
            len(times) >= 3
            and response_time > 0
            and finding_count > 0
        ):
            # Compute cost-per-finding for rounds where model produced findings
            cpf_history = []
            for t, f in zip(times[:-1], findings_hist[:-1]):
                if f > 0 and t > 0:
                    cpf_history.append(t / f)

            if len(cpf_history) >= 2:
                current_cpf = response_time / finding_count
                mean_cpf = sum(cpf_history) / len(cpf_history)
                variance = sum((x - mean_cpf) ** 2 for x in cpf_history) / len(cpf_history)
                std_cpf = variance ** 0.5

                if std_cpf > 0 and current_cpf > mean_cpf + 2 * std_cpf:
                    key = f"cpf_spike_{model_id}"
                    persistence = self._pathology_counts.get(key, 0)
                    self._pathology_counts[key] = persistence + 1
                    diag = DetectorDiagnosis(
                        detector="cpf_spike",
                        pathology=(
                            f"{model_id}: cost-per-finding {current_cpf:.1f}s "
                            f"exceeds 2σ (mean={mean_cpf:.1f}s, σ={std_cpf:.1f}s)"
                        ),
                        severity="WARNING",
                        recommended_action=(
                            f"Model {model_id} efficiency collapse: spending "
                            f"{current_cpf:.0f}s per finding vs historical "
                            f"{mean_cpf:.0f}s. Consider reducing prompt complexity, "
                            f"adjusting decomposition, or benching temporarily."
                        ),
                        evidence={
                            "model_id": model_id,
                            "current_cpf": current_cpf,
                            "mean_cpf": mean_cpf,
                            "std_cpf": std_cpf,
                            "threshold": mean_cpf + 2 * std_cpf,
                            "occurrence": persistence + 1,
                        },
                        pathology_key=f"cpf_spike_{model_id}",  # PK-2 fix (Run 5), FFF-B (Run 7b)
                        round_idx=len(self._kappa_history),
                    )
                    results.append(diag)

        return results

    def set_remediation_state(
        self,
        pathology_key: str,
        chain_idx: int,
        applied_round: int,
        metric_at_apply: float,
        target_metric: str,
        verification_window: int = 2,
        chain_length: int = 999,
    ) -> None:
        """Record that a remediation was applied, for outcome verification.

        Args:
            pathology_key: The pathology being remediated (e.g. "kappa_stuck").
            chain_idx: Index in the remediation chain (0 = first fix tried).
            applied_round: Round when the fix was applied.
            metric_at_apply: Value of the target metric when fix was applied.
            target_metric: Name of the metric to check ("kappa", "mu", etc.).
            verification_window: Rounds to wait before checking outcome.
        """
        self._remediation_state[pathology_key] = {
            "chain_idx": chain_idx,
            "applied_round": applied_round,
            "metric_at_apply": metric_at_apply,
            "target_metric": target_metric,
            "verification_window": verification_window,
            "chain_length": chain_length,  # RV-1: for bounds check
        }

    def _verify_remediation_outcomes(self) -> List[DetectorDiagnosis]:
        """Check if previously applied remediations improved their target metrics.

        Called at the end of each record_round(). For each pending remediation,
        checks whether enough rounds have passed and whether the target metric
        improved. Emits outcome diagnoses.
        """
        outcomes: List[DetectorDiagnosis] = []
        current_round = len(self._kappa_history) - 1

        for pathology_key, state in list(self._remediation_state.items()):
            rounds_since = current_round - state["applied_round"]
            if rounds_since < state["verification_window"]:
                continue  # Not enough data yet

            # Get current metric value
            target = state["target_metric"]
            if target == "kappa" and self._kappa_history:
                current_val = self._kappa_history[-1]
            elif target == "mu" and self._mu_history:
                current_val = self._mu_history[-1]
            elif target == "novelty" and self._novelty_history:
                current_val = self._novelty_history[-1]
            elif target == "finding_count" and self._finding_counts:
                current_val = float(self._finding_counts[-1])
            elif target == "vocab_growth" and self._vocab_growth_history:
                current_val = self._vocab_growth_history[-1]
            else:
                continue

            old_val = state["metric_at_apply"]
            chain_idx = state["chain_idx"]

            # RV-2 fix (Run 5): direction-aware improvement check.
            # Default: higher is better (kappa, finding_count).
            # mu: abs decrease (stabilisation) is improvement.
            # vocab_growth: compare against threshold, not raw direction —
            #   the pathology is "below tau_vg", so improvement means
            #   current_val >= tau_vg, not just current_val > old_val.
            if target in ("mu",):
                improved = abs(current_val) < abs(old_val) * 0.95
            elif target == "vocab_growth":
                tau_vg = self._config.tau_vocab_growth if self._config else 0.04
                improved = current_val >= tau_vg
            else:
                improved = current_val > old_val  # kappa, finding_count, novelty

            log_entry = {
                "pathology": pathology_key,
                "chain_idx": chain_idx,
                "applied_round": state["applied_round"],
                "verified_round": current_round,
                "metric": target,
                "value_at_apply": old_val,
                "value_now": current_val,
                "improved": improved,
            }
            self._remediation_log.append(log_entry)

            # Feed Level 3 self-performance tracker
            self.record_remediation_outcome(
                pathology_key, chain_idx, improved, old_val, current_val
            )

            if improved:
                severity = "INFO"
                detail = (
                    f"Remediation SUCCESSFUL for {pathology_key} "
                    f"(chain step {chain_idx}): {target} {old_val:.4f} → "
                    f"{current_val:.4f}"
                )
                # Clear remediation state — fix worked
                del self._remediation_state[pathology_key]
                # RV-3 fix (Run 5): also clear pathology_counts so a
                # future recurrence starts from zero, not the old count.
                # FFF-C fix (Run 7b): use mapped counter key, not chain key.
                self._pathology_counts.pop(self._CHAIN_TO_COUNTER.get(pathology_key, pathology_key), None)
            else:
                severity = "WARNING"
                detail = (
                    f"Remediation INEFFECTIVE for {pathology_key} "
                    f"(chain step {chain_idx}): {target} {old_val:.4f} → "
                    f"{current_val:.4f}. Escalating to next fix in chain."
                )
                # Increment chain index for escalation — the next apply_diagnosis
                # call will try the next fix in the chain.
                # IM_F002: Reset applied_round and metric_at_apply so the
                # verification window for the escalated step starts from NOW,
                # not from the original application point.
                # RV-1 fix (Run 5): bounds-check before incrementing.
                # If we'd exceed the chain length, record exhaustion and
                # clear the state instead of creating a zombie entry.
                next_idx = chain_idx + 1
                chain_len = state.get("chain_length", 999)
                if next_idx >= chain_len:
                    self.record_chain_exhaustion(pathology_key)
                    # RV-4 fix (Run 5): clear stale remediation state AND
                    # pathology counts on exhaustion, so a natural recurrence
                    # starts fresh instead of at the inflated historical count.
                    self._remediation_state.pop(pathology_key, None)
                    # FFF-C fix (Run 7b): use mapped counter key, not chain key.
                    self._pathology_counts.pop(self._CHAIN_TO_COUNTER.get(pathology_key, pathology_key), None)
                else:
                    state["chain_idx"] = next_idx
                    state["applied_round"] = current_round
                    state["metric_at_apply"] = current_val

            diag = DetectorDiagnosis(
                detector="remediation_outcome",
                pathology=detail,
                severity=severity,
                recommended_action=(
                    "No further action needed." if improved
                    else f"Escalate to chain step {chain_idx + 1} for {pathology_key}."
                ),
                evidence=log_entry,
                round_idx=current_round,
            )
            outcomes.append(diag)

        return outcomes

    @property
    def remediation_log(self) -> List[Dict[str, Any]]:
        """Full audit trail of all remediation attempts and outcomes."""
        return list(self._remediation_log)

    # --- Level 3: Self-adaptive immune layer (Exp15b) ---

    def record_remediation_outcome(
        self,
        pathology_key: str,
        chain_idx: int,
        success: bool,
        metric_before: float,
        metric_after: float,
    ) -> None:
        """Record whether a remediation actually worked (for self-assessment).

        Called by _verify_remediation_outcomes when a verdict is reached.
        Feeds the self-performance tracker.
        """
        entry = {
            "pathology": pathology_key,
            "chain_idx": chain_idx,
            "success": success,
            "metric_before": metric_before,
            "metric_after": metric_after,
            "round": len(self._kappa_history) - 1,
        }
        self._remediation_outcomes.append(entry)

        # Update per-step effectiveness
        if pathology_key not in self._step_effectiveness:
            self._step_effectiveness[pathology_key] = {}
        if chain_idx not in self._step_effectiveness[pathology_key]:
            self._step_effectiveness[pathology_key][chain_idx] = {"success": 0, "fail": 0}
        key = "success" if success else "fail"
        self._step_effectiveness[pathology_key][chain_idx][key] += 1

    def record_natural_resolution(self, detector: str) -> None:
        """Record that a pathology resolved without intervention.

        Called when _pathology_counts > 0 transitions to 0 AND no remediation
        was active for that pathology. This is a false positive (or at least
        a self-resolving transient).
        """
        self._false_positive_history.append({
            "detector": detector,
            "round": len(self._kappa_history) - 1,
        })

    def record_chain_exhaustion(self, chain_key: str) -> None:
        """Record that a remediation chain was fully exhausted."""
        self._chain_exhaustion_history.append({
            "chain_key": chain_key,
            "round": len(self._kappa_history) - 1,
        })

    @property
    def remediation_success_rate(self) -> float:
        """Rolling success rate of applied remediations (last 10)."""
        recent = self._remediation_outcomes[-10:]
        if not recent:
            return 1.0  # No data → assume healthy
        return sum(1 for r in recent if r["success"]) / len(recent)

    @property
    def false_positive_rate(self) -> float:
        """Ratio of natural resolutions to total detections (last 10 rounds)."""
        current_round = len(self._kappa_history) - 1
        window = 10
        start_round = max(0, current_round - window)

        # SY-1 fix (Run 7b): use exact windowed counting via round_idx field
        # instead of proportional-tail approximation. DetectorDiagnosis now
        # carries round_idx, so we can filter precisely.
        all_detections = [
            d for d in self._diagnoses
            if hasattr(d, 'evidence') and isinstance(d.evidence, dict)
            and d.detector not in ("remediation_outcome",)
        ]
        windowed_detections = [
            d for d in all_detections
            if d.round_idx >= start_round
        ]
        total_detections = len(windowed_detections)
        natural_resolutions = sum(
            1 for fp in self._false_positive_history
            if fp["round"] >= start_round
        )
        if total_detections == 0:
            return 0.0
        return min(1.0, natural_resolutions / max(1, total_detections))

    @property
    def chain_exhaustion_rate(self) -> float:
        """Fraction of recent pathology encounters that exhausted their chain."""
        recent_outcomes = self._remediation_outcomes[-10:]
        recent_exhaustions = self._chain_exhaustion_history[-5:]
        # SY-3 re-examined: exhaustions and outcomes are from MUTUALLY
        # EXCLUSIVE code paths (record_chain_exhaustion vs
        # record_remediation_outcome), so they ARE additive.
        # SymPy falsified the original "subset" claim.
        total = len(recent_outcomes) + len(recent_exhaustions)
        if total == 0:
            return 0.0
        return len(recent_exhaustions) / max(1, total)

    def recommended_chain_start(self, chain_key: str) -> int:
        """Return the recommended starting step for a chain based on history.

        Simplest-sufficient preference: if step 0 has never succeeded for this
        pathology but step 1 has, skip step 0 next time. This prevents wasting
        rounds on fixes that historically don't work.

        Conservative: requires at least 2 failures before skipping a step.
        """
        if chain_key not in self._step_effectiveness:
            return 0
        steps = self._step_effectiveness[chain_key]
        last_skipped = -1
        for idx in sorted(steps.keys()):
            stats = steps[idx]
            total = stats["success"] + stats["fail"]
            if total >= 2 and stats["fail"] >= 2 and stats["success"] == 0:
                last_skipped = idx
                continue  # Skip this step — historically ineffective
            return idx
        # All known steps were ineffective — start at the next one
        return last_skipped + 1 if last_skipped >= 0 else 0

    # --- FFF-C fix (Run 7b): chain-key to counter-key mapping ---
    # _pathology_counts uses detector-family keys ("kappa", "mu") but
    # remediation chains use pathology keys ("kappa_stuck", "mu_distortion").
    # This mapping bridges the two namespaces.
    _CHAIN_TO_COUNTER: ClassVar[Dict[str, str]] = {
        "kappa_stuck": "kappa",
        "mu_distortion": "mu",
        "findings_decline": "findings_decline",
        "vocab_saturation": "vocab_saturation",
        "mu_novelty_disagree": "mu_novelty_disagree",
    }

    # --- Multi-modular fix classification ---
    # Transforms that affect multiple independent components (models, detection
    # windows, cross-area parameters) require extended P-pass. Single-parameter
    # transforms get the standard lightweight P-pass.
    _MULTI_MODULAR_TRANSFORMS: ClassVar[Set[str]] = {
        "add_synthesis_directive",    # affects per_model_directives for ALL models
    }

    # Self-diagnosis adjustments are always multi-modular because they change
    # detection parameters (stuck_window, mu_window) AND remediation behaviour
    # (sensitivity_decay) simultaneously — cross-module interaction risk.
    _MULTI_MODULAR_SELF_ADJUSTMENTS: ClassVar[Set[str]] = {
        "low_remediation_success_rate",   # adjusts stuck_window + mu_window
        "high_false_positive_rate",       # adjusts sensitivity_decay
    }

    def _is_multi_modular(
        self, chain_key: str, chain_idx: int, transform_name: str
    ) -> bool:
        """Classify whether a fix is multi-modular (requires extended P-pass).

        Multi-modular = the fix changes 3+ independent components with their
        own constraint sets. Per the CLAUDE.md extended P-pass trigger:
        "multi-module work with three or more distinct components that have
        independent constraint sets."

        Returns True if extended P-pass is required.
        """
        if transform_name in self._MULTI_MODULAR_TRANSFORMS:
            return True
        # Self-diagnosis adjustments that touch multiple detection parameters
        # are classified in self_diagnose() directly.
        return False

    def p_pass_remediation(
        self,
        chain_key: str,
        chain_idx: int,
        transform_description: str,
        current_metric: float,
        target_metric: str,
        transform_name: str = "",
        affected_models: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """P-pass a proposed remediation before application.

        Routes to standard P-pass (single-module) or extended P-pass
        (multi-modular) based on fix classification.

        Standard P-pass: 3 checks (history, trend, regression risk).
        Extended P-pass: modular passes per affected component + adversarial
        cross-component pass + iterate toward simplest sufficient solution.

        Args:
            chain_key: Pathology being remediated.
            chain_idx: Step in the remediation chain.
            transform_description: Human-readable description.
            current_metric: Current value of the target metric.
            target_metric: Name of the metric to check.
            transform_name: Internal transform name (for modularity check).
            affected_models: List of model IDs affected (for multi-modular).

        Returns:
            (proceed: bool, rationale: str)
        """
        if self._is_multi_modular(chain_key, chain_idx, transform_name):
            return self._extended_p_pass_remediation(
                chain_key, chain_idx, transform_description,
                current_metric, target_metric,
                affected_models=affected_models or [],
            )
        return self._standard_p_pass_remediation(
            chain_key, chain_idx, transform_description,
            current_metric, target_metric,
        )

    def _standard_p_pass_remediation(
        self,
        chain_key: str,
        chain_idx: int,
        transform_description: str,
        current_metric: float,
        target_metric: str,
    ) -> Tuple[bool, str]:
        """Standard (lightweight) P-pass for single-module fixes.

        Checks:
        1. Has this exact transform failed before for this pathology? (history)
        2. Is the current metric already improving? (intervention may be unnecessary)
        3. Is there a known regression risk? (step effectiveness data)

        Returns:
            (proceed: bool, rationale: str)
        """
        # Check 1: Historical effectiveness
        if chain_key in self._step_effectiveness:
            step_stats = self._step_effectiveness[chain_key].get(chain_idx, {})
            total = step_stats.get("success", 0) + step_stats.get("fail", 0)
            if total >= 3 and step_stats.get("success", 0) == 0:
                return (False, (
                    f"P-pass REJECT: {transform_description} has failed "
                    f"{step_stats['fail']}/{total} times for {chain_key}. "
                    f"Historical evidence against effectiveness."
                ))

        # Check 2: Is the metric already trending in the right direction?
        history = self._get_metric_history(target_metric)
        if len(history) >= 3:
            recent_3 = history[-3:]
            # Run 6 bug 1: flatlined metric at 0.0 bypasses remediation.
            # abs(0) <= abs(0) * 1.05 is always True, so a metric stuck at
            # exactly zero is classified as "improving" and remediation is
            # permanently vetoed. Guard against this explicitly.
            if all(v == 0.0 for v in recent_3):
                # Metric is flatlined at zero — this is NOT improving,
                # it's a dead signal. Do NOT veto remediation.
                pass
            else:
                # For most metrics, increasing is good
                if target_metric in ("mu",):
                    improving = all(
                        abs(recent_3[i]) <= abs(recent_3[i - 1]) * 1.05
                        for i in range(1, len(recent_3))
                    )
                else:
                    improving = all(
                        recent_3[i] >= recent_3[i - 1] * 0.95
                        for i in range(1, len(recent_3))
                    )
                if improving:
                    return (False, (
                    f"P-pass SKIP: {target_metric} already improving "
                    f"({[f'{v:.3f}' for v in recent_3]}). Intervention "
                    f"may be unnecessary — let natural trend continue."
                ))

        # Check 3: Known regression risk from step effectiveness
        if chain_key in self._step_effectiveness:
            step_stats = self._step_effectiveness[chain_key].get(chain_idx, {})
            fail_count = step_stats.get("fail", 0)
            success_count = step_stats.get("success", 0)
            if fail_count > 0 and success_count > 0:
                rate = success_count / (success_count + fail_count)
                if rate < 0.4:
                    return (True, (
                        f"P-pass WARN: {transform_description} has mixed "
                        f"results ({success_count}/{success_count + fail_count} "
                        f"success rate). Proceeding with caution."
                    ))

        return (True, (
            f"P-pass PASS: {transform_description} — no historical "
            f"contraindications."
        ))

    def _extended_p_pass_remediation(
        self,
        chain_key: str,
        chain_idx: int,
        transform_description: str,
        current_metric: float,
        target_metric: str,
        affected_models: Optional[List[str]] = None,
        max_iterations: int = 1,
    ) -> Tuple[bool, str]:
        """Extended P-pass for multi-modular fixes.

        Run 6 bug 3: max_iterations reduced from 3 to 1. No state is
        mutated between iterations (the "simplest-sufficient iteration"
        block only appends to reports, it doesn't change the input to
        the next pass), so the convergence check always triggered on
        iteration 2. The loop was dead code — same input, same output,
        same failure signatures, early stop.

        Follows the extended P-pass protocol from CLAUDE.md:
        1. Modular passes: check each affected component independently
        2. Adversarial pass: check for cross-component contradictions

        The adversarial pass examines the combined effect of the fix across
        all affected modules, looking for:
        - Contradictory parameter movements (one module needs X up, another
          needs X down)
        - Cascade risk (fixing one module destabilises another)
        - Over-specification (fix is more complex than necessary)

        Converges when:
        - All HARD constraints satisfied (no contradictions, no cascade risk)
        - Or max_iterations reached (diminishing returns)

        Args:
            chain_key: Pathology being remediated.
            chain_idx: Step in the remediation chain.
            transform_description: Human-readable description.
            current_metric: Current value of the target metric.
            target_metric: Name of the metric to check.
            affected_models: List of model IDs affected by this fix.
            max_iterations: Maximum P-pass iterations (default 3).

        Returns:
            (proceed: bool, rationale: str) with full pass report.
        """
        pass_reports: List[str] = []
        all_failures: List[str] = []
        models = affected_models or []

        for iteration in range(max_iterations):
            iteration_failures: List[str] = []

            # --- Modular passes: one per affected component ---

            # Module 1: Target metric check (same as standard P-pass check 1+3)
            if chain_key in self._step_effectiveness:
                step_stats = self._step_effectiveness[chain_key].get(chain_idx, {})
                total = step_stats.get("success", 0) + step_stats.get("fail", 0)
                if total >= 3 and step_stats.get("success", 0) == 0:
                    iteration_failures.append(
                        f"Module:target_metric — {transform_description} has "
                        f"failed {step_stats['fail']}/{total} times"
                    )

            # Module 2: Natural trend check (same as standard check 2)
            history = self._get_metric_history(target_metric)
            if len(history) >= 3:
                recent_3 = history[-3:]
                # Run 6 bug 1: flatlined metric at 0.0 guard (same as standard P-pass).
                if all(v == 0.0 for v in recent_3):
                    pass  # Dead signal, not "improving"
                elif target_metric in ("mu",):
                    improving = all(
                        abs(recent_3[i]) <= abs(recent_3[i - 1]) * 1.05
                        for i in range(1, len(recent_3))
                    )
                    if improving:
                        iteration_failures.append(
                            f"Module:trend — {target_metric} already improving "
                            f"({[f'{v:.3f}' for v in recent_3]}), intervention "
                            f"may be counterproductive"
                        )
                else:
                    improving = all(
                        recent_3[i] >= recent_3[i - 1] * 0.95
                        for i in range(1, len(recent_3))
                    )
                    if improving:
                        iteration_failures.append(
                        f"Module:trend — {target_metric} already improving "
                        f"({[f'{v:.3f}' for v in recent_3]}), intervention "
                        f"may be counterproductive"
                    )

            # Module 3: Per-model impact assessment (multi-modular specific)
            # For fixes affecting multiple models, check whether any model
            # has been adversely affected by similar past fixes.
            if models:
                for mid in models:
                    model_history = self._model_finding_history.get(mid, [])
                    if len(model_history) >= 3:
                        recent = model_history[-3:]
                        # If model's finding count has been declining, adding
                        # directives may further suppress output
                        if all(recent[i] < recent[i - 1]
                               for i in range(1, len(recent)) if recent[i - 1] > 0):
                            iteration_failures.append(
                                f"Module:model_{mid} — findings declining "
                                f"({recent}), additional directives may "
                                f"further suppress output"
                            )

            # Module 4: Detection parameter coherence (for self-adjustments)
            # Check that current detection parameters aren't already at
            # bounds or in contradiction with each other
            if self._stuck_window >= self._original_stuck_window * 2:
                iteration_failures.append(
                    f"Module:detection — stuck_window already at maximum "
                    f"({self._stuck_window}), further widening impossible"
                )

            # --- Adversarial pass: cross-component interactions ---
            # This pass examines the combined effect, not individual modules.
            # "Focus on cross-module interactions, shared assumptions, and
            # emergent contradictions that component-level review would miss."

            adversarial_failures: List[str] = []

            # Cross-check 1: Does the fix create contradictory signals?
            # E.g., lowering a threshold to increase sensitivity while
            # simultaneously widening a window to decrease sensitivity.
            if (chain_key in ("findings_decline",)
                    and self._stuck_window > self._original_stuck_window):
                adversarial_failures.append(
                    f"Adversarial:contradiction — adding synthesis directives "
                    f"to compensate for findings decline, but detection window "
                    f"is already widened ({self._stuck_window} > "
                    f"{self._original_stuck_window}). These work against each "
                    f"other: wider window delays detection, synthesis directive "
                    f"attempts to accelerate production."
                )

            # Cross-check 2: Cascade risk — will this fix trigger another
            # pathology? E.g., adding directives to all models increases
            # prompt length, which may push models past decomposition
            # thresholds, causing more decomposed dispatches, which changes
            # the finding distribution.
            if models and len(models) >= 3:
                # Affecting 3+ models simultaneously has cascade risk
                adversarial_failures.append(
                    f"Adversarial:cascade — fix affects {len(models)} models "
                    f"simultaneously. Prompt length increase may trigger "
                    f"decomposition threshold crossings."
                )

            # Cross-check 3: Over-specification — is the fix more complex
            # than necessary? If the pathology has been seen fewer than 3
            # times, a multi-model fix may be premature.
            # FFF-C fix (Run 7b): use _CHAIN_TO_COUNTER mapping instead of
            # fragile .replace() chain (which missed _distortion until Run 6 bug 7).
            pathology_occurrence = self._pathology_counts.get(
                self._CHAIN_TO_COUNTER.get(chain_key, chain_key),
                0,
            )
            if pathology_occurrence < 3 and models and len(models) >= 3:
                adversarial_failures.append(
                    f"Adversarial:over_specification — pathology only observed "
                    f"{pathology_occurrence} times, but fix affects "
                    f"{len(models)} models. Simpler targeted fix may suffice."
                )

            iteration_failures.extend(adversarial_failures)

            # --- Convergence check ---
            pass_report = (
                f"Extended P-pass iteration {iteration + 1}/{max_iterations}: "
                f"{len(iteration_failures)} failures "
                f"({len(adversarial_failures)} adversarial)"
            )
            pass_reports.append(pass_report)
            all_failures.extend(iteration_failures)

            if not iteration_failures:
                # Clean pass — converged
                return (True, (
                    f"Extended P-pass PASS ({iteration + 1} iterations): "
                    f"{transform_description}. "
                    + "; ".join(pass_reports)
                ))

            # Check for diminishing returns: if this iteration found the
            # same failures as the previous one, stop (no new information)
            if iteration > 0:
                prev_count = len(pass_reports) - 1
                # Compare failure signatures
                current_sigs = set(f.split(" — ")[0] for f in iteration_failures)
                prev_failures_for_sig = all_failures[:-len(iteration_failures)]
                prev_sigs = set(f.split(" — ")[0] for f in prev_failures_for_sig) if prev_failures_for_sig else set()
                new_failures = current_sigs - prev_sigs
                if not new_failures:
                    # Two consecutive passes, no new failures — early stop
                    break

            # --- Simplest-sufficient iteration ---
            # If adversarial pass found over-specification, try to simplify.
            # For multi-model fixes: suggest applying to fewer models.
            # This is the "iterate to simplest sufficient" requirement.
            if any("over_specification" in f for f in adversarial_failures):
                # Cannot actually simplify the transform here (that's the
                # caller's job), but we can signal what simplification looks like
                if models and len(models) > 1:
                    # Suggest applying to worst-performing models only
                    worst_models = self._identify_worst_performers(models, 2)
                    if worst_models and len(worst_models) < len(models):
                        pass_reports.append(
                            f"Simplification candidate: apply only to "
                            f"{worst_models} instead of all {len(models)} models"
                        )

        # --- Final verdict ---
        # Separate HARD failures (contradictions, cascade) from SOFT (trend, mixed)
        hard_failures = [f for f in all_failures
                         if f.startswith("Adversarial:contradiction")
                         or f.startswith("Module:target_metric")]
        soft_failures = [f for f in all_failures if f not in hard_failures]

        if hard_failures:
            return (False, (
                f"Extended P-pass REJECT ({len(pass_reports)} iterations, "
                f"{len(hard_failures)} HARD failures): "
                f"{transform_description}. "
                + "; ".join(hard_failures[:3])  # Limit report length
            ))

        # SOFT failures only — proceed with warning
        return (True, (
            f"Extended P-pass WARN ({len(pass_reports)} iterations, "
            f"{len(soft_failures)} SOFT failures): "
            f"{transform_description}. "
            + "; ".join(soft_failures[:3])
        ))

    def _identify_worst_performers(
        self, model_ids: List[str], top_n: int
    ) -> List[str]:
        """Identify the N worst-performing models for targeted remediation.

        Used by extended P-pass to suggest simplest-sufficient fix scope.
        Ranks by: lowest recent finding count, highest failure count.
        """
        scores: List[Tuple[str, float]] = []
        for mid in model_ids:
            history = self._model_finding_history.get(mid, [])
            failures = self._model_failure_counts.get(mid, 0)
            recent_avg = sum(history[-3:]) / max(len(history[-3:]), 1) if history else 0
            # Lower score = worse performer
            score = recent_avg - failures * 5
            scores.append((mid, score))
        scores.sort(key=lambda x: x[1])
        return [mid for mid, _ in scores[:top_n]]

    def _p_pass_self_adjustment(
        self,
        trigger: str,
        adjustments: Dict[str, Tuple[Any, Any]],
        success_rate: float = 0.0,
        max_iterations: int = 3,
    ) -> Tuple[bool, str]:
        """Extended P-pass for immune layer self-adjustments.

        Multi-modular self-adjustments (e.g. changing stuck_window AND
        mu_window together) require the extended protocol:
        1. Modular pass per adjusted parameter
        2. Adversarial pass: cross-parameter contradiction check
        3. Iterate toward simplest sufficient

        Args:
            trigger: What triggered this self-adjustment.
            adjustments: {param_name: (old_value, new_value)}.
            success_rate: Current remediation success rate (context).
            max_iterations: Max P-pass iterations.

        Returns:
            (proceed: bool, rationale: str)
        """
        pass_reports: List[str] = []
        prev_failures: List[str] = []

        for iteration in range(max_iterations):
            failures: List[str] = []

            # --- Modular passes: one per adjusted parameter ---
            for param, (old_val, new_val) in adjustments.items():
                if old_val == new_val:
                    continue  # No change — skip

                # Check: is this parameter already at its bound?
                if param == "stuck_window":
                    if new_val >= self._original_stuck_window * 2:
                        failures.append(
                            f"Module:{param} — at maximum bound "
                            f"({new_val} >= {self._original_stuck_window * 2})"
                        )
                elif param == "mu_window":
                    if new_val >= self._original_mu_window * 2:
                        failures.append(
                            f"Module:{param} — at maximum bound "
                            f"({new_val} >= {self._original_mu_window * 2})"
                        )

                # Check: has this adjustment been tried before and failed?
                past_adjustments = [
                    h for h in self._self_diagnosis_history
                    if h.get("trigger") == trigger
                    and h.get("adjustment", {}).get(param, {}).get("new") == new_val
                ]
                if len(past_adjustments) >= 2:
                    # Same value tried 2+ times — diminishing returns
                    failures.append(
                        f"Module:{param} — value {new_val} tried "
                        f"{len(past_adjustments)} times previously"
                    )

            # --- Adversarial pass: cross-parameter interactions ---
            active_adjustments = {
                k: v for k, v in adjustments.items() if v[0] != v[1]
            }
            if len(active_adjustments) >= 2:
                # Cross-check: are the adjustments working in the same
                # direction? Both widening windows is coherent. One widening
                # and one narrowing would be contradictory.
                directions = {}
                for param, (old_val, new_val) in active_adjustments.items():
                    if isinstance(old_val, (int, float)):
                        directions[param] = "widen" if new_val > old_val else "narrow"

                unique_directions = set(directions.values())
                if len(unique_directions) > 1:
                    failures.append(
                        f"Adversarial:contradiction — parameters moving in "
                        f"opposite directions: {directions}. This creates "
                        f"incoherent detection behaviour."
                    )

                # Cross-check: cumulative window widening may mask real
                # pathologies. If both windows are already above original
                # (i.e. old_val > original), further widening is high-risk.
                all_already_above = True
                for param, (old_val, new_val) in active_adjustments.items():
                    if param == "stuck_window" and old_val <= self._original_stuck_window:
                        all_already_above = False
                    elif param == "mu_window" and old_val <= self._original_mu_window:
                        all_already_above = False
                if all_already_above and len(active_adjustments) >= 2:
                    failures.append(
                        f"Adversarial:cumulative_risk — all detection windows "
                        f"already above original values. Further widening may "
                        f"mask genuine pathologies."
                    )

            pass_report = (
                f"Self-adjustment P-pass iteration {iteration + 1}: "
                f"{len(failures)} failures"
            )
            pass_reports.append(pass_report)

            if not failures:
                return (True, (
                    f"Self-adjustment extended P-pass PASS "
                    f"({iteration + 1} iterations). "
                    + "; ".join(pass_reports)
                ))

            # Early stop: same failure SET as previous iteration
            # IM_F032 fix: compare failure sets, not string reports (which
            # include iteration number and thus can never be equal)
            if iteration > 0 and set(failures) == set(prev_failures):
                break
            prev_failures = list(failures)

        # Verdict: HARD failures (contradictions) reject, SOFT warn
        hard = [f for f in failures if "contradiction" in f]
        if hard:
            return (False, (
                f"Self-adjustment extended P-pass REJECT: "
                + "; ".join(hard)
            ))
        return (True, (
            f"Self-adjustment extended P-pass WARN "
            f"({len(pass_reports)} iterations, {len(failures)} SOFT): "
            + "; ".join(failures[:2])
        ))

    def _get_metric_history(self, metric_name: str) -> List[float]:
        """Get the history list for a named metric."""
        if metric_name == "kappa":
            return self._kappa_history
        elif metric_name == "mu":
            return self._mu_history
        elif metric_name == "novelty":
            return self._novelty_history
        elif metric_name == "finding_count":
            return [float(f) for f in self._finding_counts]
        elif metric_name == "vocab_growth":
            return self._vocab_growth_history
        return []

    def self_diagnose(self) -> List[DetectorDiagnosis]:
        """Level 3 meta-diagnosis: check the immune layer's own performance.

        Called at the end of record_round(). Detects:
        - Low remediation success rate → detection miscalibration
        - High false positive rate → over-sensitive detection windows
        - High chain exhaustion rate → chains need extension

        Applies self-corrections and P-passes them.
        """
        diagnoses: List[DetectorDiagnosis] = []
        current_round = len(self._kappa_history) - 1

        if current_round < 5:
            return diagnoses  # Too early for meaningful self-assessment

        # FFF-E fix (Run 7b): if immune feedback is disabled, self-diagnosis
        # should also be disabled — it feeds the same feedback loop.
        if self._config and not getattr(self._config, 'immune_feedback_enabled', True):
            return diagnoses

        # SD-2 fix: check immune_damping_rounds before self-adjustment.
        # SY-2 fix (Run 7b): per-trigger-type damping — each self-check has
        # its own trigger key so one adjustment doesn't damp unrelated checks.
        damping_rounds = getattr(self._config, 'immune_damping_rounds', 2) if self._config else 2

        # --- Self-check 1: Remediation success rate ---
        # This is a MULTI-MODULAR self-adjustment: it changes stuck_window
        # (kappa detection) AND mu_increase_window (mu detection) — two
        # independent detection modules. Extended P-pass required.
        _trigger_key_1 = "low_remediation_success"
        _last_1 = self._last_self_adjust_round.get(_trigger_key_1, -999)
        success_rate = self.remediation_success_rate
        if len(self._remediation_outcomes) >= 3 and success_rate < 0.3 and current_round - _last_1 >= damping_rounds:
            old_stuck = self._stuck_window
            old_mu = self._mu_increase_window

            max_stuck = self._original_stuck_window * 2
            max_mu = self._original_mu_window * 2

            new_stuck = min(max_stuck, self._stuck_window + 1)
            new_mu = min(max_mu, self._mu_increase_window + 1)

            can_adjust = (new_stuck != old_stuck) or (new_mu != old_mu)
            if not can_adjust:
                # At bounds — can't widen further, defer to human
                diag = DetectorDiagnosis(
                    detector="self_diagnosis",
                    pathology=(
                        f"Immune layer self-assessment: success rate "
                        f"{success_rate:.1%} but detection windows at "
                        f"maximum bounds (stuck={old_stuck}, mu={old_mu})"
                    ),
                    severity="CRITICAL",
                    recommended_action=(
                        "DEFER to human: detection windows at 2× original "
                        "bounds. Manual parameter tuning or chain extension "
                        "needed."
                    ),
                    evidence={
                        "success_rate": success_rate,
                        "stuck_window": old_stuck,
                        "mu_window": old_mu,
                        "bounds": {
                            "stuck_max": max_stuck,
                            "mu_max": max_mu,
                        },
                        "round": current_round,
                    },
                    round_idx=current_round,
                )
                diagnoses.append(diag)
            if can_adjust:
                # Extended P-pass on the self-adjustment before applying.
                # Iterate toward simplest sufficient: try adjusting both,
                # then only one, then neither.
                # SD-3 fix: try single-parameter adjustments before combined
                candidates = []
                if new_stuck != old_stuck and new_mu != old_mu:
                    candidates.append(("stuck_only", new_stuck, old_mu))
                    candidates.append(("mu_only", old_stuck, new_mu))
                    candidates.append(("both", new_stuck, new_mu))
                elif new_stuck != old_stuck:
                    candidates.append(("stuck_only", new_stuck, old_mu))
                else:
                    candidates.append(("mu_only", old_stuck, new_mu))

                applied = False
                for label, cand_stuck, cand_mu in candidates:
                    # Run extended P-pass on this candidate
                    proceed, rationale = self._p_pass_self_adjustment(
                        trigger="low_remediation_success_rate",
                        adjustments={
                            "stuck_window": (old_stuck, cand_stuck),
                            "mu_window": (old_mu, cand_mu),
                        },
                        success_rate=success_rate,
                    )
                    if proceed:
                        if cand_stuck != old_stuck:
                            self._stuck_window = cand_stuck
                        if cand_mu != old_mu:
                            self._mu_increase_window = cand_mu

                        entry = {
                            "trigger": "low_remediation_success_rate",
                            "success_rate": success_rate,
                            "candidate": label,
                            "p_pass_rationale": rationale,
                            "adjustment": {
                                "stuck_window": {"old": old_stuck, "new": cand_stuck},
                                "mu_window": {"old": old_mu, "new": cand_mu},
                            },
                            "round": current_round,
                            "rationale": (
                                f"Remediation success rate {success_rate:.1%} < 30%. "
                                f"Widening detection windows ({label})."
                            ),
                        }
                        self._self_adjustment_log.append(entry)
                        self._self_diagnosis_history.append(entry)
                        self._last_self_adjust_round[_trigger_key_1] = current_round  # SD-2, SY-2

                        diag = DetectorDiagnosis(
                            detector="self_diagnosis",
                            pathology=(
                                f"Immune layer self-assessment: remediation success "
                                f"rate {success_rate:.1%} indicates detection "
                                f"miscalibration"
                            ),
                            severity="WARNING",
                            recommended_action=(
                                f"Self-adjusted ({label}): stuck_window "
                                f"{old_stuck}→{cand_stuck}, mu_window "
                                f"{old_mu}→{cand_mu}. {rationale}"
                            ),
                            evidence=entry,
                            round_idx=current_round,
                        )
                        diagnoses.append(diag)
                        applied = True
                        break  # Simplest sufficient found

                if not applied:
                    # All candidates P-pass rejected — log but don't adjust
                    diag = DetectorDiagnosis(
                        detector="self_diagnosis",
                        pathology=(
                            f"Immune layer self-assessment: success rate "
                            f"{success_rate:.1%} but all self-adjustments "
                            f"rejected by extended P-pass"
                        ),
                        severity="WARNING",
                        recommended_action=(
                            "DEFER to human: immune layer cannot find a safe "
                            "self-adjustment. Manual parameter tuning needed."
                        ),
                        evidence={
                            "success_rate": success_rate,
                            "candidates_tried": len(candidates),
                            "round": current_round,
                        },
                        round_idx=current_round,
                    )
                    diagnoses.append(diag)

        # --- Self-check 2: High false positive rate ---
        # Single-module (sensitivity_decay only) — standard P-pass sufficient.
        _trigger_key_2 = "high_false_positive"
        _last_2 = self._last_self_adjust_round.get(_trigger_key_2, -999)
        fp_rate = self.false_positive_rate
        if len(self._false_positive_history) >= 2 and fp_rate > 0.5 and current_round - _last_2 >= damping_rounds:
            old_decay = self._sensitivity_decay
            new_decay = min(0.95, old_decay + 0.05)

            if new_decay != old_decay:
                # Standard P-pass: check if sensitivity is already improving
                fp_improving = (
                    len(self._self_diagnosis_history) >= 2
                    and any(
                        h.get("trigger") == "high_false_positive_rate"
                        and h.get("false_positive_rate", 1.0) > fp_rate
                        for h in self._self_diagnosis_history[-2:]
                    )
                )
                if fp_improving:
                    # Trend is already improving — skip intervention
                    diag = DetectorDiagnosis(
                        detector="self_diagnosis",
                        pathology=(
                            f"Immune layer: false positive rate {fp_rate:.1%} "
                            f"still > 50% but trending down — skipping "
                            f"further sensitivity reduction"
                        ),
                        severity="INFO",
                        recommended_action="No action — natural trend improving.",
                        evidence={"fp_rate": fp_rate, "round": current_round},
                        round_idx=current_round,
                    )
                    diagnoses.append(diag)
                else:
                    # FFF-F: wire actual P-pass for self-check 2 (mirrors self-check 1)
                    proceed, rationale = self._p_pass_self_adjustment(
                        trigger="high_false_positive_rate",
                        adjustments={
                            "sensitivity_decay": (old_decay, new_decay),
                        },
                        success_rate=self.remediation_success_rate,
                    )
                    if not proceed:
                        # P-pass rejected — skip adjustment
                        diag = DetectorDiagnosis(
                            detector="self_diagnosis",
                            pathology=(
                                f"Immune layer: false positive rate {fp_rate:.1%} "
                                f"but self-adjustment rejected by P-pass"
                            ),
                            severity="INFO",
                            recommended_action=rationale,
                            evidence={"fp_rate": fp_rate, "round": current_round},
                            round_idx=current_round,
                        )
                        diagnoses.append(diag)
                    else:
                        self._sensitivity_decay = new_decay
                        self._last_self_adjust_round[_trigger_key_2] = current_round  # SD-2, SY-2
                        entry = {
                            "trigger": "high_false_positive_rate",
                            "false_positive_rate": fp_rate,
                            "adjustment": {
                                "sensitivity_decay": {"old": old_decay, "new": new_decay},
                            },
                            "round": current_round,
                            "rationale": (
                                f"False positive rate {fp_rate:.1%} > 50%. "
                                f"Reducing detection sensitivity "
                                f"(decay {old_decay}→{new_decay})."
                            ),
                        }
                        self._self_adjustment_log.append(entry)
                        self._self_diagnosis_history.append(entry)

                        diag = DetectorDiagnosis(
                            detector="self_diagnosis",
                            pathology=(
                                f"Immune layer self-assessment: false positive rate "
                                f"{fp_rate:.1%} indicates over-sensitive detection"
                            ),
                            severity="WARNING",
                            recommended_action=(
                                f"Self-adjusted: sensitivity_decay "
                                f"{old_decay}→{new_decay}. {rationale}"
                            ),
                            evidence=entry,
                            round_idx=current_round,
                        )
                        diagnoses.append(diag)

        # --- Self-check 3: Chain exhaustion rate ---
        _trigger_key_3 = "chain_exhaustion"
        _last_3 = self._last_self_adjust_round.get(_trigger_key_3, -999)
        exhaust_rate = self.chain_exhaustion_rate
        if len(self._chain_exhaustion_history) >= 2 and exhaust_rate > 0.5 and current_round - _last_3 >= damping_rounds:
            diag = DetectorDiagnosis(
                detector="self_diagnosis",
                pathology=(
                    f"Immune layer self-assessment: chain exhaustion rate "
                    f"{exhaust_rate:.1%} — remediation chains too short "
                    f"or pathologies need reclassification"
                ),
                severity="CRITICAL",
                recommended_action=(
                    "DEFER to human: extend remediation chains or redefine "
                    "pathology classification. The immune layer cannot "
                    "self-generate new chain steps."
                ),
                evidence={
                    "exhaustion_rate": exhaust_rate,
                    "recent_exhaustions": self._chain_exhaustion_history[-5:],
                    "round": current_round,
                },
                round_idx=current_round,
            )
            diagnoses.append(diag)

        return diagnoses

    @property
    def self_adjustment_log(self) -> List[Dict[str, Any]]:
        """Full audit trail of self-adjustments to immune layer parameters."""
        return list(self._self_adjustment_log)

    @property
    def self_diagnosis_summary(self) -> Dict[str, Any]:
        """Summary of immune layer self-performance metrics."""
        return {
            "remediation_success_rate": self.remediation_success_rate,
            "false_positive_rate": self.false_positive_rate,
            "chain_exhaustion_rate": self.chain_exhaustion_rate,
            "total_remediations": len(self._remediation_outcomes),
            "total_false_positives": len(self._false_positive_history),
            "total_chain_exhaustions": len(self._chain_exhaustion_history),
            "self_adjustments": len(self._self_adjustment_log),
            "step_effectiveness": {
                k: {str(idx): stats for idx, stats in v.items()}
                for k, v in self._step_effectiveness.items()
            },
        }

    # --- Phase E (Exp14): Dispatch health monitoring ---
    # Three new pathology types for operational health, not just detector health.

    def check_dispatch_health(
        self,
        dispatch_blocks: Dict[str, List[int]],
        dispatch_successes: Dict[str, List[int]],
        verification_rates: Dict[str, List[float]],
        round_idx: int,
    ) -> List[DetectorDiagnosis]:
        """Check for dispatch and verification pathologies.

        Called after each round by DynamicManager.  Detects:
        - Dispatch false positive: model blocked then succeeded via decomposition
        - Verification miscalibration: model's self-verification diverges from peers
        - Cross-model verification contradiction: model reports FALSE on finding
          corroborated TRUE by peers (requires finding-level data, handled separately)

        Args:
            dispatch_blocks: model_id → list of rounds where model was blocked.
            dispatch_successes: model_id → list of rounds where model succeeded
                after being blocked in a prior round.
            verification_rates: model_id → list of per-round verification rates.
            round_idx: Current round index.

        Returns:
            List of new diagnoses (may be empty).
        """
        new_diagnoses: List[DetectorDiagnosis] = []

        # Pathology 4: Dispatch false positive.
        # A model was blocked in round R but succeeded in round R+1 via decomposition.
        for model_id, blocks in dispatch_blocks.items():
            successes = dispatch_successes.get(model_id, [])
            for block_round in blocks:
                if any(s > block_round for s in successes):
                    # Already diagnosed this block?
                    key = f"dispatch_fp_{model_id}_{block_round}"
                    if key not in self._pathology_counts:
                        self._pathology_counts[key] = 1
                        diag = DetectorDiagnosis(
                            detector="dispatch",
                            pathology=(
                                f"Dispatch false positive: {model_id} blocked "
                                f"at round {block_round} but succeeded later "
                                f"via decomposition"
                            ),
                            severity="WARNING",
                            recommended_action=(
                                f"Pre-decompose {model_id} in future blind rounds "
                                f"to prevent false-positive blocking."
                            ),
                            evidence={
                                "model_id": model_id,
                                "blocked_round": block_round,
                                "success_rounds": [s for s in successes if s > block_round],
                            },
                            pathology_key="dispatch_false_positive",
                            round_idx=round_idx,
                        )
                        new_diagnoses.append(diag)

        # Pathology 5: Verification miscalibration.
        # A model's mean verification rate is >2σ below the population mean.
        all_rates: List[float] = []
        model_means: Dict[str, float] = {}
        for model_id, rates in verification_rates.items():
            if rates:
                m = sum(rates) / len(rates)
                model_means[model_id] = m
                all_rates.extend(rates)

        if len(model_means) >= 3 and all_rates:
            # IM_F009: Compute std from model means, not individual observations.
            # Using individual observations biases pop_std toward long-running
            # models and compares a mean against an observation-level std.
            means_list = list(model_means.values())
            pop_mean = sum(means_list) / len(means_list)
            pop_std = (sum((m - pop_mean) ** 2 for m in means_list) / len(means_list)) ** 0.5
            n_models = len(model_means)
            for model_id, m in model_means.items():
                # VM-1 fix: adaptive threshold for small populations.
                # For N < 5 models, z-scores are unreliable (Samuelson bound
                # max|z| = sqrt(N-1)), so use direct comparison instead.
                flagged = False
                z_score = 0.0
                if n_models < 5:
                    # Direct comparison: flag if below 70% of population mean
                    flagged = m < pop_mean * 0.7
                    if pop_std > 0.01:
                        z_score = (m - pop_mean) / pop_std
                else:
                    if pop_std > 0.01:
                        z_score = (m - pop_mean) / pop_std
                        flagged = z_score < -1.2
                if flagged:
                    # Check if already diagnosed
                    key = f"verif_miscal_{model_id}"
                    persistence = self._pathology_counts.get(key, 0)
                    self._pathology_counts[key] = persistence + 1
                    severity = "CRITICAL" if persistence >= 1 else "WARNING"

                    diag = DetectorDiagnosis(
                        detector="verification",
                        pathology=(
                            f"Verification miscalibration: {model_id} mean "
                            f"verification rate {m:.2f} is {abs(z_score):.1f}σ "
                            f"below population mean {pop_mean:.2f}"
                        ),
                        severity=severity,
                        recommended_action=(
                            f"Flag VERIFIED field for {model_id} as unreliable. "
                            f"Add per-model directive to re-examine verification."
                        ),
                        pathology_key="verification_miscalibration",
                        round_idx=round_idx,
                        evidence={
                            "model_id": model_id,
                            "model_mean": m,
                            "population_mean": pop_mean,
                            "population_std": pop_std,
                            "z_score": z_score,
                            "occurrence": persistence + 1,
                        },
                    )
                    new_diagnoses.append(diag)
                else:
                    # VM-2 fix: clear pathology count when model recovers
                    # FFF-I: use resolution_counter + hysteresis instead of immediate deletion
                    key = f"verif_miscal_{model_id}"
                    if self._pathology_counts.get(key, 0) > 0:
                        self._resolution_counter[key] = (
                            self._resolution_counter.get(key, 0) + 1
                        )
                        hysteresis = getattr(self._config, "resolution_hysteresis", 2)
                        if self._resolution_counter.get(key, 0) >= hysteresis:
                            self._pathology_counts[key] = 0
                            self._resolution_counter[key] = 0

        self._diagnoses.extend(new_diagnoses)
        return new_diagnoses

    @property
    def all_diagnoses(self) -> List[DetectorDiagnosis]:
        """All diagnoses emitted so far."""
        return list(self._diagnoses)

    @property
    def has_critical(self) -> bool:
        """Whether any CRITICAL diagnosis has been emitted."""
        return any(d.severity == "CRITICAL" for d in self._diagnoses)
