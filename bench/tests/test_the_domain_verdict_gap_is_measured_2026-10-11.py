"""Item 5: the domain-verdict gap is measured by a script, and the script self-checks.

HIS RULING, 2026-10-11: *"If there is valid work to do, then you should do it."*
He was right that saying the premise needed rebuilding and then saying to park the
item could not both stand.

HIS CHALLENGE, 2026-10-08, which the self-check answers mechanically: *"Ae you even
checking if these numbers make any practical sense before writing them"*.

WHAT THIS PINS
  1. The measurement exists, runs, and its --help costs nothing.
  2. The settled/unsettled split is taken from the runner's own position, not invented.
  3. The arithmetic that condemned the withdrawn figures is itself correct -- checked
     against SymPy on exact rationals, because the first attempt at that arithmetic
     was ALSO wrong.
  4. The self-check CAN refuse. A rate outside [0,1] or parts that do not sum to
     their total exits 3 rather than printing.
  5. The denominator excludes what it should: test outcomes sharing the `status` key,
     and the same finding counted twice from a run's state file and its report.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "the_domain_verdict_gap_2026-10-11.py"
sys.path.insert(0, str(REPO / "bench"))


def _mod():
    spec = importlib.util.spec_from_file_location("dvg", str(SCRIPT))
    m = importlib.util.module_from_spec(spec)
    sys.modules["dvg"] = m
    spec.loader.exec_module(m)
    return m


class TestItExistsAndRunsForFree:
    def test_help_is_answered_without_doing_the_work(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           capture_output=True, text=True, timeout=120, cwd=str(REPO))
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "SETTLED-VERDICT RATE BY DOMAIN" not in r.stdout, (
            "--help ran the whole measurement")

    def test_it_runs_and_its_checks_pass(self):
        r = subprocess.run([sys.executable, str(SCRIPT)],
                           capture_output=True, text=True, timeout=900, cwd=str(REPO))
        assert r.returncode == 0, f"the consistency check refused: {r.stdout[-800:]}"
        assert "shares of all settled outcomes sum to 1.000000" in r.stdout


class TestTheDefinitionsComeFromTheCode:
    def test_unconfirmed_is_not_settled_as_the_runner_states(self):
        """`reference_runner_v3.py:3207`: *"That path already excludes UNCONFIRMED
        from 'settled' and is correct"*."""
        m = _mod()
        assert "UNCONFIRMED" in m.UNSETTLED
        assert "UNCONFIRMED" not in m.SETTLED

    def test_a_refuted_finding_reached_a_verdict(self):
        m = _mod()
        assert "REFUTED" in m.SETTLED, "a refuted finding was decided, not left open"

    def test_the_two_sets_are_disjoint(self):
        m = _mod()
        assert not (m.SETTLED & m.UNSETTLED)
        assert not (m.SETTLED & m.NOT_A_FINDING_STATUS)

    def test_test_outcomes_are_excluded_from_the_denominator(self):
        """PASS/FAIL/SKIP/WARN share the `status` key and are not findings.
        Counting them is how a denominator inflates silently."""
        m = _mod()
        for v in ("PASS", "FAIL", "SKIP", "WARN"):
            assert v in m.NOT_A_FINDING_STATUS


class TestTheCondemningArithmeticIsItselfCorrect:
    def test_sympy_confirms_the_implied_share(self):
        import sympy as sp
        implied = (sp.Rational(7603, 10000) * 1304) / (
            sp.Rational(7603, 10000) * 1304 + sp.Rational(4003, 10000) * 1093)
        assert implied == sp.Rational(9914312, 14289591)
        assert abs(float(implied) - 0.693814) < 1e-6

    def test_sympy_confirms_the_impossible_rate(self):
        import sympy as sp
        r = sp.Symbol("r", positive=True)
        needed = sp.solve(sp.Eq((r * 1304) / (r * 1304 + sp.Rational(4003, 10000) * 1093),
                                sp.Rational(9684, 10000)), r)[0]
        assert abs(float(needed) - 10.282432) < 1e-6
        assert float(needed) > 1.0, "the withdrawal's whole basis"

    def test_the_first_attempt_at_this_arithmetic_was_wrong_and_says_so(self):
        """0.6142 and 14.6356 went to the founder. Both were wrong. The conclusion
        held, but a correction with its own arithmetic error must be recorded."""
        src = SCRIPT.read_text(encoding="utf-8")
        assert "0.6142" in src and "14.6356" in src, (
            "the second-order error must stay recorded, not quietly fixed")
        assert "MISCALCULATED" in src

    def test_mpmath_agrees_with_sympy(self):
        import mpmath as mp
        mp.mp.dps = 30
        v = (mp.mpf("0.7603") * 1304) / (mp.mpf("0.7603") * 1304
                                         + mp.mpf("0.4003") * 1093)
        assert abs(float(v) - 0.693814) < 1e-6


class TestTheSelfCheckCanRefuse:
    """A check that cannot fail is not a check."""

    def test_parts_that_do_not_sum_to_their_total_are_refused(self, monkeypatch):
        import collections
        m = _mod()
        monkeypatch.setattr(m, "collect", lambda: (
            {"bogus": collections.Counter(
                {"settled": 10, "unsettled": 2, "unclassified": 0, "total": 99})},
            {}))
        assert m.main(["x"]) == 3, "parts that do not sum to the total were accepted"

    def test_an_empty_attribution_is_refused(self, monkeypatch):
        m = _mod()
        monkeypatch.setattr(m, "collect", lambda: ({}, {}))
        assert m.main(["x"]) == 3

    def test_a_consistent_set_is_accepted(self, monkeypatch):
        import collections
        m = _mod()
        monkeypatch.setattr(m, "collect", lambda: (
            {"a": collections.Counter({"settled": 8, "unsettled": 2,
                                       "unclassified": 0, "total": 10}),
             "b": collections.Counter({"settled": 3, "unsettled": 7,
                                       "unclassified": 0, "total": 10})},
            {}))
        assert m.main(["x"]) == 0


class TestTheBoundaryIsStated:
    def test_it_says_the_gap_is_not_attributed_to_the_domain_alone(self):
        """Domains differ in target article, roster, runner version and date. A
        measured difference between them is not caused BY the domain."""
        r = subprocess.run([sys.executable, str(SCRIPT)],
                           capture_output=True, text=True, timeout=900, cwd=str(REPO))
        assert ("not attributable to the domain alone"
                in r.stdout.replace("\n", " ").lower())

    def test_domain_is_run_level_and_the_script_says_so(self):
        src = SCRIPT.read_text(encoding="utf-8")
        assert "RUN-LEVEL" in src
        assert "no finding record in the" in src
