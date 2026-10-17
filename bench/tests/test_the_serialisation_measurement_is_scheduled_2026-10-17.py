#!/usr/bin/env python3
"""The serialisation cure is a hypothesis, and the measurement is now scheduled.

HIS INSTRUCTION, 2026-10-05: *"Then that measurement should be added to our
outstanding programme of study."* Task C5.

WHAT WAS LIVE AND WHAT WAS NOT. The scheduling change was made -- free seats
sharing one subscription are dispatched one at a time -- and the project labelled
that change itself *"a hypothesis with strong correlational support, not a
demonstrated cure"*. The correlation behind it was measured at p = 1.6e-7, which
is strong evidence that the failures are MATCHED across seats sharing a
subscription and NO evidence that serialising them removes the cause. The
measurement that would settle it was on neither the master task list nor the
programme of study, so nothing scheduled could ever settle it. It stayed
untracked for 12 days.

WHAT IS GUARDED HERE. Not the outcome -- the measurement has not been run. What
is guarded is that it is SCHEDULED: present in the programme with a design, and
visible as outstanding rather than quietly marked done. The programme's own hook
reads this file and now reports "1 of 13 measurements outstanding" by name,
where before it reported that every measurement had a result.
"""
from __future__ import annotations

import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
STUDY = REPO / "experimental_notes" / "STUDY_IN_FLIGHT.json"

MEASUREMENT_ID = "serialisation_cures_matched_failures"


def _study() -> dict:
    return json.loads(STUDY.read_text(encoding="utf-8"))


def test_the_programme_file_is_readable():
    assert STUDY.is_file(), "the programme of study is missing"
    d = _study()
    assert isinstance(d.get("measurements"), list) and d["measurements"]


def test_the_measurement_is_in_the_programme():
    ids = {m.get("id") for m in _study()["measurements"]}
    assert MEASUREMENT_ID in ids, (
        f"his instruction of 2026-10-05 was to add this measurement to the "
        f"outstanding programme of study. Present ids: {sorted(ids)}")


def test_it_carries_his_ruling_and_a_design():
    m = next(x for x in _study()["measurements"] if x.get("id") == MEASUREMENT_ID)
    assert "2026-10-05" in (m.get("founder_ruling") or ""), (
        "the entry does not cite the ruling that put it there")
    design = m.get("design") or ""
    assert "both" in m.get("what", "").lower() or "BOTH" in m.get("what", ""), (
        "the measurement must dispatch BOTH ways; one arm settles nothing")
    assert "scheduling" in design.lower(), (
        "the design does not say the arms differ only in scheduling, which is "
        "the whole comparison")
    assert "free" in design.lower(), (
        "the design does not record that free seats keep the cost at zero")


def test_it_is_outstanding_rather_than_quietly_closed():
    """A scheduled measurement with a result invented would be worse than none."""
    m = next(x for x in _study()["measurements"] if x.get("id") == MEASUREMENT_ID)
    assert not m.get("result"), (
        "this measurement has a result but has not been run; a fabricated "
        "outcome is the one thing worse than an unscheduled measurement")
    assert not m.get("headline")
    assert _study().get("status") == "OPEN", (
        "the programme is closed while a measurement is outstanding")


def test_the_hypothesis_is_labelled_as_one():
    """The honest framing must survive, or the measurement loses its point."""
    m = next(x for x in _study()["measurements"] if x.get("id") == MEASUREMENT_ID)
    why = (m.get("why") or "") + (m.get("the_named_loss") or "")
    assert "correlation" in why.lower(), (
        "the entry no longer records that the live change rests on a "
        "correlation rather than a demonstrated cure")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
