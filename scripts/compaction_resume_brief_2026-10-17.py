#!/usr/bin/env python3
"""Task B17: the post-compaction notice carries CONTENT, not a reading list.

HIS QUESTION, 2026-10-16, verbatim: *"If you can detect compaction
mechanically, why can't you also make rs run mechanically too after
compaction?"*

TWO THIRDS WERE ALREADY MECHANICAL and the honest answer names the third that
was not. `~/.claude/hooks/compaction_watch.py` already RUNS
`scripts/cdsfl_recover.py --record-restore` on the first post-compaction turn,
and `~/.claude/hooks/compaction_task_boundary.py` already returns 2 to refuse
the stop so the recovery actually lands. What a hook CANNOT do is make the
assistant open the documents a notice names. On the compaction of 2026-10-16 the
notice supplied a FIRST READ list of 10 paths: running the script was
mechanical, opening the master task list was discretionary -- and a notice
delivers information only if something reads it.

SO THE BRIEF IS INJECTED INSTEAD OF ADVERTISED. The resume pointer and the open
task entries arrive INLINE on the first turn after a compaction, where they
cannot be skipped.

THE SIZE WAS MEASURED BEFORE THE SHAPE WAS CHOSEN, by
`scripts/what_would_injecting_the_resume_state_cost_2026-10-17.py`, against 151
entries of which 21 were open:

    the master task list in full ........................ 654,237 characters
    open entries, headings capped at  90 .................   2,009
    open entries, headings capped at 120 .................   2,639
    open entries with `ruled` state, capped at 110 .......   2,828
    identifiers alone ...................................      97

THIS USES THE 2,828 SHAPE, and the reasoning is stated so it can be overruled:
the differences between 2,009 and 2,828 are immaterial against any context
window, while the `ruled` state is the field that distinguishes work he has
already decided from work he has not -- the exact distinction whose ABSENCE
left the zero-plant control appearing as an open decision for 70 days. The cap
is a flag, so the budget remains his to set without editing anything.

WHY THE LOGIC LIVES IN THE REPOSITORY AND NOT IN THE HOOK. A hook under
`~/.claude/` is unversioned and exists on one machine. Putting the brief here
makes it reviewable, testable and recoverable; the hook becomes a thin shim
that calls it. The project's own rule is that an addition must be wired to a
caller and executed by a test, and a fix that lives only in an unversioned file
is one disk failure from never having existed.

Costs nothing: reads 2 local files and dispatches to nothing.

Usage:
  compaction_resume_brief_2026-10-17.py                # the brief
  compaction_resume_brief_2026-10-17.py --cap 90       # tighter headings
  compaction_resume_brief_2026-10-17.py --budget 4000  # hard character ceiling
"""
from __future__ import annotations

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

DEFAULT_CAP = 110
DEFAULT_BUDGET = 4000
TRACKER = REPO / "experimental_notes" / "CDSFL_Agent_Operational_Plan.md"
LIVE_STATES = ("OPEN", "BLOCKED")


def _heading(entry, cap: int) -> str:
    """The entry's own first sentence, capped, with the markup stripped."""
    text = entry.text.strip()
    if text.startswith("**"):
        text = text[2:]
    for marker in ("**", ".**"):
        if marker in text:
            text = text.split(marker)[0]
            break
    text = " ".join(text.split())
    return text[:cap] + ("..." if len(text) > cap else "")


def resume_pointer() -> str:
    """The tracker's own resume line, if it has one."""
    if not TRACKER.is_file():
        return ""
    for line in TRACKER.read_text(encoding="utf-8",
                                  errors="replace").splitlines():
        low = line.lower()
        if "resume" in low and (":" in line or "**" in line):
            return " ".join(line.replace("*", "").split())[:220]
    return ""


def brief(cap: int = DEFAULT_CAP, budget: int = DEFAULT_BUDGET) -> str:
    import task_list_markers as markers

    entries = markers.parse_entries()
    live = [e for e in entries if e.state in LIVE_STATES]
    done = sum(1 for e in entries if e.state == "DONE")

    lines = [
        "## THE OPEN WORK, INLINE — not a reading list",
        f"  {len(entries)} entries: {len(live)} open, {done} done. "
        f"`ruled` names the date HE decided it; an entry without one is a "
        f"question or a decision still owed.",
    ]
    pointer = resume_pointer()
    if pointer:
        lines.append(f"  RESUME POINTER: {pointer}")
    for e in live:
        ruled = f"ruled {e.ruled}" if e.ruled else "NOT RULED"
        lines.append(f"  {e.ident:<5} {e.status:<10} {ruled:<16} "
                     f"{_heading(e, cap)}")
    lines.append("  The master task list is the canonical copy; this is its "
                 "open subset, injected because a path can be skipped and "
                 "content cannot.")
    out = "\n".join(lines)
    if len(out) > budget:
        #: TRUNCATION IS ANNOUNCED, never silent. A brief that quietly drops
        #: half the open work is worse than no brief, because it reads as
        #: complete. The identifiers alone cost 97 characters, so the fallback
        #: always fits.
        kept, total = [], 0
        head = lines[:3]
        total = sum(len(l) + 1 for l in head)
        for line in lines[3:-1]:
            if total + len(line) + 1 > budget - 200:
                break
            kept.append(line)
            total += len(line) + 1
        dropped = len(live) - len(kept)
        out = "\n".join(head + kept + [
            f"  ... {dropped} further open entries OMITTED to stay inside the "
            f"{budget}-character budget; their identifiers are: "
            f"{', '.join(e.ident for e in live[len(kept):])}",
            "  Read experimental_notes/CDSFL_MASTER_TASK_LIST.md for those."])
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP,
                        help=f"characters per heading (default {DEFAULT_CAP})")
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                        help=f"hard ceiling on the whole brief "
                             f"(default {DEFAULT_BUDGET}); overflow is "
                             f"announced, never dropped silently")
    args = parser.parse_args(argv)
    text = brief(cap=args.cap, budget=args.budget)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
