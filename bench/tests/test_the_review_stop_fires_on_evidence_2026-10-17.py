#!/usr/bin/env python3
"""The human-review stop must fire on evidence, not on a flag -- entry B27.

HIS DESIGN, 2026-10-11: a human review stop "should only be triggered if there is
substantial evidence that a an experimental run is unlikely to converge under the
given conditions and with the available resources ... including mechanical errors,
number of rounds in any given experiment, available compute resources etc."

WHAT THIS FILE REFUSES TO DO. It does not assert on the runner's SOURCE TEXT. A
test that greps for a function name proves only that the module describes itself
consistently, which is the `execute-do-not-grep` failure this project has now hit
four separate times. So the predicate is CALLED against the real archive, and the
two call sites are verified STRUCTURALLY through the abstract syntax tree -- which
is the shape of the code the interpreter runs, not a string that happens to appear
in a comment.

PINNED AS A SET, NOT A COUNT. The archive grows, so "28 converged runs" is a fact
about today. What must never change is that the SET of converged runs the predicate
would interrupt stays EMPTY, and that specific named runs known to have converged
remain in the population being checked. A count cannot tell a new archived run from
a regression that silently stops checking one.
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.hil_review_trigger import RunEvidence, Thresholds, assess  # noqa: E402

RUNNER = REPO / "bench" / "reference_runner_v3.py"
REPLAY = REPO / "scripts" / "would_the_review_stop_have_fired_2026-10-17.py"

#: Runs known from their own reports to have CONVERGED. Interrupting any of these
#: is a false pause, which destroys the measurement the run exists to produce.
#: Named individually so that a replay which stops examining one fails loudly
#: instead of quietly shrinking its denominator.
MUST_NOT_INTERRUPT = (
    "leg3_final_shakedown_20261015T220118Z",
    "exp44_evidence_locationkey_live_20260727T002",
    "exp47_divergence_locationkey_live_20260728T2",
    "free_run2_severity_spec_20261015T073418Z_20261",
)


def _load_replay():
    spec = importlib.util.spec_from_file_location("b27_replay", REPLAY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rows():
    mod = _load_replay()
    out = []
    for p in sorted((REPO / "bench" / "logs").rglob("*_report.json")):
        if "sandbox_harvest" in str(p):
            continue
        try:
            row = mod.replay(p, Thresholds())
        except Exception:                                          # noqa: BLE001
            continue
        if row["rounds_recorded"] >= 2:
            out.append(row)
    return out


# ── The decision itself, executed ─────────────────────────────────────────────

def test_a_converging_run_is_never_paused():
    """Rising critical gamma above threshold is not evidence of a stall."""
    v = assess(RunEvidence(
        round_idx=4, max_rounds=21, gamma_critical=0.42,
        gamma_critical_threshold=0.30, gamma_critical_history=(0.10, 0.25, 0.42),
        total_findings=20, mechanical_faults=1))
    assert v.should_pause is False
    assert v.clause is None


def test_a_flat_late_run_with_no_room_is_paused():
    v = assess(RunEvidence(
        round_idx=16, max_rounds=21, gamma_critical=0.05,
        gamma_critical_threshold=0.30, gamma_critical_history=(0.049, 0.050, 0.050),
        total_findings=30, mechanical_faults=2,
        elapsed_s=26000, wall_clock_cap_s=28800))
    assert v.should_pause is True
    assert v.clause == "STALLED_AND_OUT_OF_ROOM"
    assert any("round budget is spent" in r for r in v.reasons)
    assert any("cannot close" in r or "rounds needed" in r or "against" in r
               for r in v.reasons)


def test_a_mechanically_broken_run_is_paused_early():
    """Mostly-malfunction output does not improve with more rounds."""
    v = assess(RunEvidence(
        round_idx=2, max_rounds=21, gamma_critical=0.0,
        gamma_critical_threshold=0.30, total_findings=10, mechanical_faults=7))
    assert v.should_pause is True
    assert v.clause == "MECHANICALLY_BROKEN"


def test_a_single_fault_cannot_pause_a_run():
    """The share needs a floor, or 1 of 1 fires the clause."""
    v = assess(RunEvidence(
        round_idx=2, max_rounds=21, gamma_critical=0.0,
        gamma_critical_threshold=0.30, total_findings=1, mechanical_faults=1))
    assert v.clause != "MECHANICALLY_BROKEN"


def test_before_the_earliest_round_nothing_fires():
    v = assess(RunEvidence(
        round_idx=1, max_rounds=21, gamma_critical=0.0,
        gamma_critical_threshold=0.30, earliest_round=3))
    assert v.should_pause is False
    assert any("earliest" in r for r in v.reasons)


def test_one_observation_is_unknown_progress_not_zero_progress():
    """A run with no trend must not be called stalled."""
    v = assess(RunEvidence(
        round_idx=18, max_rounds=21, gamma_critical=0.01,
        gamma_critical_threshold=0.30, gamma_critical_history=(0.01,),
        total_findings=4))
    assert v.should_pause is False
    assert any("UNKNOWN" in r for r in v.reasons)


def test_a_degenerate_budget_does_not_raise_or_fire():
    v = assess(RunEvidence(round_idx=0, max_rounds=0, gamma_critical=0.0,
                           gamma_critical_threshold=0.30))
    assert v.should_pause is False


# ── It reads the DECIDING series, which is the defect that was made ───────────

def test_the_decision_follows_the_critical_series_not_the_all_series():
    """The old field names are GONE, so the wrong series cannot be passed.

    Measured 2026-10-17: feeding the all-findings series produced 2 false pauses
    out of 28 converged runs, because exp44's all-findings gamma sat flat while
    its critical gamma climbed 0.1803 -> 0.4316 on the way to converging.
    """
    with pytest.raises(TypeError):
        RunEvidence(round_idx=4, max_rounds=21, gamma=0.42,       # type: ignore[call-arg]
                    gamma_threshold=0.30)                          # noqa: B026
    v = assess(RunEvidence(
        round_idx=16, max_rounds=21, gamma_critical=0.42,
        gamma_critical_threshold=0.30,
        gamma_critical_history=(0.40, 0.41, 0.42), total_findings=20))
    assert v.should_pause is False, (
        "a critical series ABOVE threshold must never pause, whatever the "
        "all-findings series is doing")


# ── Against the real archive ──────────────────────────────────────────────────

def test_it_interrupts_no_run_that_actually_converged():
    rows = _rows()
    assert rows, "no archived reports replayed -- the check could not be performed"
    converged = [r for r in rows if r["converged_at"] is not None]
    assert converged, "no converged run in the archive, so the question is unasked"
    interrupted = sorted(r["run"] for r in converged if r["first_pause"])
    assert interrupted == [], (
        "the predicate would have INTERRUPTED these converged runs, which is a "
        f"false pause and destroys their measurement: {interrupted}"
    )


def test_the_named_converged_runs_are_still_being_checked():
    """A shrinking denominator must not read as a pass."""
    seen = {r["run"] for r in _rows() if r["converged_at"] is not None}
    missing = [
        name for name in MUST_NOT_INTERRUPT
        if not any(s.startswith(name) or name.startswith(s) for s in seen)
    ]
    assert missing == [], (
        f"these runs converged but are no longer in the replayed population, so "
        f"the false-pause check has stopped covering them: {missing}"
    )


def test_it_still_catches_a_run_that_did_not_converge():
    """An inert predicate is not additive: it must fire on something real."""
    rows = _rows()
    stalled = [r for r in rows if r["converged_at"] is None]
    caught = sorted(r["run"] for r in stalled if r["first_pause"])
    assert caught, (
        "the predicate fires on NO non-converged archived run, so enabling the "
        "facility would pause nothing and the gate would be inert"
    )


# ── Both call sites are gated, verified on the syntax tree ───────────────────

def _hil_review_guards(tree: ast.AST) -> list[ast.If]:
    """Every `if` whose test reads cfg.hil_review."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        for sub in ast.walk(node.test):
            if (isinstance(sub, ast.Attribute) and sub.attr == "hil_review"
                    and isinstance(sub.value, ast.Name) and sub.value.id == "cfg"):
                out.append(node)
                break
    return out


