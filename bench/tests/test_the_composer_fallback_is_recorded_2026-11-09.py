"""The 10th admission step no longer degrades in silence. B21.

MEASURED, not asserted. `scripts/how_many_places_must_change_to_add_a_model_
2026-10-16.py` computes how a new seat's 10 admission steps behave. Before this
change: 8 ANNOUNCED their default, 1 failed LOUDLY, and exactly 1 was SILENT --
**1 of 10, 10.0000%, Wilson [1.7876%, 40.4150%], Clopper-Pearson
[0.2529%, 44.5016%]**.

THAT ONE WAS DIRECTIVE COMPOSITION. `compose()` RAISES for an unregistered
seat, `_dispatch_single_model_inner` catches it, logs a line, and the run
continues ON A DEGRADED PROMPT. The log line was never the gap: what was
missing is a RECORD against the model's stable identity, which is what every
instrument downstream counts. On 2026-08-30 a seat with no composer entry
composed to 0 characters and nothing reported it -- that incident is quoted in
`bench/routing.py`'s own announcement text.

THE RECORDING IS EXTRACTED, NOT COPIED, and that is the design point rather
than tidiness. `bench/routing.py`'s docstring warns that 2 identity functions
is the producer/consumer drift this project keeps finding, and that an
announcement keyed on a different digest from the decision it describes would
be worse than no announcement. A second copy of the recording is exactly how
that would arrive. So `record_miss` has 1 home and 2 callers:
`resolve_or_alarm` for a table lookup, and the composer fallback for a
composition that raised.

BEHAVIOUR IS UNCHANGED AND THAT IS DELIBERATE. The run still continues on a
degraded prompt. Raising instead would turn a degradation into a dead run,
which the C18 note gives as its own reason for announcing rather than
refusing.

WHAT THIS DOES NOT DO: it does not settle B21. Its 3 options -- consolidate
registration, leave it and revisit after Bench Run 2, or pass a role at
dispatch -- are untouched. This is the independent defect inside the entry.
"""
from __future__ import annotations
import ast

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


@pytest.fixture()
def routing():
    from bench import routing as R
    R.reset_lookup_misses() if hasattr(R, "reset_lookup_misses") else None
    return R


def test_record_miss_exists_and_has_one_home(routing):
    assert callable(getattr(routing, "record_miss", None)), (
        "bench/routing.py exposes no record_miss, so the composer fallback "
        "would need its own copy of the recording -- 2 identity computations, "
        "which this module's own docstring names as the drift to avoid")


def test_resolve_or_alarm_delegates_to_it(routing):
    """1 DEFINITION, 2 CALLERS. A second copy is the defect, not the fix."""
    import ast
    src = (REPO / "bench/routing.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    body = None
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == "resolve_or_alarm":
            body = ast.get_source_segment(src, n)
    assert body, "resolve_or_alarm is gone"
    assert "record_miss(" in body, (
        "resolve_or_alarm no longer delegates, so the recording exists twice")
    assert "_LOOKUP_MISSES.append" not in body, (
        "resolve_or_alarm still appends to the ledger itself, so there are 2 "
        "recording paths and they can drift")


def test_a_miss_is_recorded_and_returns_the_default(routing):
    """EXECUTED. The lookup contract must be unchanged."""
    before = len(routing.lookup_misses()) if hasattr(routing, "lookup_misses") else 0
    got = routing.resolve_or_alarm({"known": 1}, "unknown-seat",
                                   "composer directive-set mapping",
                                   default="FALLBACK")
    assert got == "FALLBACK", f"the default is no longer returned: {got!r}"
    if hasattr(routing, "lookup_misses"):
        after = routing.lookup_misses()
        assert len(after) == before + 1, (
            f"the miss was not recorded: {before} -> {len(after)}")
        assert after[-1]["key"] == "unknown-seat"
        assert after[-1]["identity"], "the record carries no identity"


def test_a_hit_records_nothing(routing):
    """ANTI-VACUITY. A function that recorded every call would pass the test
    above while making the ledger meaningless."""
    before = len(routing.lookup_misses()) if hasattr(routing, "lookup_misses") else 0
    got = routing.resolve_or_alarm({"known": 7}, "known", "whatever", default=0)
    assert got == 7
    if hasattr(routing, "lookup_misses"):
        assert len(routing.lookup_misses()) == before, (
            "a successful lookup was recorded as a miss")


def test_record_miss_returns_an_identity_and_announces_once(routing):
    """The announcement is deduplicated per (what, identity): the composer runs
    once per seat per round, so 20 rounds and 6 seats would print 120 lines for
    1 defect."""
    seen: list = []
    a = routing.record_miss("composer directive set", "seat-x",
                            log=seen.append)
    b = routing.record_miss("composer directive set", "seat-x",
                            log=seen.append)
    assert a == b and a, (a, b)
    assert len(seen) == 1, (
        f"the announcement fired {len(seen)} times for 1 (what, identity); it "
        f"must be announced once and recorded every time")


def _statement_calls(src: str, name: str = "record_miss"):
    """Every line where `name` is called as a WHOLE statement.

    A SUBSTRING IS NOT A CALL, and that is why this helper exists rather than a
    `in` test written inline 3 times. Both of this guard's first 2 reversions
    came back GREEN on 2026-11-09: `None and _cap_identity.record_miss(...)`
    still contains the name, and `pass  # record_miss(...)` begins with `pass`
    so stripping the comment does not help either. The same mid-line-comment
    miss is already recorded against 2026-11-08.

    A call that is the direct value of an expression, assignment or return
    statement runs whenever its block runs. One buried in a sub-expression need
    not. Only the first kind counts here.
    """
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expr, ast.Assign, ast.Return)):
            value = node.value
        else:
            continue
        if not isinstance(value, ast.Call):
            continue
        func = value.func
        called = (func.attr if isinstance(func, ast.Attribute)
                  else getattr(func, "id", ""))
        if called == name:
            out.append(getattr(node, "lineno", 0))
    return out


