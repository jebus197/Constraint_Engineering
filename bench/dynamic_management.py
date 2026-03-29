"""dynamic_management.py — CDSFL Dynamic Management & Load-Balancing Layer.

Implements the converged formalisation from Experiment 11, Phase 3 (4-model
synthesis). All six areas of the CDSFL management layer are implemented as
callable classes and functions matching the interface contracts from the
converged plan.

Areas:
    1. Role Assignment — weighted linear capability scoring, static PM
    2. Load Balancing — multi-objective constrained allocation (GAP variant)
    3. Round Progression — deterministic acyclic FSM
    4. Convergence Detection — three-metric conservative combination
    5. Diminishing Returns — marginal value/cost with ascending abstraction guard
    6. Failure Handling — typed failures with priority, recovery policy, PM abort

Three additions from Codex timeout analysis:
    - Pre-dispatch probabilistic feasibility (Area 2 extension)
    - Correlated failure model (Area 6 extension)
    - Real-time manager monitoring interface (event callback protocol)

Attribution (minority variations adopted):
    - Failure-history penalty in role reassignment: ChatGPT (GPT-5.4)
    - Hysteresis band for COL oscillation prevention: ChatGPT (GPT-5.4)
    - Severity veto clause in convergence: ChatGPT (GPT-5.4)
    - Adoption stabilisation metric kappa_adopt: ChatGPT (GPT-5.4)
    - Persistence window for underperformance: ChatGPT (GPT-5.4)
    - Disjunctive abstraction guard catalogued (not adopted): Gemini (3.1 Pro)
    - Capability decay on underperformance catalogued (not adopted): Gemini (3.1 Pro)
    - Smoothing window for VCR: CC2 (Claude Opus 4.6)
    - Cascade reallocation guard: CC2 (Claude Opus 4.6)
    - Sufficiency constraint concept: DeepSeek (V3.2)

Design decisions (locked by founder):
    1. Ascending abstraction guard: CONJUNCTIVE (not disjunctive veto)
    2. Convergence threshold tau_kappa: SEPARATE from Duane gamma

Notation follows §3 of the converged plan. No collision with immutable symbols
from §7-8 of the existing Mathematical Appendix (C(n), F_n, D(n), R_n, G_n,
Y(t), V_hat(t,T), Delta, Sev(f), S_v(f), lambda(t), gamma, H(x), O_A).
"""

from __future__ import annotations

import enum
import math
import time
import warnings
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    Union,
)

import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class DynamicManagementConfig:
    """Single configuration dataclass for all thresholds, weights, and parameters.

    Defaults match the converged plan (§11.2). All values are SOFT parameters
    unless noted otherwise.

    Example::

        cfg = DynamicManagementConfig()
        cfg.tau_kappa = 0.90  # relax convergence threshold
        cfg.lambda_lat = 0.5  # increase latency penalty weight
    """

    # --- Area 1: Role Assignment ---
    # Role-specific capability weight vectors alpha^rho, shape (4,), sum to 1.
    # Dimensions: (1-D_decay_norm, v_bar_norm, A_norm, C_norm)
    alpha_pm: NDArray[np.float64] = field(
        default_factory=lambda: np.array([0.15, 0.35, 0.35, 0.15])
    )
    alpha_col: NDArray[np.float64] = field(
        default_factory=lambda: np.array([0.20, 0.30, 0.25, 0.25])
    )
    alpha_par: NDArray[np.float64] = field(
        default_factory=lambda: np.array([0.25, 0.25, 0.25, 0.25])
    )
    # Hysteresis band for COL reassignment (ChatGPT contribution)
    epsilon_rho: float = 0.05
    # COL threshold (only used if threshold-based COL selection is enabled)
    theta_col: Optional[float] = None  # None = use argmax (default)

    # --- Area 2: Load Balancing ---
    lambda_lat: float = 0.1  # latency penalty weight
    lambda_bal: float = 0.1  # balance penalty weight
    epsilon_bal: float = 0.1  # balance tolerance for balanced() predicate
    tau_critical: float = 0.8  # criticality threshold for full redundancy
    tau_moderate: float = 0.4  # criticality threshold for half redundancy
    # Pre-dispatch feasibility threshold (Codex timeout addition)
    feasibility_threshold: float = 0.90  # P(feasible) >= this to dispatch

    # --- Area 3: Round Progression ---
    max_rounds: int = 5  # N (protocol constant)
    blind_first: bool = True  # HARD: always start with blind round

    # --- Area 4: Convergence Detection ---
    tau_sim: float = 0.8  # finding similarity threshold for equivalence
    tau_kappa: float = 0.95  # convergence threshold (SEPARATE from gamma)
    eta_veto: float = 0.9  # severity veto threshold (ChatGPT contribution)
    epsilon_conv: float = 1e-8  # zero-denominator regulariser
    min_rounds_for_convergence: int = 2  # r >= this to allow convergence

    # --- Area 5: Diminishing Returns ---
    tau_mu: float = 0.05  # minimum acceptable VCR
    r_min: int = 2  # minimum rounds before early stop
    smoothing_window: int = 2  # W: VCR smoothing window (CC2 contribution)
    epsilon_cost: float = 1e-8  # cost regulariser for c_r = 0

    # --- Area 6: Failure Handling ---
    timeout_multiplier: float = 1.5  # Theta_r = eta * tau_m
    theta_under: float = 0.3  # underperformance fraction threshold
    n_fail: int = 2  # failure repetition threshold for escalation
    persistence_window: int = 2  # h: underperformance persistence (ChatGPT)
    eta_underperform: float = 0.5  # fraction of window that must underperform
    delta_deg: float = 0.5  # degradation severity scaling
    max_realloc_depth: int = 2  # cascade guard (CC2 contribution)
    k_min: int = 1  # minimum active models before abort

    # --- Correlated failure model (Codex timeout addition) ---
    default_vulnerability: float = 0.0  # v_ij default (no correlation)

    # --- Live fingerprint update (adaptive routing feedback loop) ---
    # EMA smoothing factor for fingerprint updates. 0.3 = 30% weight on new
    # observation, 70% weight on prior. Lower values = more stable but slower
    # to adapt. Higher values = faster adaptation but noisier allocation.
    fingerprint_ema_alpha: float = 0.3

    # --- Role-specific baseline coefficients for expected performance ---
    # b_rho vectors for expected(m, r) = b_rho . q_m
    b_pm: NDArray[np.float64] = field(
        default_factory=lambda: np.array([0.10, 0.30, 0.40, 0.20])
    )
    b_col: NDArray[np.float64] = field(
        default_factory=lambda: np.array([0.15, 0.35, 0.30, 0.20])
    )
    b_par: NDArray[np.float64] = field(
        default_factory=lambda: np.array([0.20, 0.30, 0.25, 0.25])
    )

    def __post_init__(self) -> None:
        """Validate configuration invariants."""
        for name, vec in [
            ("alpha_pm", self.alpha_pm),
            ("alpha_col", self.alpha_col),
            ("alpha_par", self.alpha_par),
        ]:
            vec = np.asarray(vec, dtype=np.float64)
            if vec.shape != (4,):
                raise ValueError(f"{name} must have shape (4,), got {vec.shape}")
            if not np.all(vec >= 0):
                raise ValueError(f"{name} must be non-negative")
            if not np.isclose(vec.sum(), 1.0):
                raise ValueError(f"{name} must sum to 1.0, got {vec.sum()}")
        if self.max_rounds < 1:
            raise ValueError(f"max_rounds must be >= 1, got {self.max_rounds}")
        if not (0.0 < self.tau_kappa <= 1.0):
            raise ValueError(f"tau_kappa must be in (0, 1], got {self.tau_kappa}")
        if not (0.0 < self.feasibility_threshold <= 1.0):
            raise ValueError(
                f"feasibility_threshold must be in (0, 1], got {self.feasibility_threshold}"
            )

    def get_alpha(self, role: Role) -> NDArray[np.float64]:
        """Return the capability weight vector for a given role."""
        if role == Role.PM:
            return np.asarray(self.alpha_pm, dtype=np.float64)
        elif role == Role.COL:
            return np.asarray(self.alpha_col, dtype=np.float64)
        else:
            return np.asarray(self.alpha_par, dtype=np.float64)

    def get_baseline(self, role: Role) -> NDArray[np.float64]:
        """Return the performance baseline vector for a given role."""
        if role == Role.PM:
            return np.asarray(self.b_pm, dtype=np.float64)
        elif role == Role.COL:
            return np.asarray(self.b_col, dtype=np.float64)
        else:
            return np.asarray(self.b_par, dtype=np.float64)


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class Role(enum.Enum):
    """Model roles in the CDSFL framework. Uses rho (ρ) to avoid R_n collision."""

    PM = "PM"  # Player Manager — static for run duration (HARD)
    COL = "COL"  # Collator — may be reassigned between rounds
    PAR = "PAR"  # Participant — may be reassigned between rounds


