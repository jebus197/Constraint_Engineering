#!/usr/bin/env python3
"""The external-citation producer is EXECUTED here, and its 0 is made falsifiable.

WHY THE SENSITIVITY PINS CARRY THIS FILE. The producer reports that 0 of the
record's arXiv identifiers carry a structural fault. A 0 from a validator that
decides nothing is indistinguishable from a 0 from one that works, and this
project has retired several mechanisms that ran and decided nothing. So the
validator is a PURE FUNCTION here and is fed PLANTED identifiers in both
directions: 4 that must be caught and 2 that must NOT be, the second group
mattering more because a validator that refuses everything would pass the first.

THE NEGATIVE CONTROL IS THE PRE-2015 SUFFIX. arXiv used a 4-digit sequence
before 2015 and 5 digits after, so `0704.1459` is a legitimate 2007 identifier
and must report no fault. Without that control the suffix rule could be widened
to accuse every old paper and every other test here would still pass.
"""
from __future__ import annotations

import datetime
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "is_any_external_citation_verified_2026-11-04.py"
TODAY = datetime.date(2026, 11, 4)


@pytest.fixture(scope="module")
def mod():
    if not PRODUCER.is_file():
        pytest.skip("the producer is absent from this checkout")
    sys.path.insert(0, str(PRODUCER.parent))
    spec = importlib.util.spec_from_file_location("_extcit", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def r(mod):
    return mod.measure(today=TODAY)


class TestTheValidatorCatchesWhatItMust:
    @pytest.mark.parametrize("ident,fragment", [
        ("2613.14590", "impossible month"),
        ("2700.14590", "impossible month"),
        ("2712.14590", "in the future"),
        ("2608.1459", "digit sequence"),
        ("not-an-id", "not a YYMM"),
    ])
    def test_a_planted_fault_is_caught(self, mod, ident, fragment):
        got = mod.faults(ident, TODAY)
        assert got, f"{ident} was passed as sound"
        assert any(fragment in f for f in got), f"{ident} -> {got}"


class TestTheValidatorDoesNotAccuseWhatIsSound:
    """THE CONTROLS. A validator that refuses everything passes every test in
    the class above and measures nothing."""

    @pytest.mark.parametrize("ident", [
        "2608.14590",   # August 2026, 5-digit sequence
        "2610.10488",   # October 2026, in the past
        "1706.03762",   # June 2017
    ])
    def test_a_valid_modern_identifier_is_passed(self, mod, ident):
        assert mod.faults(ident, TODAY) == [], mod.faults(ident, TODAY)

    def test_a_legitimate_pre_2015_four_digit_sequence_is_passed(self, mod):
        """arXiv used 4 digits before 2015. Accusing those would turn the rule
        into a blanket refusal of every old paper in the bibliography."""
        assert mod.faults("0704.1459", TODAY) == [], (
            "a 2007 identifier with a 4-digit sequence was accused; the "
            "suffix rule must apply only from 2015")

    def test_the_boundary_month_values_are_accepted(self, mod):
        for ident in ("2601.00001", "2512.99999"):
            assert mod.faults(ident, TODAY) == [], f"{ident} rejected"


class TestTheRecordItself:
    def test_the_population_is_not_empty(self, r):
        assert r["arxiv"] > 20, (
            f"only {r['arxiv']} arXiv identifiers found, so the walk is not "
            f"reaching the record it claims")
        assert r["doi"] > 10 and r["url"] > 100

    def test_no_identifier_carries_a_structural_fault(self, r):
        for key in ("bad_month", "future", "short_suffix"):
            assert r[key] == [], f"{key}: {r[key]}"

    def test_exactly_the_known_identifier_is_exercised_by_a_test(self, r):
        """1 of the 43 IS verified, by execution rather than assertion: the
        ouroboros tests resolve it, derive its PDF url and parse it. If this
        count RISES that is good news and the figure in entry B131 needs
        updating; if it falls, a test stopped exercising the download path."""
        assert r["verified_by_a_test"] == ["1706.03762"], (
            f"expected exactly 1706.03762 to be named by a test, got "
            f"{r['verified_by_a_test']}")

    def test_the_internal_citation_guards_still_outnumber_it(self, r):
        assert len(r["citation_guard_files"]) >= 14, (
            f"only {len(r['citation_guard_files'])} citation guard files found; "
            f"the contrast this entry draws is that 14 guard INTERNAL citations "
            f"and 1 external citation is exercised")


class TestTheInstrumentExcludesItself:
    """MEASURED THE MOMENT THIS PAIR WAS PLACED, and both figures moved.

    This file's name carries "citation", so the producer counted it among the
    citation-guarding test files and the count rose from 14 to 15. And the
    control pins below name 2608.14590, 2610.10488 and 1706.03762 as planted
    fixtures, so the count of identifiers "named by a test" rose from 1 to 3 --
    the instrument reading its own test data as evidence about the record.
    """

    def test_this_file_is_excluded_by_name(self, mod):
        import inspect
        src = inspect.getsource(mod.measure)
        assert "test_is_any_external_citation_verified_2026-11-04.py" in src, (
            "the producer no longer excludes this guard, so it counts itself "
            "among the citation guards and reads its own fixtures as evidence")

    def test_the_fixtures_in_this_file_are_not_counted_as_verified(self, mod, r):
        """EXECUTED. The 3 identifiers this file plants must NOT appear in the
        producer's verified list, except 1706.03762 which is independently
        exercised by the ouroboros tests."""
        planted = {"2608.14590", "2610.10488"}
        leaked = planted & set(r["verified_by_a_test"])
        assert not leaked, (
            f"{sorted(leaked)} are planted in THIS file and are being reported "
            f"as verified by a test, so the instrument is reading its own "
            f"fixtures as evidence about the record")

    def test_the_guard_count_is_unaffected_by_this_file(self, mod, r):
        assert "test_is_any_external_citation_verified_2026-11-04.py" not in \
            r["citation_guard_files"], (
            "the producer lists its own guard among the citation guards")


class TestItRunsAndItsHelpDoesNot:
    def test_it_exits_zero(self):
        p = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=600)
        assert p.returncode == 0, p.stderr[-700:]
        assert "IS ANY EXTERNAL CITATION IN THIS RECORD VERIFIED" in p.stdout

    def test_help_answers_without_measuring(self):
        p = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr[-400:]
        assert "distinct arXiv identifiers" not in p.stdout, "`--help` measured"
        assert "usage:" in p.stdout
