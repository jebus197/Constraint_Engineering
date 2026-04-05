"""CDSFL Dynamic Management — Types and Configuration Layer.

This module contains all dataclasses, enums, and configuration types used by the
dynamic management subsystem.  It is the foundational types layer: it imports
nothing from the ``bench`` package and can be imported by any module without
risk of circular dependencies.

Extracted from ``bench/dynamic_management.py`` to support modular decomposition
of the management layer while preserving identical semantics.
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    TYPE_CHECKING,
)

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    # Allocation lives in the load-balancing area, not extracted here.
    # Used only as a type annotation in RoundResult.
    from bench.dynamic_management import Allocation


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
    tau_sim: float = 0.33  # finding similarity threshold for equivalence
    # Run 8 calibration: max pairwise sim was 0.553, old 0.8 was unreachable.
    # At 0.33 (centroid-based): 67 clusters from 339 findings (80% churn detected).
    tau_kappa: float = 0.95  # convergence threshold (SEPARATE from gamma)
    eta_veto: float = 0.9  # severity veto threshold (ChatGPT contribution)
    epsilon_conv: float = 1e-8  # zero-denominator regulariser
    min_rounds_for_convergence: int = 2  # r >= this to allow convergence

    # --- Area 5: Diminishing Returns ---
    tau_mu: float = 0.05  # minimum acceptable VCR
    tau_novelty_stop: float = 0.15  # novelty rate below which to stop (cost-decoupled)
    tau_novelty: float = 0.40  # similarity threshold for "related" — calibrated from
    # Exp12 R8 data: genuine duplicates (same function, same bug) score 0.40-0.56,
    # different findings score 0.30-0.40. The gap is narrow, so 0.40 is conservative.
    r_min: int = 2  # minimum rounds before early stop
    smoothing_window: int = 2  # W: VCR smoothing window (CC2 contribution)
    epsilon_cost: float = 1e-8  # cost regulariser for c_r = 0
    # Vocabulary saturation: similarity-independent stop signal.
    # Measures growth rate of cumulative unique vocabulary terms.
    # When growth rate drops below threshold for sustained_window consecutive
    # rounds, the stop predicate fires.  This is immune to the Jaccard
    # semantic-equivalence problem that defeated kappa and novelty_rate.
    # Recalibrated for Exp14: Exp13b showed premature termination at round 4
    # because decomposed dispatch (~629 lines/model/round) produces much less
    # new vocabulary per round than full-artifact dispatch.  Heaps' law β≈0.024
    # means vocabulary was effectively exhausted by the blind round alone.
    # Lowered from 0.10 to 0.04, window from 3 to 5.
    tau_vocab_growth: float = 0.04  # stop when vocab growth rate < 4%
    vocab_sustained_window: int = 5  # require 5 consecutive rounds below threshold

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

    # --- Self-adaptive CDSFL (Exp14: Phases A-E) ---
    # Per-model prompt directives loaded from registry Layer 4 TOML.
    # Dict mapping model_id → additional prompt text prepended to CDSFL.
    per_model_directives: Dict[str, str] = field(default_factory=dict)
    # Immune feedback loop: whether apply_diagnosis() can auto-adjust params.
    immune_feedback_enabled: bool = True
    # Damping: minimum rounds between adjustments to the same parameter.
    immune_damping_rounds: int = 2
    # Maximum characters of per-model prompt modifications (corruption cascade guard).
    max_per_model_directive_chars: int = 500
    # Pre-decompose models that had false-positive blocking in prior experiments.
    pre_decompose_models: Set[str] = field(default_factory=set)
    # No-exclusion mode: ABORT does not trigger FAIL_CRITICAL in the FSM.
    # Run 9 bug: DM internally set critical_failure=True on ABORT, sending
    # the FSM to TERMINAL before the runner could override. With this flag,
    # ABORT is a recoverable action, not a state-machine-ending event.
    no_exclusion_mode: bool = False

    # --- Resolution hysteresis (Run 6 bug 4) ---
    # Require this many consecutive non-pathological rounds before resolving
    # a detected pathology. Prevents flip-flopping when metrics hover near
    # detection thresholds.
    resolution_hysteresis: int = 2

    # --- Resolution parameter (Run 6: convergence validity) ---
    # Severity floor for compound objective Ω computation.
    # Findings with severity < resolution_threshold are excluded from
    # γ_output, A, and Ω, but NOT from the findings log or report.
    resolution_threshold: float = 0.5  # 0.8=fast/critical, 0.3=thorough, 0.0=unbounded
    # Compound objective threshold — per-model benching when Ω < τ
    convergence_omega_tau: float = 0.10
    # Consecutive rounds below τ to declare a model converged
    convergence_omega_window: int = 2

    # --- Context budget (Run 7: IT Crowd fix) ---
    # Maximum chars of prior-findings context to inject per model per round.
    # When accumulated findings exceed this budget, the model gets a "context
    # reset": base code + summary-only findings (IDs + one-line descriptions)
    # instead of full finding text. The model effectively restarts with a
    # clean slate but knows what's been found.
    # Default 80K chars ≈ 20K tokens — leaves room for the base prompt
    # (~120K chars of dynamic_management.py + appendices) within a 200K
    # context window. Models with smaller windows need lower values.
    context_budget_chars: int = 80_000
    # Per-model overrides: {model_label: max_chars}. Models not listed
    # use context_budget_chars. DeepSeek Reasoner needs a lower budget
    # because its CoT consumes output tokens proportional to input size.
    context_budget_overrides: Dict[str, int] = field(default_factory=lambda: {
        "DeepSeek": 30_000,  # Reasoner CoT scales with input — keep lean
        "CC2": 30_000,       # WP4c: match DeepSeek's proven limit
    })

    # --- Live fingerprint update (adaptive routing feedback loop) ---
    # EMA smoothing factor for fingerprint updates. 0.3 = 30% weight on new
    # observation, 70% weight on prior. Lower values = more stable but slower
    # to adapt. Higher values = faster adaptation but noisier allocation.
    fingerprint_ema_alpha: float = 0.3
    # Windowed fingerprint: if > 0, use windowed mean over last N rounds
    # instead of EMA.  EMA collapses to ~0 over 20 rounds (Exp12 finding).
    # Set to 5 for windowed mean; set to 0 to revert to EMA.
    fingerprint_window: int = 5
    # Minimum fingerprint signal: when all models fall below this on all
    # dimensions, switch to round-robin allocation.
    fingerprint_min_signal: float = 0.05

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
        # Exp14 fix (ChatGPT F006, sev 0.89, triple-corroborated):
        # Comprehensive bounds checks for all bounded thresholds.
        if not (0.0 < self.tau_sim <= 1.0):
            raise ValueError(f"tau_sim must be in (0, 1], got {self.tau_sim}")
        if not (0.0 < self.tau_vocab_growth <= 1.0):
            raise ValueError(f"tau_vocab_growth must be in (0, 1], got {self.tau_vocab_growth}")
        if not (0.0 <= self.eta_veto <= 1.0):
            raise ValueError(f"eta_veto must be in [0, 1], got {self.eta_veto}")
        if self.epsilon_conv <= 0:
            raise ValueError(f"epsilon_conv must be > 0, got {self.epsilon_conv}")
        if self.vocab_sustained_window < 1:
            raise ValueError(f"vocab_sustained_window must be >= 1, got {self.vocab_sustained_window}")
        if self.immune_damping_rounds < 0:
            raise ValueError(f"immune_damping_rounds must be >= 0, got {self.immune_damping_rounds}")
        if self.max_per_model_directive_chars < 0:
            raise ValueError(f"max_per_model_directive_chars must be >= 0, got {self.max_per_model_directive_chars}")
        if self.resolution_hysteresis < 1:
            raise ValueError(f"resolution_hysteresis must be >= 1, got {self.resolution_hysteresis}")
        if not (0.0 <= self.resolution_threshold <= 1.0):
            raise ValueError(f"resolution_threshold must be in [0, 1], got {self.resolution_threshold}")
        if self.convergence_omega_tau <= 0:
            raise ValueError(f"convergence_omega_tau must be > 0, got {self.convergence_omega_tau}")
        if self.convergence_omega_window < 1:
            raise ValueError(f"convergence_omega_window must be >= 1, got {self.convergence_omega_window}")
        if self.context_budget_chars < 1000:
            raise ValueError(f"context_budget_chars must be >= 1000, got {self.context_budget_chars}")
        for label, budget in self.context_budget_overrides.items():
            if budget < 1000:
                raise ValueError(f"context_budget_overrides[{label}] must be >= 1000, got {budget}")

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
    proposed_fix: str = ""  # Model's proposed fix (CX: was parsed but discarded)
    verified: bool = False  # Whether finding was independently verified (SymPy, etc.)
    escalated: bool = False  # Escalated to HIL — no programmatic fix possible
    pm_verdict: str = ""  # PM's verdict on this finding (Category 2)
    dedup_of: str = ""  # finding_id this is a duplicate of, if any (Category 2)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND PROGRESSION TYPES
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


# ═══════════════════════════════════════════════════════════════════════════════
# CONVERGENCE DETECTION TYPES
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


# ═══════════════════════════════════════════════════════════════════════════════
# FAILURE HANDLING TYPES
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


@dataclass
class DetectorDiagnosis:
    """Diagnosis from the detector health monitor."""
    detector: str  # "kappa", "mu", "d_decay"
    pathology: str  # human-readable description
    severity: str  # "WARNING", "CRITICAL"
    recommended_action: str  # what to do about it
    evidence: Dict[str, Any] = field(default_factory=dict)
    # IM_F013: Machine-readable key for remediation routing, decoupled from
    # human-readable pathology string. Must match _REMEDIATION_CHAINS keys.
    pathology_key: str = ""
    # SY-1 fix (Run 7b): round index when diagnosis was produced. Enables
    # exact windowed counting in false_positive_rate (replaces proportional-
    # tail approximation).
    round_idx: int = -1


# ═══════════════════════════════════════════════════════════════════════════════
# REAL-TIME MANAGER MONITORING TYPES
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


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATION TYPES
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
    recovery_actions: Dict[str, str] = field(default_factory=dict)  # model_id -> action name (Exp15 fix)
    active_models: Set[str] = field(default_factory=set)
    state: str = ""
