# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_role_layer_b21_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 37a9c6dd0b5bc56ac67825cb2884b76263b77555e7e5796e79f6d9afdd5fb7c9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The structural role axis DOES carry promotion and demotion. Pin it.

JOINT ROUND `the_role_layer_b21_2026-10-30`, seat fable, round 2.

The joint brief lists as settled, measured by both seats: "`bench/routing.py` --
the mechanism that actually promotes and demotes -- contains 0 occurrences of
`role` ... Promotion and demotion are not on the role axis at all." The first
clause is true of `bench/routing.py`. The GENERALISATION is false, and these
tests are the execution that shows it: `bench/dm/` moves seats between role
values on failure and on measured capability.

  * `FailureHandler.get_recovery` maps a repeated UNDERPERFORM to
    `RecoveryAction.DOWNGRADE_ROLE` and MUTATES `role_map`, COL -> PAR, then
    escalates PAR -> EXCLUDE because PAR has no lower role
    (`bench/dm/_failure_handler.py`, the `IM_F008` branch).
  * `RoleAssignment.reassign` re-chooses COL between rounds on capability
    fingerprints, holding PM static for the run duration (HARD constraint C3).
  * `LoadBalancer._eligibility_mask` gates which seats may receive tasks on the
    same role values -- PM is excluded from standard tasks when K > 1.

WHY IT MATTERS, AND IT IS THE CAVEAT'S OWN QUESTION. The founder's caveat says
the football framing was adopted "to help us decide how things should be
organised, and when models should be demoted/promoted", and asks what the
scaffolding held up. The answer is not "nothing": it holds up these three
mechanisms, all keyed on role IDENTITY. A rename that moved the dispatch
vocabulary (`experiment_11_orchestrator.Role`) without moving this one would
leave demotion keyed on names no longer used, and nothing would say so. These
tests make that loud.

They pin BEHAVIOUR (a demotion happens, keyed on role) and NOT the spelling, so
they survive whichever vocabulary the founder rules for -- they fail only if the
demotion mechanism stops being role-keyed.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.dm._failure_handler import FailureHandler          # noqa: E402
from bench.dm._load_balancer import LoadBalancer              # noqa: E402
from bench.dm._role_assignment import RoleAssignment          # noqa: E402
from bench.dm._types import (                                 # noqa: E402
    CapabilityFingerprint, DynamicManagementConfig, FailureType, ModelSpec,
    RecoveryAction, Role,
)


def _models() -> list[ModelSpec]:
    return [
        ModelSpec("m1", CapabilityFingerprint(0.9, 0.9, 0.9, 0.9)),
        ModelSpec("m2", CapabilityFingerprint(0.5, 0.8, 0.6, 0.5)),
        ModelSpec("m3", CapabilityFingerprint(0.2, 0.3, 0.4, 0.3)),
    ]


class TestDemotionIsRoleKeyed:
    def test_a_repeated_failure_demotes_a_seat_on_the_role_axis(self):
        cfg = DynamicManagementConfig()
        fh = FailureHandler(
            _models(), {"m1": Role.PM, "m2": Role.COL, "m3": Role.PAR}, cfg)
        assert fh.role_map["m2"] is Role.COL

        first = fh.get_recovery("m2", 1, FailureType.UNDERPERFORM)
        assert first is RecoveryAction.RETRY
        assert fh.role_map["m2"] is Role.COL, "a single failure must not demote"

        second = fh.get_recovery("m2", 2, FailureType.UNDERPERFORM)
        assert second is RecoveryAction.DOWNGRADE_ROLE
        assert fh.role_map["m2"] is Role.PAR, (
            "the demotion is a mutation OF THE ROLE MAP -- this is the "
            "promotion/demotion semantics living on the role axis")

    def test_the_bottom_role_escalates_to_exclusion_rather_than_no_op(self):
        cfg = DynamicManagementConfig()
        fh = FailureHandler(
            _models(), {"m1": Role.PM, "m2": Role.COL, "m3": Role.PAR}, cfg)
        for r in (1, 2):
            fh.get_recovery("m2", r, FailureType.UNDERPERFORM)
        assert fh.role_map["m2"] is Role.PAR
        third = fh.get_recovery("m2", 3, FailureType.UNDERPERFORM)
        assert third is RecoveryAction.EXCLUDE
        assert "m2" not in fh.active_models

    def test_pm_is_static_and_col_is_the_reassignable_one(self):
        cfg = DynamicManagementConfig()
        ra = RoleAssignment.assign(_models(), cfg)
        assert ra.role_map["m1"] is Role.PM
        assigned = {r for r in ra.role_map.values()}
        assert Role.COL in assigned, (
            "the collator value IS constructed -- on the dm declaration, which "
            "an AST scan of ModelConfig(role=...) call sites cannot see")
        pm_before = ra.pm_model_id
        ra.reassign(1, {"m1", "m2", "m3"})
        assert ra.pm_model_id == pm_before, "PM static for the run (HARD C3)"

    def test_task_admissibility_is_gated_on_the_same_role_values(self):
        cfg = DynamicManagementConfig()
        models = _models()
        from bench.dm._types import Task
        tasks = [Task(task_id="t1", token_demand=1.0, flaw_class=1, criticality=0.5)]
        lb = LoadBalancer(
            models, tasks, {"m1": Role.PM, "m2": Role.COL, "m3": Role.PAR}, cfg)
        mask = lb._admissibility_mask()
        # PM is excluded from standard tasks when more than one seat is in play.
        assert mask[0][0] == 0, "PM excluded from standard tasks when K > 1"
        assert mask[0][1] == 1 and mask[0][2] == 1, "COL and PAR are eligible"
