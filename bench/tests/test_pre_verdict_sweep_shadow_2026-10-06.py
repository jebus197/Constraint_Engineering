#!/usr/bin/env python3
"""The closing sweep's effect on the verdict is measured, and the verdict is untouched.

THE FOUNDER'S POSITION, 2026-10-06, verbatim: *"The closing sweep is part of the
convergence mechanics of the schema ... It is not just an 'afterthought'"*, and *"Doing
it your way just makes the closing sweep an unfalsifiable loose cannon"*. His
instruction: run the closing sweep BEFORE the verdict, and keep the existing one in
parallel until the new one is tested.

THE RUNNER ALREADY AGREES WITH HIM, IN ITS OWN COMMENTS. Beside the sweep call it says
"The verdict is already recorded above; the sweep can only clean the residual ledger,
never touch convergence", and that the sweep "ATTACHES falsifiers and resolves findings,
and it is the last thing that runs. Two per-round passes therefore never see its
results" -- already costing 15 entries recorded as carrying no falsifier of which 11 do,
a set identical to the one the sweep cleared.

WHAT WAS BUILT IS THE TEST, NOT THE MOVE. Reordering the sweep ahead of the verdict
changes what `converged` means on every run, which is the highest-blast-radius edit
available in `reference_runner_v3.py`. So the gate is REPLAYED against the swept
ledger, using the inputs captured at the real verdict, and both answers are recorded in
`result["pre_verdict_sweep_shadow"]`. If the replay ever disagrees with the recorded
verdict, sweep ORDERING decided a convergence outcome and the reorder is justified by
evidence. If it never disagrees, it is not.

THE PLACEMENT BUG THIS FILE EXISTS TO HOLD. The shadow was first written into the
`except` handler of the sweep's try block, so it would have computed ONLY when the sweep
RAISED -- the one case in which there is no swept ledger to replay against. It would
have produced an empty measurement that looked like a measurement.
`test_the_shadow_runs_on_sweep_SUCCESS_not_failure` is the regression test.
"""
import ast
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import bench.reference_runner_v3 as R  # noqa: E402

SRC = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
TREE = ast.parse(SRC)


def _sweep_try():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Try) and "_post_convergence_sweep(" in (
                ast.get_source_segment(SRC, node) or ""):
            return node
    raise AssertionError("the sweep's try block was not found")


def _holds(seq):
    return any("pre_verdict_sweep_shadow" in (ast.get_source_segment(SRC, n) or "")
               for n in seq)


class TestPlacement:
    def test_the_shadow_runs_on_sweep_SUCCESS_not_failure(self):
        """REGRESSION. Written first into the except handler, where there is no
        swept ledger to replay against."""
        t = _sweep_try()
        assert _holds(t.orelse), (
            "the shadow is not in the else branch, so it does not run when the "
            "sweep succeeds — which is the only case it can measure")
        assert not any(_holds(h.body) for h in t.handlers), (
            "the shadow is in the except handler, so it would compute only when "
            "the sweep RAISED and there is nothing swept to replay against")

    def test_the_shadow_never_assigns_the_verdict(self):
        """It measures; it must not decide. A shadow that wrote `converged`
        would be the reorder, silently."""
        t = _sweep_try()
        for node in t.orelse:
            seg = ast.get_source_segment(SRC, node) or ""
            if "pre_verdict_sweep_shadow" not in seg:
                continue
            for sub in ast.walk(node):
                if isinstance(sub, ast.Assign):
                    for tgt in sub.targets:
                        assert getattr(tgt, "id", None) not in ("converged",
                                                                "conv_reason"), (
                            "the shadow assigns the verdict; it is supposed to "
                            "record what the verdict WOULD have been")

    def test_the_gate_inputs_are_captured_at_the_real_verdict(self):
        assert "_gate_inputs_at_verdict" in SRC, (
            "nothing captures the gate inputs, so the replay would have to "
            "re-derive round-local values and would measure a gate nobody ran")


class TestTheMeasurementIsNotVacuous:
    """If the gate were insensitive to what the sweep changes, the shadow would
    be guaranteed to report 'no difference' and would measure nothing."""

    def _gate(self, unresolved):
        return R._check_gamma_alt_convergence(
            8, 0.9, [0, 0, 0], R.RunnerConfig(
                experiment_name="t", models=["A", "B"]),
            unresolved_critical=unresolved, contested=0, rho_churn=False,
            irreducible_queue=0, gamma_critical=0.9, total_findings=12)

    def test_clearing_criticals_can_change_the_gate(self):
        blocked, reason_blocked = self._gate(3)
        cleared, reason_cleared = self._gate(0)
        assert blocked != cleared, (
            f"the gate returns the same verdict with 3 unresolved criticals and "
            f"with 0 ({blocked} vs {cleared}: {reason_blocked!r} / "
            f"{reason_cleared!r}), so the sweep could never change it and the "
            f"shadow is measuring a foregone conclusion")

    def test_the_blocked_direction_is_the_blocked_one(self):
        blocked, _ = self._gate(3)
        cleared, _ = self._gate(0)
        assert cleared is True and blocked is False, (
            "clearing criticals does not move the gate toward convergence, which "
            "inverts the premise of the whole measurement")


class TestTheRecordIsLegible:
    def test_the_shadow_records_both_verdicts_and_the_comparison(self):
        for key in ("recorded_converged", "replayed_converged",
                    "verdict_would_differ", "unresolved_critical_after_sweep"):
            assert f'"{key}"' in SRC, (
                f"the shadow does not record {key}, so a reader cannot tell "
                f"whether ordering mattered")

    def test_a_difference_is_logged_loudly(self):
        assert "PRE-VERDICT SWEEP SHADOW: the verdict WOULD DIFFER" in SRC, (
            "a disagreement is recorded in the report but never surfaced in the "
            "run log, so nobody watching the run would see it")

    def test_the_shadow_cannot_kill_a_run(self):
        t = _sweep_try()
        found = False
        for node in t.orelse:
            seg = ast.get_source_segment(SRC, node) or ""
            if "pre_verdict_sweep_shadow" in seg and isinstance(node, ast.Try):
                found = True
        assert found, (
            "the shadow is not wrapped in its own try, so a fault in a "
            "measurement could destroy the run it was measuring")
