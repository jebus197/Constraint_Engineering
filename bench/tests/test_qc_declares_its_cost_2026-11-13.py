"""`qc` must not spend the suite unasked, and its waiter must outlast it.

ENTRY B172. `scripts/cdsfl_qc.py` is documented on both of his surfaces as
quality control to run and fix what it prints. It silently ran the FULL test
suite, which occupies the only heavy process slot an 8 GiB machine has.

2 defects, independent, and the 2nd is the one the entry did not name:

  D1  the suite ran BY DEFAULT.
  D2  `PYTEST_SUITE_TIMEOUT_S = 1800` was 6.27x SHORTER than the recorded
      suite at 11278.43 s, so `measure_suite` could only ever raise
      TimeoutExpired and return None after burning 30 minutes. The
      "Suite is GREEN, measured this run" branch was UNREACHABLE at every
      suite size this project has recorded, including the 8036.30 s the
      entry itself quotes.

★ NEITHER CAPABILITY IS REMOVED. `--with-suite` runs the measurement exactly
as before, and the typed constant survives as the FLOOR for a checkout with
no ledger to derive from. `additive-standard` forbids removing a feature
without a committed measurement showing a replacement dominates, and none
exists here -- the measurement is useful, it was merely unasked-for.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
QC = REPO / "scripts" / "cdsfl_qc.py"


@pytest.fixture(scope="module")
def qc():
    spec = importlib.util.spec_from_file_location("cdsfl_qc_under_test", QC)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_qc_under_test"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


class TestTheDefaultDoesNotSpendTheSuite:

    @pytest.fixture(autouse=True)
    def _no_collection(self, qc, monkeypatch):
        """★ FAKE THE COLLECTION COUNT, NOT THE THING UNDER TEST.

        `check_test_consistency` also calls `test_count()`, which shells out to
        collect all 17547 tests and costs about 10 s. These 4 tests assert on
        the SUITE-MEASUREMENT branches and nothing about collection, so paying
        that 4 times on every commit board buys nothing -- 42 s against 0.4 s.

        This is the sibling file's own idiom (`_fake_counts` patches
        `test_count` the same way) and it does NOT make these tests vacuous:
        the mutation harness `scripts/the_residue_rule_mutations...`'s sibling
        for this entry drives 7 reversions through them and every one goes red
        with this fixture in place. A guard that got faster by ceasing to test
        is a defect this project has already recorded; this one got faster by
        not re-measuring something it never asserted on.
        """
        monkeypatch.setattr(qc, "test_count", lambda: 17547)

    def test_the_default_never_calls_measure_suite(self, qc, monkeypatch):
        """★ BY EXECUTION, NOT BY READING THE SOURCE. A test asserting that
        the string `--with-suite` appears would pass with the call still in
        place; only driving it can tell a guard from a comment."""
        def explode(*a, **k):
            raise AssertionError(
                "qc ran the full test suite without being asked. That is "
                "hours of his machine for a command his own list documents "
                "as a documentation sweep.")
        monkeypatch.setattr(qc, "measure_suite", explode)
        findings = qc.check_test_consistency(REPO)
        assert isinstance(findings, list)

    def test_the_skip_is_announced_and_names_the_flag(self, qc, monkeypatch):
        """A silent skip is as bad as a silent spend: the reader cannot tell
        'the suite passed' from 'the suite was never run'."""
        monkeypatch.setattr(qc, "measure_suite",
                            lambda *a, **k: pytest.fail("called"))
        findings = qc.check_test_consistency(REPO)
        skips = [f for f in findings
                 if "NOT run" in f["detail"] or "not run" in f["detail"]]
        assert len(skips) == 1, (
            f"the skip is not announced exactly once: {findings}")
        assert "--with-suite" in skips[0]["detail"], (
            "the skip does not tell him how to get the measurement back")

    def test_a_deliberate_skip_is_not_a_failed_measurement(self, qc, monkeypatch):
        """★ A FAIL-SAFE MUST NOT BE RECORDED AS A FACT. Reporting the skip
        as 'could not measure pass count' would be the right decision carrying
        a false reason -- a shape already logged in this project as a defect."""
        monkeypatch.setattr(qc, "measure_suite",
                            lambda *a, **k: pytest.fail("called"))
        findings = qc.check_test_consistency(REPO)
        warns = [f for f in findings
                 if f["category"] == "WARN" and "Could not measure" in f["detail"]]
        assert not warns, (
            f"a deliberate skip was reported as a failure to measure: {warns}")
        skips = [f for f in findings if "NOT run" in f["detail"]]
        assert skips and skips[0]["category"] == "INFO", (
            f"the skip is categorised {skips[0]['category'] if skips else None!r}, "
            f"not INFO")

    def test_the_capability_is_preserved_under_the_flag(self, qc, monkeypatch):
        """The measurement is made ASKED-FOR, not removed."""
        calls = []
        monkeypatch.setattr(qc, "measure_suite",
                            lambda root: calls.append(root) or
                            {"passed": 1, "skipped": 0, "failed": 0, "error": 0})
        qc.check_test_consistency(REPO, with_suite=True)
        assert len(calls) == 1, (
            "--with-suite no longer runs the suite; the capability was removed "
            "rather than gated, which additive-standard forbids without a "
            "committed measurement that none exists for")


class TestTheWaiterOutlastsTheSuite:

    def test_the_derived_timeout_exceeds_the_recorded_runtime(self, qc):
        """★ THE DEFECT B172 DID NOT NAME. 1800 s against 11278.43 s."""
        record = json.loads(
            (REPO / "resources" / "suite_record.json").read_text())
        recorded = float(record["seconds"])
        assert recorded > 0, "the ledger has no runtime; this fixture is stale"
        derived = qc.suite_timeout(REPO)
        assert derived > recorded, (
            f"the waiter is {derived} s against a suite recorded at "
            f"{recorded} s, so measure_suite can only time out and return "
            f"None after spending every one of those seconds")
        assert qc.PYTEST_SUITE_TIMEOUT_S < recorded, (
            "the fixture is vacuous: the typed constant now exceeds the "
            "recorded runtime, so this test would pass without the derivation")

    def test_a_checkout_with_no_ledger_falls_back_to_the_floor(self, qc, tmp_path):
        """★ THE FLOOR IS KEPT, NOT REPLACED. A fresh checkout has no record."""
        assert qc.suite_timeout(tmp_path) == qc.PYTEST_SUITE_TIMEOUT_S

    def test_a_corrupt_ledger_does_not_crash_the_sweep(self, qc, tmp_path):
        (tmp_path / "resources").mkdir()
        (tmp_path / "resources" / "suite_record.json").write_text("{ not json")
        assert qc.suite_timeout(tmp_path) == qc.PYTEST_SUITE_TIMEOUT_S
        (tmp_path / "resources" / "suite_record.json").write_text('{"seconds": 0}')
        assert qc.suite_timeout(tmp_path) == qc.PYTEST_SUITE_TIMEOUT_S


class TestHelpCostsNothing:

    def test_help_does_not_run_the_suite(self):
        """★ A --help MUST NEVER COST MONEY OR TIME. Measured, not assumed:
        if --help reached the suite this would exceed its own timeout."""
        r = subprocess.run([sys.executable, str(QC), "--help"],
                           cwd=str(REPO), capture_output=True, text=True,
                           timeout=60)
        assert r.returncode == 0, r.stderr[-400:]
        assert "--with-suite" in r.stdout, (
            "the flag is undocumented in --help, so the only way to discover "
            "the capability is to read the source")


class TestTheWiringItselfHolds:
    """★ THE 3 GAPS THE MUTATION HARNESS FOUND, and it found them because the
    tests above all call `check_test_consistency` DIRECTLY.

    Driving a function is not driving the program. Reverting `main()`'s flag to
    a hard-coded True, and reverting the subprocess call site to the typed
    constant, both left every test above green -- the first because nothing
    exercised `main()`'s dispatch, the second because nothing asserted what
    value actually reaches `subprocess.run`. Both reversions restore the exact
    defect B172 exists to fix.
    """

    def _stub_everything_else(self, qc, monkeypatch, tmp_path):
        """Stub the other checks so main() is cheap, as the sibling file does."""
        monkeypatch.setattr(qc, "repo_root", lambda: tmp_path)
        monkeypatch.setattr(qc, "timestamp_iso", lambda: "2026-11-13T00:00:00+00:00")
        for name in ("check_staleness", "check_experiment_consistency",
                     "check_results_document", "check_glossary",
                     "check_onboard_script", "check_log_seals"):
            if hasattr(qc, name):
                monkeypatch.setattr(qc, name, lambda _r, **_k: [])
        monkeypatch.setattr(qc, "check_broken_references", lambda _r, **_k: [])
        monkeypatch.setattr(qc, "test_count", lambda: 17547)

    def test_main_does_not_spend_the_suite_by_default(self, qc, monkeypatch, tmp_path):
        """★ CATCHES: main() passing a hard-coded True. Drives the PROGRAM."""
        self._stub_everything_else(qc, monkeypatch, tmp_path)

        def explode(*a, **k):
            raise AssertionError(
                "main() ran the full suite with no flag given. That is hours "
                "of his machine for a command documented as a documentation "
                "sweep, which is the whole of B172.")

        monkeypatch.setattr(qc, "measure_suite", explode)
        monkeypatch.setattr(sys, "argv", ["cdsfl_qc.py"])
        assert qc.main() == 0

    def test_main_does_spend_it_when_asked(self, qc, monkeypatch, tmp_path):
        """The discrimination half: without this the test above passes with
        the capability deleted rather than gated."""
        self._stub_everything_else(qc, monkeypatch, tmp_path)
        calls = []
        monkeypatch.setattr(
            qc, "measure_suite",
            lambda root: calls.append(root) or {
                "passed": 1, "skipped": 0, "failed": 0, "error": 0})
        monkeypatch.setattr(sys, "argv", ["cdsfl_qc.py", "--with-suite"])
        qc.main()
        assert len(calls) == 1, (
            "--with-suite did not reach the check; the flag is decorative and "
            "the measurement is unreachable from the command line")

    def test_the_derived_timeout_actually_reaches_subprocess(self, qc, monkeypatch):
        """★ CATCHES: the call site reverting to the typed constant.

        Asserting that `suite_timeout()` returns a large number proves nothing
        if `measure_suite` still passes the 1800 s constant. This captures the
        value that actually arrives at `subprocess.run`.
        """
        seen = {}

        def capture(*a, **kw):
            seen.update(kw)
            return subprocess.CompletedProcess(a, 0, "1 passed in 1.00s\n", "")

        monkeypatch.setattr(subprocess, "run", capture)
        qc.measure_suite(REPO)
        assert "timeout" in seen, "measure_suite stopped bounding the run at all"
        assert seen["timeout"] == qc.suite_timeout(REPO), (
            f"the call site passes {seen['timeout']} where the derivation says "
            f"{qc.suite_timeout(REPO)}")
        recorded = float(json.loads(
            (REPO / "resources" / "suite_record.json").read_text())["seconds"])
        assert seen["timeout"] > recorded, (
            f"the waiter that reaches subprocess is {seen['timeout']} s "
            f"against a suite recorded at {recorded} s, so the measurement can "
            f"only ever time out -- B172's 2nd defect, restored")
