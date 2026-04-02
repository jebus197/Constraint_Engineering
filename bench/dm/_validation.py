"""_validation.py — Reduction property validation and module self-test.

Extracted from bench/dynamic_management.py (lines ~6774–6891).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from bench.dm._types import (
    DynamicManagementConfig,
    CapabilityFingerprint,
    ModelSpec,
    ManagerEvent,
)
from bench.dm._role_assignment import RoleAssignment
from bench.dm._load_balancer import LoadBalancer
from bench.dm._fsm import RoundProgressionFSM
from bench.dm._convergence import ConvergenceDetector
from bench.dm._diminishing_returns import DiminishingReturnsDetector
from bench.dm._failure_handler import FailureHandler
from bench.dm._manager import DynamicManager


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
