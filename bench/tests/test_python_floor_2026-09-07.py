"""Every module must parse on the oldest interpreter that can reach this repo.

FOUND BY CODEX, 2026-09-07, and it was right. Three files used PEP 701 f-string
constructs that parse only on Python 3.12+:

  * scripts/cdsfl_sv.py:2271 -- a MULTI-LINE expression inside a replacement
    field; below 3.12 it reads as "unterminated string literal";
  * scripts/assemble_panel_record.py:63 and
    scripts/assemble_panel_record_0819.py:63 -- a BACKSLASH inside a
    replacement field (`len('\\n'.join(out))`), which pre-3.12 is the hard error
    "f-string expression part cannot include a backslash".

WHY IT MATTERED RATHER THAN BEING A CURIOSITY. 14 test files import cdsfl_sv, so
on any interpreter below 3.12 the suite fails to COLLECT -- not one test fails,
the whole run refuses to start. This machine carries Python 3.11.2 and a system
3.9.6 alongside the 3.13.3 that happens to be first on PATH, and the project
declares no minimum version anywhere: no setup.py, no pyproject.toml, no
setup.cfg. The code had an undeclared floor of 3.12 that three files enforced by
accident.

THE DISAGREEMENT THAT PRODUCED THIS, and it is worth recording because both sides
were right. Codex reported "the full suite cannot collect". Measured here under
3.13.3: 5333 tests collected in 3.38 s, 0 errors. Measured under 3.11.2: 3
SyntaxErrors, and collection cannot start. Neither observation was wrong; they
were made on different interpreters, and nothing in the repository said which one
was intended.

This test executes the check rather than asserting on source text: it compiles
every tracked module with the OLDEST interpreter it can find on this machine.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from bench.repo_paths import is_archived_run_output

REPO = Path(__file__).resolve().parents[2]

#: The floor this project intends. Raise it deliberately, never by accident.
PYTHON_FLOOR = (3, 11)

_CANDIDATES = ["python3.11", "python3.12", "python3.10", "python3.9"]


def _oldest_interpreter() -> tuple[str, tuple[int, int]] | None:
    """The oldest interpreter present that is at or above the declared floor."""
    best = None
    for name in _CANDIDATES:
        path = shutil.which(name)
        if not path:
            continue
        try:
            out = subprocess.run(
                [path, "-c", "import sys;print(sys.version_info[0],sys.version_info[1])"],
                capture_output=True, text=True, timeout=30)
            major, minor = (int(x) for x in out.stdout.split())
        except Exception:
            continue
        ver = (major, minor)
        if ver < PYTHON_FLOOR:
            continue
        if best is None or ver < best[1]:
            best = (path, ver)
    return best


def _sources() -> list[Path]:
    out = []
    for p in sorted(REPO.rglob("*.py")):
        rel = p.relative_to(REPO).as_posix()
        if (rel.startswith(".git/") or is_archived_run_output(rel)
                or "__pycache__" in rel):
            continue
        out.append(p)
    return out


def test_a_floor_interpreter_is_available_to_check_against():
    """If this skips, the check below proves nothing -- say so out loud rather
    than reporting a green that was never run."""
    found = _oldest_interpreter()
    if found is None:
        pytest.skip(
            f"no interpreter at or above {PYTHON_FLOOR} other than the current "
            f"{sys.version_info[:2]}; the floor check cannot execute here")
    assert found[1] >= PYTHON_FLOOR


def test_every_module_parses_on_the_oldest_available_interpreter():
    found = _oldest_interpreter()
    if found is None:
        pytest.skip("no older interpreter available to check against")
    path, ver = found
    srcs = _sources()
    assert srcs, "no sources found; the scan is vacuous"
    prog = (
        "import sys\n"
        "bad=[]\n"
        "for f in sys.argv[1:]:\n"
        "    try: compile(open(f,encoding='utf-8',errors='replace').read(), f, 'exec')\n"
        "    except SyntaxError as e: bad.append(f'{f}:{e.lineno} {e.msg}')\n"
        "print('\\n'.join(bad))\n"
    )
    r = subprocess.run([path, "-c", prog, *[str(s) for s in srcs]],
                       capture_output=True, text=True, timeout=600)
    failures = [ln for ln in r.stdout.splitlines() if ln.strip()]
    assert not failures, (
        f"{len(failures)} of {len(srcs)} modules do not parse on Python "
        f"{ver[0]}.{ver[1]}, so the suite cannot COLLECT there:\n  "
        + "\n  ".join(failures))


def test_the_two_constructs_that_caused_this_are_gone():
    """Named directly, because a regression here is silent on 3.12+ and total
    below it."""
    sv = (REPO / "scripts" / "cdsfl_sv.py").read_text()
    assert "_mirror_action" in sv, "the hoisted variable is gone"
    for name in ("assemble_panel_record.py", "assemble_panel_record_0819.py"):
        src = (REPO / "scripts" / name).read_text()
        assert "_written = " in src, f"{name}: the hoisted join is gone"
        assert "len('\\n'.join(out))" not in src, (
            f"{name}: the backslash is back inside the f-string expression")
