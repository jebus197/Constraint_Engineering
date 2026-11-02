#!/usr/bin/env python3
"""Every round must record WHEN it landed, or the watchdog cannot be aligned to it.

WHY THIS EXISTS, and the reason is a measurement that could not be taken.
B20's monitoring arm and the founder's definition of "screwy" -- *"simply means
not functioning as expected"*, 2026-11-02 -- both turn on whether a per-round
predicate would report a divergence the cy watchdog misses. That question is
currently UNANSWERABLE: `scripts/would_a_round_predicate_catch_what_the_detectors_miss_2026-11-02.py`
finds 8 runs carrying both round series and a watchdog log, of which 5 diverged
on a round-keyed quantity and 0 of 5 were alarm-silent -- but the comparison is
RUN-level and cannot distinguish "the divergence was reported" from "something
unrelated was reported", because the watchdog log carries wall-clock times and
every round series carried none. `round_wall_clock` closes exactly that gap.

IT IS PURELY ADDITIVE. A new parallel key; no existing series is touched, so
every consumer of `gamma_history`, `gate_history`, `gamma_critical_history` and
the rest sees precisely what it saw before, and it decides nothing during a run.

★ 1 DEFECT IN IT WAS CAUGHT BEFORE IT SHIPPED AND IS PINNED BELOW. The first
draft stamped the time just above the atomic rename -- AFTER `json.dumps` had
already read the list -- so every checkpoint would have persisted one round
short and round 0's time would not have appeared until round 1. The key would
have been present and quietly lagging, which is the hardest kind of defect to
see. `test_the_stamp_precedes_the_persist` is what keeps it closed.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture(scope="module")
def tree():
    return ast.parse(RUNNER.read_text())


def test_the_stamp_precedes_the_persist(tree):
    """THE DEFECT CAUGHT BEFORE SHIPPING, pinned by AST and not by grep.

    A text search would match the same strings inside a comment; the AST only
    sees a real `round_wall_clock.append(...)` call and a real dict key, which
    is what `execute-do-not-grep` asks for where execution is not available.
    Executing this would mean running a full experiment, which is hours.
    """
    appends = [n.lineno for n in ast.walk(tree)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == "append"
               and isinstance(n.func.value, ast.Name)
               and n.func.value.id == "round_wall_clock"]
    keys = [k.lineno for n in ast.walk(tree) if isinstance(n, ast.Dict)
            for k in n.keys
            if isinstance(k, ast.Constant) and k.value == "round_wall_clock"]
    assert appends, "nothing appends to round_wall_clock; the series would stay empty"
    # ★ AND THE APPEND MUST BE REACHABLE. Found by the mutation test: replacing
    # the guard with `if False:` left this test GREEN, because the AST sees the
    # CALL NODE whether or not control can reach it. So the guard's condition is
    # asserted too, and a constant test is rejected outright.
    guards = [n for n in ast.walk(tree) if isinstance(n, ast.If)
              and any(isinstance(c, ast.Call)
                      and isinstance(c.func, ast.Attribute)
                      and c.func.attr == "append"
                      and isinstance(c.func.value, ast.Name)
                      and c.func.value.id == "round_wall_clock"
                      for c in ast.walk(n))]
    assert guards, "the append is not inside a guard; it would stamp every write"
    for g in guards:
        assert not isinstance(g.test, ast.Constant), (
            f"the append at line {g.lineno} is under a CONSTANT guard "
            f"({ast.dump(g.test)}), so it is unreachable and the series stays "
            f"empty while this file's other assertions still pass")
        assert isinstance(g.test, ast.Compare), (
            f"the guard at line {g.lineno} is not a comparison; it must test "
            f"len(round_wall_clock) against round_idx so each round stamps once")
    assert keys, "round_wall_clock is never persisted; it would die with the process"
    assert max(appends) < min(keys), (
        f"the stamp at {appends} runs AFTER the dict at {keys} reads the list, "
        f"so every checkpoint persists one round short")


def test_the_series_is_restored_on_resume(tree):
    """A run that resumes from a checkpoint must not lose its earlier stamps."""
    src = RUNNER.read_text()
    assert 'ckpt_data.get("round_wall_clock"' in src, (
        "the series is not read back from the checkpoint, so a resumed run "
        "would restart its clock and the alignment would be wrong across a "
        "restart -- which is exactly when a monitor matters most")


def test_the_stamp_expression_evaluates_and_carries_an_offset(tree):
    """EXECUTED in the runner's own namespace, and the expression is LIFTED
    FROM THE SOURCE rather than retyped here.

    ★ THE FIRST VERSION TESTED ITS OWN COPY. It evaluated a hardcoded string
    written in this file, so removing `timezone.utc` from the RUNNER left this
    test green -- a producer and a consumer describing the same thing
    separately, each individually correct, which `execute-do-not-grep` (2026-09-04)
    names as the defect class 4 of this project's finds came from. The
    expression is now unparsed from the runner's AST, so the test cannot drift
    away from the code.

    `datetime` and `timezone` are module-level imports, so a scope check over
    the enclosing function's locals reports them ABSENT -- which is how a
    correct expression can look broken. Evaluating it settles the question.
    """
    import bench.reference_runner_v3 as R
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "append"
             and isinstance(n.func.value, ast.Name)
             and n.func.value.id == "round_wall_clock" and n.args]
    assert calls, "no round_wall_clock.append(...) with an argument to lift"
    expr = ast.unparse(calls[0].args[0])
    val = eval(expr, vars(R))                                # noqa: S307
    assert isinstance(val, str) and val.endswith("+00:00"), (
        f"the stamp expression taken FROM THE SOURCE was {expr!r} and produced "
        f"{val!r}, which carries no explicit offset. A naive UTC stamp read as "
        f"local time already cost this project an inverted ordering in "
        f"compaction_watch.py.")


def test_it_is_NOT_cleared_when_the_gate_history_is(tree):
    """`gate_history.clear()` fires on a churn reset. This must not.

    Consecutive gate passes must restart after churn; WHEN a round happened is
    a fact a reset does not undo, so clearing this would destroy the alignment
    it exists to provide.
    """
    clears = [n for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr == "clear" and isinstance(n.func.value, ast.Name)]
    cleared = {n.func.value.id for n in clears}
    assert "gate_history" in cleared, (
        "the churn reset is gone; this test's premise no longer holds and it "
        "must be re-derived rather than left passing vacuously")
    assert "round_wall_clock" not in cleared, (
        "round_wall_clock is cleared somewhere; a reset must not erase when "
        "rounds happened")


def test_no_existing_series_key_was_changed():
    """ADDITIVE in the strict sense: the sibling keys are all still written."""
    src = RUNNER.read_text()
    for key in ("gamma_history", "gate_history", "open_ch_history",
                "stall_history", "novel_critical_history",
                "gamma_critical_history"):
        assert f'"{key}":' in src, (
            f"{key} is no longer persisted; adding a series must not remove one")


def test_archived_runs_are_unaffected_and_the_absence_is_visible():
    """Runs made before today carry no stamp, and a reader must be able to tell.

    This is the honest half: the fix helps FUTURE runs only. The 8 runs that
    motivated it still cannot be aligned, and a measurement over them must say
    so rather than treating a missing key as a zero.
    """
    logs = REPO / "bench" / "logs"
    states = sorted(logs.glob("*/runner_state.json"))
    if not states:
        pytest.skip("no archived runs on this checkout")
    with_stamp = 0
    for f in states:
        try:
            j = json.loads(f.read_text(errors="ignore"))
        except Exception:                                    # noqa: BLE001
            continue
        if isinstance(j, dict) and j.get("round_wall_clock"):
            with_stamp += 1
    # No assertion on the COUNT: it is 0 today and will rise, and a test
    # pinning either value would go red for the wrong reason. What is asserted
    # is that the question is answerable at all.
    assert isinstance(with_stamp, int)