@dataclass(frozen=True)
class CapabilityFingerprint:
    """Per-model capability fingerprint (D_decay, v_bar, A, C) from §7.

    All values in [0, 1] or ℝ≥0 as defined in the existing schema.

    Example::

        fp = CapabilityFingerprint(D_decay=0.1, v_bar=0.8, A=0.9, C=0.7)
    """

    D_decay: float  # Detection decay rate (lower = better)
    v_bar: float  # Mean verification quality
    A: float  # Accuracy / alignment
    C: float  # Coverage breadth

    def as_array(self) -> NDArray[np.float64]:
        """Return raw (D_decay, v_bar, A, C) as numpy array."""
        return np.array([self.D_decay, self.v_bar, self.A, self.C], dtype=np.float64)

    def as_normalised_array(self, pool_max: NDArray[np.float64]) -> NDArray[np.float64]:
        """Return normalised fingerprint q_tilde with D_decay inverted.

        q_tilde = (1 - D_decay_hat, v_bar_hat, A_hat, C_hat)
        where X_hat = X / max(X across pool). If max = 0, set to 0.

        Args:
            pool_max: Array of shape (4,) with max values across the model pool
                      for (D_decay, v_bar, A, C).
        """
        raw = self.as_array()
        with np.errstate(divide="ignore", invalid="ignore"):
            normed = np.where(pool_max > 0, raw / pool_max, 0.0)
        # Invert D_decay: higher (1 - D_decay_hat) = better
        normed[0] = 1.0 - normed[0]
        return normed


@dataclass(frozen=True)
class ModelSpec:
    """Specification for a model in the pool.

    Example::

        spec = ModelSpec(
            model_id="claude-opus-4.6",
            fingerprint=CapabilityFingerprint(0.1, 0.8, 0.9, 0.7),
            tau=120.0, L=32768, c=0.015
        )
    """

    model_id: str
    fingerprint: CapabilityFingerprint
    tau: float = 300.0  # Response time (seconds)
    L: float = 32768.0  # Token limit
    c: float = 0.01  # Cost per token
    # Uncertainty in token limit (Codex timeout addition).
    # If > 0, L is treated as a mean with this std dev.
    L_std: float = 0.0


@dataclass(frozen=True)
class Task:
    """A verification task to be allocated.

    Example::

        task = Task(task_id="t1", token_demand=5000, flaw_class=2, criticality=0.7)
    """

    task_id: str
    token_demand: float  # b_j: tokens required
    flaw_class: int  # k: flaw class index (connects to w_k in F_n)
    criticality: float = 0.5  # w(t_j) = w_k, in [0, 1]


