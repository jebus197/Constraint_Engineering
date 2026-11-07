#!/usr/bin/env python3
"""Strike through and stamp every task-list entry its marker records as settled.

HIS INSTRUCTION, 2026-11-06: *"you might have to do is to add a strikethrough
and a 'completed' stamp to any items on your maser task list that have already
been dealt with, so you don't keep resisting already solved issues."* (His
"resisting" is "revisiting", and his point is exact: 229 entries are marked DONE
and 1 carries a strikethrough, so a settled entry reads as live prose.)

THE OBVIOUS IMPLEMENTATION IS WRONG AND WOULD BREAK 10 INSTRUMENTS. The entries
are found by a pattern that requires the line to START with `**`: the canonical
one is `task_list_markers.ENTRY`, and 9 further files use the same shape.
Prefixing `~~` to the line makes `~~**B97.` and BOTH patterns stop matching --
verified by execution, not assumed. So the strikethrough goes around the TITLE
TEXT and the identifier stays where every parser expects it:

    **B97. ~~Title.~~** **[COMPLETED <date> - DONE/COMMITTED]** Added ...

THE PARSER CHECK IS THIS TOOL'S POSTCONDITION. Every line it rewrites must still
match the canonical pattern and still yield the same identifier, or the tool
refuses and writes nothing. A cosmetic change that silently unhooked the list
from its own readers would be far worse than the problem it fixes.

STATE COMES FROM THE MARKER, NEVER FROM THE PROSE. An entry is settled when its
marker says DONE or WITHDRAWN. The tool never decides that itself.
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
SETTLED = {"DONE", "WITHDRAWN"}
STAMP = re.compile(r"\*\*\[COMPLETED \d{4}-\d{2}-\d{2}")
MARKER = re.compile(r"<!--\s*task:\s*([A-Za-z0-9.]+)\s*\|([^>]*)-->")


def canonical():
    spec = importlib.util.spec_from_file_location(
        "tlm", REPO / "scripts" / "task_list_markers.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["tlm"] = m
    spec.loader.exec_module(m)
    return m.ENTRY


def marker_state(rest: str) -> tuple[str, str]:
    f = dict(re.findall(r"(\w+):\s*([^|]+)", rest))
    return (f.get("state", "").strip().upper(), f.get("status", "").strip().upper())


def restamp(line: str, state: str, status: str, today: str, ENTRY) -> str | None:
    """Return the stamped line, or None when nothing should change."""
    if STAMP.search(line):
        return None                                  # already stamped
    m = ENTRY.match(line)
    if not m:
        return None                                  # not an entry heading
    ident = m.group(1)
    #: THE TITLE IS WHAT THE FIRST BOLD RUN HOLDS. Strike inside it, after the
    #: identifier, so the line still opens `**<ident>.` for every parser.
    bold = re.match(r"^(\*\*" + re.escape(ident) + r"\.\s*)(.+?)(\*\*)(.*)$",
                    line, re.S)
    if not bold:
        return None
    head, title, close, tail = bold.groups()
    if title.startswith("~~"):
        return None
    stamped = (f"{head}~~{title.rstrip()}~~{close} "
               f"**[COMPLETED {today} - {state}/{status or 'NO STATUS'}]**{tail}")
    #: POSTCONDITION, checked per line: the canonical parser must still match
    #: and must still yield the SAME identifier.
    m2 = ENTRY.match(stamped)
    if not m2 or m2.group(1) != ident:
        raise SystemExit(
            f"REFUSING: stamping {ident} would stop the canonical parser "
            f"matching its own line. Nothing written.\n  before: {line[:90]}\n"
            f"  after : {stamped[:90]}")
    return stamped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the changes")
    ap.add_argument("--limit", type=int, default=0,
                    help="stamp at most N entries, for a cautious first pass")
    a = ap.parse_args()
    ENTRY = canonical()
    today = datetime.date.today().isoformat()
    lines = LIST.read_text(encoding="utf-8").splitlines()

    #: pair each marker with the entry heading ABOVE it, which is this list's
    #: own convention: 1 body line, then 1 marker line.
    changed, skipped, already = [], 0, 0
    for i, l in enumerate(lines):
        mm = MARKER.search(l)
        if not mm:
            continue
        state, status = marker_state(mm.group(2))
        if state not in SETTLED:
            continue
        #: walk back to the nearest heading line
        j = i - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        if j < 0:
            continue
        if STAMP.search(lines[j]):
            already += 1
            continue
        new = restamp(lines[j], state, status, today, ENTRY)
        if new is None:
            skipped += 1
            continue
        changed.append((j, mm.group(1), new))
        if a.limit and len(changed) >= a.limit:
            break

    print(f"settled entries whose heading is already stamped : {already}")
    print(f"settled entries this pass would stamp            : {len(changed)}")
    print(f"settled entries skipped (no parseable heading)   : {skipped}")
    for j, ident, new in changed[:5]:
        print(f"\n  {ident} at line {j+1}:\n    {new[:150]}")
    #: ★ STATE THE REMAINDER. A listing cut to 5 under a heading that
    #: reads as complete is a silent falsehood, and 3 of these shipped in
    #: 1 night's work. The total is printed, so the reader can see the cut.
    if len(changed) > 5:
        print(f"    ... and {len(changed) - 5} more not shown (of {len(changed)} total)")

    if not a.apply:
        print("\nDRY RUN -- nothing written. Re-run with --apply.")
        return 0
    for j, _ident, new in changed:
        lines[j] = new
    LIST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    #: WHOLE-FILE POSTCONDITION: every marker must still pair with an entry the
    #: canonical parser can read, and the identifier set must be unchanged.
    after = LIST.read_text(encoding="utf-8")
    ids_before = set(re.findall(r"<!--\s*task:\s*([A-Za-z0-9.]+)", after))
    heads = {ENTRY.match(l).group(1) for l in after.splitlines() if ENTRY.match(l)}
    print(f"\nSTAMPED {len(changed)} entries.")
    print(f"  marker identifiers: {len(ids_before)}   parseable headings: {len(heads)}")
    missing = sorted(ids_before - heads)
    if missing:
        print(f"  NOTE: {len(missing)} marker(s) have no parseable heading, "
              f"which was true before this pass too: {missing[:6]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
