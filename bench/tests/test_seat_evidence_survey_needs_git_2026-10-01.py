"""The seat-evidence survey must not answer from an empty result after git fails.

FREE PANEL, 2026-10-01. Re-executing the day-review brief's own declared figure
in the panel sandbox gave `251 of 251 unpreserved` where the brief declares
`46 of 251`. The sandbox copy carries no `.git`, `_tracked` never read
`subprocess.CompletedProcess.returncode`, and an empty tracked set classifies
every row as stranded. `_ignored` has the same shape and fails the other way,
printing a reassuring `ignored by git: 0 of 251` from the same run.

This is the `measured-rate-travels-with-its-script` rule turned on the script
itself: a producer that cannot take its measurement must say so, not emit the
extreme value.

WHY THE `ok` TUPLE IS TESTED SEPARATELY. `git check-ignore` exits **1** when
nothing is ignored, which is a success with an empty answer. A naive
`returncode != 0` check would raise on every clean batch, so the fix is only
correct if exit 1 still passes.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "scripts" / "seat_evidence_is_gitignored_2026-09-30.py"
FALSIFIER = ROOT / "scripts" / "seat_evidence_survey_trusts_git_2026-10-01.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def mod():
    assert TARGET.is_file(), f"missing {TARGET}"
    return _load(TARGET, "seat_evidence_under_test")


@pytest.mark.parametrize("helper", ["_tracked", "_ignored"])
def test_a_git_failure_raises_rather_than_returning_empty(mod, helper, tmp_path):
    """The real helpers, in a real non-repository."""
    probe = tmp_path / "a_file.txt"
    probe.write_text("x", encoding="utf-8")
    mod.ROOT = tmp_path
    rc = subprocess.run(["git", "ls-files", "-z", "--", "a_file.txt"],
                        cwd=tmp_path, capture_output=True, text=True)
    if rc.returncode == 0:
        pytest.skip("git answered in a non-repository; no failure to observe")
    with pytest.raises(RuntimeError) as exc:
        getattr(mod, helper)([probe])
    assert "git" in str(exc.value).lower()


def test_nothing_ignored_is_not_a_failure(mod):
    """`git check-ignore` exit 1 means no matches and must be accepted."""
    done = subprocess.CompletedProcess(args=["git", "check-ignore"],
                                       returncode=1, stdout="", stderr="")
    mod._require_git(done, "check-ignore", ok=(0, 1))   # must not raise


@pytest.mark.parametrize("code", [2, 128])
def test_a_real_git_error_is_still_refused(mod, code):
    done = subprocess.CompletedProcess(args=["git", "check-ignore"],
                                       returncode=code, stdout="",
                                       stderr="fatal: not a git repository")
    with pytest.raises(RuntimeError):
        mod._require_git(done, "check-ignore", ok=(0, 1))


def test_the_falsifier_for_this_finding_exits_clean():
    assert FALSIFIER.is_file(), f"missing {FALSIFIER}"
    assert _load(FALSIFIER, "seat_evidence_git_probe").main() == 0