def _guarded_by_try(src: str, lineno: int) -> bool:
    """True when `lineno` sits inside the BODY of a try statement.

    `"try:" in window[:offset]` was the old test and it only asked whether the
    word appears EARLIER IN THE FILE, which it does whether or not the call is
    inside that try. Ancestry is the actual question.
    """
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for stmt in node.body:
            lo = getattr(stmt, "lineno", 0)
            hi = getattr(stmt, "end_lineno", lo)
            if lo <= lineno <= hi:
                return True
    return False


def test_the_runner_calls_it_at_the_composer_fallback():
    """AN ADDITION NOTHING REACHES IS NOT ADDITIVE."""
    src = (REPO / "bench/reference_runner_v3.py").read_text(encoding="utf-8")
    i = src.find("COMPOSER FALLBACK for")
    assert i > 0, "the composer fallback handler is gone"
    lo = src.count("\n", 0, i) + 1
    live = [n for n in _statement_calls(src) if lo <= n <= lo + 40]
    assert live, (
        "the composer fallback logs and does not RECORD, so this is still the "
        "1 admission step of 10 that degrades in silence")


def test_the_record_cannot_cost_a_round():
    """A record is worth a lost line, never a dead run."""
    src = (REPO / "bench/reference_runner_v3.py").read_text(encoding="utf-8")
    i = src.find("COMPOSER FALLBACK for")
    lo = src.count("\n", 0, i) + 1
    live = [n for n in _statement_calls(src) if lo <= n <= lo + 40]
    assert live, "no unconditional record_miss call in the fallback block"
    assert _guarded_by_try(src, live[0]), (
        "the record is not guarded, so a failure inside it could kill a round "
        "that was already surviving a degraded prompt")

def test_the_producer_can_see_the_record_not_just_the_log():
    """THE MEASUREMENT HAD TO BE FIXED TOO, and that is the finding.

    `scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py`
    classified this step SILENT purely because the string "COMPOSER FALLBACK
    for" appears in the runner. So when the handler was changed to RECORD the
    degradation, the instrument went on reporting 1 of 10 silent: the fix was
    real and the measurement could not see it. That is `execute-do-not-grep`
    applied to the measuring script, which the same function's own note
    records having needed once before.

    The predicate must therefore test for the RECORD. A log line alone leaves
    nothing any downstream instrument can count.
    """
    src = (REPO / "scripts"
           / "how_many_places_must_change_to_add_a_model_2026-10-16.py"
           ).read_text(encoding="utf-8")
    assert "_records_unconditionally" in src, (
        "the producer no longer tests STRUCTURALLY for the record, so a "
        "short-circuited call reads to it as a live one -- which is how 2 of "
        "2 reversions came back green on 2026-11-09")
    assert "ast.parse" in src, (
        "the producer has gone back to a textual predicate")
    assert "_composer_records" in src, (
        "the producer has no separate notion of recording, so the ANNOUNCED "
        "branch cannot exist")


def test_the_silent_count_is_now_zero():
    """EXECUTED. The outcome, not the intention."""
    import subprocess
    r = subprocess.run(
        ["python3", str(REPO / "scripts"
                        / "how_many_places_must_change_to_add_a_model_2026-10-16.py")],
        capture_output=True, text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, r.stderr[-600:]
    assert "SILENT DEGRADE 0" in r.stdout, (
        "the composer step is still counted as a silent degradation; either "
        "the handler stopped recording or the predicate stopped looking")
    assert "FAIL SILENTLY (default or degrade): 0 of 10" in r.stdout, (
        "a new seat still passes through an admission step that fails in "
        "silence")
