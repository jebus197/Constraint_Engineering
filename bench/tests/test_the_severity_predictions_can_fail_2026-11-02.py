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
at `bench/reference_runner_v3.py:10432` checks that the model's stated R_k
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

class TestTheMissingPredicateBranchIS_EXECUTED:
    """The source check above is weak, so the branch is EXECUTED here.

    WHY BOTH. `test_a_missing_predicate_is_NOT_TESTABLE_not_held` reads the
    scorer's SOURCE TEXT. On 2026-11-02 the handling was written with the phrase
    split across 2 adjacent string literals -- "could not be " and "imported,
    so any" -- and the source check could not see across the line break, so it
    failed against a scorer that handled the case correctly. The project's own
    rule names this: a test that asserts on source text asserts only that the
    text describes itself, and where both forms exist as live code the test must
    CALL them and compare outputs.

    THE DEFECT THAT PRECEDED BOTH, and it is why this class exists at all:
    `proven_available` and `_why_unavailable` were SET by the import handler and
    never READ -- 3 writes, 0 reads -- so an import failure was detected and
    silently discarded. The scorer still ran and still printed a plausible
    answer, which is exactly the shape nothing but a guard would notice.
    """

    def _run_with_import_broken(self):
        """Execute the scorer with `severity_is_proven` made unimportable."""
        import builtins
        import importlib.util
        import io
        import contextlib

        spec = importlib.util.spec_from_file_location("_scorer_probe", SCORER)
        mod = importlib.util.module_from_spec(spec)
        real_import = builtins.__import__

        def broken(name, *a, **k):
            if name == "bench.reference_runner_v3" or name.endswith(
                    "reference_runner_v3"):
                raise ImportError("broken on purpose by the guard")
            return real_import(name, *a, **k)

        buf = io.StringIO()
        sys.modules["_scorer_probe"] = mod
        builtins.__import__ = broken
        # ★ `main()` reads `sys.argv` through argparse, so an in-process call
        # inherits PYTEST's arguments and argparse exits with "unrecognized
        # arguments". Found by this test failing on its first run, which is the
        # right way round. argv is replaced for the call and restored after.
        saved_argv = sys.argv
        sys.argv = ["score_the_severity_predictions_2026-11-02.py"]
        try:
            spec.loader.exec_module(mod)
            with contextlib.redirect_stdout(buf):
                try:
                    mod.main()
                except SystemExit:
                    pass
        finally:
            sys.argv = saved_argv
            builtins.__import__ = real_import
            sys.modules.pop("_scorer_probe", None)
        return buf.getvalue()

    def test_the_scorer_SAYS_the_predicate_was_unavailable(self):
        out = self._run_with_import_broken()
        assert "could not be imported" in out, (
            "with the live predicate unimportable the scorer printed no notice; "
            "the import result is detected and discarded again. Its output "
            f"began: {out[:200]!r}")

    def test_it_says_NOT_TESTABLE_rather_than_reporting_a_verdict(self):
        out = self._run_with_import_broken()
        assert "NOT TESTABLE" in out, (
            "the scorer must say a prediction resting on the missing predicate "
            "is NOT TESTABLE rather than scoring a proxy")

    def test_the_HEALTHY_path_says_the_opposite_so_this_is_not_vacuous(self):
        """ANTI-VACUITY. Without this, a scorer that printed the unavailable
        notice unconditionally would satisfy both tests above."""
        import importlib.util
        import io
        import contextlib

        spec = importlib.util.spec_from_file_location("_scorer_ok", SCORER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_scorer_ok"] = mod
        buf = io.StringIO()
        saved_argv = sys.argv
        sys.argv = ["score_the_severity_predictions_2026-11-02.py"]
        try:
            spec.loader.exec_module(mod)
            with contextlib.redirect_stdout(buf):
                try:
                    mod.main()
                except SystemExit:
                    pass
        finally:
            sys.argv = saved_argv
            sys.modules.pop("_scorer_ok", None)
        out = buf.getvalue()
        assert "imported cleanly" in out, (
            "on the healthy path the scorer must say the predicate imported, "
            "so the unavailable notice is conditional rather than constant")
        assert "could not be imported" not in out, (
            "the scorer printed the unavailable notice on a healthy import, so "
            "the 2 tests above would pass on a constant")
