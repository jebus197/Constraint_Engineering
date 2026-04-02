"""dynamic_management.py — Backward-compatible re-export shim.

All classes, functions, and constants that were previously defined in this
6,890-line monolith are now in bench/dm/ submodules. This file re-exports
them so that existing imports continue to work unchanged:

    from dynamic_management import DynamicManager       # runners (bench/ CWD)
    from bench.dynamic_management import DynamicManager  # tests (repo root CWD)

Module structure (bench/dm/):
    _types.py              Config, enums, dataclasses (all shared vocabulary)
    _role_assignment.py    RoleAssignment (Area 1)
    _load_balancer.py      Allocation, LoadBalancer (Area 2)
    _fsm.py                RoundProgressionFSM (Area 3)
    _convergence.py        ConvergenceDetector, finding similarity (Area 4)
    _diminishing_returns.py DiminishingReturnsDetector (Area 5)
    _immune.py             DetectorHealthMonitor (immune detection layer)
    _failure_handler.py    FailureHandler, CorrelatedFailureModel
    _events.py             ManagerEventStream
    _manager.py            DynamicManager (orchestrator, _REMEDIATION_CHAINS,
                           apply_diagnosis, _apply_transform, process_round)
    _validation.py         validate_all_reductions

Run 7b refactor: split for model review coherence. Each module is small
enough (~15-25K tokens) for any AI model to review in a single pass.
The immune layer review boundary is: _types.py + _immune.py + _manager.py.
"""

# ── Types, config, enums, dataclasses ─────────────────────────────────────
from bench.dm._types import (  # noqa: F401
    DynamicManagementConfig,
    Role,
    CapabilityFingerprint,
    ModelSpec,
    Task,
    Finding,
    FailureType,
    RecoveryAction,
    FailureRecord,
    ModelResponse,
    DetectorDiagnosis,
    State,
    Event,
    TerminationReason,
    ManagerEventType,
    ManagerEvent,
    RoundResult,
    FindingEquivalenceClass,
)

# ── Area implementations ──────────────────────────────────────────────────
from bench.dm._role_assignment import RoleAssignment  # noqa: F401
from bench.dm._load_balancer import Allocation, LoadBalancer  # noqa: F401
from bench.dm._fsm import RoundProgressionFSM  # noqa: F401
from bench.dm._convergence import (  # noqa: F401
    ConvergenceDetector,
    _finding_similarity,
    _tokenize_for_similarity,
    _bigrams,
    _STOPWORDS,
)
from bench.dm._diminishing_returns import DiminishingReturnsDetector  # noqa: F401

# ── Immune layer ──────────────────────────────────────────────────────────
from bench.dm._immune import DetectorHealthMonitor  # noqa: F401
from bench.dm._failure_handler import (  # noqa: F401
    FailureHandler,
    CorrelatedFailureModel,
)

# ── Event stream ──────────────────────────────────────────────────────────
from bench.dm._events import ManagerEventStream  # noqa: F401

# ── Orchestrator ──────────────────────────────────────────────────────────
from bench.dm._manager import DynamicManager  # noqa: F401

# ── Validation ────────────────────────────────────────────────────────────
from bench.dm._validation import validate_all_reductions  # noqa: F401
