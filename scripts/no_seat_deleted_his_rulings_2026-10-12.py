#!/usr/bin/env python3
"""A WITHDRAWN CLAIM: no seat deleted the founder's rulings. The diff direction did.

THE CLAIM, AND IT WAS MINE. Commit b912268d states that cc2's record patch
"would have deleted two of his rulings" -- the R1 block carrying his Exp 53
ruling and a reversion of task 10.2 from WITHDRAWN back to BLOCKED -- and adds
that "neither is mentioned anywhere in its reply". The claim was made after
reading the removals in cc2's harvested diff and finding no account of them in
cc2's return. It was presented as the clearest demonstration in the record of
why fixes are suggested to the human in the loop and never auto-applied.

WHAT REFUTED IT. fable's harvested diff carries the SAME two removals, verbatim.
Two seats sandboxed separately and blind to each other cannot coincidentally
delete the same two blocks of the same file. That is not a coincidence, it is a
common cause, and the common cause is the DIFF DIRECTION:

    ---  the LIVE repository file          modified 2026-10-12 19:16:09
    +++  the seat's SANDBOX copy           modified 2026-10-12 19:30:42
    sandbox created (cc2)                           2026-10-12 19:15:13
    sandbox created (fable)                         2026-10-12 19:15:33

Both clones were taken BEFORE 19:16:09, so neither ever contained the 19:16:09
edit. A line present in the live file and absent from an older clone appears in
a unified diff with a leading minus, which reads identically to a deletion the
seat performed. The two "deleted" blocks are the assistant's OWN additions,
recording the founder's rulings, made 36 seconds after cc2's sandbox was cut.

WHAT IT IMPLIES, AND WHAT IT DOES NOT. The DECISION taken was still correct:
only cc2's additive A19 hunk (+14, -0) was applied, and copying the seat's whole
file would genuinely have reverted the founder's two rulings out of the live
tree. But the REASON recorded for that decision was wrong, and the difference
matters, because one version accuses a seat of destroying the founder's words
and the other describes a stale clone base. The scope of the failure is the
attribution, not the handling.

AND THE FAILURE CLASS IS ONE THIS PROJECT HAS RECORDED BEFORE: a predicate
checked against the wrong baseline. The instrument was a diff whose reference
side was newer than the thing being measured, and the symptom was a confident
reading of an artefact as an action.

Usage: python3 scripts/no_seat_deleted_his_rulings_2026-10-12.py
"""
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
ROUND = REPO / "bench" / "logs" / "clear_the_outstanding_2026-10-12"
HARVEST = ROUND / "sandbox_harvest"
TARGET = "CDSFL_MASTER_TASK_LIST.md"
BLOCKS = ("RULED 2026-10-12, AND THE RULING CARRIES A CAVEAT",
          "task: 10.2 | state: WITHDRAWN")


def seat_diff(seat: str) -> str:
    p = HARVEST / seat / "attempt-1" / "changes.diff"
    return p.read_text(errors="replace") if p.is_file() else ""


def removals(seat: str) -> list[str]:
    """Lines the diff marks as removed from the TARGET file, for this seat."""
    out, grab = [], False
    lines = seat_diff(seat).splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("--- "):
            grab = TARGET in (lines[i + 1] if i + 1 < len(lines) else "")
            continue
        if grab and ln.startswith("-") and not ln.startswith("---"):
            out.append(ln[1:])
    return out


def stamps(seat: str) -> dict:
    d = seat_diff(seat)
    sb = re.search(r"\+\+\+ .*deny_canonical_writes\.sb\t(\S+ \S+)", d)
    live = re.search(r"--- .*" + re.escape(TARGET) + r"\t(\S+ \S+)", d)
    sand = re.search(r"\+\+\+ .*" + re.escape(TARGET) + r"\t(\S+ \S+)", d)
    return {"sandbox_created": sb.group(1) if sb else None,
            "live_file_mtime": live.group(1) if live else None,
            "sandbox_file_mtime": sand.group(1) if sand else None}


def main() -> int:
    answer_help(__doc__, __file__)
    seats = ["cc2", "fable"]
    rem = {s: removals(s) for s in seats}
    print("Blocks the diffs mark as REMOVED from " + TARGET + ":")
    for s in seats:
        hits = [b for b in BLOCKS if any(b in ln for ln in rem[s])]
        print(f"  {s:<6} {len(rem[s])} removed line(s); "
              f"{len(hits)} of {len(BLOCKS)} ruling blocks among them")
    both = all(any(b in ln for ln in rem[s]) for s in seats for b in BLOCKS)
    print(f"\nBOTH blind seats show BOTH removals: {both}")
    if not both:
        print("  -> the common-cause argument does not hold; re-examine.")
        return 3

    print("\nTimestamps, from the diffs' own headers:")
    for s in seats:
        st = stamps(s)
        print(f"  {s:<6} sandbox created {st['sandbox_created']}   "
              f"live file {st['live_file_mtime']}   "
              f"sandbox file {st['sandbox_file_mtime']}")

    created = [stamps(s)["sandbox_created"] for s in seats]
    live = stamps("cc2")["live_file_mtime"]
    before = all(c is not None and live is not None and c < live for c in created)
    print(f"\nEvery sandbox was created BEFORE the live file was modified: {before}")
    if before:
        print("  -> the removed lines are the LIVE file's own later additions,")
        print("     absent from an older clone. No seat deleted anything.")
        print("\nVERDICT: the claim in commit b912268d is WITHDRAWN.")
        return 0
    print("  -> clones postdate the edit; the removals need another explanation.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
