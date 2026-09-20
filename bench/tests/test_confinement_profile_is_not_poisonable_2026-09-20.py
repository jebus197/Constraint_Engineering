#!/usr/bin/env python3
"""The confinement profile must never be readable from disk by the confined child.

THE DEFECT THIS PREVENTS, measured 2026-09-20 and reproduced end to end.

The first version of `_confined` cached the sandbox profile at
`pathlib.Path(tempfile.gettempdir()) / "cdsfl_tool_readonly.sb"` and passed it as
`sandbox-exec -f <path>`, reusing the file whenever it existed and never checking
its contents. The profile GRANTS the confined child write access to `/tmp`, and
`tempfile.gettempdir()` returns `/tmp` whenever TMPDIR is unset. So:

    call 1  ->  REPO WRITE: DENIED PermissionError
    call 2  ->  the seat overwrites the cached profile with "(allow default)"
    call 3  ->  REPO WRITE: ALLOWED

Two tool calls took a review seat from confined to unconfined. It was not live on
the maintainer's machine, where TMPDIR points outside the allow-list -- which is
exactly why it needed a test. A guard whose integrity depends on an environment
variable is a guard that silently degrades, and that is the defect the module's
own docstring says it exists to prevent.

WHY THIS TEST IS NOT A DUPLICATE of the source-text guard in
test_build_experiment_tools.py. That one asserts no write token appears in the
module. This one asserts a PROPERTY OF THE COMMAND ACTUALLY BUILT: that no
argument names a file the confined child could reach. A future author could
reintroduce the escape without writing `write_text(` -- by pre-creating the
profile elsewhere, or by having a helper module write it -- and the source-text
guard would stay green. This one would not.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.build_experiment_tools import _confined  # noqa: E402

pytestmark = pytest.mark.skipif(
    sys.platform != "darwin", reason="sandbox-exec is a macOS facility")


def _argv():
    cmd, note = _confined(["python3", "-c", "print('ok')"])
    if cmd is None:
        pytest.skip(f"sandbox-exec unavailable here: {note}")
    return cmd


def test_the_profile_is_passed_inline_not_as_a_file():
    """The whole escape needed an on-disk profile. There must not be one."""
    argv = _argv()
    assert "-p" in argv, f"profile is not passed inline: {argv}"
    assert "-f" not in argv, (
        "the profile is passed as a FILE again. A file inside the profile's own "
        "write allow-list can be overwritten by the confined child, which is the "
        "2026-09-20 escape.")


def test_no_argument_names_a_file_the_confined_child_could_reach():
    """Stronger, and the one that survives a clever reintroduction.

    Any argument that is an existing path is a candidate for poisoning. The
    inline form has none: the profile travels as a string.
    """
    argv = _argv()
    for a in argv[1:]:
        if not isinstance(a, str):
            continue
        # The profile string itself starts with "(version" and is not a path.
        if a.startswith("("):
            continue
        assert not os.path.isfile(a), (
            f"argument {a!r} is a file on disk; if it sits inside the profile's "
            f"write allow-list a confined seat can rewrite it between calls")


def test_the_confinement_still_actually_confines(tmp_path):
    """A guard that stopped guarding would also pass the 2 tests above.

    Executes a real write into the repository and requires the kernel to refuse
    it. Nothing is left behind: the probe path is removed if it ever appears.
    """
    probe = ROOT / "_confinement_regression_probe_DELETEME.txt"
    code = (f"try:\n"
            f"    open({str(probe)!r}, 'w').write('x')\n"
            f"    print('ALLOWED')\n"
            f"except Exception as e:\n"
            f"    print('DENIED', type(e).__name__)\n")
    cmd, note = _confined(["python3", "-c", code])
    if cmd is None:
        pytest.skip(note)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=120)
        assert "DENIED" in r.stdout, (
            f"the confinement did not refuse a repository write: "
            f"{r.stdout.strip()!r} {r.stderr.strip()[:200]!r}")
    finally:
        if probe.exists():
            probe.unlink()
            pytest.fail("a probe file reached the repository: confinement is OFF")


def test_reading_and_symbolic_work_still_succeed():
    """The guard must not be vacuous by refusing everything."""
    cmd, note = _confined(
        ["python3", "-c", "import sympy as sp; print(sp.simplify('x + x'))"])
    if cmd is None:
        pytest.skip(note)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    assert "2*x" in r.stdout, f"confined symbolic work failed: {r.stdout!r} {r.stderr[:200]!r}"
