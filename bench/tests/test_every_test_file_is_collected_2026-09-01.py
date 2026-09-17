"""A test file the suite does not collect is not a test.

Three regression files written on 2026-09-01 landed in a root `tests/` directory
that the suite command (`python3 -m pytest bench/tests`) does not reach. They
passed when invoked directly and contributed nothing to the suite count. That
was caught by accident, in `git status`.

The same class had already cost more than a near-miss. On 2026-08-30 a panel
reviewer wrote eight commissioning tests for two repairs -- the overlay leaking
the real `.git`, and the fix-efficacy probe that had been built and never called.
The file was rescued from the sandbox into `experimental_notes/` and never wired
in. Seven of the eight test names appeared nowhere under `bench/tests/`. They
guarded repairs nobody was re-checking for two days.

This test makes the collection root a property of the tree rather than a habit.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
COLLECTED_ROOT = "bench/tests/"

# Files named test_*.py that are deliberately NOT pytest modules. Each entry
# needs a reason, and the reason is checked below -- an allowlist nobody
# justifies becomes a place to hide failures.
NOT_PYTEST_MODULES = {
    "bench/test_falsifier_matrix_2026-06-06.py":
        "a live dispatch script, not a pytest module: it runs the real composer "
        "target against models and writes metric-harness logs. `pytest` on it "
        "collects zero tests. Named test_* by an older convention and left "
        "alone because scripts and notes reference it by that path.",
    "experimental_notes/unextracted_sandbox_2026-08-30/"
    "test_repair_loop_wiring_2026-08-30.py":
        "the archived artefact of what a reviewer wrote inside its sandbox on "
        "2026-08-30, kept as a record of the review. The live copy was "
        "integrated at bench/tests/test_repair_loop_wiring_2026-08-30.py on "
        "2026-09-01; this one stays frozen and still names reference_runner_v2, "
        "which is what the file was called when it was written.",
}


#: Directories that are not the project: another checkout's worktree, a build
#: cache, a seat's harvested copy. A test file inside one of these is not a
#: stray project test.
_NOT_THE_PROJECT = (".git/", ".claude/worktrees/", "node_modules/", "__pycache__/",
                    "bench/logs/", ".venv/", "venv/", "sandbox_harvest/",
                    "worktree_harvest/")


def _walked_test_files():
    """Every `test_*.py` in the tree, found by walking it.

    THE FALLBACK, AND WHY IT IS A REPAIR RATHER THAN A SKIP. The founder,
    2026-09-17: *"Surely you can't repair these ... and skip? That doesn't make
    any sense. Why not just repair?"* Right, where a real answer survives the
    missing precondition. `git ls-files` answers "which test files does the
    project TRACK", and in a copy with no `.git` -- a panel sandbox, a ZIP, a
    Zenodo archive -- git exits 128 and the old assertion reported a project
    defect that was really a missing directory. Walking the tree answers the
    question that still HAS an answer there: which test files EXIST outside the
    collected root, which is the thing this test is protecting against. Nothing
    is skipped, and in a real checkout git remains the authority.
    """
    out = []
    for path in sorted(REPO.rglob("test_*.py")):
        rel = path.relative_to(REPO).as_posix()
        if any(part in f"{rel}/" for part in _NOT_THE_PROJECT):
            continue
        out.append(rel)
    return out


def _tracked_test_files():
    out = subprocess.run(["git", "ls-files", "*/test_*.py", "test_*.py"],
                         cwd=str(REPO), capture_output=True, text=True,
                         timeout=120)
    if out.returncode == 0:
        return [ln for ln in out.stdout.splitlines() if ln.strip()]
    if out.returncode == 128 or "not a git repository" in (out.stderr or "").lower():
        return _walked_test_files()
    assert False, out.stderr


def _is_repo() -> bool:
    return subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(REPO),
                          capture_output=True, text=True).returncode == 0


class TestEveryTestFileIsReachable:
    def test_no_test_file_sits_outside_the_collected_root(self):
        stray = [f for f in _tracked_test_files()
                 if not f.startswith(COLLECTED_ROOT)
                 and f not in NOT_PYTEST_MODULES]
        assert not stray, (
            ("" if _is_repo() else
             "NOTE: this tree has no .git, so the list came from walking the "
             "directory rather than from git, and an uncommitted local file "
             "counts as a stray here. ") +
            "test files outside the suite's collection root -- they will pass "
            "when invoked directly and contribute nothing to the suite:\n  "
            + "\n  ".join(stray)
            + f"\nMove them under {COLLECTED_ROOT}, or add an entry to "
              "NOT_PYTEST_MODULES saying why they are not pytest modules.")

    def test_the_allowlist_is_not_a_place_to_hide_failures(self):
        """Every exemption names a real file and gives a substantive reason."""
        for path, reason in NOT_PYTEST_MODULES.items():
            assert (REPO / path).is_file(), (
                f"allowlisted file no longer exists: {path}. Remove the entry.")
            assert len(reason) > 60, (
                f"allowlist entry for {path} does not explain itself")

    def test_an_allowlisted_script_really_collects_no_tests(self):
        """The one claim the allowlist makes that can be checked mechanically."""
        script = "bench/test_falsifier_matrix_2026-06-06.py"
        out = subprocess.run(
            [sys.executable, "-m", "pytest", script, "--collect-only", "-q",
             "-p", "no:cacheprovider"],
            cwd=str(REPO), capture_output=True, text=True, timeout=600)
        combined = out.stdout + out.stderr
        assert "no tests collected" in combined or "no tests ran" in combined, (
            f"{script} now defines real tests and must move under "
            f"{COLLECTED_ROOT}:\n{out.stdout[-600:]}")


class TestTheRescuedTestsAreLive:
    """The instance that motivated this file, pinned so it cannot regress."""

    def test_the_repair_loop_commissioning_tests_are_in_the_suite(self):
        live = REPO / "bench" / "tests" / "test_repair_loop_wiring_2026-08-30.py"
        assert live.is_file(), (
            "the 2026-08-30 commissioning tests for the overlay .git leak and "
            "the fix-efficacy probe are no longer in the suite")
        body = live.read_text(encoding="utf-8")
        for name in ("test_overlay_does_not_mirror_dot_git",
                     "test_the_runner_actually_reaches_the_probe",
                     "test_the_probe_is_contributory_and_cannot_gate_anything"):
            assert f"def {name}" in body, f"{name} has gone missing"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
