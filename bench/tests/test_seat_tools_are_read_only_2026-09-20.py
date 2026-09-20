#!/usr/bin/env python3
"""A review seat may not modify the repository it is reviewing.

MEASURED 2026-09-20, AND THE HOLE WAS 3 HOURS OLD WHEN IT WAS FOUND. The panel's
paid seats were given `run_python` so they could execute the package under
review -- without it they had no tool that reads a file or runs a script, and a
whole round was wasted on that. The tool ran `python3 -c <code>` with `cwd=REPO`
and no confinement: a probe wrote a file into the repository root and it
succeeded.

WHY THE EXISTING CONFINEMENT DID NOT COVER IT. `panel_sandbox` confines the CLI
seats POSITIONALLY, by working directory, and an HTTP seat has no working
directory to confine. So the paid seats' confinement rested entirely on their
having no filesystem tool at all. Giving them one removed the only thing that
was stopping them, and the tool's own description -- "Run a short read-only
Python snippet ... Do not write files" -- is an instruction, not a guard. This
project has twice recorded panel agents editing the repository mid-run.

IT FAILS CLOSED, which is the half that matters. Where `sandbox-exec` is
unavailable the call is refused rather than run unconfined.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))

from openrouter_tools import dispatch_tool_call  # noqa: E402

needs_sandbox = pytest.mark.skipif(
    not shutil.which("sandbox-exec"),
    reason="sandbox-exec absent; the tool refuses rather than running unconfined")


@needs_sandbox
def test_a_seat_cannot_write_into_the_repository():
    target = ROOT / "_seat_write_guard_probe.txt"
    if target.exists():
        target.unlink()
    dispatch_tool_call("run_python", json.dumps(
        {"code": 'open("_seat_write_guard_probe.txt", "w").write("x")'}))
    existed = target.exists()
    if existed:
        target.unlink()
    assert not existed, (
        "a review seat wrote into the repository it is reviewing; the "
        "confinement is not in force")


@needs_sandbox
def test_a_seat_cannot_write_by_ABSOLUTE_path_either():
    target = ROOT / "_seat_abs_guard_probe.txt"
    if target.exists():
        target.unlink()
    dispatch_tool_call("run_python", json.dumps(
        {"code": f'open({str(target)!r}, "w").write("x")'}))
    existed = target.exists()
    if existed:
        target.unlink()
    assert not existed, "an absolute path bypassed the confinement"


@needs_sandbox
def test_the_guard_is_NOT_vacuous_reading_still_works():
    """A confinement that blocked reading would make the seats useless again,
    which is the defect this was built on top of rather than a fix for it."""
    out = dispatch_tool_call("run_python", json.dumps(
        {"code": 'import runpy; runpy.run_path('
                 '"docs/maths_revision_review_2026-09-10/VERIFY_PACKAGE.py")'}))
    assert "PASS: 41 files match the package manifest" in out, out[:200]


@needs_sandbox
def test_symbolic_work_still_runs():
    out = dispatch_tool_call("run_python", json.dumps(
        {"code": 'import sympy as sp; R,p=sp.symbols("R p"); '
                 'print(sp.simplify(R*(1-p)/(1-p*R)))'}))
    assert "R" in out and "error" not in out.lower(), out[:200]


def test_it_refuses_rather_than_degrading_when_confinement_is_absent(monkeypatch):
    """The half that decides whether this is a guard at all. With sandbox-exec
    unavailable the call must REFUSE, not run unconfined."""
    import build_experiment_tools as bt
    monkeypatch.setattr(bt.shutil, "which", lambda _name: None)
    cmd, note = bt._confined(["python3", "-c", "print(1)"])
    assert cmd is None, "it produced a command with no confinement available"
    assert "REFUSED" in note and "unconfined" in note, note
