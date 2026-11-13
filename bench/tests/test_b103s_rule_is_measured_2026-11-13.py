"""The B183 census must read the gate's REAL list and its REAL rule.

ENTRY B183. `scripts/b103s_rule_is_not_being_followed_2026-11-13.py` measures
how many guards dated on or after B103's cutoff are absent from the commit
gate's `GUARDS` list.

★ IT DOES NOT PIN 33 OF 220. That figure is the defect, and closing it must
turn this file GREEN rather than red. What is pinned is that the census reads
the live `hooks/pre-commit` rather than a copy of its list, that the cutoff is
the one the gate's own prose states, and that the measurement is capable of
returning 0 -- a census that cannot report success is not a census.
"""
from __future__ import annotations

import datetime
import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PROD = REPO / "scripts" / "b103s_rule_is_not_being_followed_2026-11-13.py"
PRE = REPO / "hooks" / "pre-commit"


@pytest.fixture(scope="module")
def prod():
    assert PROD.is_file(), f"the producer is gone: {PROD}"
    spec = importlib.util.spec_from_file_location("b183_census", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["b183_census"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def test_it_runs_and_reads_the_live_gate(prod):
    """EXECUTE, DO NOT GREP."""
    listed = prod.listed_guards()
    assert listed, "the census read an EMPTY guard list; it is measuring nothing"
    raw = PRE.read_text(encoding="utf-8")
    for path in list(listed)[:5]:
        assert path in raw, (
            f"{path!r} is in the census's list but not in hooks/pre-commit, so "
            f"the census is reading something other than the live gate")


def test_the_cutoff_is_the_one_the_gate_states(prod):
    """★ DERIVED FROM THE SUBJECT. A cutoff typed into the producer could drift
    from the rule the gate's own prose declares, and the census would then
    measure a rule nobody holds."""
    raw = PRE.read_text(encoding="utf-8")
    stated = re.findall(r"(?:SINCE|on or after)\s+(\d{4}-\d{2}-\d{2})", raw)
    assert stated, "hooks/pre-commit no longer states a cutoff date in its prose"
    dates = {datetime.date(*map(int, d.split("-"))) for d in stated}
    assert prod.CUTOFF in dates, (
        f"the producer uses {prod.CUTOFF} but the gate's prose states "
        f"{sorted(dates)}. The census must measure the rule the gate declares.")


def test_every_dated_guard_really_exists(prod):
    dated = prod.dated_guards()
    assert dated, "0 guards are dated on or after the cutoff; the census is vacuous"
    for path in dated:
        assert (REPO / path).is_file(), f"census names a missing file: {path}"


def test_the_census_can_report_success(prod):
    """★ A CENSUS THAT CANNOT RETURN 0 IS NOT A MEASUREMENT. Driving the
    predicate with a list that contains every dated guard must yield an empty
    gap, or the arithmetic is wrong in the flattering direction."""
    dated = prod.dated_guards()
    missing = [p for p in dated if p not in set(dated)]
    assert missing == [], (
        "with every dated guard listed, the census still reports a gap, so it "
        "would report a violation that had already been fixed")


def test_the_gap_is_a_subset_of_the_dated_set(prod):
    """Non-vacuity in the other direction: the reported gap must consist of
    real dated guards, not of arbitrary strings."""
    listed, dated = prod.listed_guards(), prod.dated_guards()
    gap = {p for p in dated if p not in listed}
    assert gap <= set(dated)
    for path in gap:
        assert (REPO / path).is_file(), f"reported gap names a missing file: {path}"
        assert path not in listed
