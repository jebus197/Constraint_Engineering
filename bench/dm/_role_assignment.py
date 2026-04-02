"""CDSFL Dynamic Management — Role Assignment (Area 1).

Implements weighted linear capability scoring with static PM assignment.
Extracted from ``bench/dynamic_management.py``.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
from numpy.typing import NDArray

from bench.dm._types import (
    CapabilityFingerprint,
    DynamicManagementConfig,
    ModelSpec,
    Role,
)


@dataclass
class RoleAssignment:
    """Role assignment map rho : M -> Roles with capability ordering.

    Implements the merged formulation from §2 of the converged plan:
    - Linear mapping from 4D capability fingerprint to scalar role-suitability
    - PM selected by argmax with deterministic tie-breaking
    - PM static for run duration (HARD constraint C3)
    - COL/PAR dynamic between rounds

    Example::

        models = [
            ModelSpec("m1", CapabilityFingerprint(0.1, 0.9, 0.8, 0.7)),
            ModelSpec("m2", CapabilityFingerprint(0.2, 0.7, 0.9, 0.8)),
            ModelSpec("m3", CapabilityFingerprint(0.3, 0.6, 0.7, 0.6)),
        ]
        cfg = DynamicManagementConfig()
        ra = RoleAssignment.assign(models, cfg)
        print(ra.role_map)  # {'m1': Role.PM, 'm2': Role.COL, 'm3': Role.PAR}
    """

    role_map: Dict[str, Role]
    capability_scores: Dict[str, Dict[str, float]]  # model_id -> {role_name: score}
    pm_model_id: str  # Locked for run duration (HARD)
    _config: DynamicManagementConfig = field(repr=False)
    _models: List[ModelSpec] = field(repr=False)
    _failure_history: Dict[str, List[bool]] = field(
        default_factory=dict, repr=False
    )  # model_id -> [failed_in_round_r]

    @staticmethod
    def _compute_pool_max(models: Sequence[ModelSpec]) -> NDArray[np.float64]:
        """Compute per-dimension max across the model pool for normalisation."""
        if not models:
            return np.zeros(4, dtype=np.float64)
        raw = np.array([m.fingerprint.as_array() for m in models], dtype=np.float64)
        return np.max(raw, axis=0)

    @staticmethod
    def _capability_score(
        model: ModelSpec,
        role: Role,
        pool_max: NDArray[np.float64],
        config: DynamicManagementConfig,
    ) -> float:
        """Compute cap_rho(m) = alpha^rho . q_tilde_m.

        Args:
            model: The model to score.
            role: The role to score for.
            pool_max: Per-dimension max across pool for normalisation.
            config: Configuration with alpha vectors.

        Returns:
            Scalar capability score in [0, 1].
        """
        q_tilde = model.fingerprint.as_normalised_array(pool_max)
        alpha = config.get_alpha(role)
        return float(np.dot(alpha, q_tilde))

    @staticmethod
    def _tie_break_key(model: ModelSpec) -> Tuple[float, float, float, float]:
        """Deterministic tie-breaking: lexicographic on (A, v_bar, 1-D_decay, C).

        Higher values win. This matches the converged plan's tie-breaking rule.
        """
        fp = model.fingerprint
        return (fp.A, fp.v_bar, 1.0 - fp.D_decay, fp.C)

    @classmethod
    def assign(
        cls,
        models: Sequence[ModelSpec],
        config: DynamicManagementConfig,
    ) -> "RoleAssignment":
        """Initial role assignment. PM is locked after this call.

        Implements the constructive algorithm from §2.2 of the converged plan.

        Args:
            models: Available model pool M.
            config: Configuration with alpha vectors and thresholds.

        Returns:
            RoleAssignment with role_map, scores, and locked PM.

        Raises:
            ValueError: If models is empty.
        """
        if not models:
            raise ValueError("Cannot assign roles to empty model pool")

        models_list = list(models)
        pool_max = cls._compute_pool_max(models_list)

        # Compute all scores
        scores: Dict[str, Dict[str, float]] = {}
        for m in models_list:
            scores[m.model_id] = {
                role.value: cls._capability_score(m, role, pool_max, config)
                for role in Role
            }

        # Step 1-2: Select PM by argmax with tie-breaking
        pm_candidates = sorted(
            models_list,
            key=lambda m: (scores[m.model_id][Role.PM.value], cls._tie_break_key(m)),
            reverse=True,
        )
        pm_model = pm_candidates[0]

        role_map: Dict[str, Role] = {pm_model.model_id: Role.PM}

        # Step 3-4: Assign COL (if K >= 3)
        remaining = [m for m in models_list if m.model_id != pm_model.model_id]
        if len(models_list) >= 3 and remaining:
            col_candidates = sorted(
                remaining,
                key=lambda m: (
                    scores[m.model_id][Role.COL.value],
                    cls._tie_break_key(m),
                ),
                reverse=True,
            )
            col_model = col_candidates[0]
            role_map[col_model.model_id] = Role.COL
            remaining = [m for m in remaining if m.model_id != col_model.model_id]

        # Step 5: All remaining are PAR
        for m in remaining:
            role_map[m.model_id] = Role.PAR

        return cls(
            role_map=role_map,
            capability_scores=scores,
            pm_model_id=pm_model.model_id,
            _config=config,
            _models=models_list,
            _failure_history={m.model_id: [] for m in models_list},
        )

    def reassign(
        self,
        round_idx: int,
        active_models: Optional[Set[str]] = None,
        live_fingerprints: Optional[Dict[str, "CapabilityFingerprint"]] = None,
    ) -> Dict[str, Role]:
        """Reassign COL/PAR roles between rounds. PM is never reassigned (HARD C3).

        Incorporates failure-history penalty (ChatGPT) and hysteresis band
        (ChatGPT) to prevent oscillation.

        Args:
            round_idx: Current round index (for failure history).
            active_models: Set of active model IDs. If None, all models active.
            live_fingerprints: Optional live-updated fingerprints from
                DynamicManager._live_fingerprints.  When provided, models
                are scored with current performance data rather than initial
                estimates.  (Exp14 fix: 5 findings, triple-corroborated,
                sev 0.90 — reassign used stale initial fingerprints.)

        Returns:
            Updated role_map (also updates self.role_map in place).
        """
        if active_models is None:
            active_models = set(self.role_map.keys())

        # Use live fingerprints when available (Exp14 fix)
        models_for_scoring = list(self._models)
        if live_fingerprints:
            # LB_F007: Warn if active models are missing from live_fingerprints
            # (stale data would silently degrade scoring accuracy).
            missing = active_models - {self.pm_model_id} - set(live_fingerprints.keys())
            if missing:
                import warnings as _warnings
                _warnings.warn(
                    f"RoleAssignment.reassign(): active models {missing} missing "
                    f"from live_fingerprints — using stale initial fingerprints",
                    stacklevel=2,
                )
            models_for_scoring = []
            for m in self._models:
                if m.model_id in live_fingerprints:
                    # Create a copy with updated fingerprint
                    updated = ModelSpec(
                        model_id=m.model_id,
                        fingerprint=live_fingerprints[m.model_id],
                        tau=m.tau, L=m.L, c=m.c, L_std=m.L_std,
                    )
                    models_for_scoring.append(updated)
                else:
                    models_for_scoring.append(m)

        pool_max = self._compute_pool_max(
            [m for m in models_for_scoring if m.model_id in active_models]
        )

        # PM stays locked
        new_map: Dict[str, Role] = {self.pm_model_id: Role.PM}

        remaining_ids = [
            mid for mid in active_models if mid != self.pm_model_id
        ]
        if not remaining_ids:
            self.role_map = new_map
            return new_map

        # Compute COL scores with failure-history penalty
        col_scores: Dict[str, float] = {}
        for mid in remaining_ids:
            model = next((m for m in models_for_scoring if m.model_id == mid), None)
            if model is None:
                continue
            base_score = self._capability_score(model, Role.COL, pool_max, self._config)

            # Failure history penalty: phi_hist(m, r-1) = mean(failures)
            hist = self._failure_history.get(mid, [])
            phi_hist = sum(hist) / len(hist) if hist else 0.0
            adjusted = base_score * (1.0 - phi_hist)
            col_scores[mid] = adjusted

        if not col_scores:
            self.role_map = new_map
            return new_map

        # Hysteresis: only change COL if score difference exceeds epsilon_rho
        current_col = None
        for mid, role in self.role_map.items():
            if role == Role.COL and mid in active_models:
                current_col = mid
                break

        best_col_id = max(col_scores, key=lambda mid: col_scores[mid])

        if (
            current_col is not None
            and current_col in col_scores
            and len(remaining_ids) >= 2
        ):
            # Apply hysteresis: keep current COL unless beaten by epsilon_rho
            if (
                col_scores[best_col_id]
                <= col_scores[current_col] + self._config.epsilon_rho
            ):
                best_col_id = current_col

        if len(self._models) >= 3:
            new_map[best_col_id] = Role.COL

        for mid in remaining_ids:
            if mid not in new_map:
                new_map[mid] = Role.PAR

        # Persist updated COL scores back to capability_scores
        # (Exp15 convergent finding: scores were computed but discarded)
        for mid, score in col_scores.items():
            if mid in self.capability_scores:
                self.capability_scores[mid][Role.COL.value] = score

        self.role_map = new_map
        return new_map

    def pm_performance_warning(
        self,
        live_fingerprints: Optional[Dict[str, "CapabilityFingerprint"]] = None,
        active_models: Optional[Set[str]] = None,
    ) -> Optional[str]:
        """LB_F005: Check if PM has degraded below worst active PAR.

        C3 prevents PM replacement, but monitoring should flag when the lock
        is costing output quality. Returns warning string or None.
        """
        if not live_fingerprints or not active_models:
            return None
        pm_fp = live_fingerprints.get(self.pm_model_id)
        if pm_fp is None:
            return None
        pm_score = self._capability_score(
            ModelSpec(self.pm_model_id, pm_fp), Role.PM,
            self._compute_pool_max(
                [ModelSpec(m, live_fingerprints[m])
                 for m in active_models if m in live_fingerprints]
            ),
            self._config,
        )
        par_scores = {}
        for mid in active_models:
            if mid == self.pm_model_id or mid not in live_fingerprints:
                continue
            par_scores[mid] = self._capability_score(
                ModelSpec(mid, live_fingerprints[mid]), Role.PAR,
                self._compute_pool_max(
                    [ModelSpec(m, live_fingerprints[m])
                     for m in active_models if m in live_fingerprints]
                ),
                self._config,
            )
        if par_scores and pm_score < min(par_scores.values()):
            worst_par = min(par_scores, key=lambda k: par_scores[k])
            return (
                f"PM {self.pm_model_id} score ({pm_score:.3f}) below worst "
                f"PAR {worst_par} ({par_scores[worst_par]:.3f}). C3 prevents "
                f"replacement but output quality may be degraded."
            )
        return None

    def record_failure(self, model_id: str, failed: bool) -> None:
        """Record whether a model failed in the current round.

        Args:
            model_id: The model that did or did not fail.
            failed: True if the model failed this round.
        """
        if model_id not in self._failure_history:
            self._failure_history[model_id] = []
        self._failure_history[model_id].append(failed)

    def get_failure_history_rate(self, model_id: str) -> float:
        """Return phi_hist(m) = mean failure rate across all recorded rounds."""
        hist = self._failure_history.get(model_id, [])
        if not hist:
            return 0.0
        return sum(hist) / len(hist)

    def get_ordering(self, role: Role) -> List[Tuple[str, float]]:
        """Return the capability ordering ≽_rho as sorted (model_id, score) pairs.

        Args:
            role: The role to order by.

        Returns:
            List of (model_id, score) sorted descending by score.
        """
        pairs = [
            (mid, self.capability_scores[mid][role.value])
            for mid in self.capability_scores
        ]
        return sorted(pairs, key=lambda x: x[1], reverse=True)

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(models: Sequence[ModelSpec], config: DynamicManagementConfig) -> bool:
        """Validate K=1 reduction: single model gets PM, performs all functions.

        Example::

            m = ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7))
            assert RoleAssignment.validate_k1([m], DynamicManagementConfig())
        """
        if len(models) != 1:
            return False
        ra = RoleAssignment.assign(models, config)
        return (
            ra.role_map[models[0].model_id] == Role.PM
            and len(ra.role_map) == 1
        )

    @staticmethod
    def validate_homogeneous(
        k: int, config: DynamicManagementConfig
    ) -> bool:
        """Validate homogeneous reduction: all identical models, tie-breaking assigns PM.

        Example::

            assert RoleAssignment.validate_homogeneous(4, DynamicManagementConfig())
        """
        fp = CapabilityFingerprint(0.5, 0.5, 0.5, 0.5)
        models = [ModelSpec(f"m{i}", fp) for i in range(k)]
        ra = RoleAssignment.assign(models, config)
        pm_count = sum(1 for r in ra.role_map.values() if r == Role.PM)
        # All scores equal, exactly one PM assigned
        scores = set()
        for mid in ra.capability_scores:
            scores.add(ra.capability_scores[mid][Role.PM.value])
        return pm_count == 1 and len(scores) == 1
