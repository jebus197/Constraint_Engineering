"""`--help` must be inert however the script is INVOKED, not only when run directly.

WHAT IS BROKEN, 2026-09-17. `scripts/assemble_panel_record_0819.py` destroys the
verbatim panel record it assembles when invoked as
`python3 -m scripts.assemble_panel_record_0819 --help`: 56,368 bytes to 24,699,
exit code 0. Run directly it is correctly inert. Its sibling
`scripts/assemble_panel_record.py` is inert under both.

WHY THE GUARD LEAKS. The repair reads:

    if __name__ == "__main__":
        try:
            from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
        except ImportError:
            ...

Under `-m`, the REPOSITORY ROOT is `sys.path[0]`, not `scripts/`, so the bare
`from _cli_help import ...` raises ImportError, the except arm swallows it, and
the ordinary work runs with `--help` on the command line. The comment beside the
import states the assumption that fails.

THIS IS THE A26 DEFECT CLASS, NOT A NEW ONE. A26 records a `--help` that
destroyed a 55,814-byte record and exited 0, and closed as repaired. The repair
shut one entrance. The seat fable found the second; this test was written after
reproducing it in a clean worktree with a fresh copy of the record per
invocation form, because a first attempt that reused one copy proved nothing.

The test COPIES the record into a temp tree. It never runs the assemblers
against the repository's own file.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RECORD = REPO / "experimental_notes" / "Panel_Enforcement_Prose_FULL_RECORD_2026-08-19.md"
ASSEMBLERS = sorted(REPO.glob("scripts/assemble_panel_record*.py"))


def _staged(tmp_path: Path) -> Path:
    """A tree holding the scripts and a COPY of the record."""
    (tmp_path / "scripts").mkdir()
    for f in (REPO / "scripts").glob("*.py"):
        shutil.copy2(f, tmp_path / "scripts" / f.name)
    (tmp_path / "experimental_notes").mkdir()
    shutil.copy2(RECORD, tmp_path / "experimental_notes" / RECORD.name)
    return tmp_path


def _run(tree: Path, argv: list[str]) -> tuple[int, int]:
    target = tree / "experimental_notes" / RECORD.name
    before = target.stat().st_size
    subprocess.run(argv, cwd=tree, capture_output=True, text=True, timeout=300)
    return before, target.stat().st_size


def test_there_are_assemblers_to_check():
    assert ASSEMBLERS, "no assemble_panel_record*.py found"


@pytest.mark.parametrize("script", ASSEMBLERS, ids=lambda p: p.stem)
def test_help_is_inert_when_run_directly(tmp_path, script):
    tree = _staged(tmp_path)
    before, after = _run(tree, [sys.executable, f"scripts/{script.name}", "--help"])
    assert after == before, (
        f"{script.name} --help changed the record: {before} -> {after} bytes")


@pytest.mark.parametrize("script", ASSEMBLERS, ids=lambda p: p.stem)
def test_help_is_inert_under_dash_m(tmp_path, script):
    """THE LEAKING ENTRANCE. Under -m the repo root is sys.path[0]."""
    tree = _staged(tmp_path)
    before, after = _run(tree, [sys.executable, "-m", f"scripts.{script.stem}", "--help"])
    assert after == before, (
        f"{script.stem} destroyed the record under -m --help: {before} -> {after} "
        f"bytes. The --help guard is inside a try/except ImportError that only "
        f"resolves when scripts/ is sys.path[0], which -m does not provide.")


def test_the_record_this_test_protects_is_still_whole():
    """Anti-footgun: the test must never touch the repository's own record."""
    assert RECORD.stat().st_size > 50000, (
        f"the live record is {RECORD.stat().st_size} bytes; a test copy leaked "
        f"onto the real file")