@dataclass(frozen=True)
class Finding:
    """A finding produced by a model in a round.

    Example::

        f = Finding(
            finding_id="f1", model_id="claude", round_idx=1,
            flaw_class=2, severity=0.8, abstraction_index=0.6,
            description="Buffer overflow in parser"
        )
    """

    finding_id: str
    model_id: str
    round_idx: int
    flaw_class: int
    severity: float  # Sev(f) in [0, 1]
    abstraction_index: float  # H(f) in [0, 1]
    description: str = ""
    verified: bool = False  # Whether finding was independently verified (SymPy, etc.)


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 1: ROLE ASSIGNMENT
# ═══════════════════════════════════════════════════════════════════════════════


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
    ) -> Dict[str, Role]:
        """Reassign COL/PAR roles between rounds. PM is never reassigned (HARD C3).

        Incorporates failure-history penalty (ChatGPT) and hysteresis band
        (ChatGPT) to prevent oscillation.

        Args:
            round_idx: Current round index (for failure history).
            active_models: Set of active model IDs. If None, all models active.

        Returns:
            Updated role_map (also updates self.role_map in place).
        """
        if active_models is None:
            active_models = set(self.role_map.keys())

        pool_max = self._compute_pool_max(
            [m for m in self._models if m.model_id in active_models]
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
            model = next((m for m in self._models if m.model_id == mid), None)
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

        self.role_map = new_map
        return new_map

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


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 2: LOAD BALANCING
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Allocation:
    """Task allocation A : T -> 2^M, represented as indicator matrix.

    Example::

        alloc = Allocation(
            task_ids=["t1", "t2"],
            model_ids=["m1", "m2"],
            matrix=np.array([[1, 0], [1, 1]]),
        )
        print(alloc.get_assigned_models("t1"))  # {"m1"}
    """

    task_ids: List[str]
    model_ids: List[str]
    matrix: NDArray[np.int_]  # a_{jm}, shape (J, K)

    def get_assigned_models(self, task_id: str) -> Set[str]:
        """Return set of model IDs assigned to a task."""
        j = self.task_ids.index(task_id)
        return {
            self.model_ids[m]
            for m in range(len(self.model_ids))
            if self.matrix[j, m] == 1
        }

    def get_assigned_tasks(self, model_id: str) -> Set[str]:
        """Return set of task IDs assigned to a model."""
        m = self.model_ids.index(model_id)
        return {
            self.task_ids[j]
            for j in range(len(self.task_ids))
            if self.matrix[j, m] == 1
        }

    def model_load(self, model_id: str, tasks: Sequence[Task]) -> float:
        """Return total token load on a model: sum_j a_{jm} * b_j."""
        m = self.model_ids.index(model_id)
        task_map = {t.task_id: t for t in tasks}
        total = 0.0
        for j, tid in enumerate(self.task_ids):
            if self.matrix[j, m] == 1:
                total += task_map[tid].token_demand
        return total

    def model_load_fraction(
        self, model_id: str, tasks: Sequence[Task], models: Sequence[ModelSpec]
    ) -> float:
        """Return load fraction: sum_j a_{jm} * b_j / L_m."""
        m_idx = self.model_ids.index(model_id)
        model = next(ms for ms in models if ms.model_id == model_id)
        load = self.model_load(model_id, tasks)
        if model.L <= 0:
            return float("inf") if load > 0 else 0.0
        return load / model.L


class LoadBalancer:
    """Multi-objective constrained task allocation (GAP variant).

    Implements the merged formulation from §3 of the converged plan:
    - Multi-model allocation A : T -> 2^M
    - Cost objective J(A) with monetary, latency, and balance terms
    - Feasibility constraints F1 (token), F2 (coverage), F3 (role admissibility)
    - Redundancy targets based on criticality
    - Connection to D(n) through allocation

    The solver uses a greedy heuristic (practical for K <= 10, J <= 50).
    For larger instances, replace _solve_greedy with an ILP solver.

    Example::

        models = [
            ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7), L=10000, c=0.01),
            ModelSpec("m2", CapabilityFingerprint(0.2, 0.7, 0.8, 0.6), L=10000, c=0.02),
        ]
        tasks = [Task("t1", 3000, 1, 0.5), Task("t2", 4000, 2, 0.9)]
        role_map = {"m1": Role.PAR, "m2": Role.PAR}
        cfg = DynamicManagementConfig()
        lb = LoadBalancer(models, tasks, role_map, cfg)
        alloc, cost, is_balanced = lb.solve()
    """

    def __init__(
        self,
        models: Sequence[ModelSpec],
        tasks: Sequence[Task],
        role_map: Dict[str, Role],
        config: DynamicManagementConfig,
    ) -> None:
        self.models = list(models)
        self.tasks = list(tasks)
        self.role_map = role_map
        self.config = config
        self._model_idx = {m.model_id: i for i, m in enumerate(self.models)}
        self._task_idx = {t.task_id: i for i, t in enumerate(self.tasks)}

    def _admissibility_mask(self) -> NDArray[np.int_]:
        """Compute role admissibility matrix ell^adm_{jm}.

        Default: PM excluded from standard tasks unless K=1.
        Returns shape (J, K).
        """
        J = len(self.tasks)
        K = len(self.models)
        mask = np.zeros((J, K), dtype=np.int_)
        k_total = sum(1 for r in self.role_map.values() if r in (Role.COL, Role.PAR, Role.PM))

        for j in range(J):
            for m_idx, model in enumerate(self.models):
                role = self.role_map.get(model.model_id, Role.PAR)
                if k_total == 1:
                    # K=1: PM does everything
                    mask[j, m_idx] = 1
                elif role in (Role.COL, Role.PAR):
                    mask[j, m_idx] = 1
                # PM excluded from standard tasks when K > 1
        return mask

    def _redundancy_target(self, task: Task) -> int:
        """Compute redundancy target r(t_j) based on criticality.

        Returns:
            Number of models that should cover this task.
        """
        K = len(self.models)
        if task.criticality >= self.config.tau_critical:
            return K
        elif task.criticality >= self.config.tau_moderate:
            return max(1, math.ceil(K / 2))
        else:
            return 1

    def _objective(
        self,
        matrix: NDArray[np.int_],
    ) -> float:
        """Compute J(A) = monetary_cost + lambda_lat * bottleneck + lambda_bal * variance.

        Args:
            matrix: Allocation matrix a_{jm}, shape (J, K).

        Returns:
            Total cost J(A).
        """
        J, K = matrix.shape
        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        costs = np.array([m.c for m in self.models], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)
        taus = np.array([m.tau for m in self.models], dtype=np.float64)

        # Per-model load: sum_j a_{jm} * b_j
        loads = matrix.T.astype(np.float64) @ demands  # shape (K,)

        # Monetary cost: sum_m c_m * load_m
        monetary = float(np.dot(costs, loads))

        # Load fractions
        with np.errstate(divide="ignore", invalid="ignore"):
            fractions = np.where(limits > 0, loads / limits, 0.0)

        # Bottleneck: max_m tau_m * fraction_m
        bottleneck = float(np.max(taus * fractions)) if K > 0 else 0.0

        # Variance of load fractions
        variance = float(np.var(fractions)) if K > 1 else 0.0

        return (
            monetary
            + self.config.lambda_lat * bottleneck
            + self.config.lambda_bal * variance
        )

    def _check_feasibility(
        self,
        matrix: NDArray[np.int_],
        admissibility: NDArray[np.int_],
    ) -> Tuple[bool, List[str]]:
        """Check all HARD feasibility constraints.

        Returns:
            (feasible, list_of_violations)
        """
        violations: List[str] = []
        J, K = matrix.shape
        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)

        # F1: Token feasibility — sum_j a_{jm} * b_j <= L_m
        loads = matrix.T.astype(np.float64) @ demands
        for m_idx in range(K):
            if loads[m_idx] > limits[m_idx]:
                violations.append(
                    f"F1: model {self.models[m_idx].model_id} overloaded "
                    f"({loads[m_idx]:.0f} > {limits[m_idx]:.0f})"
                )

        # F2: Coverage — every task assigned to at least one model
        for j in range(J):
            if matrix[j].sum() < 1:
                violations.append(f"F2: task {self.tasks[j].task_id} unassigned")

        # F3: Role consistency — a_{jm} <= ell^adm_{jm}
        role_violations = matrix & ~admissibility
        if role_violations.any():
            for j, m_idx in zip(*np.where(role_violations)):
                violations.append(
                    f"F3: task {self.tasks[j].task_id} assigned to "
                    f"inadmissible model {self.models[m_idx].model_id}"
                )

        return len(violations) == 0, violations

    def _balanced(self, matrix: NDArray[np.int_]) -> bool:
        """Check balance predicate: Var(load_fractions) <= epsilon_bal."""
        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)
        loads = matrix.T.astype(np.float64) @ demands
        with np.errstate(divide="ignore", invalid="ignore"):
            fractions = np.where(limits > 0, loads / limits, 0.0)
        if len(fractions) <= 1:
            return True
        return float(np.var(fractions)) <= self.config.epsilon_bal

    def _solve_greedy(self) -> NDArray[np.int_]:
        """Greedy allocation heuristic.

        Strategy:
        1. Sort tasks by criticality (descending) — high-criticality first.
        2. For each task, assign to admissible models with lowest current load
           fraction, up to redundancy target.
        3. Respect token limits (F1).

        Returns:
            Allocation matrix a_{jm}, shape (J, K).
        """
        J = len(self.tasks)
        K = len(self.models)
        matrix = np.zeros((J, K), dtype=np.int_)
        admissibility = self._admissibility_mask()

        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)
        current_loads = np.zeros(K, dtype=np.float64)

        # Sort tasks by criticality descending
        task_order = sorted(range(J), key=lambda j: self.tasks[j].criticality, reverse=True)

        for j in task_order:
            target = self._redundancy_target(self.tasks[j])
            admissible = [m_idx for m_idx in range(K) if admissibility[j, m_idx] == 1]

            if not admissible:
                # No admissible model — assign to least-loaded model as fallback
                # (this can only happen if all models are PM and K > 1, which
                # shouldn't occur, but handle gracefully)
                admissible = list(range(K))

            # Sort admissible models by current load fraction (ascending)
            admissible.sort(
                key=lambda m_idx: (
                    current_loads[m_idx] / limits[m_idx] if limits[m_idx] > 0 else float("inf")
                )
            )

            assigned = 0
            for m_idx in admissible:
                if assigned >= target:
                    break
                # Check F1: would this assignment exceed token limit?
                if current_loads[m_idx] + demands[j] <= limits[m_idx]:
                    matrix[j, m_idx] = 1
                    current_loads[m_idx] += demands[j]
                    assigned += 1

            # If we couldn't meet redundancy target, ensure at least coverage (F2)
            if assigned == 0:
                # Force-assign to least-loaded admissible model even if over limit
                # (F1 violation is reported but coverage is maintained)
                if admissible:
                    m_idx = admissible[0]
                    matrix[j, m_idx] = 1
                    current_loads[m_idx] += demands[j]

        return matrix

    def solve(self) -> Tuple[Allocation, float, bool]:
        """Solve the allocation problem.

        Returns:
            (allocation, cost, is_balanced)

        Example::

            alloc, cost, balanced = lb.solve()
            print(f"Cost: {cost:.4f}, Balanced: {balanced}")
        """
        if not self.tasks:
            alloc = Allocation([], [m.model_id for m in self.models], np.zeros((0, len(self.models)), dtype=np.int_))
            return alloc, 0.0, True

        matrix = self._solve_greedy()
        admissibility = self._admissibility_mask()
        feasible, violations = self._check_feasibility(matrix, admissibility)

        if not feasible:
            warnings.warn(
                f"Allocation has feasibility violations: {violations}",
                stacklevel=2,
            )

        cost = self._objective(matrix)
        balanced = self._balanced(matrix)

        alloc = Allocation(
            task_ids=[t.task_id for t in self.tasks],
            model_ids=[m.model_id for m in self.models],
            matrix=matrix,
        )
        return alloc, cost, balanced

    def feasibility_probability(
        self,
        model: ModelSpec,
        task_load: float,
    ) -> float:
        """Pre-dispatch probabilistic feasibility estimate.

        P(task fits within model capacity) when L_m is uncertain.
        If L_std = 0, returns 1.0 if feasible, 0.0 otherwise.

        Uses a normal approximation: L_m ~ N(L, L_std^2).
        P(feasible) = P(task_load <= L_m) = Phi((L - task_load) / L_std).

        This addresses the Codex timeout gap: CLI delivery mechanisms may not
        expose exact token limits.

        Args:
            model: Model specification (with L and L_std).
            task_load: Total token demand to be dispatched.

        Returns:
            Probability in [0, 1] that the task fits.

        Example::

            m = ModelSpec("codex", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7),
                          L=32768, L_std=5000)
            p = lb.feasibility_probability(m, 30000)
            print(f"P(feasible) = {p:.3f}")
        """
        if model.L_std <= 0:
            return 1.0 if task_load <= model.L else 0.0

        # Standard normal CDF via error function
        z = (model.L - task_load) / model.L_std
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

    def dispatch_check(
        self,
        model: ModelSpec,
        task_load: float,
    ) -> Tuple[bool, float]:
        """Check whether to dispatch to a model given uncertainty.

        Returns:
            (should_dispatch, p_feasible)

        Example::

            ok, p = lb.dispatch_check(model, 30000)
            if not ok:
                print(f"Skip dispatch: P(feasible) = {p:.3f} < {cfg.feasibility_threshold}")
        """
        p = self.feasibility_probability(model, task_load)
        return p >= self.config.feasibility_threshold, p

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(config: DynamicManagementConfig) -> bool:
        """Validate K=1 reduction: A(t_j) = {m1} for all j, feasibility = sum b_j <= L1.

        Example::

            assert LoadBalancer.validate_k1(DynamicManagementConfig())
        """
        m = ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7), L=10000, c=0.01)
        tasks = [Task("t1", 3000, 1, 0.5), Task("t2", 4000, 2, 0.9)]
        role_map = {"m1": Role.PM}
        lb = LoadBalancer([m], tasks, role_map, config)
        alloc, _, _ = lb.solve()
        # Every task assigned to m1
        for j in range(len(tasks)):
            if alloc.matrix[j, 0] != 1:
                return False
        return True

    @staticmethod
    def validate_homogeneous(k: int, config: DynamicManagementConfig) -> bool:
        """Validate homogeneous reduction: equal distribution optimal.

        Example::

            assert LoadBalancer.validate_homogeneous(3, DynamicManagementConfig())
        """
        fp = CapabilityFingerprint(0.5, 0.5, 0.5, 0.5)
        models = [ModelSpec(f"m{i}", fp, L=10000, c=0.01) for i in range(k)]
        tasks = [Task(f"t{j}", 1000, j % 3, 0.3) for j in range(k)]
        role_map = {f"m0": Role.PM}
        for i in range(1, k):
            role_map[f"m{i}"] = Role.PAR
        lb = LoadBalancer(models, tasks, role_map, config)
        alloc, _, balanced = lb.solve()
        # With homogeneous models and equal tasks, should be balanced
        return balanced


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 3: ROUND PROGRESSION
# ═══════════════════════════════════════════════════════════════════════════════


