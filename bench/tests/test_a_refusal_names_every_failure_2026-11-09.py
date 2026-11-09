"""A refusal that does not name what failed costs a whole board to diagnose.

THE DEFECT, MEASURED 2026-11-09. `hooks/pre-commit` reported a red board with

    grep -E '^(FAILED|ERROR)|^E  ' | head -20

and that cap dropped the only lines a reader needs. pytest emits `E  `
traceback lines FIRST and its `FAILED` short-summary lines LAST, so on a board
with more than about 2 failures the 20 lines were spent entirely on tracebacks.
A refusal reporting `9 failed, 3924 passed` named **0 of the 9**. The remaining
7 had to be hunted by re-running guards by hand, at 26 minutes a board -- which
is the exact cost the block's own comment was written to prevent. The earlier
fix had replaced `tail -25` with a grep, and then capped a stream it did not
order, so the names were always the first thing lost.

THE REPAIR IS 2 GREPS: every name, unbounded, then bounded detail. The pytest
invocation is NOT touched, because `test_desktop_mirrors_stay_current_2026-09-10`
pins that exact command string and an ordering around it.

WHY THIS FILE EXECUTES THE GREPS RATHER THAN ONLY READING THEM. A shell script
has no importable form, so a source-text assertion is the only structural check
available -- and `execute-do-not-grep` records that a test asserting on source
text proves only that the file describes itself consistently. So the pipeline is
EXTRACTED from the hook and RUN against a captured pytest output sample
carrying 3 failures. If the cap ever returns, the executing test loses a name.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks/pre-commit"

#: A faithful miniature of pytest `-q` output: tracebacks first, summary last.
SAMPLE = "\n".join(
    ["=" * 30, "____ test_one ____"]
    + [f"E       AssertionError: detail line {i}" for i in range(25)]
    + ["=========================== short test summary info ====================",
       "FAILED bench/tests/test_alpha.py::test_one",
       "FAILED bench/tests/test_beta.py::TestX::test_two",
       "ERROR bench/tests/test_gamma.py::test_three",
       "3 failed, 100 passed in 12.34s"]
)


def _names_pipeline(sample: str) -> str:
    """Run the hook's OWN names grep, read out of the hook rather than retyped."""
    src = HOOK.read_text(encoding="utf-8")
    m = re.search(r"_NAMES=\$\(printf '%s\\n' \"\$OUT\" \| (grep -E '[^']+')\)", src)
    assert m, ("the hook no longer builds _NAMES with a grep; this guard cannot "
               "find the pipeline it is meant to execute")
    return subprocess.run(["bash", "-c", f"printf '%s\\n' \"$1\" | {m.group(1)}",
                           "_", sample],
                          capture_output=True, text=True).stdout


def test_every_failure_is_named_by_the_hooks_own_pipeline():
    """EXECUTED. 3 failures in, 3 names out, with 25 traceback lines ahead."""
    out = _names_pipeline(SAMPLE)
    for want in ("test_alpha.py::test_one",
                 "test_beta.py::TestX::test_two",
                 "test_gamma.py::test_three"):
        assert want in out, (
            f"{want} was not reported. The names grep is dropping failures, "
            f"which is how a 9-failure board named 0 of them.\ngot:\n{out}")
    assert out.count("\n") >= 3, out


def test_the_names_grep_is_not_capped():
    """The cap is the defect, so its absence is the property.

    A source-text check, and the only structural one available for a shell
    script. It is paired with the executing test above rather than standing
    alone.
    """
    src = HOOK.read_text(encoding="utf-8")
    m = re.search(r"_NAMES=\$\([^)]*\)", src)
    assert m, "the hook no longer builds _NAMES"
    assert "head" not in m.group(0), (
        "the names grep is capped again. pytest puts its FAILED summary LAST, "
        "so any cap on this stream drops names before detail")


def test_the_detail_is_still_bounded():
    """Unbounded tracebacks would bury the names the fix exists to surface."""
    src = HOOK.read_text(encoding="utf-8")
    m = re.search(r"_DETAIL=\$\([^)]*\)", src)
    assert m, "the hook no longer builds _DETAIL separately from _NAMES"
    assert "head" in m.group(0), (
        "the traceback detail is unbounded; on a wide failure it would push "
        "the names off the top of the terminal, which is the same loss by "
        "another route")


def test_the_names_are_printed_before_the_detail():
    """Order on screen, not merely presence."""
    src = HOOK.read_text(encoding="utf-8")
    i_names = src.index('printf \'%s\\n\' "$_NAMES"')
    i_detail = src.index('printf \'%s\\n\' "$_DETAIL"')
    assert i_names < i_detail, (
        "the detail prints before the names, so a long traceback scrolls the "
        "names away")


def test_the_pytest_invocation_is_untouched():
    """The fix must not disturb the command another guard pins.

    `test_desktop_mirrors_stay_current_2026-09-10` asserts this exact string
    and an ordering around it, so adding a flag such as `-ra` there would have
    turned a second guard red to fix this one.
    """
    src = HOOK.read_text(encoding="utf-8")
    assert "python3 -m pytest -q -p no:cacheprovider $GUARDS" in src, (
        "the gate's pytest invocation changed; check "
        "test_desktop_mirrors_stay_current_2026-09-10 before accepting it")


def test_the_fallback_for_a_failure_with_neither_survives():
    """A crash produces no FAILED and no `E  `; the tail must still print.

    ★ THE FIRST VERSION OF THIS CHECK WAS VACUOUS, AND FOR THE REASON THIS
    PROJECT KEEPS RECORDING. It asserted `"tail -25" in src`, and the hook's
    own comment contains the words ``This printed `tail -25` `` -- a SCAR
    describing the defect that was removed. So the detector matched a
    quotation of its own pattern, and deleting the live fallback left it
    green. Comment text is stripped before the check, and the predicate is
    the REDIRECTED form, which a prose mention does not carry.
    """
    src = HOOK.read_text(encoding="utf-8")
    live = "\n".join(l.split("#", 1)[0] for l in src.splitlines())
    assert "tail -25 >&2" in live, (
        "the fallback branch is gone from the LIVE code, so a failure that "
        "emits neither a FAILED line nor assertion text would be reported as "
        "nothing at all")
    assert "tail -25" not in live.replace("tail -25 >&2", ""), (
        "there is more than 1 live `tail -25`; this predicate can no longer "
        "say which one it is testing")
