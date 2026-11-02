"""The apply-back gate must not blame a candidate for a failure it did not cause.

THE DEFECT THIS PINS, OBSERVED 2026-11-02. `_apply_back_gate` required exit 0
from a suite it ran in a sandbox that excludes `.git`, `bench/logs` and the
credentials. A suite containing a test that reads the archive therefore failed
there whatever the candidate said, and the gate reported it as the candidate's
doing. `study_run1b_rerun_20261102T033919Z` made 19 apply-back decisions: 19
REJECT, 0 PROMOTE, every one carrying the byte-identical reason
`suite_fail:3 failed, 48 passed, 28 skipped`. Across the whole run archive the
facility had REFUSED 34 of 34, Wilson 95% [0.898485, 1.000000] -- equivalently
promoted 0 of 34, Wilson [0.000000, 0.101515]. Producer:
`scripts/the_apply_back_gate_has_no_baseline_2026-11-02.py`.

IT DOES NOT NEED THE LIVE DEFECT TO BE PRESENT, which is the requirement in
`feedback_a_regression_guard_must_not_need_a_live_defect_2026-10-31`. Nothing
here reads the project's real suite, the real sandbox or the archive, so the
guard keeps its force once the real sandbox is green or the real suite changes.

IT EXECUTES THE GATE RATHER THAN DESCRIBING IT (`execute-do-not-grep`), but it
does NOT pay for a 364 MiB copy of the repository 6 times: `REPO_ROOT` is pointed
at a tiny tree and the "suite" is a 9-line script that reads the target and
reports failures accordingly. The function under test is the shipped one,
unmodified -- only the world it copies is small. The same device is used by
`bench/tests/test_build_acceptance_commissioning.py`, which fakes a suite with
`python3 -c "print('FAILED ...')"` for the same reason.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import reference_runner_v3 as rr  # noqa: E402

#: A "suite" that reports a failure which exists on BOTH sides, and a second one
#: only when the candidate carries the marker. Exits 1 either way, which is what
#: pytest does when tests fail.
FAKE_SUITE = '''\
import pathlib, sys
text = pathlib.Path("target.py").read_text()
print("FAILED tests/pre_existing.py::test_already_red")
if "BREAKS_IT" in text:
    print("FAILED tests/brand_new.py::test_newly_red")
sys.exit(1)
'''

#: A "suite" that aborts the way a pytest collection error does: exit 2. It
#: reads whichever target it is pointed at by argv, because the BASELINE is
#: measured against the PRISTINE file -- so making the baseline abort requires a
#: target whose pristine content already carries the marker, not a candidate
#: that carries it. Getting that wrong was the first version of this guard.
ABORTING_SUITE = '''\
import pathlib, sys
text = pathlib.Path(sys.argv[1]).read_text()
print("ERROR tests/collect.py")
sys.exit(2 if "ABORTS" in text else 1)
'''

TARGET = "target.py"
#: Pristine content already aborts, so the BASELINE exits 2 as well.
ABORTING_TARGET = "already_aborts.py"


@pytest.fixture
def tiny(tmp_path, monkeypatch):
    """A 3-file repository, so the gate's `copytree` is effectively free."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / TARGET).write_text("x = 1\n", encoding="utf-8")
    (repo / "fake_suite.py").write_text(FAKE_SUITE, encoding="utf-8")
    (repo / "aborting_suite.py").write_text(ABORTING_SUITE, encoding="utf-8")
    (repo / ABORTING_TARGET).write_text("x = 1  # ABORTS\n", encoding="utf-8")
    (repo / "spec.md").write_text("# A prose target\n\nSome prose.\n",
                                  encoding="utf-8")
    monkeypatch.setattr(rr, "REPO_ROOT", repo)
    rr._APPLY_BACK_BASELINE.clear()
    yield repo
    rr._APPLY_BACK_BASELINE.clear()


class TestAPreExistingFailureIsNotBlamedOnTheCandidate:
    def test_a_candidate_that_adds_nothing_is_accepted(self, tiny):
        """The property the 19 rejections violated."""
        ok, detail = rr._apply_back_gate("x = 2\n", TARGET,
                                         "python3 fake_suite.py")
        assert ok, (
            "a failure present WITHOUT the candidate was blamed on it: "
            f"{detail}")
        assert "pre-existing" in detail, detail

    def test_the_acceptance_says_the_sandbox_was_not_green(self, tiny):
        """A reader must never take `ok` to mean the suite passed."""
        ok, detail = rr._apply_back_gate("x = 2\n", TARGET,
                                         "python3 fake_suite.py")
        assert ok and "1 pre-existing" in detail, detail

    def test_a_genuinely_new_failure_is_still_rejected(self, tiny):
        """ANTI-VACUITY. A gate repaired into accepting everything is worse
        than the defect it replaced."""
        ok, detail = rr._apply_back_gate("x = 2  # BREAKS_IT\n", TARGET,
                                         "python3 fake_suite.py")
        assert not ok, f"a new failure was accepted: {detail}"
        assert "suite_regressed" in detail, detail
        assert "test_newly_red" in detail, (
            "the refusal must NAME the new failure, or a reader cannot act on "
            f"it: {detail}")
        assert "test_already_red" not in detail, (
            "the pre-existing failure must not appear in the reason, or the "
            f"reader is sent to the wrong place: {detail}")

    def test_the_guard_is_not_vacuous_because_the_baseline_is_what_saves_it(
            self, tiny):
        """Seed an EMPTY baseline -- what the old code assumed -- and the same
        candidate that passes above must now be refused. Without this, the first
        test could pass because the fake suite happened to be green."""
        rr._APPLY_BACK_BASELINE[(TARGET, "python3 fake_suite.py")] = (
            frozenset(), 0)
        ok, detail = rr._apply_back_gate("x = 2\n", TARGET,
                                         "python3 fake_suite.py")
        assert not ok, (
            "with an assumed-green baseline the pre-existing failure MUST look "
            "new; if it does not, the baseline is not what the first test "
            "measures")
        assert "test_already_red" in detail, detail


