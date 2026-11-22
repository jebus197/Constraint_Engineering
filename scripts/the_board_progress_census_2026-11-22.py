#!/usr/bin/env python3
"""Read a commit board's progress stream, with the instrument VALIDATED first.

WRITTEN 2026-11-22, after my own census of the same stream was wrong in BOTH
directions on the batch-2 board.

★ WHAT WENT WRONG, BECAUSE THE FIX IS ONLY LEGIBLE AGAINST IT. At 77 per cent of
a live board I reported `5 F / 4 E / 1 X` and called the board certain to refuse.
The summary read **6 failed, 0 errors, 0 xpassed**. So the census MISSED a
failure, INVENTED 4 errors, and INVENTED an unexpected pass -- and a paragraph of
reasoning was built on that phantom X.

★ THE CAUSE: it ran `tr -d '\\n' | grep -oE '[.sFExX]'` over the WHOLE log. A
board log OPENS with the hook's own prose -- `MEMORY_EXCLUSIONS`, `HEAD`,
`repaired 0 citation(s)` -- and every capital E and F in that prose was counted
as a pytest progress marker. **A character census over a file that is not only
characters measures the prose too.**

★ THE FIX IS NOT A BETTER REGEX, IT IS A POPULATION. Count only lines that are
ENTIRELY marker characters, after stripping the trailing `[ NN%]` gauge. Prose
lines contain spaces and punctuation and so never match.

★ AND IT IS VALIDATED AGAINST A KNOWN ANSWER, which is the whole point. Run with
`--validate <log>` on a COMPLETED board, it compares its own census against that
board's own summary line and REFUSES if they disagree. On the 2026-11-22 board
that first exposed the defect it returns F=6, E=0, s=22, passes=5476, matching
`6 failed, 5476 passed, 22 skipped` on every figure.

**AN INSTRUMENT WITH A KNOWN-ANSWER CASE AVAILABLE HAS NO EXCUSE FOR BEING
UNVALIDATED.** Validation here costs 1 command, and I ran the broken version
twice before trying it.

WHY IT IS WORTH HAVING AT ALL: `pytest -q` names failures only in its final
summary, so during a 47-minute board the characters are the ONLY failure signal.
Read correctly they give about 20 minutes of warning; read incorrectly they give
confident nonsense.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import Counter

#: A progress line is ONLY marker characters, optionally closing with the gauge.
#: `u` is included because pytest marks an unexpectedly-passing xfail `X` and a
#: skipped-at-setup case can surface as `u` in some plugin configurations; an
#: unknown marker is better counted than silently dropped.
PROGRESS = re.compile(r"^[.sFExXu]+(\s*\[\s*\d+%\])?$")
GAUGE = re.compile(r"\s*\[\s*\d+%\]$")
SUMMARY = re.compile(
    r"(?:(\d+) failed)?[, ]*(?:(\d+) passed)?[, ]*(?:(\d+) skipped)?", re.I)


def census(path: pathlib.Path) -> "dict[str, int]":
    """Marker counts, read ONLY from lines that are entirely markers."""
    marks = []
    for line in path.read_text(errors="ignore").splitlines():
        if PROGRESS.match(line):
            marks.append(GAUGE.sub("", line))
    c = Counter("".join(marks))
    return {"markers": sum(c.values()), "passed": c.get(".", 0),
            "failed": c.get("F", 0), "errors": c.get("E", 0),
            "skipped": c.get("s", 0), "xfailed": c.get("x", 0),
            "xpassed": c.get("X", 0)}


def declared(path: pathlib.Path) -> "dict[str, int] | None":
    """What the board's OWN summary line says, or None if it has not finished."""
    for line in reversed(path.read_text(errors="ignore").splitlines()):
        if " passed" in line and " in " in line:
            f = re.search(r"(\d+) failed", line)
            p = re.search(r"(\d+) passed", line)
            s = re.search(r"(\d+) skipped", line)
            return {"failed": int(f.group(1)) if f else 0,
                    "passed": int(p.group(1)) if p else 0,
                    "skipped": int(s.group(1)) if s else 0}
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", help="a commit board log")
    ap.add_argument("--validate", action="store_true",
                    help="compare the census against the board's own summary "
                         "and REFUSE if they disagree")
    a = ap.parse_args()
    p = pathlib.Path(a.log)
    if not p.is_file():
        raise SystemExit(f"no log at {p}")

    c = census(p)
    print(f"census of {p.name}")
    for k in ("markers", "passed", "failed", "errors", "skipped",
              "xfailed", "xpassed"):
        print(f"  {k:9s}: {c[k]}")

    d = declared(p)
    if d is None:
        print("\n  the board has NOT finished: no summary line yet.")
        print("  The census above is the only failure signal available, and it")
        print("  is UNVALIDATED against this run -- validate on a completed log.")
        return 0 if c["failed"] == 0 and c["errors"] == 0 else 1

    print(f"\n  the board's own summary: failed={d['failed']} "
          f"passed={d['passed']} skipped={d['skipped']}")
    agree = (c["failed"] == d["failed"] and c["passed"] == d["passed"]
             and c["skipped"] == d["skipped"])
    print(f"  census AGREES with the summary: {agree}")

    if a.validate and not agree:
        raise SystemExit(
            "VALIDATION FAILED: the census and the board's own summary "
            "disagree, so this instrument may not be trusted on a live board. "
            "Fix the population before reading any in-flight figure from it -- "
            "that is exactly how 5 F / 4 E / 1 X was reported for a board whose "
            "truth was 6 failed, 0 errors, 0 xpassed.")
    return 0 if d["failed"] == 0 else 1


if __name__ == "__main__":
    # ★ NO `answer_help` CALL, AND I GOT THIS WRONG TWICE ON THE SAME DAY.
    # That helper is for a script with NO parser: its `takes_no_arguments`
    # defaults to True, so placing it here refuses this script's own `log` and
    # `--validate` before argparse ever sees them. Measured by running it:
    # "unrecognised argument(s): --validate ...". The identical note already sat
    # in `scripts/score_the_dry_run_arm_2026-11-22.py`, written hours earlier
    # the same day -- so this is a documented lesson I failed to apply, not a
    # new discovery. argparse supplies `--help` by itself.
    sys.exit(main())
