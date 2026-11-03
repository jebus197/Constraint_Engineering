"""The superlative check has 2 independent routes, and they can disagree.

WHY THIS GUARD EXISTS. `scripts/c0001_provenance_does_not_reconcile_2026-11-03.py`
tested the claim `the highest of the 28` by counting registry entries at or above
a severity of 1.0 and asking whether that count was 0. That is 1 route through a
threshold CONSTANT, and a constant is exactly what drifts. A second route -- take
the run's actual maximum severity and compare -- was added on 2026-11-03 under
the primary/secondary falsifier rule of 2026-10-31.

THE DECISIVE TEST IS THE DISAGREEMENT CASE, not the agreement case. On the live
archive the 2 routes agree in 4 of 4 candidate runs, so a guard built only from
real runs would pass with the second route DELETED and would prove nothing. The
case that separates them is a run whose maximum severity sits BELOW the 1.0
threshold: the counting route then reports 0 entries at or above 1.0 and so
concludes the finding IS the highest, while the maximum route sees a higher
entry and concludes it is not. That case is planted here.

AND NO CONFIDENCE INTERVAL IS EXPECTED ANYWHERE, which is tested as a behaviour
rather than asserted about the source: every figure the producer reports is a
complete enumeration serving an identification question, and an interval on
`1 of 4` would answer what fraction of composer runs carry severity 0.90 --
a different question. See the producer's own `_max_severity` docstring.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = REPO / "scripts" / "c0001_provenance_does_not_reconcile_2026-11-03.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_c0001_guard", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_c0001_guard"] = m
    spec.loader.exec_module(m)
    return m


class TestTheSecondRouteIsReal:
    def test_the_maximum_route_returns_the_maximum(self, mod):
        ents = {"C0001": {"severity": 0.9}, "C0002": {"severity": 1.0},
                "C0003": {"severity": 0.5}}
        assert mod._max_severity(ents) == 1.0

    def test_the_two_routes_disagree_when_the_top_is_below_the_threshold(self, mod):
        """THE ANTI-VACUITY CASE. Max severity 0.95, so nothing reaches 1.0.

        The counting route concludes C0001 IS the highest (0 entries at or above
        1.0). The maximum route sees 0.95 > 0.90 and concludes it is not. If this
        test ever passes with the second route removed, the second route was
        never load-bearing.
        """
        ents = {"C0001": {"severity": 0.90}, "C0002": {"severity": 0.95}}
        at_top = sum(1 for v in ents.values()
                     if isinstance(v, dict) and float(v.get("severity") or 0) >= 1.0)
        mx = mod._max_severity(ents)
        route_a = (at_top == 0)                    # primary: "it is the highest"
        route_b = (0.90 >= mx)                     # secondary: it is not
        assert route_a is True, "the counting route should be fooled here"
        assert route_b is False, "the maximum route should catch it"
        assert route_a != route_b, (
            "the 2 routes must be able to disagree, or the second adds nothing")

    def test_an_empty_registry_yields_no_maximum(self, mod):
        assert mod._max_severity({}) is None

    def test_a_missing_severity_is_not_read_as_zero(self, mod):
        """A None severity must be SKIPPED, not coerced to 0.0.

        THE FIRST VERSION OF THIS TEST WAS VACUOUS and the fix is recorded
        because the shape recurs. It asserted that
        `{"A": None, "B": 0.4}` yields 0.4 -- but coercing None to 0.0 ALSO
        yields 0.4, because 0.0 can never be the maximum of a set containing a
        positive number. A test of a maximum cannot detect a floor being
        inserted beneath it.

        The discriminating case is a registry where the None is the ONLY entry:
        skipping returns None, coercing returns 0.0. Those differ, so this
        assertion can actually fail.
        """
        assert mod._max_severity({"A": {"severity": None}}) is None, (
            "a None severity was coerced to 0.0 rather than skipped")
        assert mod._max_severity(
            {"A": {"severity": None}, "B": {"severity": 0.4}}) == 0.4


class TestTheProducerReportsBothRoutes:
    def test_it_runs_and_names_both_routes_and_their_agreement(self):
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=300)
        assert r.returncode == 0, r.stderr[-800:]
        out = r.stdout
        for needle in ("route A", "route B", "THE 2 ROUTES AGREE"):
            assert needle in out, f"the producer does not report {needle!r}"

    def test_it_states_the_superlative_fails_against_every_candidate(self):
        """The claim the 2nd route adds: not the highest in ANY candidate run,
        so the open identification cannot rescue the superlative."""
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=300)
        assert "candidate " in r.stdout and "not only the matching one" in r.stdout

    def test_it_reports_no_confidence_interval(self):
        """Every figure here is a complete enumeration serving an
        identification, so an interval would answer a different question."""
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=300)
        low = r.stdout.lower()
        for banned in ("wilson", "clopper", "95%"):
            assert banned not in low, (
                f"{banned!r} appeared: an interval on a census answers what "
                f"fraction of composer runs carry that severity, which is not "
                f"the question this producer asks")
