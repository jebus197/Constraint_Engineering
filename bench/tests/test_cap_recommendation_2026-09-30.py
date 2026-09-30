"""The raise-the-cap prompt must fire when convergence was in reach, and not otherwise.

THE FOUNDER'S RULING, 2026-09-30: *"Go with 10 -- with a recommendation to the
reviewer to set a higher cap if convergence appears within direct reach."*

THE CASE IT EXISTS FOR, and this file checks it against the ACTUAL RUN rather
than a fixture alone. `commissioning_arm1_panel_20260929T214647Z` used all 8 of
its 8 rounds and stopped with `gamma_critical` at 0.29 against a configured
`gamma_alt_threshold` of 0.30 -- short by 0.01 -- while carrying 3 unverified
criticals, which is the A4 fail-safe refusing the zero-critical streak. Its
novelty was still RISING, at 9 new findings in the last round. That run had
neither converged nor failed: it ran out of budget 1 round from the gate, and
nothing in the artefact said so.

WHAT THIS FILE WILL NOT ACCEPT. A prompt that fires on every run is noise, and a
prompt that fires on none is an addition that does nothing -- the defect class
this session spent the day measuring. So both directions are pinned: the real
arm-1 report must produce a recommendation, and a converged run, a run far from
the gate, and a run that stopped early must produce none.

IT DECIDES NOTHING. `feedback_fixes_hil_only`: the reviewer raises the cap or
does not. No verdict, score or convergence decision reads it.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
ARMS_MODULE = REPO / "bench" / "tools" / "commissioning_arms_2026-09-21.py"


def _arms():
    spec = importlib.util.spec_from_file_location("arms_for_cap_test", ARMS_MODULE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["arms_for_cap_test"] = m
    spec.loader.exec_module(m)
    return m


def _report(rounds_run, cap, gamma_critical, threshold=0.3, unverified=0, novel=0):
    return {
        "max_rounds": cap,
        "convergence_config": {"gamma_alt_threshold": threshold},
        "rounds": [{"round": i} for i in range(rounds_run - 1)] + [{
            "round": rounds_run - 1, "gamma_critical": gamma_critical,
            "unverified_critical": unverified, "novel_this_round": novel,
        }],
    }


class TestItFiresWhenConvergenceWasInReach:
    def test_the_real_arm1_report_gets_a_recommendation(self):
        """The run the ruling came from. If this stops firing, say why."""
        a = _arms()
        reports = sorted((REPO / "bench" / "logs").glob(
            "commissioning_arm1_panel_*/commissioning_arm1_panel_report.json"))
        if not reports:
            pytest.skip("the arm-1 archive is not in this clone; the fixture "
                        "cases below still pin both directions")
        hits = [r for r in reports if a.cap_recommendation(json.loads(r.read_text()))]
        assert hits, (
            f"none of {len(reports)} archived arm-1 report(s) produced a "
            f"recommendation. At least one used its whole budget with "
            f"gamma_critical of 0.29 against a 0.30 threshold, which is the case "
            f"this prompt exists for.")
        note = a.cap_recommendation(json.loads(hits[-1].read_text()))
        assert "raise the round cap" in note
        assert "0.29" in note or "short by" in note, note

    def test_the_gate_met_but_held_by_the_failsafe_fires(self):
        """gamma_critical satisfied and A4 holding it open is also 'in reach'."""
        a = _arms()
        note = a.cap_recommendation(_report(10, 10, 0.44, unverified=2))
        assert note and "fail-safe" in note, note

    def test_just_short_of_the_threshold_fires(self):
        a = _arms()
        assert a.cap_recommendation(_report(10, 10, 0.29)), "0.29 of 0.30 is in reach"


class TestItStaysSilentOtherwise:
    def test_a_run_that_stopped_before_the_cap_is_silent(self):
        """A run that converged early must never be told to buy more rounds."""
        a = _arms()
        assert a.cap_recommendation(_report(6, 10, 0.44, unverified=2)) is None

    def test_a_run_far_from_the_gate_is_silent(self):
        a = _arms()
        assert a.cap_recommendation(_report(10, 10, 0.05)) is None

    def test_a_report_missing_the_fields_is_silent_not_loud(self):
        """An unreadable report is silence, not an accusation."""
        a = _arms()
        for bad in ({}, {"rounds": []}, {"max_rounds": 10, "rounds": [{}]},
                    {"max_rounds": 10, "rounds": [{"gamma_critical": 0.29}]}):
            assert a.cap_recommendation(bad) is None, bad


class TestTheThresholdIsNotVacuous:
    def test_the_reach_fraction_actually_discriminates(self):
        """If REACH_FRACTION were 0 everything would fire; if 1, almost nothing."""
        a = _arms()
        t = 0.3
        fires = a.cap_recommendation(_report(10, 10, t * a.REACH_FRACTION))
        silent = a.cap_recommendation(_report(10, 10, t * a.REACH_FRACTION - 0.01))
        assert fires is not None, "at exactly the reach fraction it must fire"
        assert silent is None, "just below the reach fraction it must not"

    def test_it_is_wired_into_the_launcher(self):
        """An unwired recommendation is an addition that does nothing."""
        src = ARMS_MODULE.read_text(encoding="utf-8")
        assert src.count("cap_recommendation(") >= 2, (
            "cap_recommendation is defined but called nowhere in its own module; "
            "the reviewer would never see it")
