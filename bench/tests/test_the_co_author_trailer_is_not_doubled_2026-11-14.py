"""`sv` must not append a co-author trailer the message already ends with.

★ THE LIVE INSTANCE THAT FOUND IT. The harness's attribution rule tells the
author to END a commit message with `Co-Authored-By: ...`. `scripts/cdsfl_sv.py`
then appended its own unconditionally, so following the rule and committing
through `sv` produced the trailer TWICE. Commit `4a802768` of 2026-11-14 carries
2 identical trailers. This was measured on the commit, not supposed.

★ WHY THE TEST IS SCOPED TO THE TRAILER BLOCK AND NOT THE WHOLE MESSAGE, which
is the half a careless repair gets wrong. A substring test -- `trailer in
message` -- fails in the direction that SUPPRESSES a real trailer: a commit
message whose BODY quotes `Co-Authored-By:`, for example one describing this
very defect, would match and the commit would carry no attribution at all.
Losing an attribution is a provenance failure; duplicating one is cosmetic. So
the dedupe looks only at the message's LAST paragraph, and only when every
non-empty line in it is trailer-shaped.

★ 2 OF THE 7 EXPECTATIONS WERE WRITTEN WRONG FIRST AND ARE CORRECTED HERE
RATHER THAN QUIETLY FIXED, because this project has a standing rule that an
anchor is derived from the subject and an expectation never is. The first draft
asserted 1 occurrence for `body_mention_does_not_suppress`, which contradicts
the stated design -- 1 quoted plus 1 appended is 2 -- and 2 occurrences for
`a_different_trailer_block_does_not_suppress`, whose input contains the
co-author trailer 0 times. The function was right both times.

EXECUTES the function. It does not read its source text.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import cdsfl_sv as sv  # noqa: E402

T = "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
OTHER = "Co-Authored-By: Claude Code <noreply@anthropic.com>"


def _n(msg: str, trailer: str = T) -> int:
    return sv._append_co_author(msg, trailer).count(trailer)


def test_a_message_with_no_trailer_gains_exactly_one():
    out = sv._append_co_author("fix a thing\n\nsome body prose.", T)
    assert out.count(T) == 1
    assert out.rstrip().endswith(T)


def test_a_message_already_ending_in_the_trailer_gains_none():
    assert _n(f"fix a thing\n\nbody.\n\n{T}") == 1


def test_trailing_whitespace_does_not_defeat_the_dedupe():
    assert _n(f"fix\n\nbody.\n\n{T}\n\n\n") == 1


def test_a_trailer_among_other_trailers_in_the_block_is_seen():
    assert _n(f"fix\n\nSee: nothing\n{T}") == 1


def test_body_mention_does_not_suppress_the_real_trailer():
    """The substring-test failure mode, asserted in the direction that matters.

    1 quoted occurrence plus 1 appended is 2, and the message MUST still end
    with the trailer. A repair that made this 1 would have dropped the
    attribution from every commit whose prose mentions it.
    """
    msg = f"fix\n\nThe defect: sv appended `{T}` twice.\n\nmore prose."
    out = sv._append_co_author(msg, T)
    assert out.count(T) == 2
    assert out.rstrip().endswith(T)


def test_a_prose_last_paragraph_mentioning_the_trailer_does_not_suppress_it():
    """A paragraph that MENTIONS a trailer is not a trailer BLOCK."""
    msg = f"fix\n\n{T} was appended twice and that is the defect."
    out = sv._append_co_author(msg, T)
    assert out.count(T) == 2
    assert out.rstrip().endswith(T)


def test_a_quoted_trailer_LINE_inside_a_prose_paragraph_does_not_suppress():
    """★ ADDED BECAUSE THE MUTATION HARNESS CAUGHT ITS ABSENCE, not because it
    was foreseen. Loosening `_TRAILER_LINE` to match any line left the guard
    GREEN on the first pass, which means nothing was testing what that pattern
    is for.

    It is for THIS: a last paragraph that is prose but happens to carry the
    trailer on a line of its own. Without the trailer-shape requirement, that
    paragraph reads as a trailer block, the dedupe fires, and the commit loses
    its attribution entirely -- the provenance failure, not the cosmetic one.
    """
    msg = ("fix\n\nThis is prose about the defect:\n"
           + T + "\nand that line is quoted inside a prose paragraph.")
    out = sv._append_co_author(msg, T)
    assert out.count(T) == 2, (
        "the quoted line was mistaken for a trailer block and the real "
        "attribution was suppressed")
    assert out.rstrip().endswith(T)


def test_a_different_trailer_block_does_not_suppress():
    """Input carries the co-author trailer 0 times, so the result carries 1."""
    out = sv._append_co_author("fix\n\nbody.\n\nSigned-off-by: someone <a@b>", T)
    assert out.count(T) == 1
    assert out.rstrip().endswith(T)


def test_a_different_co_author_value_is_not_treated_as_the_same_trailer():
    """`Claude Code` and `Claude Opus 5` are different attributions."""
    out = sv._append_co_author(f"fix\n\nbody.\n\n{OTHER}", T)
    assert out.count(T) == 1
    assert OTHER in out


def test_an_empty_trailer_appends_nothing():
    assert sv._append_co_author("fix\n\nbody.", "") == "fix\n\nbody."


def test_the_live_regression_commit_reduces_to_one():
    """The real message of `4a802768`, which carries the duplicate.

    SKIPS rather than fails where the commit is not reachable, because a
    shallow clone or a fresh worktree is not a defect in the repair.
    """
    r = subprocess.run(["git", "log", "-1", "--format=%B", "4a802768"],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0 or T not in r.stdout:
        pytest.skip("commit 4a802768 is not reachable from this checkout")
    real = r.stdout.rstrip()
    assert real.count(T) == 2, "the regression fixture no longer carries the defect"
    once = real.rsplit("\n\n" + T, 1)[0]
    assert sv._append_co_author(once, T).count(T) == 1


def test_the_function_is_the_one_the_commit_path_uses():
    """NON-VACUITY: the call site must route through it, or this file guards nothing.

    ★ CONVERTED FROM A SOURCE-TEXT ASSERTION TO AN AST CALL-SITE CHECK,
    2026-11-14, on the census's own advice. It read
    `"_append_co_author(message, trailer)" in src`, which is the class
    `scripts/source_text_assertions_2026-09-11.py` exists to retire: 4 guards of
    that class broke on CORRECT changes in a single day, and a reformatting that
    split the call across 2 lines would have turned this red while the code was
    right. The AST form asserts the STRUCTURE -- that a call to this function
    appears inside the commit path -- and survives any reformatting that keeps
    the call.
    """
    import ast
    assert callable(getattr(sv, "_append_co_author", None))
    tree = ast.parse((REPO / "scripts" / "cdsfl_sv.py").read_text(encoding="utf-8"))

    #: ★ THE COMMIT PATH IS FOUND BY WHAT IT DOES, NOT BY ITS NAME. A first
    #: version of this looked inside a function called `main` and went red: the
    #: call lives in `_commit_and_push`. That was the probe being wrong rather
    #: than the code, so the function is now located by the `git commit` it
    #: runs, and a rename cannot break it.
    def _calls(fn):
        out = set()
        for c in ast.walk(fn):
            if not isinstance(c, ast.Call):
                continue
            out.add(c.func.id if isinstance(c.func, ast.Name)
                    else getattr(c.func, "attr", ""))
            for a in c.args:
                if isinstance(a, ast.Constant) and a.value == "commit":
                    out.add("<<runs git commit>>")
        return out

    committers = [n for n in ast.walk(tree)
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and "<<runs git commit>>" in _calls(n)]
    assert committers, (
        "no function in cdsfl_sv.py runs a `git commit`, so the commit path "
        "cannot be located and this guard would pass vacuously")
    for fn in committers:
        assert "_append_co_author" in _calls(fn), (
            f"`{fn.name}` at line {fn.lineno} builds a commit without calling "
            f"`_append_co_author`, so every test above is exercising a helper "
            f"that commit path does not use")
