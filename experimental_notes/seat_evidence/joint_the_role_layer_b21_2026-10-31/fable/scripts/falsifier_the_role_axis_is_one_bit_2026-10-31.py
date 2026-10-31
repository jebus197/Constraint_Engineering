# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_role_layer_b21_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 84024519bdf59662af3e42f37cdf717c58ad9630c0b8215906e5b1c8a8c30e4b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER: round 2 of the_role_layer_b21_2026-10-30 (seat fable).

Claim under test (seat cc2, round 1, load-bearing for its UNIFIED verdict,
and generalised by the joint brief's settled fact 1):

    "the live role dimension carries exactly one discriminating bit:
     arbitrator-that-dispatches-last, or not"
    "Promotion and demotion are not on the role axis at all."

cc2's own refutation condition 1: "A role value other than player_manager
changing an outcome" overturns the claim, and cc2 scoped its instrument to
literal role= kwargs on ModelConfig, naming non-ModelConfig routes as the
scan's weakest link. This falsifier walks exactly that route: the second
Role declaration at bench/dm/_types.py:311, which is live via
run_exp20_confer.py:641 / run_exp35_policy_engine.py:2170 ->
DynamicManager.__init__ (dm/_manager.py:106 RoleAssignment.assign) ->
round completion (dm/_manager.py:600 .reassign; :605 role_map handoff to
FailureHandler).

Imports the REAL modules. Retypes nothing.

Polarity: prints FALSIFIED and raises AssertionError iff the one-bit claim
is genuinely false (a non-PM role value changes an outcome). Exits clean
iff the claim stands.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from bench.dm._failure_handler import FailureHandler
from bench.dm._role_assignment import RoleAssignment
from bench.dm._types import (
    CapabilityFingerprint,
    DynamicManagementConfig,
    FailureType,
    ModelSpec,
    RecoveryAction,
    Role,
)

violations = []
cfg = DynamicManagementConfig()

# --- A: Role.COL is CONSTRUCTED live by the real assignment algorithm. ---
pool = [
    ModelSpec("m_a", CapabilityFingerprint(0.1, 0.9, 0.8, 0.7)),
    ModelSpec("m_b", CapabilityFingerprint(0.2, 0.7, 0.9, 0.8)),
    ModelSpec("m_c", CapabilityFingerprint(0.3, 0.6, 0.7, 0.6)),
]
ra = RoleAssignment.assign(pool, cfg)
roles_assigned = set(ra.role_map.values())
print(f"A: RoleAssignment.assign role_map = { {k: v.value for k, v in ra.role_map.items()} }")
if Role.COL in roles_assigned:
    violations.append(
        "A: Role.COL is assigned to a live seat by RoleAssignment.assign "
        "(bench/dm/_role_assignment.py:150) -- 'collator names the harness, "
        "not a seat' does not hold for the dm declaration."
    )
if len(roles_assigned) >= 3:
    violations.append(
        f"A2: the structural axis carries {len(roles_assigned)} simultaneously "
        "live values (PM, COL, PAR), not 1 bit."
    )

# --- B: capability scoring discriminates COL from PAR numerically. ---
a_col, a_par = cfg.get_alpha(Role.COL), cfg.get_alpha(Role.PAR)
b_col, b_par = cfg.get_baseline(Role.COL), cfg.get_baseline(Role.PAR)
print(f"B: alpha_col={a_col} alpha_par={a_par}")
print(f"B: b_col={b_col} b_par={b_par}")
if not np.allclose(a_col, a_par) or not np.allclose(b_col, b_par):
    violations.append(
        "B: get_alpha/get_baseline return different vectors for COL vs PAR "
        "(bench/dm/_types.py:289-304) -- the scoring that drives reassignment "
        "discriminates between two non-PM role values."
    )

# --- C: identical seat, identical failures, different non-PM role -> ---
# ---    divergent survival (DOWNGRADE_ROLE vs EXCLUDE).              ---
def run_failure_sequence(seat_role):
    models = [
        ModelSpec("pm", CapabilityFingerprint(0.1, 0.9, 0.9, 0.9)),
        ModelSpec("mx", CapabilityFingerprint(0.2, 0.7, 0.7, 0.7)),
        ModelSpec("mo", CapabilityFingerprint(0.3, 0.6, 0.6, 0.6)),
    ]
    role_map = {"pm": Role.PM, "mx": seat_role, "mo": Role.PAR}
    fh = FailureHandler(models, role_map, cfg)
    actions = []
    for rnd in (1, 2, 3):
        act = fh.get_recovery("mx", rnd, FailureType.UNDERPERFORM)
        actions.append(act)
        if act in (RecoveryAction.DOWNGRADE_ROLE, RecoveryAction.EXCLUDE):
            break
    active = getattr(fh, "active_models", None)
    if active is None:
        active = fh._active_models
    return actions, fh.role_map["mx"], ("mx" in active)

acts_col, final_role_col, alive_col = run_failure_sequence(Role.COL)
acts_par, final_role_par, alive_par = run_failure_sequence(Role.PAR)
print(f"C: COL seat: actions={[a.value for a in acts_col]} final_role={final_role_col.value} still_active={alive_col}")
print(f"C: PAR seat: actions={[a.value for a in acts_par]} final_role={final_role_par.value} still_active={alive_par}")

if (acts_col[-1], alive_col) != (acts_par[-1], alive_par):
    violations.append(
        "C: same seat, same repeated UNDERPERFORM, only the non-PM role "
        f"differs: COL -> {acts_col[-1].value} (demoted to {final_role_col.value}, "
        f"still active={alive_col}); PAR -> {acts_par[-1].value} (still "
        f"active={alive_par}). bench/dm/_failure_handler.py:321-331 (IM_F008) "
        "executes a role-keyed DEMOTION. A non-player_manager role value "
        "changes whether the seat survives the run."
    )

if violations:
    print("FALSIFIED")
    raise AssertionError(
        "The one-bit claim is false at system scope:\n  - "
        + "\n  - ".join(violations)
    )
print("CLEAN: no non-PM role value changed any outcome; the one-bit claim stands.")
