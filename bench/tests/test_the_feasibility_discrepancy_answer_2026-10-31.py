#!/usr/bin/env python3
"""His feasibility question is answered by measurement, and the answer holds.

HIS QUESTION, 2026-10-30: *"So there is an unresolved discrepancy, that neither
you, or the other panel models can resolve? Is it significant to our
deliberations on this topic? If so how?"*

The answer is NO, and this guard holds the 2 properties it rests on: that the
2 seats' figures are statistically indistinguishable at n = 53, and that the
producer reaches the panel's OWN instrument rather than restating it.

★ IT ALSO PINS THE HONEST LIMIT. The leading hypothesis for the gap -- that the
seats counted over archives differing by a run -- is marked SPECULATIVE in the
producer, because both seats ran the same day within 1 round of each other. A
test that let that hypothesis harden into a claim would undo the care, so one
below asserts the marking is still there.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "scripts"
            / "is_the_feasibility_discrepancy_significant_2026-10-31.py")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("feas", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheAnswerIsNo:
    def test_neither_pair_is_distinguishable(self, mod):
        for a, b in ((mod.CC1_PAIR[0], mod.FABLE_PAIR[0]),
                     (mod.CC1_PAIR[1], mod.FABLE_PAIR[1])):
            r = mod.compare(a, b, mod.DATED_DENOMINATOR)
            assert r["fisher_p"] > 0.05, (
                f"{a} against {b} of {r['n']} IS distinguishable at "
                f"p = {r['fisher_p']:.6f}, so the answer to his question "
                "changes and the record must change with it")
            assert r["intervals_overlap"], (a, b, r)

    def test_the_two_tests_agree_with_each_other(self, mod):
        """Fisher exact against chi-square with Yates, per the 2-tool rule."""
        for a, b in ((mod.CC1_PAIR[0], mod.FABLE_PAIR[0]),
                     (mod.CC1_PAIR[1], mod.FABLE_PAIR[1])):
            r = mod.compare(a, b, mod.DATED_DENOMINATOR)
            assert abs(r["fisher_p"] - r["chi2_yates_p"]) < 0.01, r
            assert r["mpmath_agrees"] is True, r

    def test_the_comparison_can_detect_a_real_difference(self, mod):
        """DISCRIMINATION FIRST. If compare() returned a large p for everything,
        the test above would pass on nothing."""
        r = mod.compare(50, 10, 53)
        assert r["fisher_p"] < 0.001, (
            "a 50-against-10 split was not detected, so compare() cannot "
            "distinguish anything and the real answer is meaningless: %r" % (r,))
        assert not r["intervals_overlap"]

    def test_the_recorded_pairs_are_the_panels_own(self, mod):
        assert mod.CC1_PAIR == (34, 21)
        assert mod.FABLE_PAIR == (32, 16)
        assert mod.DATED_DENOMINATOR == 53


class TestItReachesThePanelsOwnInstrument:
    def test_it_imports_the_producer_rather_than_restating_it(self, mod):
        assert mod.PRODUCER.is_file(), mod.PRODUCER
        loaded = mod._load()
        for fn in ("collect", "first_fire_rate"):
            assert hasattr(loaded, fn), (
                f"the quiet-run producer no longer exposes {fn}, so the "
                "today-against-then comparison cannot be made from its own "
                "instrument and would have to be restated -- which is the "
                "defect this avoids")

    def test_the_population_really_has_moved(self, mod):
        """The second half of the answer. If the archive were unchanged, the
        denominator explanation would be unfounded."""
        loaded = mod._load()
        reports = loaded.collect(0.7)
        assert len(reports) != 63, (
            "the archive still holds 63 reports, so the claim that the "
            "population moved is no longer true and the answer needs redoing")
        a, n = loaded.first_fire_rate(reports, 3)
        assert n != mod.DATED_DENOMINATOR, (
            f"the K=3 denominator is still {n}, so the dated-denominator "
            "explanation does not hold")


class TestTheHonestLimitIsStillMarked:
    def test_the_snapshot_hypothesis_is_marked_speculative(self):
        src = PRODUCER.read_text()
        assert "[SPECULATIVE]" in src, (
            "the snapshot hypothesis is no longer marked speculative; both "
            "seats ran the same day within 1 round of each other, so it is "
            "plausible and not demonstrated")

    def test_it_names_what_would_settle_it(self):
        src = PRODUCER.read_text()
        assert "WHAT WOULD SETTLE IT" in src, (
            "the producer no longer says how the question could be closed, so "
            "it records an open question without a route out of it")
        assert "seat_evidence" in src


class TestAHelpMustNeverCostMoney:
    def test_help_answers_without_running_the_measurement(self):
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-400:]
        assert "usage" in r.stdout.lower()
        assert "Fisher" not in r.stdout, (
            "--help ran the measurement; a help flag must never cost money")
