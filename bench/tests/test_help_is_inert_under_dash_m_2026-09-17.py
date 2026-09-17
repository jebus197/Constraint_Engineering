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

WIDENED BY PANEL ROUND 16, 2026-09-17. The first version staged ONLY the
2026-08-19 record and compared its SIZE. With the `-m` fix removed from
`scripts/assemble_panel_record.py` it stayed green, because that script writes
`Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md`, which was never staged; in a stage
that held it, the same mutant under `-m --help` rewrote it from 76,171 bytes to
1,326 and exited 0. `generate_topology` and `compose_all_2026-08-23` were not
run at all. Every script repaired for `-m` in d673edd is now run under both forms, in a
stage holding every file those scripts write, and the WHOLE staged tree is
compared by SHA-256 before and after. The run must also exit 0 and print a usage
line, so a script that crashes before its guard does not pass for inert.

The test COPIES everything into a temp tree. It never runs the scripts against
the repository's own files.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RECORD = REPO / "experimental_notes" / "Panel_Enforcement_Prose_FULL_RECORD_2026-08-19.md"
ASSEMBLERS = sorted(REPO.glob("scripts/assemble_panel_record*.py"))
#: Every file the scripts below write when their guard leaks.
STAGED = (
    RECORD,
    REPO / "experimental_notes" / "Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md",
    REPO / "docs" / "CDSFL_Topology.svg",
)
#: The assemblers, plus the 2 other scripts d673edd repaired for `-m`.
SCRIPTS = sorted({p.stem for p in ASSEMBLERS} | {"generate_topology", "compose_all_2026-08-23"})
FORMS = ("direct", "dash_m")


def _staged(tmp_path: Path) -> Path:
    """A tree holding every script and a COPY of every file they write."""
    (tmp_path / "scripts").mkdir()
    for f in (REPO / "scripts").glob("*.py"):
        shutil.copy2(f, tmp_path / "scripts" / f.name)
    for f in STAGED:
        dest = tmp_path / f.relative_to(REPO)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
    return tmp_path


def _digest(tree: Path) -> dict[str, str]:
    return {str(p.relative_to(tree)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(tree.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def test_there_are_assemblers_to_check():
    assert ASSEMBLERS, "no assemble_panel_record*.py found"
    for f in STAGED:
        assert f.is_file(), f"a file this test stages is gone: {f}"


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("stem", SCRIPTS)
def test_help_is_inert(tmp_path, stem, form):
    tree = _staged(tmp_path)
    argv = ([sys.executable, f"scripts/{stem}.py", "--help"] if form == "direct"
            else [sys.executable, "-m", f"scripts.{stem}", "--help"])
    before = _digest(tree)
    try:
        r = subprocess.run(argv, cwd=tree, capture_output=True, text=True, timeout=60,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        pytest.fail(f"{stem} {form} --help ran for 60 s: it is doing its work, "
                    f"not printing usage")
    after = _digest(tree)
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    assert not changed, (
        f"{stem} {form} --help changed the staged tree: {changed} "
        f"(exit {r.returncode}). Under -m the repository root is sys.path[0], so a "
        f"guard whose ImportError arm swallows the failure runs the ordinary work.")
    assert r.returncode == 0, f"{stem} {form} --help exited {r.returncode}:\n{r.stderr[-1500:]}"
    assert "usage" in (r.stdout + r.stderr).lower(), (
        f"{stem} {form} --help printed no usage line:\n{r.stdout[-800:]}{r.stderr[-800:]}")


def test_the_record_this_test_protects_is_still_whole():
    """Anti-footgun: the test must never touch the repository's own record."""
    assert RECORD.stat().st_size > 50000, (
        f"the live record is {RECORD.stat().st_size} bytes; a test copy leaked "
        f"onto the real file")
