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


def test_it_carries_no_invented_result_whether_outstanding_or_retired():
    """A scheduled measurement with a result invented would be worse than none.

    ★ WIDENED 2026-10-29, AND THE PART THAT MATTERS IS UNCHANGED. This test read
    that the measurement must be outstanding AND the programme OPEN. His ruling
    of 2026-10-19 retired the measurement unrun -- "It cannot work. I told you my
    preference was for staggered dispatch (for models from the same vendor), not
    serialised dispatch!" -- so the programme is now legitimately CLOSED with
    this measurement never having run.

    THE PROHIBITION ON A FABRICATED RESULT IS KEPT EXACTLY AS IT WAS. What is
    relaxed is only the demand that the programme stay OPEN, and that is replaced
    by a demand that the closure be JUSTIFIED: if the programme is CLOSED while
    this measurement has no result, it must carry a retirement, and
    `test_a_retirement_is_more_demanding_than_a_result` in
    test_the_study_announces_itself_2026-10-03.py holds that retirement to his
    ruling, a reason and producers that exist on disk.
    """
    study = _study()
    m = next(x for x in study["measurements"] if x.get("id") == MEASUREMENT_ID)
    assert not m.get("result"), (
        "this measurement has a result but has not been run; a fabricated "
        "outcome is the one thing worse than an unscheduled measurement")
    assert not m.get("headline")
    if study.get("status") != "OPEN":
        assert m.get("retired"), (
            "the programme is CLOSED while this measurement has neither a result "
            "nor a retirement, so it went quiet without either measuring or "
            "deciding not to")


def test_the_hypothesis_is_labelled_as_one():
    """The honest framing must survive, or the measurement loses its point."""
    m = next(x for x in _study()["measurements"] if x.get("id") == MEASUREMENT_ID)
    why = (m.get("why") or "") + (m.get("the_named_loss") or "")
    assert "correlation" in why.lower(), (
        "the entry no longer records that the live change rests on a "
        "correlation rather than a demonstrated cure")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
