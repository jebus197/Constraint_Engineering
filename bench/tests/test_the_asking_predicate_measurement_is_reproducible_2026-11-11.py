#!/usr/bin/env python3
"""The asking-predicate producer runs, and its own control still refutes it.

★ WHY THIS EXISTS. `scripts/the_asking_predicate_misses_three_phrasings_2026-11-10.py`
was written on 2026-11-10 to measure a gap: entries the decision classifier labels
MINE while their own prose says the residue is the founder's. The commit was
refused by `test_an_unreached_producer_set_cannot_grow_2026-11-08.py` --
*"1 producer(s) are reached by NO test"* -- which is `additive-standard`'s
symmetric form doing its job: an addition nothing reaches is not additive. The
figure it produces is cited in task-list entry B143 and in the decisions file, so
under `measured-rate-travels-with-its-script` the producer must stay AND must be
executed.

★ AND THE THING THIS GUARD PINS IS THE PRODUCER'S OWN REFUTATION, which is the
only honest shape for it. The producer's `OWED_PROSE` pattern found the 3 live
entries it was written to find -- and its CONTROL arm found 21 DONE entries
matching the same pattern, of which inspection showed at least 4 using the phrase
to explain a STANDING PATTERN ("his standing pattern is that loosening a guard's
effect is his call") or to say why a question was raised in a DIFFERENT entry.
So the pattern over-matches and was NOT wired into the classifier; the repair
that shipped instead was positional retirement scoping, plus explicit markers,
on the recorded lesson that an explicit marker and fixed widths beat a shape.

THEREFORE THIS GUARD MUST NOT ASSERT THAT THE PATTERN IS SOUND. It asserts that
the producer still RUNS, that its split still agrees with the live classifier,
and that the CONTROL ARM IS STILL REPORTED AND STILL NON-ZERO -- because the
tempting "fix" for an over-matching detector is to delete the control that
exposes it, and that is exactly the move this file exists to catch.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "scripts" / "the_asking_predicate_misses_three_phrasings_2026-11-10.py"
CLASSIFIER = ROOT / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def prod():
    assert PRODUCER.is_file(), f"{PRODUCER} is missing"
    return _load(PRODUCER, "_asking_predicate_producer")


@pytest.fixture(scope="module")
def measured(prod):
    return prod.measure()


class TestItRuns:
    def test_the_producer_executes_and_exits_zero(self):
        done = subprocess.run([sys.executable, str(PRODUCER)],
                              capture_output=True, text=True,
                              cwd=str(ROOT), timeout=300)
        assert done.returncode == 0, done.stderr[-900:]
        out = done.stdout
        for expected in ("THE ASKING PREDICATE AGAINST THE ENTRIES' OWN PROSE",
                         "CONTROL", "THE COUNT HE READS", "THE CORRECTED COUNT"):
            assert expected in out, f"{expected!r} is absent from the output"

    def test_help_costs_nothing_and_measures_nothing(self, tmp_path):
        """A `--help` must never do work: his ruling, and 15 of 17 runners
        once billed for one."""
        env = dict(os.environ)
        done = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                              capture_output=True, text=True,
                              cwd=str(tmp_path), timeout=120, env=env)
        assert done.returncode == 0, done.stderr[-400:]
        assert "usage" in done.stdout.lower()
        assert "CONTROL" not in done.stdout, (
            "--help printed a measurement, so it did work rather than describing it")

    def test_the_json_mode_carries_every_number_it_prints(self, prod):
        done = subprocess.run([sys.executable, str(PRODUCER), "--json"],
                              capture_output=True, text=True,
                              cwd=str(ROOT), timeout=300)
        assert done.returncode == 0, done.stderr[-400:]
        import json
        line = [ln for ln in done.stdout.splitlines() if ln.startswith("{")]
        assert line, "no JSON object on stdout under --json"
        obj = json.loads(line[-1])
        for key in ("open", "owed", "d1", "corrected", "d1_idents", "ctrl", "d2"):
            assert key in obj, f"{key} missing from the JSON"
        assert obj["corrected"] == obj["owed"] + obj["d1"]


class TestItAgreesWithTheLiveClassifier:
    """The producer must not drift from the thing it measures."""

    def test_the_split_reproduces_from_the_classifier_itself(self, measured):
        cls = _load(CLASSIFIER, "_asking_predicate_classifier")
        bodies = cls.bodies()
        sys.path.insert(0, str(ROOT / "scripts"))
        import task_list_markers as tlm                       # noqa: PLC0415
        live_owed, live_mine = set(), set()
        for e in tlm.parse_entries():
            if (e.state or "").upper() != "OPEN":
                continue
            kind = cls.classify_text(e.state, e.ruled,
                                     bodies.get(e.ident, ""))["kind"]
            (live_owed if kind == "OWED" else live_mine).add(e.ident)
        rows_open = [r for r in measured["open"]]
        prod_owed = {r["ident"] for r in rows_open if r["kind"] == "OWED"}
        prod_mine = {r["ident"] for r in rows_open if r["kind"] in ("MINE", "GRANTED")}
        assert prod_owed == live_owed, (prod_owed ^ live_owed)
        assert prod_mine == live_mine, (prod_mine ^ live_mine)

    def test_every_open_entry_is_classified_exactly_once(self, measured):
        idents = [r["ident"] for r in measured["open"]]
        assert len(idents) == len(set(idents)), "an entry was counted twice"
        assert idents, "no OPEN entry at all, so the producer measures nothing"


class TestTheControlArmStillRefutesThePattern:
    """★ THE ANTI-VACUITY PIN, AND THE REASON THIS FILE IS NOT A RUBBER STAMP."""

    def test_the_control_arm_exists_and_is_reported(self, measured):
        assert "ctrl" in measured, (
            "the producer no longer computes a control arm. The control is what "
            "showed `OWED_PROSE` over-matching -- 21 DONE entries carrying the "
            "same phrasing, several of them using it to describe a STANDING "
            "PATTERN rather than a live residue. Without it the pattern reads as "
            "a sound detector, which it is not.")

    def test_the_control_still_fires_on_closed_entries(self, measured):
        """If this ever reaches 0, the pattern has become narrow enough to
        consider wiring in -- and that is a DECISION, not a silent promotion.
        Going red here means re-examining it, not re-pinning the number."""
        assert len(measured["ctrl"]) > 0, (
            "the prose pattern now matches 0 DONE entries. That may be an "
            "improvement, but it changes the standing conclusion that the "
            "pattern over-matches and must not be wired into the classifier. "
            "Re-read the control before touching this assertion.")

    def test_the_producer_recommends_no_wiring(self):
        """The producer must not acquire a recommendation to adopt its own
        pattern. Its measured operating characteristic does not support one."""
        text = PRODUCER.read_text(encoding="utf-8")
        for claim in ("RECOMMENDATION: adopt", "recommend adopting",
                      "should be wired into the classifier"):
            assert claim.lower() not in text.lower(), (
                f"the producer now recommends adopting a pattern its own control "
                f"refutes: {claim!r}")

    def test_the_two_defects_are_reported_apart(self, measured):
        """D1 (the pattern misses phrasings) and D2 (a stale marker retires a
        later ask) have different fixes, so a single count would hide which
        surface was blind -- the shape this project records as a figure
        answering a different question."""
        assert "d1" in measured and "d2" in measured
        assert measured["d1"] is not measured["d2"]


class TestTheIntervalIsCorrect:
    def test_wilson_matches_statsmodels_on_the_live_figure(self, measured, prod):
        """2 independent routes per the 21 April 2026 rule."""
        k, n = len(measured["d1"]), len([r for r in measured["open"]
                                         if r["kind"] in ("MINE", "GRANTED")])
        if n == 0:
            pytest.skip("no MINE entry today, so there is no proportion to bound")
        lo, hi = prod.wilson(k, n)
        from statsmodels.stats.proportion import proportion_confint
        lo2, hi2 = proportion_confint(k, n, alpha=0.05, method="wilson")
        assert abs(lo - lo2) < 1e-9 and abs(hi - hi2) < 1e-9, (
            f"closed form [{lo}, {hi}] against statsmodels [{lo2}, {hi2}]")
        assert 0.0 <= lo <= hi <= 1.0

    def test_wilson_is_degenerate_only_at_a_zero_denominator(self, prod):
        """★ THE TOLERANCE IS NOT LAZINESS. At k = n the Wilson upper bound is
        1 in exact arithmetic and 0.9999999999999999 in binary floating point,
        because the closed form subtracts 2 nearly equal quantities. The first
        version of this test asserted `hi == 1.0` and went red on a CORRECT
        producer -- a guard failing on the arithmetic rather than on the claim.
        The bound is therefore compared with a tolerance, while the exact 0 at
        the lower end is asserted exactly, because that one IS exact: p = 0
        makes the numerator identically 0."""
        assert prod.wilson(0, 0) == (0.0, 0.0)
        lo, hi = prod.wilson(0, 10)
        assert lo == 0.0, "p = 0 must give an exact 0 lower bound"
        assert 0.0 < hi < 1.0
        lo, hi = prod.wilson(10, 10)
        assert 0.0 < lo < 1.0
        assert hi == pytest.approx(1.0, abs=1e-12), hi
