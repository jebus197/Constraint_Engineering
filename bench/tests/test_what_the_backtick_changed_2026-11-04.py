#!/usr/bin/env python3
"""The producer behind B120's replaced figure is EXECUTED here, never read.

WHAT EACH CHECK EARNS ITS PLACE FOR.
- The pre-fix pattern is DERIVED from the live one and the derivation changes
  exactly 1 character. A retyped pattern would drift from its subject; a
  derivation that silently matched nothing would make the whole comparison
  vacuous, which is why the producer raises rather than returning a no-op.
- The derivation reproduces the defect. A backticked heading must match under
  the live predicate and NOT under the derived one. Without this the 1-character
  claim is unpinned and the pattern could be narrowed to nothing undetected.
- The 4 cells close on the reply count. A paired table whose cells do not sum to
  the population is not a partition of it.
- The direction claim is pinned: 0 verdicts lost. That is the claim B120 rests
  on and it is the one worth a regression guard.
- Both p-values agree across 2 independent routes, and McNemar is reported as
  the test that fits a paired design while Fisher is reported because the entry
  claimed it. A guard that accepted either silently would hide the distinction
  the producer exists to draw.
- `--help` does not measure: the producer walks every archived round.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "what_the_backtick_changed_2026-11-04.py"
SUBJECT = REPO / "scripts" / "panel_condition_compliance_2026-09-10.py"


@pytest.fixture(scope="module")
def mod():
    if not PRODUCER.is_file():
        pytest.skip("the producer is absent from this checkout")
    sys.path.insert(0, str(PRODUCER.parent))
    spec = importlib.util.spec_from_file_location("_btk", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def r(mod):
    if not (REPO / "bench" / "logs").is_dir():
        pytest.skip("no archive in this checkout, so no replies can be walked")
    return mod.measure()


class TestThePreFixPatternIsDerivedNotRetyped:
    def test_the_derivation_changes_exactly_one_character(self, mod):
        live = mod._load().DISAGREEMENT_RE.pattern
        before = mod._without_backtick(live)
        assert len(live) - len(before) == 1, (
            f"the derivation changed {len(live) - len(before)} characters; the "
            f"claim under test is a 1-character fix")
        assert before != live

    def test_the_derivation_reproduces_the_defect(self, mod):
        """SENSITIVITY PIN. Without this the pattern could be narrowed to
        nothing and every other test here would still pass."""
        m = mod._load()
        live = m.DISAGREEMENT_RE
        before = re.compile(mod._without_backtick(live.pattern), live.flags)
        probe = ("## `disagreement`\nThe brief's framing is wrong because the "
                 "figure it rests on is stale.")
        assert live.search(probe), "the live predicate no longer matches a backticked heading"
        assert not before.search(probe), (
            "the derived pre-fix predicate ALSO matches a backticked heading, so "
            "it does not reproduce the defect and the comparison is vacuous")

    def test_it_refuses_when_the_class_is_gone(self, mod):
        with pytest.raises(SystemExit):
            mod._without_backtick(r"no markup class here at all")


class TestThePairedTableIsAPartition:
    def test_the_four_cells_close_on_the_population(self, r):
        total = r["n_gained"] + r["n_lost"] + r["both"] + r["neither"]
        assert total == r["n_replies"], (
            f"{r['n_gained']} + {r['n_lost']} + {r['both']} + {r['neither']} = "
            f"{total}, not {r['n_replies']}")

    def test_the_population_is_not_empty(self, r):
        assert r["n_replies"] > 100, (
            f"only {r['n_replies']} replies were walked, so the measurement is "
            f"not over the archive it claims")

    def test_no_verdict_is_lost(self, r):
        """THE CLAIM B120 RESTS ON. A fix that took a verdict away would be a
        different finding and must not pass silently."""
        assert r["n_lost"] == 0, (
            f"the fix LOSES {r['n_lost']} verdict(s): {r['lost'][:4]}. B120 "
            f"claims 0 in the losing direction.")

    def test_some_verdicts_are_gained(self, r):
        assert r["n_gained"] > 0, (
            "the fix changes nothing, so either the archive no longer holds a "
            "backticked reply or the predicate has been altered")


class TestEveryProbabilityRestsOnTwoRoutes:
    def test_mcnemar_agrees_across_two_implementations(self, r):
        assert r["mcnemar_gap"] < 1e-12, (
            f"scipy's binomtest and the mpmath exact tail disagree by "
            f"{r['mcnemar_gap']:.3e}")

    def test_fisher_agrees_across_two_implementations(self, r):
        assert r["fisher_gap"] < 1e-9, (
            f"scipy and the subject module's own mpmath Fisher disagree by "
            f"{r['fisher_gap']:.3e}")

    def test_the_withdrawn_figure_is_not_reproduced(self, r):
        """The point of the producer. If some future change DID reproduce
        1.108513e-11 that would be a finding, not a pass."""
        for key in ("mcnemar_scipy", "fisher_scipy"):
            assert abs(r[key] - 1.108513e-11) > 1e-12, (
                f"{key} now reproduces the withdrawn figure; the withdrawal "
                f"would need revisiting rather than this test relaxing")

    def test_mcnemar_is_the_exact_binomial_on_the_discordant_pairs(self, r):
        """DERIVED, not asserted: with 0 in one direction the 2-sided exact
        p is 2 / 2**d, which is checkable in closed form."""
        d = r["n_gained"] + r["n_lost"]
        if min(r["n_gained"], r["n_lost"]) != 0:
            pytest.skip("both directions are non-empty, so the closed form differs")
        assert abs(r["mcnemar_scipy"] - 2.0 / (2 ** d)) < 1e-15, (
            f"with {d} discordant pairs all in 1 direction the 2-sided exact p "
            f"is {2.0 / (2 ** d):.6e}, and the producer reports "
            f"{r['mcnemar_scipy']:.6e}")


class TestItRunsAndItsHelpDoesNot:
    def test_it_exits_zero(self):
        p = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=1200)
        assert p.returncode == 0, p.stderr[-700:]
        assert "WHAT THE BACKTICK ACTUALLY CHANGED" in p.stdout

    def test_help_answers_without_measuring(self):
        p = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr[-400:]
        assert "replies enumerated" not in p.stdout, "`--help` ran the measurement"
        assert "usage:" in p.stdout
