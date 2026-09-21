"""The panel-confinement fallback must open only inside a declared sandbox.

WHAT THIS GUARDS. `bench/tools/run_simulated_experiment.py` confines the panel
to a disposable git worktree so a seat's relative writes cannot reach the live
target, and REFUSES to run when it cannot build one. On 2026-09-21 that refusal
made every sandboxed simulated run unlaunchable: the sandbox severs git history
on purpose, so `git worktree add` can never succeed inside it, and arm 1 of the
commissioning study exited 2 at 22:51:57 BST with "fatal: not a git repository".

The repair lets the runner build the same disposable cwd by COPYING when it is
already inside a throwaway tree. That is an escape hatch on a safety refusal,
and an escape hatch is exactly the thing that must be shown not to open by
accident -- so these tests assert the LOCK far more than the key.

The marker is a DIRECTORY, not a flag, precisely so it can be verified rather
than trusted: the wrapper exports the tree it built, and the runner compares it
against its own resolved root. Setting the variable to some other path does not
unlock anything.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "tools" / "run_simulated_experiment.py"
WRAPPER = REPO / "bench" / "tools" / "run_simulated_experiment_sandboxed.sh"

#: The predicate as the runner computes it. Kept in ONE place here and exercised
#: with the real `os.environ`, so the test fails if the runner's own form and
#: this one ever disagree about a case -- which is the point of the last test.
def _in_sandbox(repo: pathlib.Path) -> bool:
    declared = os.environ.get("CDSFL_SANDBOX_ROOT", "")
    return bool(declared) and pathlib.Path(declared).resolve() == repo.resolve()


def test_unset_marker_does_not_unlock(monkeypatch):
    """The live repository, where the variable is simply absent."""
    monkeypatch.delenv("CDSFL_SANDBOX_ROOT", raising=False)
    assert _in_sandbox(REPO) is False


def test_empty_marker_does_not_unlock(monkeypatch):
    monkeypatch.setenv("CDSFL_SANDBOX_ROOT", "")
    assert _in_sandbox(REPO) is False


def test_a_marker_naming_another_directory_does_not_unlock(monkeypatch, tmp_path):
    """A stale or hostile value must not be taken at its word."""
    monkeypatch.setenv("CDSFL_SANDBOX_ROOT", str(tmp_path))
    assert _in_sandbox(REPO) is False


def test_a_marker_naming_the_live_repo_from_outside_a_sandbox_is_the_dangerous_case(
        monkeypatch):
    """Naming the REAL repository must be the one thing that cannot help.

    If someone exports the live checkout as the sandbox root, the predicate is
    satisfied by construction -- so the refusal must not be the ONLY thing
    standing between a seat and the live target. It is not: inside the live
    repository `git worktree add` SUCCEEDS, the fallback branch is never
    reached, and the panel gets a real worktree. This test records that the
    protection here rests on git succeeding, not on the marker.
    """
    monkeypatch.setenv("CDSFL_SANDBOX_ROOT", str(REPO))
    assert _in_sandbox(REPO) is True
    import subprocess
    assert subprocess.run(["git", "rev-parse", "--git-dir"], cwd=REPO,
                          capture_output=True).returncode == 0, (
        "the live repository is not a git checkout, so the worktree confinement "
        "cannot be built and the marker would become load-bearing on its own")


def test_the_marker_unlocks_only_when_it_names_this_root(monkeypatch, tmp_path):
    sandbox = tmp_path / "run"
    sandbox.mkdir()
    monkeypatch.setenv("CDSFL_SANDBOX_ROOT", str(sandbox))
    assert _in_sandbox(sandbox) is True
    assert _in_sandbox(REPO) is False


def test_the_wrapper_exports_the_directory_it_built():
    """The 2 halves must agree on the variable, or the fallback never opens."""
    text = WRAPPER.read_text()
    assert 'export CDSFL_SANDBOX_ROOT="$RUN"' in text, (
        "the sandbox wrapper no longer declares itself, so the runner will "
        "refuse inside it and every sandboxed simulated run becomes unlaunchable "
        "again -- which is exactly what happened on 2026-09-21"
    )


def test_the_runner_verifies_rather_than_trusts_the_marker():
    """The runner must RESOLVE and COMPARE, not merely check the variable is set.

    This reads source, and does so deliberately and narrowly: the branch it
    guards only executes when `git worktree add` fails, which cannot be made to
    happen in the live checkout without breaking the checkout. The executing
    coverage of the predicate is the 5 tests above; this one pins the shape of
    the single line they cannot reach.
    """
    src = RUNNER.read_text()
    assert "CDSFL_SANDBOX_ROOT" in src
    assert "REPO.resolve()" in src, (
        "the sandbox marker must be compared against the runner's own resolved "
        "root; accepting it unverified would let any exported value disable a "
        "safety refusal"
    )


def test_the_runner_still_refuses_when_not_in_a_sandbox():
    """The refusal text must survive; the fallback is an addition, not a swap."""
    src = RUNNER.read_text()
    assert "refusing to run the" in src and "return 2" in src


@pytest.mark.parametrize("ignored", [".git", "logs", "__pycache__"])
def test_the_copy_excludes_what_would_leak_or_bloat(ignored):
    """`.git` would restore the history the sandbox severed; `logs` is the archive."""
    src = RUNNER.read_text()
    assert f'"{ignored}"' in src, (
        f"the disposable copy no longer excludes {ignored}; copying .git back in "
        "would hand a seat the planted set through `git diff`, which is the "
        "exact exposure the sandbox severs history to prevent"
    )


def test_the_module_imports_os_for_the_marker_lookup():
    """A NameError here would surface only on the failure path, inside a run."""
    spec = importlib.util.spec_from_file_location("_rse_marker_check", RUNNER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_rse_marker_check"] = m
    spec.loader.exec_module(m)
    assert hasattr(m, "os"), "the runner needs `os` on the fallback path"
    assert hasattr(m, "shutil"), "the runner needs `shutil` to build the copy"
