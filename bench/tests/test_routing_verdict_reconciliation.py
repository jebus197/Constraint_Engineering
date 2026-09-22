"""The ladder's tool verdict must overwrite a stale pre-routing UNTOOLABLE.

Guards `reconcile_routing_verdict` (bench/reference_runner_v3.py) and its
wiring inside `_apply_routing`.

THE DEFECT, measured on commissioning_arm4_prose_20260922T053349Z: 6 of 6
entries reading falsifier_verdict="UNTOOLABLE" carry routing_history verdict
"ERROR" with a non-empty body. Their falsifier was WRITTEN by a routing rung and
CRASHED under the runner's own decider -- and the entry still says nothing was
ever attached. `_rejection_lines` branches on that field to build the corrective
instruction shipped to every seat in round K+1, so all 6 were told to write a
falsifier instead of to fix the one that crashed.

An addition nothing reaches is not additive, so the wiring itself is asserted
here, not only the helper's behaviour.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from bench.reference_runner_v3 import (
    EQUIPMENT_FAILURE_VERDICTS,
    ROUTABLE_INSTRUMENT_FAULTS,
    _apply_routing,
    _rejection_lines,
    reconcile_routing_verdict,
)
from bench.routing import RoutingResult

REPO = Path(__file__).resolve().parents[2]
ARM4 = (REPO / "bench" / "logs" / "commissioning_arm4_prose_20260922T053349Z"
        / "commissioning_arm4_prose_report.json")


def _res(verdict, code, resolved=False):
    return RoutingResult("C0001", verdict, resolved, "Codex", code, rungs_tried=2)


def test_executed_and_crashed_is_relabelled_error():
    e = {"falsifier_verdict": "UNTOOLABLE"}
    assert reconcile_routing_verdict(e, _res("ERROR", "assert False\n")) is True
    assert e["falsifier_verdict"] == "ERROR"
    assert e["routing_verdict_reconciled"] == "UNTOOLABLE->ERROR"


def test_relabel_cannot_cross_a_behavioural_boundary():
    """UNTOOLABLE and ERROR are co-members of both sets the runner branches on,
    so the relabel changes the report and the feedback and nothing else."""
    for s in (EQUIPMENT_FAILURE_VERDICTS, ROUTABLE_INSTRUMENT_FAULTS):
        assert {"UNTOOLABLE", "ERROR"} <= set(s)


def test_no_source_leaves_untoolable_standing():
    """A ladder that produced nothing has not refuted the pre-routing label."""
    e = {"falsifier_verdict": "UNTOOLABLE"}
    assert reconcile_routing_verdict(e, _res("ERROR", "")) is False
    assert e["falsifier_verdict"] == "UNTOOLABLE"


@pytest.mark.parametrize("ladder", ["REFUTED", "INTEGRITY_VIOLATION", "DUPLICATE"])
def test_verdicts_outside_the_equipment_set_are_recorded_not_written(ladder):
    """Writing REFUTED back would move the entry out of EQUIPMENT_FAILURE_VERDICTS
    and change demotion behaviour. That dominance is unmeasured, so it is
    recorded for a human rather than acted on."""
    e = {"falsifier_verdict": "UNTOOLABLE"}
    assert reconcile_routing_verdict(e, _res(ladder, "assert False\n")) is False
    assert e["falsifier_verdict"] == "UNTOOLABLE"
    assert e["routing_verdict_unreconciled"] == ladder


def test_a_resolved_ladder_is_left_to_the_confirmed_path():
    e = {"falsifier_verdict": "UNTOOLABLE"}
    assert reconcile_routing_verdict(
        e, _res("CONFIRMED", "assert False\n", resolved=True)) is False
    assert e["falsifier_verdict"] == "UNTOOLABLE"


def test_a_non_untoolable_entry_is_never_touched():
    for v in ("CONFIRMED", "REFUTED", "ERROR", "NON_DISCRIMINATING", ""):
        e = {"falsifier_verdict": v}
        assert reconcile_routing_verdict(e, _res("ERROR", "x\n")) is False
        assert e["falsifier_verdict"] == v


def test_the_helper_is_actually_wired_into_apply_routing():
    """An addition nothing calls is not additive."""
    src = inspect.getsource(_apply_routing)
    assert "reconcile_routing_verdict(e, result)" in src


def test_the_feedback_line_flips_to_the_instruction_that_applies():
    """The consequence, end to end: the panel stops being told to write a
    falsifier that was already written and already crashed."""
    e = {"falsifier_verdict": "UNTOOLABLE"}
    before = " ".join(_rejection_lines(e))
    assert "nothing runnable was attached" in before
    assert "did not run to a verdict" not in before

    reconcile_routing_verdict(e, _res("ERROR", "assert False\n"))
    after = " ".join(_rejection_lines(e))
    assert "did not run to a verdict" in after
    assert "nothing runnable was attached" not in after


@pytest.mark.skipif(not ARM4.is_file(), reason="arm 4 archive not present")
def test_every_arm4_untoolable_would_have_been_relabelled():
    """Replay the real archive through the helper. All 6 flip."""
    ents = json.loads(ARM4.read_text())["registry"]["entries"]
    flipped = []
    for cid, e in sorted(ents.items()):
        if (e.get("falsifier_verdict") or "").strip().upper() != "UNTOOLABLE":
            continue
        rh = [s for s in (e.get("routing_history") or []) if isinstance(s, dict)]
        assert rh, f"{cid}: UNTOOLABLE with no routing history"
        last = rh[-1]
        replay = dict(e)
        if reconcile_routing_verdict(
                replay,
                _res(last.get("verdict"), last.get("last_falsifier_code") or "")):
            flipped.append(cid)
    assert flipped == ["C0002", "C0005", "C0006", "C0011", "C0012", "C0015"], flipped
