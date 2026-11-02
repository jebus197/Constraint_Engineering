"""The prediction scorer must be able to report FALSIFIED, and on the real predicate.

HIS RULING, 2026-11-01: *"at least one simulated run once these bounds are set to
check that the new severity mechanics work as expected and matches expectations."*

A scorer that can only ever report HELD scores nothing. This file pins that it
discriminates, using the ARCHIVED run of 2026-10-03 as the control: against that
run the scorer reports P1 and P2 HELD and P3 and P4 FALSIFIED, so both verdicts
are reachable on real data.

AND IT PINS THAT P4 USES THE LIVE PREDICATE. A first version tested
`not entry["verdicts"]` as a stand-in for `severity_is_proven`, which is a
DIFFERENT CLAIM from the one the pre-registration commits to -- the live function
at `bench/reference_runner_v3.py:10428` checks that the model's stated R_k
reproduces from its own stated inputs. The proxy and the real predicate disagree
on this very archive: 8 entries against 10. Scoring a proxy would have scored a
different prediction than the one fixed before the run, which destroys the only
thing pre-registration buys.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCORER = REPO / "scripts" / "score_the_severity_predictions_2026-11-02.py"
PREREG = REPO / "experimental_notes" / "data" / "severity_bounds_prereg_2026-11-02.json"
CONTROL = REPO / "bench" / "logs" / "study_run1b_2026-10-03_20261003T100439Z"


@pytest.fixture(scope="module")
def control_output():
    if not (CONTROL / "runner_state.json").is_file():
        pytest.skip(f"the control run {CONTROL.name} is not in this checkout")
    r = subprocess.run([sys.executable, str(SCORER), "--run-dir", str(CONTROL)],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr[-600:]
    return r.stdout


class TestTheScorerDiscriminates:

    def test_both_verdicts_occur_on_the_control(self, control_output):
        """THE ANTI-VACUITY TEST. A scorer that cannot fail is not scoring."""
        assert "FALSIFIED" in control_output, (
            "the scorer reports no FALSIFIED verdict on the control run, so it "
            "cannot discriminate and every HELD it reports is worthless")
        assert "HELD" in control_output, (
            "the scorer reports nothing HELD on the control either, so it may "
            "simply be failing everything")

    def test_each_prediction_is_scored_or_says_why_not(self, control_output):
        ids = [p["id"] for p in json.loads(PREREG.read_text())["predictions"]]
        assert ids, "the pre-registration holds no predictions"
        for pid in ids:
            assert re.search(rf"\]\s*{pid}\b", control_output), (
                f"{pid} is pre-registered and the scorer does not report it")
        assert "NOT SCORED" not in control_output, (
            "a pre-registered prediction has no test in the scorer")

    def test_an_untestable_prediction_is_not_reported_as_held(self):
        """A prediction with no denominator is neither held nor falsified, and
        calling it HELD is the flattering reading this project records."""
        src = SCORER.read_text()
        assert "NOT TESTABLE" in src
        assert "would be the flattering reading" in src, (
            "the scorer no longer states why an untestable prediction is not a "
            "pass, which is the distinction most easily lost in a summary")


class TestP4UsesTheLivePredicate:

    def test_the_scorer_imports_severity_is_proven(self):
        src = SCORER.read_text()
        assert "from bench.reference_runner_v3 import severity_is_proven" in src, (
            "P4 no longer uses the live predicate; the pre-registration's "
            "falsifier names `severity_is_proven` and a proxy scores a "
            "different claim")

    def test_the_proxy_and_the_real_predicate_actually_disagree(self):
        """If they agreed, the correction would be cosmetic. They do not."""
        if not (CONTROL / "runner_state.json").is_file():
            pytest.skip("control run absent")
        if str(REPO) not in sys.path:
            sys.path.insert(0, str(REPO))
        from bench.reference_runner_v3 import severity_is_proven
        st = json.loads((CONTROL / "runner_state.json").read_text())
        e = (st.get("registry") or {}).get("entries") or {}
        ents = list(e.values()) if isinstance(e, dict) else list(e)
        hi = [x for x in ents if isinstance(x.get("severity"), (int, float))
              and float(x["severity"]) >= 0.7
              and str(x.get("status", "")).upper() in ("RELEASED", "CLOSED")]
        by_proxy = [x for x in hi if not (x.get("verdicts") or [])]
        by_real = [x for x in hi if severity_is_proven(x)]
        assert len(by_proxy) != len(by_real), (
            f"the proxy and the live predicate now agree ({len(by_proxy)} vs "
            f"{len(by_real)}), so this test no longer demonstrates why the "
            f"correction mattered -- re-measure before trusting either")

    def test_a_missing_predicate_is_NOT_TESTABLE_not_held(self):
        src = SCORER.read_text()
        assert "could not be imported" in src and "NOT TESTABLE" in src, (
            "if the live predicate cannot be imported the scorer must say so, "
            "not fall back to a proxy and report a verdict")


class TestTheScorerIsInert:

    def test_help_costs_nothing_and_writes_nothing(self):
        before = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                                capture_output=True, text=True).stdout
        r = subprocess.run([sys.executable, str(SCORER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                               capture_output=True, text=True).stdout
        assert r.returncode == 0 and "usage" in r.stdout.lower()
        assert before == after, "--help changed the working tree"

    def test_it_writes_nothing_at_all(self):
        src = SCORER.read_text()
        assert "write_text(" not in src and "open(" not in src, (
            "the scorer writes; it must only read the run's own record")
