"""Every run must record WHY it stopped, not only the ones that converged.

Written 2026-09-09. The founder asked, verbatim: "Preferably all stop reasons
should be recorded to make them easily traceable in the future? Not just after
convergence. Is that technically possible?"

MEASURED BEFORE BUILDING. Across the archive, 23 of 41 completion signals carry an
empty reason -- 56.1%, Wilson [41.0%, 70.1%], Clopper-Pearson [39.7%, 71.5%]. All
23 are INCOMPLETE and all 16 CONVERGED runs carry a reason, so "recorded only on
convergence" is a census result rather than an inference. Structurally the round
loop has 8 `break` statements and only 2 set stop_reason.

THE ROOT CAUSE HAS A PRECEDENT IN THE SAME FILE. The irreducible-queue halt set
`result["convergence_reason"]` and never `brain.state`, so `_save_checkpoint()`
on the following line wrote an empty reason and `signal_complete()` read nothing.
The comment at the gamma-alt gate records that identical fault being repaired on
2026-05-18 -- "previously set only the result dict, so post-mortem tooling read
every hardened convergence as INCOMPLETE" -- and it was repaired for that branch
only. The 2026-09-08 run then wrote status INCOMPLETE with reason "" while its own
report named HALTED_IRREDUCIBLE_QUEUE_ALARM.

These tests EXECUTE signal_complete against constructed states rather than
asserting on source text.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO))
from insect_brain import InsectBrain  # noqa: E402
from bench.dm._types import DynamicManagementConfig  # noqa: E402

RUNNER = REPO / "bench" / "reference_runner_v3.py"


def _brain(tmp_path, **state):
    """Built the way the rest of the suite builds one, rather than a stub.

    signal_complete() reads brain.state, so a real brain with a real BrainState
    is what exercises the code path; a namespace stub would test the test.
    """
    b = InsectBrain(config=DynamicManagementConfig(), logs_dir=tmp_path,
                    source_paths=["x.py"])
    b.initialise(["CC2-SIM"])
    for k, v in state.items():
        setattr(b.state, k, v)
    return b


def test_a_converged_run_still_reports_its_reason(tmp_path):
    b = _brain(tmp_path, converged=True, convergence_reason="GAMMA_GATE", stop_reason="GAMMA_GATE")
    sig = b.signal_complete()
    assert sig["status"] == "CONVERGED"
    assert sig["reason"].strip(), "a converged run must still name its reason"


def test_a_halted_run_reports_the_halt_rather_than_an_empty_string(tmp_path):
    """The 2026-09-08 case: INCOMPLETE with reason '' while the report named the
    alarm. That combination must now be unreachable."""
    b = _brain(tmp_path, converged=False,
               stop_reason="HALTED_IRREDUCIBLE_QUEUE_ALARM")
    sig = b.signal_complete()
    assert sig["status"] == "INCOMPLETE"
    assert sig["reason"] == "HALTED_IRREDUCIBLE_QUEUE_ALARM", sig


def test_an_empty_reason_is_still_possible_at_the_brain_level(tmp_path):
    """ANTI-VACUITY. signal_complete() reports what it is given; the guarantee is
    made by the RUNNER, not here. If this ever passes with a non-empty reason the
    tests above prove nothing, because they would pass whatever was set."""
    b = _brain(tmp_path, converged=False, stop_reason="", convergence_reason="",
               failure_reason="")
    assert b.signal_complete()["reason"] == ""


# --- The runner's guarantee, checked structurally because a full run costs a day.

def test_the_alarm_halt_assigns_to_brain_state_before_the_checkpoint():
    """The precise ordering that was wrong: _save_checkpoint() reads brain.state,
    so an assignment after it would be written nowhere."""
    src = RUNNER.read_text()
    i = src.index("result[\"convergence_reason\"] = IRREDUCIBLE_QUEUE_HALT")
    window = src[i:i + 1400]
    assign = window.find("brain.state.stop_reason = IRREDUCIBLE_QUEUE_HALT")
    save = window.find("brain._save_checkpoint()")
    assert assign != -1, "the alarm halt must record its reason on brain.state"
    assert save != -1, "the alarm halt must still checkpoint"
    assert assign < save, (
        "the assignment must PRECEDE _save_checkpoint(), which reads brain.state; "
        "after it the reason would be written nowhere")


def test_a_fallback_runs_before_signal_complete():
    """Naming each exit individually would miss the 9th break somebody adds
    later, so the guarantee is made once, at the single point of exit."""
    src = RUNNER.read_text()
    call = src.index("signal = brain.signal_complete()")
    before = src[max(0, call - 1800):call]
    assert "brain.state.stop_reason" in before, (
        "nothing sets a fallback stop_reason before the signal is built")
    assert "UNRECORDED_STOP" in before, (
        "an exit that names no cause must SAY so; an empty string is "
        "indistinguishable from a named halt that was never propagated")


def test_the_unrecorded_case_is_distinguishable_from_a_named_halt():
    """'The runner did not record why' is a different and worse condition than
    any named halt, and must not look the same in the archive."""
    src = RUNNER.read_text()
    assert "UNRECORDED_STOP" in src
    assert "HALTED_IRREDUCIBLE_QUEUE_ALARM" in src
    assert "UNRECORDED_STOP" != "HALTED_IRREDUCIBLE_QUEUE_ALARM"
