#!/usr/bin/env python3
"""The duration ledger's row must parse as JSON, including when a count is 0.

GUARDS the `_cdsfl_on_exit` ledger writer in `hooks/pre-commit`.

WHY, AND IT IS MY OWN DEFECT CAUGHT BY EXECUTION RATHER THAN BY READING. On
2026-11-22 two covariates -- `guards` and `staged` -- were added to the ledger
row so the cost trend could finally be attributed to gate size rather than left
as duration against time. Both were written as:

    _cdsfl_staged=$(git ... | grep -c . || echo 0)

**`grep -c` PRINTS its count AND EXITS 1 WHEN THE COUNT IS ZERO.** So on the
zero-match path the substitution emitted BOTH the printed `0` and the fallback
`0` -- the 2-line value "0\\n0" -- and the row became:

    ..."guards":3,"staged":0
    0,"why":""}

which is not JSON. Every future ledger row would have been unparseable, breaking
the very measurement the covariates were added to enable. **The `guards` line
carried the identical fault and looked correct**, because it happened to have
matches; only the zero case exposed it. A fallback that fires ALONGSIDE a
successful print is not a fallback.

★ THIS GUARD DRIVES THE SHELL, IT DOES NOT READ IT. The block is extracted from
the live hook and executed under `sh` in a throwaway directory, and the emitted
line is handed to `json.loads`. A test asserting that the hook's source contains
`head -1` would pass while the row was still corrupt, because the defect is in
what the pipeline EMITS and not in which words it spells -- `execute-do-not-grep`.

★ THE ZERO CASE IS THE POINT, SO IT IS TESTED FIRST AND NAMED. A suite that only
ever exercised a non-empty gate would have shipped this.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import tempfile

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "hooks" / "pre-commit").is_file():
            return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()
HOOK = REPO / "hooks" / "pre-commit"


def _writer_lines() -> "tuple[str, str, str]":
    """The 2 covariate assignments and the printf, lifted from the LIVE hook."""
    t = HOOK.read_text()
    g = re.search(r"^\s*(_cdsfl_guards=\$\(.*)$", t, re.M)
    s = re.search(r"^\s*(_cdsfl_staged=\$\(.*)$", t, re.M)
    pf = re.search(r"^\s*(printf '\{\"at\".*?)\n\s*>> ", t, re.M | re.S)
    assert g and s and pf, (
        "could not locate the ledger writer in hooks/pre-commit. If the block "
        "moved, this guard must follow it rather than silently pass.")
    return g.group(1).strip(), s.group(1).strip(), pf.group(1).strip()


def _emit(guards_value: str, *, in_git: bool) -> str:
    g, s, pf = _writer_lines()
    d = tempfile.mkdtemp()
    if in_git:
        subprocess.run(["git", "init", "-q", d], capture_output=True)
    script = (f'GUARDS="{guards_value}"\n'
              f'_cdsfl_secs=1234\n_rc=0\ncd {d}\n{g}\n{s}\n{pf}\n')
    r = subprocess.run(["sh", "-c", script], capture_output=True, text=True,
                       timeout=60)
    return r.stdout.strip()


THREE = "bench/tests/a.py\nbench/tests/b.py\nbench/tests/c.py"


class TestTheRowParses:
    def test_a_ZERO_count_still_emits_valid_json(self):
        """★ THE DEFECT. Both counts zero is the path `|| echo 0` corrupted."""
        line = _emit("", in_git=False)
        row = json.loads(line)          # the assertion IS the parse
        assert row["guards"] == 0
        assert row["staged"] == 0

    def test_a_nonzero_guard_count_emits_valid_json(self):
        row = json.loads(_emit(THREE, in_git=False))
        assert row["guards"] == 3, row

    def test_inside_a_real_git_repo_with_nothing_staged(self):
        row = json.loads(_emit(THREE, in_git=True))
        assert row["staged"] == 0, row

    def test_the_covariates_are_numbers_not_strings(self):
        """A quoted count would parse but break every arithmetic reader."""
        row = json.loads(_emit(THREE, in_git=True))
        assert isinstance(row["guards"], int), type(row["guards"])
        assert isinstance(row["staged"], int), type(row["staged"])

    def test_the_row_carries_every_field_a_reader_expects(self):
        row = json.loads(_emit(THREE, in_git=True))
        for k in ("at", "seconds", "exit", "head", "guards", "staged", "why"):
            assert k in row, f"the ledger row lost the {k!r} field: {row}"


class TestTheGuardItselfCanFail:
    def test_a_double_fallback_WOULD_be_caught(self):
        """ANTI-VACUITY, and it reconstructs the original defect exactly.

        If this passes while the real writer is fixed, the test above is only
        meaningful because THIS one shows the check can see the fault.
        """
        d = tempfile.mkdtemp()
        bad = ('GUARDS=""\n_cdsfl_secs=1\n_rc=0\n'
               f'cd {d}\n'
               '_cdsfl_guards=$(printf \'%s\\n\' "$GUARDS" | grep -c \'bench/tests/\' '
               '2>/dev/null || echo 0)\n'
               'printf \'{"guards":%s}\\n\' "${_cdsfl_guards:-0}"\n')
        out = subprocess.run(["sh", "-c", bad], capture_output=True, text=True,
                             timeout=60).stdout.strip()
        assert "\n" in out, (
            f"the reconstructed double-fallback emitted a single line {out!r}; "
            f"if `grep -c` no longer exits 1 on a zero count, this whole guard "
            f"is testing a hazard that no longer exists and should be revisited")
        with pytest.raises(json.JSONDecodeError):
            json.loads(out)