class State(enum.Enum):
    """State space S (calligraphic S in notation, distinct from S_v)."""

    BLIND = "BLIND"
    SYNTH = "SYNTH"
    TERMINAL = "TERMINAL"

    @staticmethod
    def round_state(k: int) -> str:
        """Return the state name for ROUND_k."""
        return f"ROUND_{k}"


class Event(enum.Enum):
    """Event alphabet Sigma for the round progression FSM.

    Priority (HARD): FAIL_CRITICAL > CONVERGED > DIMINISHED > COMPLETE > MAX.
    """

    COMPLETE = "sigma_complete"
    CONVERGED = "sigma_converged"
    DIMINISHED = "sigma_diminished"
    MAX = "sigma_max"
    FAIL_CRITICAL = "sigma_fail_critical"

    @property
    def priority(self) -> int:
        """Higher number = higher priority."""
        return {
            Event.FAIL_CRITICAL: 5,
            Event.CONVERGED: 4,
            Event.DIMINISHED: 3,
            Event.COMPLETE: 2,
            Event.MAX: 1,
        }[self]


class TerminationReason(enum.Enum):
    """Why the FSM reached TERMINAL."""

    CONVERGED = "CONVERGED"
    DIMINISHED = "DIMINISHED"
    MAX_ROUNDS = "MAX_ROUNDS"
    FAILURE = "FAILURE"


