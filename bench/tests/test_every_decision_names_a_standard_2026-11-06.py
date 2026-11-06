#!/usr/bin/env python3
"""Every decision put to him must argue against one of the 3 standards.

RULE 33 of note standard v1.9. The rule exists because the file he rejected on
2026-10-29 carried 0 recommendations across 6 open decisions and used the words
additive, composability and simplest sufficient 0 times each.

MEASURED 2026-11-06, BEFORE the repair: of 29 live decisions, 28 carried a
recommendation (Wilson 95% [0.828245, 0.993887]) but only 15 named a standard
(Wilson [0.344310, 0.686139]). B131 carried no recommendation at all, the only
one of the 29. After attaching an argued recommendation to the 13 that lacked
one: 29 of 29 on BOTH halves, Wilson [0.883030, 1.000000].

THE 2 HALVES ARE RATCHETED SEPARATELY because they fail independently: a
decision can carry a recommendation that argues nothing against any standard,
which is the weak form Rule 33 was written to stop. A FLOOR rather than an
exact pin, because the live decision count moves with every ruling he makes --
an exact pin here would fail with the passage of his rulings, which is the
defect this session already fixed twice tonight.
"""
from __future__ import annotations
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = REPO / "scripts" / "does_every_decision_name_a_standard_2026-11-06.py"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
SURFACES = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"

STANDARD = re.compile(r"additive|simplest sufficient|composab", re.I)
RECOMMENDS = re.compile(r"this is the recommendation|\brecommend", re.I)


@pytest.fixture(scope="module")
def live():
    spec = importlib.util.spec_from_file_location("sf_r33t", SURFACES)
    sf = importlib.util.module_from_spec(spec)
    sys.modules["sf_r33t"] = sf
    spec.loader.exec_module(sf)
    detail = json.loads(DETAIL.read_text(encoding="utf-8"))

    def blob(ident):
        for k in (ident, f"task:{ident}", f"study:{ident}"):
            v = detail.get(k)
            if isinstance(v, dict):
                return json.dumps(v)
        return ""

    idents = [i for i, _h in sf.derived()]
    return idents, {i: blob(i) for i in idents}


class TestTheProducerExists:
    def test_the_figure_has_a_producer(self):
        assert PROD.exists(), f"the 29-of-29 figure has no producer: {PROD}"

    def test_help_costs_nothing(self):
        """A --help must never run the measurement. 15 of 17 runners once billed."""
        r = subprocess.run([sys.executable, str(PROD), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-600:]
        assert "live decisions awaiting him" not in r.stdout, \
            "--help ran the measurement"

    def test_the_producer_runs_and_reports_both_halves(self):
        r = subprocess.run([sys.executable, str(PROD)], cwd=REPO,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr[-1500:]
        assert "carry a recommendation" in r.stdout
        assert "name one of the 3 standards" in r.stdout
        assert "Clopper-Pearson" in r.stdout, "a proportion with 1 interval family"


class TestTheRatchet:
    def test_every_live_decision_carries_a_recommendation(self, live):
        idents, blobs = live
        gaps = sorted(i for i in idents if not RECOMMENDS.search(blobs[i]))
        assert not gaps, (
            f"{len(gaps)} of {len(idents)} live decision(s) carry no "
            f"recommendation: {gaps}. Rule 33 requires one, and he cannot rule "
            f"quickly on an item that states a problem and proposes nothing.")

    def test_every_live_decision_names_one_of_the_three_standards(self, live):
        idents, blobs = live
        gaps = sorted(i for i in idents if not STANDARD.search(blobs[i]))
        assert not gaps, (
            f"{len(gaps)} of {len(idents)} live decision(s) name none of "
            f"additive, simplest sufficient or composability: {gaps}. A "
            f"recommendation that argues against no standard is the weak form "
            f"Rule 33 exists to stop.")

    def test_the_ratchet_is_not_vacuous(self, live):
        """ANTI-VACUITY. On an empty queue both tests above pass on nothing."""
        idents, _b = live
        assert len(idents) >= 5, (
            f"only {len(idents)} live decision(s); the 2 tests above would pass "
            f"on almost nothing and the ratchet would be decorative")


class TestTheWeakFormIsActuallyDistinguished:
    def test_a_recommendation_without_a_standard_is_caught(self):
        """EXECUTED, not asserted: the 2 predicates must disagree on a case
        that carries a recommendation and names no standard. Without this the
        2 tests above could be 1 test wearing 2 names."""
        weak = json.dumps({"options": ["**Do X. This is the recommendation.**"]})
        assert RECOMMENDS.search(weak), "the recommendation predicate missed one"
        assert not STANDARD.search(weak), (
            "the standard predicate fires on text naming no standard, so the 2 "
            "halves are not independent and 1 of them is decorative")
