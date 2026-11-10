"""The cheap commit checks must run BEFORE the expensive board.

WHY. `hooks/pre-commit` has 9 refusal points. 1 of them, the guard board,
costs a mean of 1230.176471 s over 17 recorded runs (sd 477.192078). The
others together are bounded at 27.66 s, which is 0.022485 of a refused board,
a ratio of 44.4749 agreeing across numpy, sympy and mpmath to 0.0e+00. Until
2026-11-09 the note lint ran AFTER the board, so a commit refused by a
1-second lint first paid for a ~20-minute board. 7 of 17 recorded runs were
refusals, 0.411765, Wilson [0.216111, 0.639946], Clopper-Pearson [0.184437,
0.670753].

THE POSITION IS FORCED, NOT CHOSEN, and all 3 constraints are asserted here:
  1. AFTER stage 0, which writes and stages files inside the lint's own glob;
  2. NOT INSIDE the stage-0 window, which a committed guard requires to hold
     exactly 1 `exit 1` while this block holds 3;
  3. AFTER the python3-availability check, since the block runs python3.

THE BLOCK WAS MOVED, NOT EDITED. The semantic check that makes a move safe is
test_every_name_the_block_reads_is_set_before_it: a hoisted block that reads a
variable the board sets would be a silent breakage no ordering test can see.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "pre-commit"


@pytest.fixture(scope="module")
def src() -> str:
    return HOOK.read_text(encoding="utf-8")


def _at(src: str, needle: str) -> int:
    i = src.find(needle)
    assert i >= 0, f"anchor vanished from the hook: {needle!r}"
    return i


BOARD = "OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS"
LINT = "# ── 5th guard: LINT THE NOTES BEING COMMITTED"


def _lint_block(src: str) -> str:
    """The lint block ONLY. It ends where the board section begins -- slicing
    to the file's final `exit 0` swallowed the board and made 2 tests wrong."""
    start = _at(src, LINT)
    end = _at(src, BOARD)
    assert start < end
    return src[start:end]


def _live(text: str) -> str:
    return "\n".join(l for l in text.splitlines()
                      if not l.lstrip().startswith("#"))


class TestTheOrderIsCheapFirst:
    def test_the_note_lint_runs_before_the_board(self, src):
        lint = _at(src, "# ── 5th guard: LINT THE NOTES BEING COMMITTED")
        board = _at(src, "OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS")
        assert lint < board, (
            "the note lint is back below the board, so a commit refused by a "
            "1-second check pays for a 1230 s board first")

    def test_it_still_runs_after_stage_zero(self, src):
        stage0 = _at(src, "# STAGE 0 --")
        lint = _at(src, "# ── 5th guard: LINT THE NOTES BEING COMMITTED")
        assert stage0 < lint, (
            "the lint moved ABOVE stage 0, which writes and stages files inside "
            "the lint's own glob -- it would lint the unrepaired content")

    def test_it_is_not_inside_the_stage_zero_window(self, src):
        i = _at(src, "# STAGE 0 --")
        window = src[i:src.index('MISSING=""', i)]
        assert "5th guard: LINT THE NOTES" not in window, (
            "the lint landed inside the stage-0 window, which a committed "
            "guard requires to hold exactly 1 refusal")
        assert window.count("exit 1") == 1, (
            f"the stage-0 window now holds {window.count('exit 1')} refusals, "
            f"not 1")

    def test_it_runs_after_python3_is_known_to_exist(self, src):
        probe = _at(src, "command -v python3 >/dev/null 2>&1")
        lint = _at(src, "# ── 5th guard: LINT THE NOTES BEING COMMITTED")
        assert probe < lint, (
            "the lint runs python3 before the hook has checked python3 exists")


class TestTheMoveDidNotBreakIt:
    def test_the_hook_is_still_valid_shell(self):
        r = subprocess.run(["bash", "-n", str(HOOK)],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"bash -n rejects the hook: {r.stderr[-400:]}"

    def test_the_hook_is_executable(self):
        assert HOOK.stat().st_mode & 0o111, "the hook lost its execute bit"

    def test_every_name_the_block_reads_is_set_before_it(self, src):
        """THE SEMANTIC CHECK. An ordering test cannot see a hoisted block that
        reads a variable the board sets; this one can."""
        block = _lint_block(src)
        before = src[:_at(src, LINT)]
        reads = set(re.findall(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)", block))
        assigns = set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)=", block, re.M))
        assigns |= set(re.findall(r"^\s*for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in",
                                  block, re.M))
        # names that occur only inside a comment are not read at runtime
        live = _live(block)
        unmet = []
        for v in sorted(reads - assigns):
            if not re.search(rf"\$\{{?{v}\b", live):
                continue                      # comment-only, e.g. LINT_CODE
            if re.search(rf"^\s*(?:export\s+)?{v}=", before, re.M):
                continue                      # set earlier in the file
            if re.search(rf"^\s*for\s+{v}\s+in", block, re.M):
                continue
            unmet.append(v)
        assert not unmet, (
            f"the hoisted block reads {unmet} which nothing sets before its new "
            f"position -- the move is not safe")

    def test_the_block_kept_its_three_refusals(self, src):
        live = _live(_lint_block(src))
        assert live.count("exit 1") == 3, (
            f"the lint block now has {live.count('exit 1')} refusals, not 3; "
            f"the move must not change what it refuses on")

    def test_the_board_still_refuses(self, src):
        after = _live(src[_at(src, BOARD):])
        assert "exit 1" in after, "the board no longer refuses a red commit"
