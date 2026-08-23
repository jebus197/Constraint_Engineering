"""Three repairs to the mechanical acceptance gate, 2026-08-23.

All three were found by CC2 and Fable in a compelled-convergence adversarial review;
the first two independently by both. Each is the project's house failure mode -- a
harness fault rendering as a verdict about the models -- inside the gate whose whole
claim is that it is mechanical and two-sided.

  A. A pytest COLLECTION error emits no ``FAILED`` line, so the suite check saw an
     empty failure set and ACCEPTED a patch that broke every test in the repository.
  B. An unmeasurable parent baseline was cached as ``frozenset()``, making every
     PRE-EXISTING failure read as newly caused, rejecting every later candidate, and
     driving the acceptance rate to near zero -- which this project pre-registered as
     the tell for "the models cannot do the task".
  C. Model-supplied paths were joined to the worktree unvalidated, and pathlib
     discards the left operand on an absolute right operand.
"""
from __future__ import annotations

import pathlib

import pytest

from bench import build_acceptance as BA


class TestACollectionErrorIsNotAGreenSuite:
    COLLECTION_ERROR = (
        "=========================== short test summary info ============================\n"
        "ERROR bench/tests/test_thing.py\n"
        "!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!\n"
        "1 error in 0.19s\n"
    )

    def test_error_lines_are_counted_as_failures(self):
        ids = BA.failing_nodeids(self.COLLECTION_ERROR)
        assert ids == {"bench/tests/test_thing.py"}, (
            "a collection error must not read as an empty failure set; that is how a "
            "patch breaking the whole suite was certified green")

    def test_failed_lines_still_counted(self):
        out = "FAILED bench/tests/test_a.py::test_one\nFAILED bench/tests/test_b.py::test_two\n"
        assert BA.failing_nodeids(out) == {
            "bench/tests/test_a.py::test_one", "bench/tests/test_b.py::test_two"}

    def test_both_together(self):
        out = "FAILED t/test_a.py::x\nERROR t/test_b.py\n"
        assert BA.failing_nodeids(out) == {"t/test_a.py::x", "t/test_b.py"}

    def test_a_clean_run_is_still_empty(self):
        assert BA.failing_nodeids("120 passed in 3.4s\n") == frozenset()


class TestAnUnmeasuredBaselineIsNotAGreenBaseline:
    def test_returns_None_when_the_worktree_cannot_be_made(self, monkeypatch):
        BA._BASELINE.clear()
        monkeypatch.setattr(BA, "_run", lambda *a, **k: (128, "fatal: invalid reference"))
        out = BA.suite_baseline("deadbeef", ["python3", "-m", "pytest"], 60)
        assert out is None, "an unmeasurable baseline must not render as 'nothing fails'"

    def test_does_not_cache_the_failure(self, monkeypatch):
        BA._BASELINE.clear()
        monkeypatch.setattr(BA, "_run", lambda *a, **k: (128, "fail"))
        BA.suite_baseline("deadbeef", ["python3", "-m", "pytest"], 60)
        assert not BA._BASELINE, (
            "caching the failure poisons every later candidate at this parent")

    def test_returns_None_on_an_exception_too(self, monkeypatch):
        BA._BASELINE.clear()
        def boom(*a, **k): raise TimeoutError("baseline suite timed out")
        monkeypatch.setattr(BA, "_run", boom)
        assert BA.suite_baseline("deadbeef", ["python3", "-m", "pytest"], 60) is None

    def test_evaluate_refuses_rather_than_judging(self, monkeypatch):
        """The refusal must come BEFORE any worktree is made, on the baseline alone."""
        monkeypatch.setattr(BA, "suite_baseline", lambda *a, **k: None)
        response = (
            "<<<< SEARCH bench/reference_runner_v2.py\n"
            "old text\n"
            "==== REPLACE\n"
            "new text\n"
            ">>>>\n\n"
            "TEST_FILE: bench/tests/test_x.py\n"
            "```python\n"
            "def test_x():\n"
            "    assert True\n"
            "```\n"
        )
        v = BA.evaluate(response, parent="HEAD")
        assert v.outcome == BA.ERR_HARNESS, f"got {v.outcome}: {v.detail}"
        assert "baseline" in v.detail.lower()


class TestModelSuppliedPathsCannotEscapeTheWorktree:
    @pytest.mark.parametrize("bad", [
        "/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/reference_runner_v2.py",
        "/etc/hosts",
        "../../../etc/hosts",
        "bench/../../escape.py",
        "", "   ",
    ])
    def test_refused(self, tmp_path, bad):
        assert BA._confine(tmp_path, bad) is None, f"escaped the worktree: {bad!r}"

    @pytest.mark.parametrize("ok", [
        "bench/tests/test_new.py", "test_new.py", "a/b/c/d.py",
    ])
    def test_allowed(self, tmp_path, ok):
        got = BA._confine(tmp_path, ok)
        assert got is not None and str(got).startswith(str(tmp_path.resolve()))

    def test_the_pathlib_behaviour_this_guards_against_is_real(self, tmp_path):
        """Pinned so nobody 'simplifies' the guard away as paranoia."""
        assert pathlib.Path(tmp_path) / "/etc/hosts" == pathlib.Path("/etc/hosts")