class TestTheBaselineCarriesItsExitCode:
    def test_an_abnormal_exit_on_both_sides_is_not_blamed_on_the_candidate(
            self, tiny):
        """A collection error exits 2. Where the sandbox aborts WITHOUT the
        candidate too, refusing it would reinstate the very defect being fixed.
        This was a fault in the first version of the repair, found by its own
        P-pass."""
        cmd = f"python3 aborting_suite.py {ABORTING_TARGET}"
        ok, detail = rr._apply_back_gate("x = 2  # ABORTS\n",
                                         ABORTING_TARGET, cmd)
        assert ok, f"an abort present on both sides was blamed on it: {detail}"
        assert "rc2" in detail, detail

    def test_an_abnormal_exit_only_with_the_candidate_is_refused(self, tiny):
        """The other side: the baseline runs, the candidate aborts."""
        # Pointed at the ORDINARY target, whose pristine content does not
        # abort, so the baseline exits 1 and only the candidate exits 2.
        cmd = f"python3 aborting_suite.py {TARGET}"
        ok, detail = rr._apply_back_gate("x = 2  # ABORTS\n", TARGET, cmd)
        assert not ok, f"a new abort was accepted: {detail}"
        assert "rc2" in detail and "baseline rc1" in detail, detail


class TestANonPythonTargetIsRefusedBeforeTheSuite:
    def test_prose_with_a_command_configured_is_refused_for_being_prose(
            self, tiny):
        """The hoisted refusal. It sat inside `if not test_cmd:` until
        2026-11-02, so a prose target WITH a command fell through to pytest --
        and all 7 prose runs in the archive carried one, every one of them the
        launcher's argparse default."""
        ok, detail = rr._apply_back_gate("# new prose\n", "spec.md",
                                         "python3 fake_suite.py")
        assert not ok, detail
        assert "non-Python target" in detail, (
            "a prose target must be refused for being prose, not handed a "
            f"pytest result that cannot depend on it: {detail}")
        assert "suite_fail" not in detail and "regressed" not in detail, detail

    def test_prose_is_not_accused_of_a_syntax_error(self, tiny):
        """The 2026-10-17 lesson, kept: English prose must never be reported as
        broken Python."""
        ok, detail = rr._apply_back_gate("# just prose\n", "spec.md",
                                         "python3 fake_suite.py")
        assert not ok and not detail.startswith("ast:"), detail

    def test_a_python_target_with_no_command_still_says_so(self, tiny):
        ok, detail = rr._apply_back_gate("x = 2\n", TARGET, "")
        assert not ok and "no test_cmd configured" in detail, detail

    def test_the_refusal_costs_no_sandbox(self, tiny, monkeypatch):
        """Prose is refused BEFORE the copy, which is what makes it cheap and
        is also why 7 archived runs wasted a suite run per finding."""
        called = []
        monkeypatch.setattr(rr.shutil, "copytree",
                            lambda *a, **k: called.append(1))
        rr._apply_back_gate("# prose\n", "spec.md", "python3 fake_suite.py")
        assert not called, "a prose refusal must not build a sandbox first"


class TestOneParserServesBothGates:
    def test_the_runner_uses_build_acceptances_parser(self):
        """Two implementations of 'which tests failed' is two chances to omit
        collection ERRORs, which is the 2026-08-23 lesson."""
        from bench import build_acceptance as BA
        assert rr.failing_nodeids is BA.failing_nodeids

    def test_that_parser_counts_collection_errors(self):
        ids = rr.failing_nodeids("ERROR bench/tests/test_x.py\n")
        assert ids == frozenset({"bench/tests/test_x.py"}), ids

    def test_the_baseline_is_cached_with_its_exit_code(self, tiny):
        rr._apply_back_gate("x = 2\n", TARGET, "python3 fake_suite.py")
        key = (TARGET, "python3 fake_suite.py")
        assert key in rr._APPLY_BACK_BASELINE, rr._APPLY_BACK_BASELINE
        ids, rc = rr._APPLY_BACK_BASELINE[key]
        assert isinstance(ids, frozenset) and isinstance(rc, int)
        assert rc == 1 and "tests/pre_existing.py::test_already_red" in ids
