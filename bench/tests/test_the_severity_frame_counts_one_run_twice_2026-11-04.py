#!/usr/bin/env python3
"""The producer behind entry B121 is EXECUTED here, never read.

B121 reported a measurement defect while naming no script, so its 5 quantities
were claims about evidence rather than evidence. The producer now exists and
this runs it.

WHAT IS CHECKED, AND WHY EACH ONE EARNS ITS PLACE.
- The arithmetic closes. If the excluded count plus the link's own count does
  not equal the followed count, the 3 figures are not 3 views of 1 frame.
- The duplicate is EXACT. "Counted twice" is a stronger claim than "counted
  something similar twice", and only a multiset identity supports it.
- The floors are READ FROM THE GUARD FILE. This is the assertion that stops the
  producer drifting from its subject: the guard's floor is moved on disk and the
  producer must report the moved value. A hardcoded copy would not.
- Both interval routes agree. A single-route interval is a quantity resting on
  1 implementation, which this repository's own guard refuses.
- `--help` does not measure. The script loads the severity producer and reads 65
  run directories, so answering the flag by working is the defect
  test_help_never_acts_2026-09-11.py exists to catch.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_severity_frame_counts_one_run_twice_2026-11-04.py"
GUARD = REPO / "bench" / "tests" / "test_the_severity_proxy_was_never_tested_2026-10-28.py"


@pytest.fixture(scope="module")
def mod():
    if not PRODUCER.is_file():
        pytest.skip("the producer is absent from this checkout")
    spec = importlib.util.spec_from_file_location("_sfc", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def r(mod):
    if not (REPO / "bench" / "logs").is_dir():
        pytest.skip("no archive in this checkout, so the frame cannot be built")
    return mod.measure()


class TestTheDefectIsStillThere:
    def test_the_link_is_a_symlink_into_the_frame(self, r):
        """If someone replaces it with a real directory the defect is GONE, and
        this test should then be retired deliberately rather than loosened."""
        assert r["is_symlink"], (
            "exp36_evidence_latest is no longer a symbolic link. If that was "
            "done on purpose the defect B121 reports is fixed; retire this "
            "file with a note rather than relaxing it.")
        assert r["linked_dirs"] == ["exp36_evidence_latest"]

    def test_the_arithmetic_closes(self, r):
        assert r["arithmetic_closes"], (
            f"{r['n_excluded']} + {r['n_from_link']} != {r['n_followed']}, so "
            f"the 3 counts are not 3 views of 1 frame")
        assert r["n_from_link"] > 0
        assert r["n_excluded"] < r["n_followed"]

    def test_the_duplicate_is_exact_not_merely_similar(self, r):
        assert r["duplicate_is_exact"], (
            "the link's severities are not an identical multiset to its "
            "target's, so 'counted twice' overstates what was measured")

    def test_excluding_it_shifts_the_spread(self, r):
        assert r["sd_excluded"] != r["sd_followed"]


class TestTheFloorsAreReadFromTheGuardNotCopied:
    def test_it_found_every_floor_the_guard_holds(self, mod):
        src = GUARD.read_text(encoding="utf-8")
        in_guard = set(re.findall(r'\["(\w+)"\]\s*>=\s*\d+', src))
        found = set(mod.read_floors())
        expected = in_guard & set(mod.FLOORED)
        assert found == expected, (
            f"the producer read {sorted(found)} but the guard floors "
            f"{sorted(expected)} among the quantities it tracks")
        assert found, "no floor was found at all, so the comparison is vacuous"

    def test_a_moved_floor_moves_the_producers_answer(self, mod):
        """EXECUTED against a MUTATED guard. A hardcoded copy passes the test
        above and fails this one, which is the whole point of having both."""
        found = mod.read_floors()
        name, value = sorted(found.items())[0]
        src_bytes = GUARD.read_bytes()
        digest = hashlib.sha256(src_bytes).hexdigest()
        old = f'["{name}"] >= {value}'
        try:
            text = src_bytes.decode()
            assert text.count(old) == 1, f"anchor {old!r} is not unique"
            GUARD.write_text(text.replace(old, f'["{name}"] >= {value + 1}'))
            again = mod.read_floors()
            assert again[name] == value + 1, (
                f"the guard now floors {name} at {value + 1} but the producer "
                f"still reports {again[name]}, so it is not reading the guard")
        finally:
            GUARD.write_bytes(src_bytes)
            assert hashlib.sha256(GUARD.read_bytes()).hexdigest() == digest, (
                "the guard file was not restored byte-for-byte")

    def test_it_names_which_floors_would_go_red(self, r):
        reds = r["floors_that_would_go_red"]
        for k in reds:
            assert r["excluded"][k] < r["floors"][k]
        for k in set(r["floors"]) - set(reds):
            assert r["excluded"][k] >= r["floors"][k]


class TestEveryQuantityRestsOnTwoRoutes:
    def test_wilson_agrees_across_two_implementations(self, r):
        assert r["wilson_gap"] < 1e-9, (
            f"statsmodels and the mpmath closed form disagree by "
            f"{r['wilson_gap']:.3e} on the Wilson interval")

    def test_the_exact_interval_agrees_across_two_implementations(self, r):
        assert r["exact_gap"] < 1e-9, (
            f"statsmodels and scipy's beta quantiles disagree by "
            f"{r['exact_gap']:.3e} on the Clopper-Pearson interval")

    def test_the_intervals_bracket_the_point_estimate(self, r):
        for key in ("wilson", "exact"):
            lo, hi = r[key]
            assert 0.0 <= lo <= r["share"] <= hi <= 1.0, (
                f"the {key} interval [{lo}, {hi}] does not bracket "
                f"{r['share']}")


class TestItRunsAndItsHelpDoesNot:
    def test_it_exits_zero(self):
        p = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        assert p.returncode == 0, p.stderr[-700:]
        assert "THE SEVERITY FRAME COUNTS ONE RUN TWICE" in p.stdout

    def test_help_answers_without_measuring(self):
        p = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr[-400:]
        assert "severities, link followed" not in p.stdout, (
            "`--help` ran the measurement")
        assert "usage:" in p.stdout