def _calls_assess(node: ast.AST) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr == "assess":
                return True
    return False


def _exit_42_nodes(node: ast.AST) -> list[ast.Call]:
    out = []
    for sub in ast.walk(node):
        if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                and sub.func.attr == "exit"
                and sub.args and isinstance(sub.args[0], ast.Constant)
                and sub.args[0].value == 42):
            out.append(sub)
    return out


def test_both_call_sites_exist_and_consult_the_predicate():
    tree = ast.parse(RUNNER.read_text(errors="ignore"))
    guards = _hil_review_guards(tree)
    assert len(guards) >= 2, (
        f"expected both human-review call sites to test cfg.hil_review, found "
        f"{len(guards)}"
    )
    ungated = [g.lineno for g in guards if not _calls_assess(g)]
    assert ungated == [], (
        f"these cfg.hil_review blocks do not consult the evidence predicate, so "
        f"they still fire on the flag alone: lines {ungated}"
    )


def test_no_halt_is_reachable_without_the_verdict_being_checked():
    """A `sys.exit(42)` under the flag must sit inside a should_pause branch."""
    tree = ast.parse(RUNNER.read_text(errors="ignore"))
    bad = []
    for guard in _hil_review_guards(tree):
        for exit_call in _exit_42_nodes(guard):
            # Walk the guard looking for an `if`/`else` whose test mentions the
            # verdict and which CONTAINS this exit.
            protected = False
            for node in ast.walk(guard):
                if not isinstance(node, ast.If):
                    continue
                mentions = any(
                    isinstance(s, ast.Attribute) and s.attr == "should_pause"
                    for s in ast.walk(node.test)
                )
                if not mentions:
                    continue
                if any(e is exit_call for b in (node.body, node.orelse)
                       for n in b for e in _exit_42_nodes(n)):
                    protected = True
                    break
            if not protected:
                bad.append(exit_call.lineno)
    assert bad == [], (
        f"a human-review halt is reachable without the verdict being consulted, "
        f"at line(s) {bad}: the flag alone would stop the run"
    )


def test_the_uncalibrated_caveat_travels_into_the_report():
    """A pause must say its thresholds are judgements, not measurements."""
    v = assess(RunEvidence(
        round_idx=16, max_rounds=21, gamma_critical=0.05,
        gamma_critical_threshold=0.30, gamma_critical_history=(0.049, 0.05, 0.05),
        total_findings=30, mechanical_faults=2))
    fields = v.as_report_fields()
    assert fields["hil_should_pause"] is True
    assert fields["hil_clause"] == "STALLED_AND_OUT_OF_ROOM"
    assert fields["hil_reasons"], "a pause with no reasons is not evidence-based"
    assert "DEFAULTS" in fields["hil_threshold_caveat"]
    assert Thresholds().calibrated is False, (
        "calibrated must stay False until the thresholds are FITTED to runs that "
        "paused or burned out; setting it from a judgement is the thing it exists "
        "to prevent"
    )
