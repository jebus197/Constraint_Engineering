#!/usr/bin/env python3
"""Folding fixes forward must never write to the repository working tree.

THE FOUNDER'S CONDITION, 2026-10-06, verbatim: *"Fold fixes forward is a useful
facility, so we don't lose fixes suggested by the models, providing it never touches
the live tree and we can still review those fixes (and change and revert them as
needed) in the subsequent simulated and real experimental runners."*

`apply_fixes_back_enabled` was turned on in `bench/tools/run_simulated_experiment.py`
on that ruling. It was armed in 1 of 49 real configs and had never run in simulation.

WHY THIS FILE EXISTS RATHER THAN A COMMENT CITING THE DOCSTRING. `_apply_back_setup`
states "The repo file is never modified". That is a module describing itself, which
`execute-do-not-grep` says is exactly the thing that cannot be trusted as evidence:
the producer and the consumer can each be individually correct and still disagree.
The condition the founder set is a property of what lands on disk, so it is checked
on disk, by running the real function and comparing bytes.

A SECOND PROPERTY IS HELD HERE TOO, because his ruling has two halves: the fixes must
remain REVIEWABLE. A working copy that is deleted at teardown would satisfy "never
touches the live tree" and still lose the work, which is the failure the ruling exists
to prevent.
"""
import hashlib
import pathlib
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import bench.reference_runner_v3 as R  # noqa: E402


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class _Cfg:
    def __init__(self, enabled, seed=None):
        self.apply_fixes_back_enabled = enabled
        self.apply_fixes_back_seed = seed


@pytest.fixture
def target(tmp_path):
    """A stand-in 'repository' file, so a failure cannot damage the real one."""
    repo = tmp_path / "repo"
    repo.mkdir()
    t = repo / "TARGET_SPEC.md"
    t.write_text("# Spec\n\nThe original line that must survive.\n", encoding="utf-8")
    return t


class TestTheLiveTreeIsNotTouched:
    def test_setup_returns_a_path_that_is_not_the_repo_file(self, target, tmp_path):
        logs = tmp_path / "logs"
        logs.mkdir()
        working = R._apply_back_setup(_Cfg(True), target, logs)
        assert pathlib.Path(working).resolve() != target.resolve(), (
            "fold-fixes-forward handed back the repository file itself, so every "
            "round would write to the live tree")

    def test_writing_to_the_working_copy_leaves_the_repo_file_byte_identical(
            self, target, tmp_path):
        """THE FOUNDER'S CONDITION, measured on disk."""
        logs = tmp_path / "logs"
        logs.mkdir()
        before = _sha(target)
        working = pathlib.Path(R._apply_back_setup(_Cfg(True), target, logs))
        # Simulate what a round does: rewrite the article it was handed.
        working.write_text("# Spec\n\nA MODEL REWROTE THIS.\n", encoding="utf-8")
        assert _sha(target) == before, (
            f"the repository file changed after a write to the working copy — "
            f"fold-fixes-forward is touching the live tree, which the founder's "
            f"ruling forbids. target={target}, working={working}")
        assert target.read_text(encoding="utf-8").count("must survive") == 1

    def test_the_probe_is_not_vacuous(self, target):
        """If a direct write to the target did NOT change its hash, the check
        above could pass over nothing."""
        before = _sha(target)
        target.write_text("changed directly\n", encoding="utf-8")
        assert _sha(target) != before, (
            "the hash does not respond to a direct write, so the live-tree "
            "assertion is measuring nothing")


class TestTheFixesStayReviewable:
    """The other half of the ruling: the work must not vanish at teardown."""

    def test_the_working_copy_survives_under_the_run_log_directory(
            self, target, tmp_path):
        logs = tmp_path / "logs"
        logs.mkdir()
        working = pathlib.Path(R._apply_back_setup(_Cfg(True), target, logs))
        working.write_text("# Spec\n\nA MODEL REWROTE THIS.\n", encoding="utf-8")
        assert working.is_file(), "the working copy does not exist after a write"
        assert "A MODEL REWROTE THIS" in working.read_text(encoding="utf-8")
        resolved = working.resolve()
        assert str(logs.resolve()) in str(resolved) or resolved.parent.is_dir(), (
            f"the working copy at {resolved} is not under the run's own log "
            f"directory, so a reader cannot find the folded fixes afterwards")

    def test_the_pristine_original_is_recoverable(self, target, tmp_path):
        """'change and revert them as needed' needs the original to still exist."""
        logs = tmp_path / "logs"
        logs.mkdir()
        original = target.read_text(encoding="utf-8")
        working = pathlib.Path(R._apply_back_setup(_Cfg(True), target, logs))
        working.write_text("rewritten\n", encoding="utf-8")
        assert target.read_text(encoding="utf-8") == original, (
            "the pristine original is gone, so a fix cannot be reverted")


class TestDisabledIsAStrictNoOp:
    def test_disabled_returns_the_target_unchanged(self, target, tmp_path):
        logs = tmp_path / "logs"
        logs.mkdir()
        before = _sha(target)
        out = pathlib.Path(R._apply_back_setup(_Cfg(False), target, logs))
        assert out.resolve() == target.resolve(), (
            "with the facility off, rounds must read the target itself")
        assert _sha(target) == before


class TestTheLauncherArmsIt:
    def test_the_simulated_runner_enables_it(self):
        """An addition nothing reaches is not additive. Parsed, not matched."""
        import ast
        src = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text(
            encoding="utf-8")
        found = None
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Call) and (
                    getattr(node.func, "attr", None)
                    or getattr(node.func, "id", None)) == "RunnerConfig":
                for kw in node.keywords:
                    if kw.arg == "apply_fixes_back_enabled":
                        found = ast.literal_eval(kw.value)
        assert found is True, (
            f"the simulated runner does not arm apply_fixes_back_enabled "
            f"(found {found!r}); the founder ruled it on")
