"""`probe()`'s return shape agrees with itself and with its only caller.

WHY THIS EXISTS, AND IT IS NOT A FIXED-WIDTH ASSERTION. B20's actuator cannot be
built until the watchdog's events reach a program: `probe()` returns state and
`say()`s its 13 events to stdout, so the event name is in neither the return
value nor the pulse file, and the mid-run `write_pulse` call passes no verdict.
The recommended repair -- candidate B of the design recorded at B20 -- has
`probe()` return the events it emitted and the mid-run pulse carry the latest.

THE WAY THAT REPAIR GOES WRONG IS NAMED, SO THE ASSERTION TARGETS IT. `probe()`
has **2** return statements, at the stall path and the normal path, and **1**
call site. Widening 1 return and missing the other is the obvious error, and
Python would raise at the unpack -- loudly, which is the good case -- only on
whichever branch happened to run. A stall path taken rarely could carry the old
width for a long time before anybody noticed.

SO THIS PINS CONSISTENCY, NOT A NUMBER. Every return site must agree with every
other and with what the caller unpacks. That is true today at width 6, stays
true at width 7 after candidate B, and fails exactly when the change is made to
1 branch and not the other -- which is the defect, rather than the change.

A FIXED WIDTH WAS THE FIRST DRAFT AND WAS WRONG. Asserting 6 would fail on the
correct future change and would have to be edited by the person making it, which
makes the guard an obstacle rather than a check -- and a guard that must be
edited to let a change through is a guard that gets edited without being read.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
WATCHDOG = REPO / "scripts" / "cy_watchdog_2026-10-02.py"


@pytest.fixture(scope="module")
def tree():
    if not WATCHDOG.is_file():
        pytest.skip("the cy watchdog is not in this checkout")
    return ast.parse(WATCHDOG.read_text(errors="replace"))


def _probe(tree):
    return next((n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == "probe"), None)


def _return_widths(fn):
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Return) and n.value is not None:
            out.append((n.lineno,
                        len(n.value.elts) if isinstance(n.value, ast.Tuple) else 1))
    return out


def _unpack_widths(tree):
    out = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                and getattr(n.value.func, "id", "") == "probe"):
            t = n.targets[0]
            out.append((n.lineno,
                        len(t.elts) if isinstance(t, ast.Tuple) else 1))
    return out


def test_every_return_site_agrees_with_every_other(tree):
    fn = _probe(tree)
    assert fn is not None, "probe() is gone from the watchdog"
    widths = _return_widths(fn)
    assert len(widths) >= 2, (
        f"probe() has {len(widths)} return site(s); this guard exists because it "
        f"has more than 1 and they can disagree")
    distinct = {w for _ln, w in widths}
    assert len(distinct) == 1, (
        f"probe()'s return sites disagree: {widths}. Candidate B of B20's design "
        f"widens this return to carry the events it emitted, and widening 1 "
        f"branch and not the other is the error this guard names -- the stall "
        f"path can carry an old width for a long time before a run takes it.")


def test_the_caller_unpacks_what_probe_returns(tree):
    fn = _probe(tree)
    assert fn is not None
    rw = {w for _ln, w in _return_widths(fn)}
    uw = _unpack_widths(tree)
    assert uw, "nothing calls probe(); the guard would be vacuous"
    for lineno, w in uw:
        assert w in rw, (
            f"the call at line {lineno} unpacks {w} name(s) while probe() "
            f"returns {sorted(rw)}. One of the 2 was changed without the other.")


def test_the_events_are_still_emitted_rather_than_returned(tree):
    """THE PRECONDITION, RECORDED AS A FACT RATHER THAN A COMPLAINT.

    This is deliberately an observation and not a failure. While it holds, no
    program can learn which condition fired and B20's actuator cannot be built.
    When candidate B lands this test is the one that should be REPLACED, by an
    assertion that the events ARE returned -- so it names its own successor
    instead of being deleted silently.
    """
    fn = _probe(tree)
    assert fn is not None
    says = [n for n in ast.walk(fn)
            if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "say"]
    assert says, (
        "probe() no longer emits events via say(); if they are now returned, "
        "replace this test with one asserting the returned contract, which is "
        "candidate B of the design recorded at B20")


class TestTheGuardHasTeethToday:
    def test_it_would_catch_a_disagreeing_return(self):
        """ANTI-VACUITY, in-process. Without this a comparison that always
        found agreement would satisfy the assertions above."""
        src = ("def probe(a):\n"
               "    if a:\n"
               "        return (1, 2, 3)\n"
               "    return (1, 2, 3, 4)\n")
        fn = _probe(ast.parse(src))
        widths = {w for _ln, w in _return_widths(fn)}
        assert len(widths) == 2, (
            "the width reader cannot see 2 disagreeing returns, so the "
            "assertions above would pass on an inconsistent probe()")

    def test_it_would_catch_a_caller_that_disagrees(self):
        src = ("def probe(a):\n"
               "    return (1, 2, 3)\n"
               "x, y = probe(1)\n")
        t = ast.parse(src)
        rw = {w for _ln, w in _return_widths(_probe(t))}
        uw = {w for _ln, w in _unpack_widths(t)}
        assert rw != uw, (
            "the unpack reader cannot see a caller disagreeing with the "
            "return, so that assertion would be vacuous")

# ─────────────────────────────────────────────────────────────────────────────
# THE PULSE SIDE OF THE SAME PRECONDITION, added in the same file rather than a
# 5th guard: it is the same subject -- what candidate B of B20's design rests on.
# ─────────────────────────────────────────────────────────────────────────────

GATE = REPO / "hooks" / "cy_monitor_gate.py"


def test_the_pulse_has_more_than_one_write_site(tree):
    """Candidate B adds the current event to the MID-RUN write. There are 2
    write sites and only the final one carries a verdict today, so adding the
    field to 1 and not the other is the same 2-branch error as the return
    tuple -- and the mid-run site is the one an actuator reads."""
    calls = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call)
             and getattr(n.func, "id", "") == "write_pulse"]
    assert len(calls) >= 2, (
        f"write_pulse is called at {calls}; this guard exists because there is "
        f"more than 1 site and they carry different payloads")


def test_the_gate_reads_pulse_fields_tolerantly():
    """THE ASSUMPTION CANDIDATE B's SAFETY RESTS ON, pinned.

    The design's P-pass concluded that ADDING a field to the pulse cannot break
    a reader, because `hooks/cy_monitor_gate.py` reads every field with `.get()`
    and validates no schema. If that access becomes strict -- `d["verdict"]` --
    the safety argument is void and nothing would say so. This fails if any
    pulse field is read by subscript.
    """
    if not GATE.is_file():
        pytest.skip("the cy monitor gate is not in this checkout")
    g = ast.parse(GATE.read_text(errors="replace"))
    PULSE_FIELDS = {"written_at", "ended", "pid", "rounds", "log", "verdict",
                    "detail", "schema", "pid_alive", "log_bytes"}
    # ★ ONLY READS OF THE PARSED PULSE COUNT, and a first version got that
    # wrong. It flagged 4 subscripts and all 4 read `r`, the row dict the gate
    # BUILDS ITSELF with exactly those keys for the message it prints.
    # Subscripting a dict you just constructed is correct, and flagging it makes
    # the guard fire on healthy code -- the guard-accusing-correct-code shape,
    # with the guard being mine. The pulse is the value of `json.loads`, so only
    # subscripts on THAT name are the assumption this test protects.
    pulse_names = set()
    for n in ast.walk(g):
        if (isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                and ast.unparse(n.value.func).endswith("json.loads")):
            tgt = n.targets[0]
            if isinstance(tgt, ast.Name):
                pulse_names.add(tgt.id)
    assert pulse_names, (
        "no `json.loads` assignment found in the gate, so this test cannot tell "
        "which name holds the pulse and would be vacuous")
    strict = []
    for n in ast.walk(g):
        if (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                and n.slice.value in PULSE_FIELDS
                and isinstance(n.value, ast.Name)
                and n.value.id in pulse_names):
            strict.append((n.lineno, n.slice.value))
    assert not strict, (
        f"the gate reads pulse field(s) by subscript at {strict}. Candidate B of "
        f"B20's design adds a field to the pulse, and its safety argument is "
        f"that every reader uses .get() so an added field cannot break one. "
        f"Strict access voids that argument -- re-run the P-pass before adding "
        f"the field.")


def test_that_tolerance_check_can_actually_fire():
    """ANTI-VACUITY. A detector that found no subscripts because it looks for
    the wrong node would pass whatever the gate did."""
    g = ast.parse('import json\nd = json.loads(s)\nx = d["verdict"]\n')
    found = [n.slice.value for n in ast.walk(g)
             if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)]
    assert "verdict" in found, (
        "the subscript detector cannot see a strict read, so the tolerance "
        "assertion above would be vacuous")