@dataclass
class RoundProgressionFSM:
    """Deterministic acyclic FSM for round progression.

    States: {BLIND, SYNTH, ROUND_1, ..., ROUND_{N-1}, TERMINAL}
    Events: {sigma_complete, sigma_converged, sigma_diminished, sigma_max, sigma_fail_critical}

    The FSM is forward-only (acyclic). TERMINAL is the unique absorbing state.
    Terminates in at most N + 2 transitions.

    Example::

        fsm = RoundProgressionFSM(DynamicManagementConfig())
        print(fsm.current_state)  # "BLIND"
        fsm.transition(Event.COMPLETE)
        print(fsm.current_state)  # "SYNTH"
        fsm.transition(Event.COMPLETE)
        print(fsm.current_state)  # "ROUND_1"
    """

    config: DynamicManagementConfig
    current_state: str = field(init=False)
    current_round: int = field(init=False, default=-1)
    termination_reason: Optional[TerminationReason] = field(init=False, default=None)
    history: List[Tuple[str, Event, str]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.current_state = State.BLIND.value
        self.current_round = 0  # BLIND = round 0

    @property
    def is_terminal(self) -> bool:
        return self.current_state == State.TERMINAL.value

    @property
    def max_round_idx(self) -> int:
        """Maximum iterative round index (N-1)."""
        return self.config.max_rounds - 1

    def valid_events(self) -> List[Event]:
        """Return events valid in the current state."""
        if self.is_terminal:
            return []

        s = self.current_state
        events = [Event.FAIL_CRITICAL]  # Always valid from any non-terminal

        if s == State.BLIND.value:
            events.append(Event.COMPLETE)
        elif s == State.SYNTH.value:
            events.extend([Event.COMPLETE, Event.CONVERGED, Event.DIMINISHED])
        elif s.startswith("ROUND_"):
            k = int(s.split("_")[1])
            events.extend([Event.CONVERGED, Event.DIMINISHED])
            if k < self.max_round_idx:
                events.append(Event.COMPLETE)
            if k == self.max_round_idx:
                events.append(Event.MAX)

        return events

    def transition(self, event: Event) -> str:
        """Execute a state transition.

        Args:
            event: The event triggering the transition.

        Returns:
            The new state name.

        Raises:
            ValueError: If the event is invalid in the current state.
            RuntimeError: If the FSM is already terminal.
        """
        if self.is_terminal:
            raise RuntimeError(
                f"FSM is terminal (reason={self.termination_reason}). "
                f"No further transitions."
            )

        valid = self.valid_events()
        if event not in valid:
            raise ValueError(
                f"Event {event.value} invalid in state {self.current_state}. "
                f"Valid: {[e.value for e in valid]}"
            )

        old_state = self.current_state
        new_state: str

        if event == Event.FAIL_CRITICAL:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.FAILURE

        elif event == Event.CONVERGED:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.CONVERGED

        elif event == Event.DIMINISHED:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.DIMINISHED

        elif event == Event.MAX:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.MAX_ROUNDS

        elif event == Event.COMPLETE:
            if old_state == State.BLIND.value:
                new_state = State.SYNTH.value
            elif old_state == State.SYNTH.value:
                new_state = State.round_state(1)
                self.current_round = 1
            elif old_state.startswith("ROUND_"):
                k = int(old_state.split("_")[1])
                new_state = State.round_state(k + 1)
                self.current_round = k + 1
            else:
                raise ValueError(f"Unexpected state for COMPLETE: {old_state}")
        else:
            raise ValueError(f"Unhandled event: {event}")

        self.history.append((old_state, event, new_state))
        self.current_state = new_state
        return new_state

    def select_event(
        self,
        converged: bool,
        diminished: bool,
        critical_failure: bool,
        round_complete: bool,
    ) -> Event:
        """Select the highest-priority applicable event.

        Implements event priority (HARD):
        FAIL_CRITICAL > CONVERGED > DIMINISHED > COMPLETE > MAX

        Args:
            converged: Whether convergence predicate holds.
            diminished: Whether diminishing returns predicate holds.
            critical_failure: Whether an unrecoverable failure occurred.
            round_complete: Whether all allocations are complete/handled.

        Returns:
            The highest-priority applicable event.
        """
        if critical_failure:
            return Event.FAIL_CRITICAL

        if converged and Event.CONVERGED in self.valid_events():
            return Event.CONVERGED

        if diminished and Event.DIMINISHED in self.valid_events():
            return Event.DIMINISHED

        if round_complete:
            s = self.current_state
            if s.startswith("ROUND_"):
                k = int(s.split("_")[1])
                if k == self.max_round_idx:
                    return Event.MAX
            return Event.COMPLETE

        # No event applicable — caller should wait for completion
        raise ValueError(
            f"No applicable event in state {self.current_state} with "
            f"converged={converged}, diminished={diminished}, "
            f"critical_failure={critical_failure}, round_complete={round_complete}"
        )

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(config: DynamicManagementConfig) -> bool:
        """K=1: Same FSM. Single model's findings. Convergence/stop still apply."""
        fsm = RoundProgressionFSM(config)
        # Should be able to progress through all states
        fsm.transition(Event.COMPLETE)  # BLIND -> SYNTH
        assert fsm.current_state == State.SYNTH.value
        fsm.transition(Event.COMPLETE)  # SYNTH -> ROUND_1
        assert fsm.current_state == State.round_state(1)
        fsm.transition(Event.CONVERGED)  # ROUND_1 -> TERMINAL
        assert fsm.is_terminal
        assert fsm.termination_reason == TerminationReason.CONVERGED
        return True

    @staticmethod
    def validate_no_failures(config: DynamicManagementConfig) -> bool:
        """No failures: sigma_fail_critical never fires. Linear chain."""
        fsm = RoundProgressionFSM(config)
        states_visited = [fsm.current_state]
        # Walk through all rounds
        fsm.transition(Event.COMPLETE)  # BLIND -> SYNTH
        states_visited.append(fsm.current_state)
        fsm.transition(Event.COMPLETE)  # SYNTH -> ROUND_1
        states_visited.append(fsm.current_state)
        for k in range(1, config.max_rounds - 1):
            fsm.transition(Event.COMPLETE)
            states_visited.append(fsm.current_state)
        fsm.transition(Event.MAX)  # ROUND_{N-1} -> TERMINAL
        states_visited.append(fsm.current_state)
        # Verify linear chain (no repeated states)
        return len(states_visited) == len(set(states_visited))


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 4: CONVERGENCE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class FindingEquivalenceClass:
    """An equivalence class [f] of findings under the ≈ relation.

    Findings are equivalent if they share flaw_class and have
    sim(f_i, f_j) >= tau_sim.

    Example::

        ec = FindingEquivalenceClass(
            class_id="ec_1",
            flaw_class=2,
            members=[finding1, finding2],
            aggregated_severity=0.85,
        )
    """

    class_id: str
    flaw_class: int
    members: List[Finding]
    aggregated_severity: float  # Sev_agg([f]) = S_v([f])

    @property
    def support_multiplicity(self) -> int:
        """nu([f]) = number of distinct models contributing to this class."""
        return len(set(f.model_id for f in self.members))

    @property
    def mean_abstraction(self) -> float:
        """Mean abstraction index of findings in this class."""
        if not self.members:
            return 0.0
        return float(np.mean([f.abstraction_index for f in self.members]))


def _finding_similarity(f1: Finding, f2: Finding) -> float:
    """Compute similarity between two findings.

    Uses flaw-class match + description overlap (Jaccard on word sets).
    This is the operational sim() function. In production, replace with
    domain-specific similarity (e.g., embedding cosine).

    When flaw classes differ, Jaccard similarity alone determines the score
    (with a penalty for the class mismatch). This prevents models that assign
    different integer labels to the same concept from appearing maximally novel.

    Args:
        f1, f2: Findings to compare.

    Returns:
        Similarity in [0, 1].
    """
    class_match = f1.flaw_class == f2.flaw_class

    # Jaccard similarity on description words
    words1 = set(f1.description.lower().split())
    words2 = set(f2.description.lower().split())
    if not words1 and not words2:
        return 0.8 if class_match else 0.2
    if not words1 or not words2:
        return 0.3 if class_match else 0.1
    intersection = words1 & words2
    union = words1 | words2
    jaccard = len(intersection) / len(union) if union else 0.0

    if class_match:
        # 0.4 base from class match + 0.6 from Jaccard
        return 0.4 + 0.6 * jaccard
    else:
        # No class match bonus — raw Jaccard only.
        # At tau_sim=0.8, cross-class detection requires Jaccard >= 0.8
        # (80% vocabulary overlap). Strict enough to prevent false merges
        # of distinct findings sharing module-specific vocabulary, but
        # reachable for genuine duplicates with minor rephrasing.
        # Confer consensus: CC2 proposed 0.9x, CX and Gemini proposed 1.0x.
        # 2/3 agreement on raw Jaccard. Single-linkage clustering at
        # tau_sim=0.8 provides sufficient protection against weak bridges.
        return jaccard


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

        return 1.0 - (rate_r / (rate_1 + self.config.epsilon_conv))

    def kappa_adopt(self, round_idx: int) -> float:
        """Adoption stabilisation metric.

        kappa_adopt(r) = 1 - Delta_r

        where Delta_r is the adoption delta from the existing schema.
        Returns value in [0, 1].
        """
        delta = self._adoption_deltas.get(round_idx, 0.0)
        return 1.0 - delta

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

        gamma_hat = log(r) / (log(|F^(<=r)|) - log(|F^(<=1)|))

        For gamma > 1: reliability growth (kappa_rate -> 1).
        For gamma < 1: degradation (kappa_rate < 0).

        This is a DIAGNOSTIC, not the convergence threshold (founder decision).
        """
        if round_idx < 2:
            return 0.0

        cum_r = len(self.get_cumulative_classes(round_idx))
        cum_1 = len(self.get_cumulative_classes(1)) if 1 in self._round_findings else len(
            self.get_cumulative_classes(0)
        )

        if cum_r <= cum_1 or cum_1 <= 0:
            return float("inf") if cum_r == cum_1 else 0.0

        denom = math.log(cum_r) - math.log(cum_1)
        if abs(denom) < 1e-10:
            return float("inf")

        return math.log(round_idx) / denom

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


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 5: DIMINISHING RETURNS
# ═══════════════════════════════════════════════════════════════════════════════


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
        # Per-round data
        self._cumulative_yields: Dict[int, float] = {}  # Y^(<=r)
        self._round_costs: Dict[int, float] = {}  # c_r
        self._mean_abstraction_new: Dict[int, float] = {}  # H_bar^(r)_new

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

    def smoothed_marginal_value(self, round_idx: int) -> float:
        """Compute smoothed VCR over window W.

        Average mu(r) over the last W rounds to prevent premature stopping
        from a single noisy round. (CC2 contribution.)
        """
        W = self.config.smoothing_window
        start = max(0, round_idx - W + 1)
        values = []
        for r in range(start, round_idx + 1):
            if r in self._cumulative_yields:
                mv = self.marginal_value(r)
                if math.isfinite(mv):
                    values.append(mv)
        if not values:
            return 0.0
        return float(np.mean(values))

    def _abstraction_dropping(self, round_idx: int) -> bool:
        """Check if mean abstraction of new findings is dropping.

        H_bar^(r)_new < H_bar^(r-1)_new

        This is used as a CONJUNCTIVE factor (founder decision), not a
        disjunctive veto. A drop in abstraction is one signal among several.
        """
        if round_idx < 1:
            return False
        h_curr = self._mean_abstraction_new.get(round_idx, 0.5)
        h_prev = self._mean_abstraction_new.get(round_idx - 1, 0.5)
        return h_curr < h_prev

    def stop(self, round_idx: int) -> bool:
        """Diminishing returns stop predicate.

        stop(r) iff (smoothed_mu(r) < tau_mu) AND (r >= r_min)

        The ascending abstraction guard is CONJUNCTIVE (founder decision §9.1):
        abstraction drop is one factor in the stop decision, not a unilateral veto.
        A legitimate shift from abstract to concrete findings must not trigger
        premature stopping.

        Note: veto logic (e.g., from convergence detector) is external to this
        predicate. The round progression FSM handles the interaction.
        """
        if round_idx < self.config.r_min:
            return False

        smoothed_mu = self.smoothed_marginal_value(round_idx)
        return smoothed_mu < self.config.tau_mu

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
        mu_prev = self.smoothed_marginal_value(round_idx - 1) if round_idx >= 1 else mu_current
        if mu_prev > 0 and math.isfinite(mu_prev):
            decay = mu_current / mu_prev
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


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 6: FAILURE HANDLING
# ═══════════════════════════════════════════════════════════════════════════════


class FailureType(enum.Enum):
    """Failure types with priority ordering (lower value = higher priority)."""

    EMPTY = 1
    TIMEOUT = 2
    MALFORMED = 3
    FORMAT = 4
    UNDERPERFORM = 5


class RecoveryAction(enum.Enum):
    """Recovery actions for failure handling."""

    RETRY = "RETRY"
    RETRY_EXTENDED = "RETRY_EXTENDED"
    RETRY_CLARIFIED = "RETRY_CLARIFIED"
    REALLOCATE = "REALLOCATE"
    EXCLUDE = "EXCLUDE"
    DEGRADE = "DEGRADE"
    DOWNGRADE_ROLE = "DOWNGRADE_ROLE"
    ABORT = "ABORT"
    LOG_ONLY = "LOG_ONLY"


@dataclass
class FailureRecord:
    """Record of a failure event."""

    model_id: str
    round_idx: int
    failure_type: FailureType
    recovery_action: RecoveryAction
    detail: str = ""
    timestamp: float = field(default_factory=time.monotonic)


@dataclass
class ModelResponse:
    """A model's response to a task, for failure detection.

    Example::

        resp = ModelResponse(
            model_id="m1", round_idx=1, content="...",
            response_time=45.0, parseable=True, format_compliant=True,
            finding_count=3, mean_abstraction=0.6,
        )
    """

    model_id: str
    round_idx: int
    content: str
    response_time: float  # seconds
    parseable: bool = True
    format_compliant: bool = True
    finding_count: int = 0
    mean_abstraction: float = 0.5


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
            self._emit_event(
                ManagerEvent(
                    event_type=ManagerEventType.MALFORMED,
                    model_id=response.model_id,
                    round_idx=response.round_idx,
                    detail="Response parseable but not format-compliant",
                )
            )
            return FailureType.FORMAT

        # Priority 5: UNDERPERFORM (with persistence window)
        perf = self._performance_metric(response)
        self._perf_history.setdefault(response.model_id, []).append(perf)

        h = self.config.persistence_window
        recent_perfs = self._perf_history[response.model_id][-h:]
        if len(recent_perfs) >= h:
            underperform_count = sum(
                1 for p in recent_perfs if p < self.config.theta_under
            )
            if underperform_count / len(recent_perfs) >= self.config.eta_underperform:
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
        same_type_count = sum(
            1 for r in history if r.failure_type == failure_type
        )
        repeated = same_type_count >= self.config.n_fail

        # PM failure handling (HARD constraint)
        if is_pm and failure_type in (
            FailureType.EMPTY,
            FailureType.TIMEOUT,
            FailureType.MALFORMED,
        ):
            if repeated:
                action = RecoveryAction.ABORT
            else:
                action = RecoveryAction.RETRY
            self._record_failure(model_id, round_idx, failure_type, action)
            return action

        # Standard recovery policy table
        if failure_type == FailureType.EMPTY:
            action = (
                RecoveryAction.EXCLUDE if repeated else RecoveryAction.RETRY
            )
        elif failure_type == FailureType.TIMEOUT:
            action = (
                RecoveryAction.EXCLUDE if repeated else RecoveryAction.RETRY_EXTENDED
            )
        elif failure_type == FailureType.MALFORMED:
            action = (
                RecoveryAction.EXCLUDE if repeated else RecoveryAction.RETRY_CLARIFIED
            )
        elif failure_type == FailureType.FORMAT:
            action = (
                RecoveryAction.RETRY_CLARIFIED if repeated else RecoveryAction.DEGRADE
            )
        elif failure_type == FailureType.UNDERPERFORM:
            action = (
                RecoveryAction.DOWNGRADE_ROLE if repeated else RecoveryAction.LOG_ONLY
            )
        else:
            action = RecoveryAction.LOG_ONLY

        self._record_failure(model_id, round_idx, failure_type, action)

        # Execute exclusion if needed
        if action == RecoveryAction.EXCLUDE:
            self._active_models.discard(model_id)

        return action

    def _record_failure(
        self,
        model_id: str,
        round_idx: int,
        failure_type: FailureType,
        action: RecoveryAction,
    ) -> None:
        """Record a failure in the history."""
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

        # Independent component
        independent = p_i * p_j
        # Correlation component: bounded to not exceed min(p_i, p_j)
        correlation = v_ij * min(p_i, p_j) * (1.0 - max(p_i, p_j))
        joint = independent + correlation

        # Clamp to valid probability range
        return min(joint, min(p_i, p_j))

    def correlated_class_failure(
        self,
        model_ids: Sequence[str],
        failure_rates: Optional[Dict[str, float]] = None,
    ) -> float:
        """Compute probability that ALL models in a class fail simultaneously.

        Uses a conservative upper bound based on pairwise correlations:
        P(all fail) <= min over pairs of P(pair fails) for the most correlated pair,
        scaled by the product of remaining individual probabilities.

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

        # Find maximum pairwise correlation contribution
        max_correlation_boost = 0.0
        ids = list(model_ids)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                v = self.get_vulnerability(ids[i], ids[j])
                boost = v * min(rates[ids[i]], rates[ids[j]])
                max_correlation_boost = max(max_correlation_boost, boost)

        # Conservative estimate: independent product + worst-case correlation
        # Clamped to not exceed the minimum individual failure rate
        result = independent_all + max_correlation_boost
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


# ═══════════════════════════════════════════════════════════════════════════════
# REAL-TIME MANAGER MONITORING INTERFACE (Codex timeout addition)
# ═══════════════════════════════════════════════════════════════════════════════


class ManagerEventType(enum.Enum):
    """Event types for the real-time PM monitoring interface."""

    # Failure events (from Area 6)
    TIMEOUT = "TIMEOUT"
    EMPTY = "EMPTY"
    MALFORMED = "MALFORMED"
    FORMAT_VIOLATION = "FORMAT_VIOLATION"
    UNDERPERFORM = "UNDERPERFORM"

    # Recovery events
    RETRY = "RETRY"
    REALLOCATE = "REALLOCATE"
    EXCLUDE = "EXCLUDE"
    ABORT = "ABORT"

    # Progress events
    ROUND_START = "ROUND_START"
    ROUND_COMPLETE = "ROUND_COMPLETE"
    MODEL_RESPONSE = "MODEL_RESPONSE"
    CONVERGENCE_CHECK = "CONVERGENCE_CHECK"
    STOP_CHECK = "STOP_CHECK"

    # Feasibility events (Codex timeout addition)
    DISPATCH_BLOCKED = "DISPATCH_BLOCKED"
    FEASIBILITY_WARNING = "FEASIBILITY_WARNING"


@dataclass(frozen=True)
class ManagerEvent:
    """A real-time event emitted to the PM during dispatch.

    The PM receives these events via a callback and can trigger
    RETRY/REALLOCATE/EXCLUDE dynamically.

    Example::

        def on_event(event: ManagerEvent):
            if event.event_type == ManagerEventType.TIMEOUT:
                print(f"Model {event.model_id} timed out in round {event.round_idx}")

        fh = FailureHandler(models, role_map, config, event_callback=on_event)
    """

    event_type: ManagerEventType
    model_id: str
    round_idx: int
    detail: str = ""
    timestamp: float = field(default_factory=time.monotonic)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ManagerEventStream:
    """Buffered event stream for the PM monitoring interface.

    Supports both callback-based (push) and polling-based (pull) consumption.

    Example::

        stream = ManagerEventStream()
        stream.emit(ManagerEvent(ManagerEventType.ROUND_START, "m1", 0))
        events = stream.drain()  # returns and clears buffer
    """

    def __init__(
        self,
        callback: Optional[Callable[[ManagerEvent], None]] = None,
    ) -> None:
        self._callback = callback
        self._buffer: List[ManagerEvent] = []
        self._all_events: List[ManagerEvent] = []  # permanent log

    def emit(self, event: ManagerEvent) -> None:
        """Emit an event. Calls callback if registered, always buffers.

        Args:
            event: The event to emit.
        """
        self._buffer.append(event)
        self._all_events.append(event)
        if self._callback is not None:
            self._callback(event)

    def drain(self) -> List[ManagerEvent]:
        """Return and clear the event buffer (pull-based consumption).

        Returns:
            List of events since last drain.
        """
        events = self._buffer
        self._buffer = []
        return events

    def peek(self) -> List[ManagerEvent]:
        """Return the event buffer without clearing it."""
        return list(self._buffer)

    @property
    def all_events(self) -> List[ManagerEvent]:
        """Return the complete event log (never cleared)."""
        return list(self._all_events)

    def events_by_type(self, event_type: ManagerEventType) -> List[ManagerEvent]:
        """Filter all events by type."""
        return [e for e in self._all_events if e.event_type == event_type]

    def events_by_model(self, model_id: str) -> List[ManagerEvent]:
        """Filter all events by model."""
        return [e for e in self._all_events if e.model_id == model_id]


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATION: TYING IT ALL TOGETHER
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RoundResult:
    """Result of a single round of the framework.

    Captures all outputs needed for cross-area communication.
    """

    round_idx: int
    findings: List[Finding]
    responses: Dict[str, ModelResponse]
    allocation: Optional[Allocation]
    convergence_metric: float
    marginal_value: float
    converged: bool
    stop: bool
    failures: Dict[str, Optional[FailureType]]
    active_models: Set[str]
    state: str


class DynamicManager:
    """Top-level orchestrator connecting all six areas.

    This class wires together Role Assignment, Load Balancing, Round Progression,
    Convergence Detection, Diminishing Returns, and Failure Handling into a
    coherent management layer.

    It does NOT perform actual model dispatch (that's the orchestrator's job).
    It provides the decision logic: what to dispatch, how to interpret results,
    when to stop.

    Example::

        models = [
            ModelSpec("m1", CapabilityFingerprint(0.1, 0.9, 0.8, 0.7), L=32768, c=0.01),
            ModelSpec("m2", CapabilityFingerprint(0.2, 0.7, 0.9, 0.8), L=32768, c=0.02),
            ModelSpec("m3", CapabilityFingerprint(0.3, 0.6, 0.7, 0.6), L=32768, c=0.015),
        ]
        cfg = DynamicManagementConfig()
        mgr = DynamicManager(models, cfg)

        # Get initial allocation
        tasks = [Task("t1", 5000, 1, 0.5), Task("t2", 8000, 2, 0.9)]
        alloc, cost, balanced = mgr.get_allocation(tasks)

        # After receiving responses, process them
        responses = {...}  # Dict[str, ModelResponse]
        findings = [...]   # List[Finding]
        result = mgr.process_round(responses, findings, tasks, round_cost=1.5)

        # Check if we should continue
        if mgr.fsm.is_terminal:
            print(f"Done: {mgr.fsm.termination_reason}")
    """

    def __init__(
        self,
        models: Sequence[ModelSpec],
        config: Optional[DynamicManagementConfig] = None,
        event_callback: Optional[Callable[[ManagerEvent], None]] = None,
    ) -> None:
        self.config = config or DynamicManagementConfig()
        self.models = list(models)
        self.event_stream = ManagerEventStream(callback=event_callback)

        # Area 1: Role Assignment
        self.role_assignment = RoleAssignment.assign(self.models, self.config)

        # Area 3: Round Progression FSM
        self.fsm = RoundProgressionFSM(self.config)

        # Area 4: Convergence Detection
        self.convergence_detector = ConvergenceDetector(
            self.config, similarity_fn=_finding_similarity
        )

        # Area 5: Diminishing Returns
        self.diminishing_returns = DiminishingReturnsDetector(self.config)

        # Area 6: Failure Handling
        self.failure_handler = FailureHandler(
            self.models,
            self.role_assignment.role_map,
            self.config,
            event_callback=self.event_stream.emit,
        )

        # Correlated failure model
        self.correlated_failures = CorrelatedFailureModel()

        # Round results history
        self._round_results: List[RoundResult] = []

        # Live fingerprint store: tracks observed capability per model across rounds.
        # Initial values come from ModelSpec.fingerprint. Updated after each round
        # from actual output metrics. This is the adaptive routing feedback loop:
        # observe performance → update fingerprint → reallocate next round.
        self._live_fingerprints: Dict[str, CapabilityFingerprint] = {
            m.model_id: m.fingerprint for m in self.models
        }
        # Per-model per-round metrics for fingerprint estimation
        self._round_metrics: Dict[str, List[Dict[str, float]]] = {
            m.model_id: [] for m in self.models
        }

    def get_allocation(
        self, tasks: Sequence[Task]
    ) -> Tuple[Allocation, float, bool]:
        """Get task allocation for the current round.

        Uses Area 2 (Load Balancing) with LIVE fingerprints — allocation
        adapts to observed performance, not just initial estimates. Every
        active model gets work matched to its demonstrated capability.
        No model is excluded for being "weaker."

        Args:
            tasks: Tasks to allocate.

        Returns:
            (allocation, cost, is_balanced)
        """
        active_models = self.get_live_models()
        if not active_models:
            raise RuntimeError("No active models available for allocation")

        lb = LoadBalancer(
            active_models,
            tasks,
            self.role_assignment.role_map,
            self.config,
        )
        return lb.solve()

    def check_dispatch_feasibility(
        self, model: ModelSpec, task_load: float
    ) -> Tuple[bool, float]:
        """Pre-dispatch feasibility check with uncertainty.

        Args:
            model: Target model.
            task_load: Total token demand.

        Returns:
            (should_dispatch, p_feasible)
        """
        # Use a temporary LoadBalancer for the feasibility check
        lb = LoadBalancer(
            [model], [], self.role_assignment.role_map, self.config
        )
        ok, p = lb.dispatch_check(model, task_load)
        if not ok:
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.DISPATCH_BLOCKED,
                    model_id=model.model_id,
                    round_idx=self.fsm.current_round,
                    detail=f"P(feasible)={p:.3f} < threshold={self.config.feasibility_threshold}",
                    metadata={"p_feasible": p, "task_load": task_load},
                )
            )
        elif p < 0.99 and model.L_std > 0:
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.FEASIBILITY_WARNING,
                    model_id=model.model_id,
                    round_idx=self.fsm.current_round,
                    detail=f"P(feasible)={p:.3f} (uncertain L: {model.L}±{model.L_std})",
                    metadata={"p_feasible": p, "task_load": task_load},
                )
            )
        return ok, p

    def process_round(
        self,
        responses: Dict[str, ModelResponse],
        findings: List[Finding],
        tasks: Sequence[Task],
        round_cost: float,
        duration: float = 1.0,
        adoption_delta: float = 0.0,
    ) -> RoundResult:
        """Process a completed round: detect failures, update metrics, advance FSM.

        This is the main entry point after the orchestrator has dispatched tasks
        and collected responses.

        Args:
            responses: Model responses keyed by model_id.
            findings: All findings extracted from responses.
            tasks: Tasks that were allocated this round.
            round_cost: Total cost of this round.
            duration: Wall-clock duration of this round.
            adoption_delta: Delta_r from existing schema.

        Returns:
            RoundResult with all metrics and decisions.
        """
        round_idx = self.fsm.current_round

        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.ROUND_COMPLETE,
                model_id="system",
                round_idx=round_idx,
                detail=f"Processing round {round_idx} with {len(findings)} findings",
            )
        )

        # --- Area 6: Failure detection ---
        failures: Dict[str, Optional[FailureType]] = {}
        critical_failure = False

        for model_id, response in responses.items():
            failure_type = self.failure_handler.detect_failure(response)
            failures[model_id] = failure_type

            if failure_type is not None:
                action = self.failure_handler.get_recovery(
                    model_id, round_idx, failure_type
                )
                self.role_assignment.record_failure(model_id, True)

                if action == RecoveryAction.ABORT:
                    critical_failure = True
            else:
                self.role_assignment.record_failure(model_id, False)

        # Check abort condition
        if self.failure_handler.should_abort():
            critical_failure = True

        # --- Area 4: Convergence detection ---
        self.convergence_detector.add_round_findings(
            round_idx, findings, duration, adoption_delta
        )
        kappa = self.convergence_detector.kappa(round_idx)
        is_converged = self.convergence_detector.converged(round_idx)

        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.CONVERGENCE_CHECK,
                model_id="system",
                round_idx=round_idx,
                detail=f"kappa={kappa:.4f}, converged={is_converged}",
                metadata={"kappa": kappa, "converged": is_converged},
            )
        )

        # --- Area 5: Diminishing returns ---
        # Compute cumulative yield
        cumulative_classes = self.convergence_detector.get_cumulative_classes(round_idx)
        cum_findings_flat = []
        for ec in cumulative_classes:
            cum_findings_flat.extend(ec.members)

        novel_classes = self.convergence_detector._novel_classes(round_idx)
        new_findings_flat = []
        for ec in novel_classes:
            new_findings_flat.extend(ec.members)

        self.diminishing_returns.add_round_from_findings(
            round_idx, cum_findings_flat, new_findings_flat, round_cost
        )
        mu = self.diminishing_returns.marginal_value(round_idx) if round_idx in self.diminishing_returns._cumulative_yields else 0.0
        is_diminished = self.diminishing_returns.stop(round_idx)

        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.STOP_CHECK,
                model_id="system",
                round_idx=round_idx,
                detail=f"mu={mu:.4f}, stop={is_diminished}",
                metadata={"mu": mu, "stop": is_diminished},
            )
        )

        # --- Area 3: FSM transition ---
        event = self.fsm.select_event(
            converged=is_converged,
            diminished=is_diminished,
            critical_failure=critical_failure,
            round_complete=True,
        )
        new_state = self.fsm.transition(event)

        # --- Area 1: Role reassignment (if continuing) ---
        if not self.fsm.is_terminal:
            self.role_assignment.reassign(
                round_idx, self.failure_handler.active_models
            )
            # Update failure handler's role map
            self.failure_handler.role_map = self.role_assignment.role_map

        # --- Adaptive routing feedback: update live fingerprints ---
        # CRITICAL: update fingerprints BEFORE appending the RoundResult.
        # update_fingerprints() builds prior_findings from self._round_results.
        # If the current round is already appended, every finding matches itself
        # via similarity, driving D_decay to 1.0 regardless of actual duplication.
        # CX identified this in the confer round (confidence 0.98).
        if not self.fsm.is_terminal:
            self.update_fingerprints(round_idx, findings, responses)

        result = RoundResult(
            round_idx=round_idx,
            findings=findings,
            responses=responses,
            allocation=None,  # Caller retains allocation reference
            convergence_metric=kappa,
            marginal_value=mu,
            converged=is_converged,
            stop=is_diminished,
            failures=failures,
            active_models=self.failure_handler.active_models,
            state=new_state,
        )
        self._round_results.append(result)

        return result

    def update_fingerprints(
        self,
        round_idx: int,
        findings: List[Finding],
        responses: Dict[str, ModelResponse],
    ) -> None:
        """Update live fingerprints from observed round performance.

        This is the adaptive routing feedback loop. After each round, we compute
        observed capability metrics from actual output and update each model's
        fingerprint. The next round's allocation uses the updated fingerprints.

        The update uses exponential moving average (EMA) to smooth over rounds,
        preventing a single bad round from drastically changing allocation while
        still adapting to sustained performance patterns.

        Observed metrics per model per round:
            D_decay: proportion of findings that are duplicates of prior rounds
                     (higher = more repetitive = faster decay)
            v_bar:   proportion of findings with verified=True
            A:       mean severity of findings (proxy for accuracy/depth)
            C:       number of distinct flaw classes covered / total classes seen

        Every model that produced output gets updated. Models that produced no
        findings still get a valid (low) fingerprint — they are not excluded.
        The 386 principle: even minimal output contributes to coverage.

        Args:
            round_idx: Current round index.
            findings: All findings from this round.
            responses: Model responses keyed by model_id.
        """
        alpha_ema = self.config.fingerprint_ema_alpha if hasattr(self.config, 'fingerprint_ema_alpha') else 0.3

        # Group findings by model
        findings_by_model: Dict[str, List[Finding]] = {}
        for f in findings:
            findings_by_model.setdefault(f.model_id, []).append(f)

        # All flaw classes seen across all models this round
        all_classes_this_round = set()
        for f in findings:
            all_classes_this_round.add(f.flaw_class)
        total_classes = max(len(all_classes_this_round), 1)

        # Prior findings for similarity-based duplicate detection
        prior_findings: List[Finding] = []
        for prev_result in self._round_results:
            prior_findings.extend(prev_result.findings)

        for model_id in self.failure_handler.active_models:
            model_findings = findings_by_model.get(model_id, [])
            old_fp = self._live_fingerprints[model_id]

            if not model_findings:
                # Model produced no findings this round. Give it a minimal
                # but non-zero observed fingerprint. It still participates.
                obs = {
                    "D_decay": 0.5,  # neutral — no data to judge decay
                    "v_bar": 0.0,    # no findings to verify
                    "A": 0.0,        # no severity to measure
                    "C": 0.0,        # no classes covered
                }
            else:
                # D_decay: fraction of findings that are similar to prior rounds.
                # Uses the same similarity function as convergence detection
                # rather than finding_id string matching (which only catches
                # coincidental label reuse, not actual content duplication).
                if prior_findings:
                    duplicates = 0
                    for f in model_findings:
                        for pf in prior_findings:
                            if _finding_similarity(f, pf) >= self.config.tau_sim:
                                duplicates += 1
                                break
                    obs_d = duplicates / len(model_findings)
                else:
                    obs_d = 0.0  # first round, nothing is duplicate

                # v_bar: fraction verified
                verified = sum(1 for f in model_findings if f.verified)
                obs_v = verified / len(model_findings)

                # A: mean severity (depth proxy)
                obs_a = sum(f.severity for f in model_findings) / len(model_findings)

                # C: distinct flaw classes / total classes
                model_classes = set(f.flaw_class for f in model_findings)
                obs_c = len(model_classes) / total_classes

                obs = {"D_decay": obs_d, "v_bar": obs_v, "A": obs_a, "C": obs_c}

            # Store round metrics
            self._round_metrics[model_id].append(obs)

            # EMA update: new = alpha * observed + (1 - alpha) * old
            new_fp = CapabilityFingerprint(
                D_decay=alpha_ema * obs["D_decay"] + (1 - alpha_ema) * old_fp.D_decay,
                v_bar=alpha_ema * obs["v_bar"] + (1 - alpha_ema) * old_fp.v_bar,
                A=alpha_ema * obs["A"] + (1 - alpha_ema) * old_fp.A,
                C=alpha_ema * obs["C"] + (1 - alpha_ema) * old_fp.C,
            )
            self._live_fingerprints[model_id] = new_fp

        # Emit event with updated fingerprints
        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.ROUND_COMPLETE,
                model_id="system",
                round_idx=round_idx,
                detail="Fingerprints updated from observed performance",
                metadata={
                    mid: {
                        "D_decay": round(fp.D_decay, 4),
                        "v_bar": round(fp.v_bar, 4),
                        "A": round(fp.A, 4),
                        "C": round(fp.C, 4),
                    }
                    for mid, fp in self._live_fingerprints.items()
                },
            )
        )

    def get_live_models(self) -> List[ModelSpec]:
        """Return model specs with live-updated fingerprints.

        This replaces the static initial fingerprints with observed ones
        for allocation purposes. The original ModelSpec objects are immutable
        (frozen dataclass) so we create new ones with updated fingerprints.

        Every active model gets a spec. No model is excluded based on
        capability — only transport failures (EMPTY, TIMEOUT, MALFORMED)
        after repeated occurrences can remove a model from the active set.
        """
        live_models = []
        for m in self.models:
            if m.model_id in self.failure_handler.active_models:
                live_fp = self._live_fingerprints.get(m.model_id, m.fingerprint)
                # Create new spec with updated fingerprint
                live_models.append(ModelSpec(
                    model_id=m.model_id,
                    fingerprint=live_fp,
                    tau=m.tau,
                    L=m.L,
                    c=m.c,
                    L_std=m.L_std,
                ))
        return live_models

    @property
    def round_results(self) -> List[RoundResult]:
        """Return all round results."""
        return list(self._round_results)


