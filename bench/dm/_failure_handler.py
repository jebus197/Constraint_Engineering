"""CDSFL Dynamic Management — Failure Handling & Correlated Failure Model.

Extracted from ``bench/dynamic_management.py``.  Contains:

- ``FailureHandler``: typed failure detection with priority, recovery policy,
  and PM abort (Area 6 of the management layer).
- ``CorrelatedFailureModel``: shared vulnerability model for correlated
  failures across models (Codex timeout addition).

Imports types from ``bench.dm._types``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Callable,
    Dict,
    FrozenSet,
    List,
    Optional,
    Sequence,
    Set,
)

import numpy as np

from bench.dm._types import (
    CapabilityFingerprint,
    DynamicManagementConfig,
    FailureRecord,
    FailureType,
    ManagerEvent,
    ManagerEventType,
    ModelResponse,
    ModelSpec,
    RecoveryAction,
    Role,
)


class FailureHandler:
    """Typed failure detection with priority, recovery policy, and PM abort.

    Implements the merged formulation from §7 of the converged plan:
    - Five failure types: EMPTY, TIMEOUT, MALFORMED, FORMAT, UNDERPERFORM
    - Priority ordering (first match wins)
    - Recovery policy table with escalation on repetition
    - PM failure -> ABORT (HARD, follows from C3)
    - Persistence window for underperformance (ChatGPT contribution)
    - Cascade guard for reallocation depth (CC2 contribution)

    Example::

        fh = FailureHandler(
            models=[m1, m2, m3],
            role_map={"m1": Role.PM, "m2": Role.COL, "m3": Role.PAR},
            config=DynamicManagementConfig(),
        )
        resp = ModelResponse("m3", 1, "", 10.0, parseable=True, format_compliant=True)
        failure_type = fh.detect_failure(resp)
        if failure_type:
            action = fh.get_recovery(resp.model_id, resp.round_idx, failure_type)
    """

    def __init__(
        self,
        models: Sequence[ModelSpec],
        role_map: Dict[str, Role],
        config: DynamicManagementConfig,
        event_callback: Optional[Callable[["ManagerEvent"], None]] = None,
    ) -> None:
        self.models = {m.model_id: m for m in models}
        self.role_map = role_map
        self.config = config
        self.event_callback = event_callback
        # Failure history: Phi(m) = {(r, type)}
        self._failure_history: Dict[str, List[FailureRecord]] = {
            m.model_id: [] for m in models
        }
        # Active model set
        self._active_models: Set[str] = {m.model_id for m in models}
        # Performance history for underperformance detection
        self._perf_history: Dict[str, List[float]] = {
            m.model_id: [] for m in models
        }
        # Reallocation depth tracker (cascade guard)
        self._realloc_depth: Dict[str, int] = {}  # task_id -> depth
        # FH-2 fix (Run 5): dedup set for detect_failure — prevents duplicate
        # deliveries from inflating perf_history. Initialised in __init__,
        # not lazily via hasattr.
        self._perf_rounds_seen: set = set()

    def _expected_performance(self, model_id: str) -> float:
        """Compute expected(m, r) = b_rho(m) . q_m.

        Performance baseline relative to model's fingerprint and role.
        """
        model = self.models.get(model_id)
        if model is None:
            return 0.0
        role = self.role_map.get(model_id, Role.PAR)
        b = self.config.get_baseline(role)
        q = model.fingerprint.as_array()
        return float(np.dot(b, q))

    def _performance_metric(self, response: ModelResponse) -> float:
        """Compute perf(m, r) = (finding_count * mean_abstraction) / expected(m, r).

        Returns ratio >= 0. Values < 1 indicate underperformance.
        """
        expected = self._expected_performance(response.model_id)
        if expected <= 0:
            return 1.0  # Cannot assess, assume adequate
        actual = response.finding_count * response.mean_abstraction
        return actual / expected

    def _timeout_threshold(self, model_id: str) -> float:
        """Compute Theta_r = eta * tau_m (timeout threshold for model m)."""
        model = self.models.get(model_id)
        if model is None:
            return self.config.timeout_multiplier * 300.0
        return self.config.timeout_multiplier * model.tau

    def detect_failure(self, response: ModelResponse) -> Optional[FailureType]:
        """Detect failure type from a model response. First match wins (priority order).

        Args:
            response: The model's response to evaluate.

        Returns:
            FailureType if a failure is detected, None otherwise.
        """
        # Priority 1: EMPTY
        if not response.content or len(response.content.strip()) == 0:
            self._emit_event(
                ManagerEvent(
                    event_type=ManagerEventType.EMPTY,
                    model_id=response.model_id,
                    round_idx=response.round_idx,
                    detail="Empty or null response",
                )
            )
            return FailureType.EMPTY

        # Priority 2: TIMEOUT
        threshold = self._timeout_threshold(response.model_id)
        if response.response_time > threshold:
            self._emit_event(
                ManagerEvent(
                    event_type=ManagerEventType.TIMEOUT,
                    model_id=response.model_id,
                    round_idx=response.round_idx,
                    detail=f"Response time {response.response_time:.1f}s > threshold {threshold:.1f}s",
                )
            )
            return FailureType.TIMEOUT

        # Priority 3: MALFORMED
        if not response.parseable:
            self._emit_event(
                ManagerEvent(
                    event_type=ManagerEventType.MALFORMED,
                    model_id=response.model_id,
                    round_idx=response.round_idx,
                    detail="Response not parseable",
                )
            )
            return FailureType.MALFORMED

        # Priority 4: FORMAT
        if not response.format_compliant:
            # F004 fix: use FORMAT_VIOLATION instead of MALFORMED for
            # semantic correctness — FORMAT != MALFORMED.
            self._emit_event(
                ManagerEvent(
                    event_type=ManagerEventType.FORMAT_VIOLATION,
                    model_id=response.model_id,
                    round_idx=response.round_idx,
                    detail="Response parseable but not format-compliant",
                )
            )
            return FailureType.FORMAT

        # Priority 5: UNDERPERFORM (with persistence window)
        perf = self._performance_metric(response)
        # FH-2 fix (Run 5): deduplicate by round to prevent inflation
        # from repeated calls with the same response.
        key = (response.model_id, response.round_idx)
        if key not in self._perf_rounds_seen:
            self._perf_rounds_seen.add(key)
            # Run 6 bug 9: prune entries older than 2× persistence_window
            # to prevent unbounded memory growth over long runs.
            max_seen = self.config.persistence_window * 2 * len(self.models)
            if len(self._perf_rounds_seen) > max_seen:
                # Keep only the most recent entries
                sorted_keys = sorted(self._perf_rounds_seen, key=lambda k: k[1])
                self._perf_rounds_seen = set(sorted_keys[len(sorted_keys) - max_seen:])
            self._perf_history.setdefault(response.model_id, []).append(perf)

        h = self.config.persistence_window
        recent_perfs = self._perf_history[response.model_id][-h:]
        if len(recent_perfs) >= h:
            underperform_count = sum(
                1 for p in recent_perfs if p < self.config.theta_under
            )
            if underperform_count / len(recent_perfs) >= self.config.eta_underperform:
                # F006 fix: emit event for UNDERPERFORM (was the only failure
                # type that didn't emit a ManagerEvent).
                self._emit_event(
                    ManagerEvent(
                        event_type=ManagerEventType.UNDERPERFORM,
                        model_id=response.model_id,
                        round_idx=response.round_idx,
                        detail=(
                            f"Underperformance: {underperform_count}/{len(recent_perfs)} "
                            f"recent rounds below threshold {self.config.theta_under}"
                        ),
                    )
                )
                return FailureType.UNDERPERFORM

        return None

    def get_recovery(
        self,
        model_id: str,
        round_idx: int,
        failure_type: FailureType,
    ) -> RecoveryAction:
        """Determine recovery action based on failure type and history.

        Implements the recovery policy table from §7.2 of the converged plan.
        PM failure with transport/protocol type after retry -> ABORT (HARD).

        Args:
            model_id: The failing model.
            round_idx: Current round.
            failure_type: Detected failure type.

        Returns:
            RecoveryAction to take.
        """
        is_pm = self.role_map.get(model_id) == Role.PM
        history = self._failure_history.get(model_id, [])

        # FH-6 fix (Run 5): window to recent rounds, not lifetime.
        # Use persistence_window for consistency with UNDERPERFORM detection.
        window = self.config.persistence_window
        recent_history = [
            r for r in history
            if r.round_idx >= max(0, round_idx - window)
        ]
        same_type_count = sum(
            1 for r in recent_history if r.failure_type == failure_type
        )
        # FH-1 fix (Run 5): include current failure in count (off-by-one).
        # History hasn't been appended yet, so +1 for the current occurrence.
        repeated = (same_type_count + 1) >= self.config.n_fail

        # PM failure handling (HARD constraint)
        # FH-5 fix (Run 5): include FORMAT in PM hard-failure set.
        # FORMAT is a protocol-level failure — PM must be reliable.
        if is_pm and failure_type in (
            FailureType.EMPTY,
            FailureType.TIMEOUT,
            FailureType.MALFORMED,
            FailureType.FORMAT,
        ):
            if repeated:
                action = RecoveryAction.ABORT
            else:
                action = RecoveryAction.RETRY
            self._record_failure(model_id, round_idx, failure_type, action)
            return action

        # Standard recovery policy table
        if failure_type == FailureType.EMPTY:
            # 2026-05-22 (founder-directed): EMPTY never produces EXCLUDE.
            # Excluding a model from subsequent rounds is benching, which
            # feedback_no_benching.md explicitly forbids ("no model misses
            # a round"). The in-round secondary route fallback in
            # _dispatch_single_model handles the immediate per-turn
            # response; FailureHandler here just records the EMPTY event
            # and returns RETRY so the model keeps participating. The
            # persistent-empty HIL signal is raised by the runner's
            # `_persistent_empty_flags` accumulator (turns where BOTH
            # primary and secondary routes failed), not by EXCLUDE here.
            action = RecoveryAction.RETRY
        elif failure_type == FailureType.TIMEOUT:
            action = (
                RecoveryAction.EXCLUDE if repeated else RecoveryAction.RETRY_EXTENDED
            )
        elif failure_type == FailureType.MALFORMED:
            action = (
                RecoveryAction.EXCLUDE if repeated else RecoveryAction.RETRY_CLARIFIED
            )
        elif failure_type == FailureType.FORMAT:
            # IM_F030 fix: first occurrence=RETRY_CLARIFIED (lenient),
            # repeated=DEGRADE (escalate). Was previously inverted.
            action = (
                RecoveryAction.DEGRADE if repeated else RecoveryAction.RETRY_CLARIFIED
            )
        elif failure_type == FailureType.UNDERPERFORM:
            # FH-3 fix (Run 5): LOG_ONLY violates "catch-and-log is NOT handling".
            # Non-repeated: RETRY (give model another chance with feedback).
            # Repeated: DOWNGRADE_ROLE (same as before).
            action = (
                RecoveryAction.DOWNGRADE_ROLE if repeated else RecoveryAction.RETRY
            )
        else:
            # FH-3 fix (Run 5): unknown failure types should not silently
            # map to LOG_ONLY. Use RETRY as a safe default with escalation path.
            action = RecoveryAction.RETRY

        self._record_failure(model_id, round_idx, failure_type, action)

        # Execute exclusion if needed
        if action == RecoveryAction.EXCLUDE:
            self._active_models.discard(model_id)
        # IM_F008: Execute role downgrade — update role_map so subsequent
        # _expected_performance() calls use the correct baseline vector.
        elif action == RecoveryAction.DOWNGRADE_ROLE:
            current_role = self.role_map.get(model_id)
            if current_role == Role.COL:
                self.role_map[model_id] = Role.PAR
            elif current_role == Role.PAR:
                # Run 6 bug 6: PAR has no lower role. Escalate to EXCLUDE
                # instead of silently doing nothing.
                self._active_models.discard(model_id)
                action = RecoveryAction.EXCLUDE

        return action

    def _record_failure(
        self,
        model_id: str,
        round_idx: int,
        failure_type: FailureType,
        action: RecoveryAction,
    ) -> None:
        """Record a failure in the history.

        FH-1 fix (Run 5): idempotent — if a record for the same
        (model_id, round_idx, failure_type) already exists, skip.
        Network retries can call get_recovery() twice for the same failure.
        """
        history = self._failure_history.get(model_id, [])
        for existing in history:
            if (existing.round_idx == round_idx
                    and existing.failure_type == failure_type):
                return  # already recorded — idempotent
        record = FailureRecord(
            model_id=model_id,
            round_idx=round_idx,
            failure_type=failure_type,
            recovery_action=action,
        )
        self._failure_history.setdefault(model_id, []).append(record)

    def _emit_event(self, event: "ManagerEvent") -> None:
        """Emit a real-time event to the PM callback if registered."""
        if self.event_callback is not None:
            self.event_callback(event)

    def should_abort(self) -> bool:
        """Check abort condition: |M_active| < K_min.

        If only PM survives, framework degrades to single-model mode.
        If PM is not active, abort.
        """
        pm_id = None
        for mid, role in self.role_map.items():
            if role == Role.PM:
                pm_id = mid
                break

        if pm_id is not None and pm_id not in self._active_models:
            return True

        return len(self._active_models) < self.config.k_min

    @property
    def active_models(self) -> Set[str]:
        """Return the current active model set M_active^(r)."""
        return set(self._active_models)

    def get_failure_history(self, model_id: str) -> List[FailureRecord]:
        """Return Phi(m) = failure history for model m."""
        return list(self._failure_history.get(model_id, []))

    def check_reallocation_depth(self, task_id: str) -> bool:
        """Check cascade guard: whether reallocation depth is within limit.

        Returns True if reallocation is allowed, False if max depth reached.
        (CC2 contribution: max_realloc_depth.)
        """
        depth = self._realloc_depth.get(task_id, 0)
        return depth < self.config.max_realloc_depth

    def record_reallocation(self, task_id: str) -> None:
        """Increment reallocation depth for a task."""
        self._realloc_depth[task_id] = self._realloc_depth.get(task_id, 0) + 1

    def reset_round_state(self) -> None:
        """Reset per-round state at round boundaries.

        FH-7 fix (Run 5): realloc_depth was never reset, permanently
        blocking reallocation after hitting max depth once.
        """
        self._realloc_depth.clear()

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(config: DynamicManagementConfig) -> bool:
        """K=1: PM failure -> ABORT. No REALLOCATE possible."""
        m = ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7))
        fh = FailureHandler([m], {"m1": Role.PM}, config)
        # First failure: RETRY
        action1 = fh.get_recovery("m1", 0, FailureType.TIMEOUT)
        assert action1 == RecoveryAction.RETRY
        # Second failure: ABORT (repeated)
        action2 = fh.get_recovery("m1", 0, FailureType.TIMEOUT)
        # n_fail default is 2, so after 2 records of same type, repeated=True
        # First call records 1, second call sees 1 in history -> same_type_count=1
        # which is < n_fail=2, so not repeated yet. Third call would be repeated.
        action3 = fh.get_recovery("m1", 1, FailureType.TIMEOUT)
        assert action3 == RecoveryAction.ABORT
        return True

    @staticmethod
    def validate_no_failures(config: DynamicManagementConfig) -> bool:
        """No failures: phi = false for all m,r. Layer is transparent."""
        models = [
            ModelSpec(f"m{i}", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7))
            for i in range(3)
        ]
        role_map = {"m0": Role.PM, "m1": Role.COL, "m2": Role.PAR}
        fh = FailureHandler(models, role_map, config)
        # Normal response — no failure
        resp = ModelResponse("m2", 0, "valid content", 10.0, True, True, 5, 0.6)
        failure = fh.detect_failure(resp)
        return failure is None


# ═══════════════════════════════════════════════════════════════════════════════
# CORRELATED FAILURE MODEL (Codex timeout addition)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class CorrelatedFailureModel:
    """Shared vulnerability model for correlated failures across models.

    Adds a vulnerability coefficient v_ij in [0, 1] between models i and j.
    High v_ij when models share delivery mechanism, API provider, or
    architectural lineage.

    Independent failure: P(both fail) = P(i fails) * P(j fails)
    Correlated failure: P(both fail) = P(i fails) * P(j fails) + v_ij * min(P(i), P(j))

    For a model class (set of models with high mutual v_ij), the correlated
    failure probability accounts for shared vulnerabilities.

    Example::

        cfm = CorrelatedFailureModel()
        cfm.set_vulnerability("m1", "m2", 0.8)  # same API provider
        cfm.set_vulnerability("m1", "m3", 0.1)  # different providers
        p = cfm.correlated_class_failure(
            ["m1", "m2"],
            {"m1": 0.05, "m2": 0.08},
        )
    """

    _vulnerabilities: Dict[FrozenSet[str], float] = field(default_factory=dict)
    _base_failure_rates: Dict[str, float] = field(default_factory=dict)

    def set_vulnerability(self, model_i: str, model_j: str, v_ij: float) -> None:
        """Set shared vulnerability coefficient between two models.

        Args:
            model_i, model_j: Model IDs.
            v_ij: Vulnerability coefficient in [0, 1].
                  0 = independent, 1 = perfectly correlated.
        """
        if not 0.0 <= v_ij <= 1.0:
            raise ValueError(f"v_ij must be in [0, 1], got {v_ij}")
        key = frozenset({model_i, model_j})
        self._vulnerabilities[key] = v_ij

    def get_vulnerability(self, model_i: str, model_j: str) -> float:
        """Get shared vulnerability coefficient. Default 0 (independent)."""
        if model_i == model_j:
            return 1.0
        key = frozenset({model_i, model_j})
        return self._vulnerabilities.get(key, 0.0)

    def set_base_failure_rate(self, model_id: str, rate: float) -> None:
        """Set empirical base failure rate for a model.

        Args:
            model_id: Model ID.
            rate: P(failure) in [0, 1].
        """
        if not 0.0 <= rate <= 1.0:
            raise ValueError(f"rate must be in [0, 1], got {rate}")
        self._base_failure_rates[model_id] = rate

    def pairwise_joint_failure(
        self,
        model_i: str,
        model_j: str,
        p_i: Optional[float] = None,
        p_j: Optional[float] = None,
    ) -> float:
        """Compute P(both i and j fail) accounting for correlation.

        P(i,j fail) = p_i * p_j + v_ij * min(p_i, p_j) * (1 - max(p_i, p_j))

        The correlation term adds probability mass proportional to v_ij,
        bounded so total doesn't exceed min(p_i, p_j).

        Args:
            model_i, model_j: Model IDs.
            p_i, p_j: Override failure probabilities. If None, use base rates.

        Returns:
            Joint failure probability in [0, 1].
        """
        if p_i is None:
            p_i = self._base_failure_rates.get(model_i, 0.0)
        if p_j is None:
            p_j = self._base_failure_rates.get(model_j, 0.0)

        v_ij = self.get_vulnerability(model_i, model_j)

        # SY-4 fix: use bivariate normal form for consistency with
        # correlated_class_failure(). rho * sqrt(p_i*(1-p_i)*p_j*(1-p_j))
        independent = p_i * p_j
        correlation = v_ij * (p_i * (1.0 - p_i) * p_j * (1.0 - p_j)) ** 0.5
        joint = independent + correlation

        # Clamp to valid probability range
        return min(joint, min(p_i, p_j))

    def correlated_class_failure(
        self,
        model_ids: Sequence[str],
        failure_rates: Optional[Dict[str, float]] = None,
    ) -> float:
        """Compute probability that ALL models in a class fail simultaneously.

        Uses an approximate bound assuming conditional independence of non-paired models:
        P(all fail) ≈ min over pairs of P(pair fails jointly) × product of remaining
        individual failure rates.

        For practical use: this gives a risk estimate for model classes that
        share infrastructure (e.g., all OpenAI models, all models behind
        the same API gateway).

        Args:
            model_ids: List of model IDs in the class.
            failure_rates: Per-model failure rates. If None, use base rates.

        Returns:
            Estimated probability that all models in the class fail.
        """
        if not model_ids:
            return 0.0

        rates = {}
        for mid in model_ids:
            if failure_rates and mid in failure_rates:
                rates[mid] = failure_rates[mid]
            else:
                rates[mid] = self._base_failure_rates.get(mid, 0.0)

        if len(model_ids) == 1:
            return rates[model_ids[0]]

        # Product of individual rates (independent baseline)
        independent_all = 1.0
        for mid in model_ids:
            independent_all *= rates[mid]

        # Pairwise correlated failure: P(A∩B) = p^2 + rho*p*(1-p)
        # This is the mathematically correct joint formula that guarantees
        # P(A∩B) <= min(P(A), P(B)) when rho in [0,1].
        # For >2 models, use worst-case pairwise joint probability.
        max_pairwise_joint = 0.0
        ids = list(model_ids)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                rho = self.get_vulnerability(ids[i], ids[j])
                p_i = rates[ids[i]]
                p_j = rates[ids[j]]
                # CF-1 fix: use actual per-model rates for pairwise joint,
                # not p_min. Joint P(A∩B) = p_i*p_j + rho*sqrt(p_i*(1-p_i)*p_j*(1-p_j))
                # which correctly accounts for asymmetric failure rates.
                independent_pair = p_i * p_j
                corr_term = rho * (p_i * (1 - p_i) * p_j * (1 - p_j)) ** 0.5
                joint = independent_pair + corr_term
                max_pairwise_joint = max(max_pairwise_joint, joint)

        # Run 6 bug 2: for N≥3, max(independent, pairwise_joint) massively
        # overestimates because it ignores the N-2 other models' independence.
        # Corrected: worst-case pairwise joint × product of remaining individual
        # rates. This gives a tight upper bound that preserves the redundancy
        # benefit of additional models.
        if len(model_ids) <= 2:
            result = max(independent_all, max_pairwise_joint)
        else:
            # For each pair, compute: P(pair fails jointly) × Π(P(other_i fails))
            best_joint_estimate = float("inf")
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    rho = self.get_vulnerability(ids[i], ids[j])
                    p_i = rates[ids[i]]
                    p_j = rates[ids[j]]
                    pair_joint = p_i * p_j + rho * (p_i * (1 - p_i) * p_j * (1 - p_j)) ** 0.5
                    # SY-5: enforce Frechet upper bound on intermediate values
                    pair_joint = min(pair_joint, min(p_i, p_j))
                    # Remaining models fail independently
                    remaining_product = 1.0
                    for k in range(len(ids)):
                        if k != i and k != j:
                            remaining_product *= rates[ids[k]]
                    joint_all = pair_joint * remaining_product
                    best_joint_estimate = min(best_joint_estimate, joint_all)
            # Use the tightest upper bound: min over all pair decompositions,
            # but at least the fully independent product
            result = max(independent_all, best_joint_estimate)
        min_individual = min(rates.values()) if rates else 0.0
        return min(result, min_individual)

    def independence_check(self, model_ids: Sequence[str]) -> float:
        """Return the maximum vulnerability coefficient within a model set.

        0.0 = fully independent. 1.0 = at least one pair perfectly correlated.
        Useful for assessing whether the independent failure assumption holds.
        """
        max_v = 0.0
        ids = list(model_ids)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                v = self.get_vulnerability(ids[i], ids[j])
                max_v = max(max_v, v)
        return max_v
