"""Task A10: a mutation harness must never park a mutant in git state.

THE DEFECT SHAPE. A harness that holds the pristine file in `git stash` and
restores it with a later `pop` depends on that pop running. Nothing enforces it.
An exception, a timeout, a killed process or a second harness stashing on top
leaves the mutant in the working tree and the original in a stash entry nobody
will look for -- and the next `git status` reads as though the mutation were
intended work.

THE SAFE PATTERN, WHICH IS ALREADY THE ONE IN USE. The harness written on
2026-09-09 holds the original in memory, writes the mutant, and writes the
original back in a `finally` block, touching no git state at all. A `finally`
runs on the exception path; a `pop` on a later line does not.

MEASURED BEFORE WRITING THIS: no file in `scripts/` or `bench/tests/` calls
`git stash` at all. The single textual match, `scripts/cdsfl_sv.py:2247`, is a
COMMENT about agents editing the tracker, not a call. So this guard has no
instance to fix; it exists to stop the pattern returning, which is the ratchet
idiom this project already uses for unreached config fields.

WHY IT IS NOT A GREP FOR "stash". A guard that matched the word would fire on
that comment, on this docstring, and on any note quoted in a test. It matches a
CALL: a subprocess argument list or a shell string whose git subcommand mutates
repository state, inside a file that also writes to a source path.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

#: THE ONE SUBCOMMAND THIS ENTRY IS ABOUT, and the narrowness is deliberate.
#:
#: A first version also matched checkout, reset, revert and restore. It fired on
#: `scripts/cdsfl_sv.py:895` and 5 sites in
#: `bench/tests/test_sv_sync_verification_2026-08-26.py` -- all legitimate sync
#: and branch tooling, none of them a mutation harness. A guard that fires on the
#: ordinary case teaches people to ignore it, which is this project's own
#: recorded reason for keeping the commit hook cheap.
#:
#: `stash` is the shape the entry names: it PARKS the pristine file somewhere a
#: later step must retrieve it from. checkout and reset do not defer a
#: restoration to a `pop` that may never run.
DANGEROUS = ("stash",)

#: A file is a MUTATION harness if it writes to a path it did not create.
MUTATES = ("write_text", "write_bytes")

SEARCH = [ROOT / "scripts", ROOT / "bench" / "tests"]


def _python_files():
    for d in SEARCH:
        for p in sorted(d.glob("*.py")):
            yield p


def _git_calls(tree: ast.AST) -> list:
    """Every call whose arguments name `git` and a state-changing subcommand."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        words = []
        for a in list(node.args) + [k.value for k in node.keywords]:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                words += a.value.split()
            elif isinstance(a, (ast.List, ast.Tuple)):
                words += [e.value for e in a.elts
                          if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if "git" in words and any(d in words for d in DANGEROUS):
            out.append((node.lineno, [w for w in words if w in DANGEROUS]))
    return out


class TestNoHarnessParksAMutantInGit:
    def test_no_file_both_mutates_a_source_and_changes_git_state(self):
        offenders = []
        for p in _python_files():
            src = p.read_text(encoding="utf-8", errors="replace")
            if not any(m in src for m in MUTATES):
                continue
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            calls = _git_calls(tree)
            if calls:
                offenders.append((p.relative_to(ROOT), calls))
        assert not offenders, "\n".join(
            f"{p} writes source AND calls git {c} at line {l}"
            for p, calls in offenders for l, c in calls)

    def test_legitimate_git_tooling_is_not_swept_up(self):
        """The narrowing, asserted so it is not widened back by accident.

        cdsfl_sv.py and the sv sync tests call `git checkout` legitimately. A
        broader guard flagged 6 such sites and would have been ignored within a
        day.
        """
        for rel in ("scripts/cdsfl_sv.py",
                    "bench/tests/test_sv_sync_verification_2026-08-26.py"):
            p = ROOT / rel
            if not p.is_file():
                continue
            src = p.read_text(encoding="utf-8", errors="replace")
            assert "checkout" in src, (
                f"{rel} no longer calls checkout; the false-positive this "
                f"narrowing avoids may be gone")
            assert not _git_calls(ast.parse(src)), (
                f"{rel} is flagged by the narrowed guard, which should only "
                f"match `git stash`")

    def test_the_guard_is_not_a_grep_for_the_word(self):
        """`cdsfl_sv.py` mentions stash in a COMMENT and must not fire."""
        p = ROOT / "scripts" / "cdsfl_sv.py"
        if not p.is_file():
            pytest.skip("cdsfl_sv.py is not in this clone")
        src = p.read_text(encoding="utf-8")
        assert "stash" in src, (
            "the comment that made this test necessary is gone; if no file "
            "mentions stash at all, the false-positive risk is gone with it")
        assert not _git_calls(ast.parse(src)), (
            "cdsfl_sv.py now makes a state-changing git call; check whether it "
            "is a mutation harness before allowing it")


class TestTheGuardCanActuallyFail:
    """Without this it passes on any codebase, including an empty one."""

    def test_a_synthetic_stashing_harness_is_caught(self, tmp_path):
        bad = tmp_path / "bad_harness.py"
        bad.write_text(
            "import subprocess, pathlib\n"
            "def mutate(p):\n"
            "    subprocess.run(['git', 'stash', 'push'])\n"
            "    pathlib.Path(p).write_text('mutant')\n",
            encoding="utf-8")
        tree = ast.parse(bad.read_text(encoding="utf-8"))
        calls = _git_calls(tree)
        assert calls, "a harness that stashes and writes was not detected"
        assert calls[0][1] == ["stash"]

    def test_a_safe_harness_is_not_caught(self, tmp_path):
        good = tmp_path / "good_harness.py"
        good.write_text(
            "import pathlib\n"
            "def mutate(p):\n"
            "    orig = pathlib.Path(p).read_text()\n"
            "    try:\n"
            "        pathlib.Path(p).write_text('mutant')\n"
            "    finally:\n"
            "        pathlib.Path(p).write_text(orig)\n",
            encoding="utf-8")
        assert not _git_calls(ast.parse(good.read_text(encoding="utf-8"))), (
            "the in-memory-and-finally pattern was flagged; it is the safe one")

    def test_a_read_only_git_call_is_not_caught(self, tmp_path):
        """`git log` and `git show` change nothing and must stay allowed."""
        ok = tmp_path / "reader.py"
        ok.write_text(
            "import subprocess\n"
            "def versions():\n"
            "    return subprocess.run(['git', 'log', '--all', '--format=%h'])\n",
            encoding="utf-8")
        assert not _git_calls(ast.parse(ok.read_text(encoding="utf-8")))