# ═══════════════════════════════════════════════════════════════════════════════
# REDUCTION PROPERTY VALIDATION (all areas)
# ═══════════════════════════════════════════════════════════════════════════════


def validate_all_reductions(config: Optional[DynamicManagementConfig] = None) -> Dict[str, Dict[str, bool]]:
    """Run all reduction property validators across all areas.

    Returns a nested dict: {area_name: {property_name: passed}}.

    Example::

        results = validate_all_reductions()
        for area, props in results.items():
            for prop, passed in props.items():
                print(f"{area}.{prop}: {'PASS' if passed else 'FAIL'}")
    """
    cfg = config or DynamicManagementConfig()
    results: Dict[str, Dict[str, bool]] = {}

    # Area 1
    results["RoleAssignment"] = {
        "K1": RoleAssignment.validate_k1(
            [ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7))], cfg
        ),
        "Homogeneous": RoleAssignment.validate_homogeneous(4, cfg),
    }

    # Area 2
    results["LoadBalancer"] = {
        "K1": LoadBalancer.validate_k1(cfg),
        "Homogeneous": LoadBalancer.validate_homogeneous(3, cfg),
    }

    # Area 3
    results["RoundProgressionFSM"] = {
        "K1": RoundProgressionFSM.validate_k1(cfg),
        "NoFailures": RoundProgressionFSM.validate_no_failures(cfg),
    }

    # Area 4
    results["ConvergenceDetector"] = {
        "K1": ConvergenceDetector.validate_k1(cfg),
        "NoFindings": ConvergenceDetector.validate_no_findings(cfg),
    }

    # Area 5
    results["DiminishingReturnsDetector"] = {
        "K1": DiminishingReturnsDetector.validate_k1(cfg),
        "Homogeneous": DiminishingReturnsDetector.validate_homogeneous(cfg),
    }

    # Area 6
    results["FailureHandler"] = {
        "K1": FailureHandler.validate_k1(cfg),
        "NoFailures": FailureHandler.validate_no_failures(cfg),
    }

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    print("Running reduction property validations...")
    results = validate_all_reductions()
    all_pass = True
    for area, props in results.items():
        for prop, passed in props.items():
            status = "PASS" if passed else "FAIL"
            print(f"  {area}.{prop}: {status}")
            if not passed:
                all_pass = False

    print()
    if all_pass:
        print("All reduction properties validated.")
    else:
        print("SOME REDUCTION PROPERTIES FAILED.")

    # Quick integration smoke test
    print("\nRunning integration smoke test...")
    models = [
        ModelSpec("claude", CapabilityFingerprint(0.1, 0.9, 0.85, 0.8), L=32768, c=0.015),
        ModelSpec("gpt5", CapabilityFingerprint(0.15, 0.85, 0.9, 0.75), L=32768, c=0.02),
        ModelSpec("gemini", CapabilityFingerprint(0.2, 0.8, 0.8, 0.7), L=32768, c=0.01),
        ModelSpec(
            "codex", CapabilityFingerprint(0.25, 0.75, 0.85, 0.65),
            L=32768, L_std=5000, c=0.02,  # Uncertain token limit
        ),
    ]

    events_received: List[ManagerEvent] = []

    def on_event(event: ManagerEvent) -> None:
        events_received.append(event)

    mgr = DynamicManager(models, event_callback=on_event)
    print(f"  Roles: {mgr.role_assignment.role_map}")
    print(f"  PM: {mgr.role_assignment.pm_model_id}")

    # Check dispatch feasibility for codex (uncertain L)
    codex = models[3]
    ok, p = mgr.check_dispatch_feasibility(codex, 30000)
    print(f"  Codex dispatch feasibility (30k tokens): ok={ok}, P={p:.3f}")

    # Correlated failure setup
    mgr.correlated_failures.set_vulnerability("claude", "gpt5", 0.1)  # different providers
    mgr.correlated_failures.set_vulnerability("gpt5", "codex", 0.7)  # same provider
    mgr.correlated_failures.set_base_failure_rate("claude", 0.02)
    mgr.correlated_failures.set_base_failure_rate("gpt5", 0.05)
    mgr.correlated_failures.set_base_failure_rate("codex", 0.10)
    mgr.correlated_failures.set_base_failure_rate("gemini", 0.03)

    p_class = mgr.correlated_failures.correlated_class_failure(
        ["gpt5", "codex"], {"gpt5": 0.05, "codex": 0.10}
    )
    print(f"  Correlated class failure P(gpt5+codex): {p_class:.4f}")
    print("\nPhase 6 implementation complete.")
