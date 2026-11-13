#!/usr/bin/env python3
"""Does a GENERATED report stay current where a NARRATED one goes stale?

ENTRY B167 proposes reducing the narrated morning report's role in favour of
generated surfaces, and states its own condition: `additive-standard`'s removal
clause needs a COMMITTED MEASUREMENT that the replacement dominates on a named
property, the property is CURRENCY, and the entry says in its own words that the
measurement "must be taken before the narration's role is reduced rather than
asserted now". The 7-of-9 figure in that entry exists only as prose. This is the
producer.

★ WHAT IS MEASURED, AND IT IS DELIBERATELY NARROW. Only claims a machine can
re-derive: COUNTS of entries by state and by owner, taken from the report's text
and recomputed from the live task list. Prose judgements are NOT scored, because
scoring them would need a reader and would make the figure unreproducible --
which is the fault being measured.

★ WHY A GENERATED SURFACE SCORES 0 BY CONSTRUCTION, STATED SO IT IS NOT MISTAKEN
FOR A RESULT. A derived document recomputes its counts at render time, so a
freshly rendered one AGREES with the record trivially. The interesting figure is
therefore not today's generated report; it is how fast a FROZEN document decays.
Both are reported, and the generated one is labelled for what it is.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent
if not (REPO / "experimental_notes").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: Claim patterns a machine can re-derive, with the live quantity each names.
CLAIMS = {
    "decisions_need_you": (r"(\d+)\s+decisions?\s+need\s+you", "open entries awaiting him"),
    "outstanding":        (r"(\d+)\s+outstanding",             "open entries needing no decision"),
    "parked":             (r"(\d+)\s+parked",                  "live parked items"),
    "explanations_owed":  (r"(\d+)\s+explanations?\s+owed",    "explanations owed"),
}


def live_counts() -> dict[str, int]:
    """The generator's OWN derived-item count, not a quantity re-derived here.

    ★ THE FIRST VERSION OF THIS FUNCTION INVENTED AN IDENTITY AND WAS WRONG.
    It assumed `decisions + outstanding` equals the number of OPEN task entries,
    got 49 against 36, and reported DISAGREES. The generator draws on 5 sources
    -- the task-list markers, the study file, the parked file, the triage
    producer and the authored-detail file -- so its items are not task entries.
    The true identity, read from the generator rather than guessed, is
    `outstanding = items - decs` plus the no-ruling ones, so
    `decs + outstanding == len(items)`, which its own `--check` prints as
    "N derived item(s)". That is the number to compare against.
    """
    import subprocess
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm
    entries = tlm.parse_entries(LIST)
    r = subprocess.run([sys.executable, "scripts/morning_report_build_2026-10-12.py",
                        "--check"], cwd=REPO, capture_output=True, text=True)
    m = re.search(r"(\d+) derived item", r.stdout)
    out = {"derived_items": int(m.group(1)) if m else -1,
           "open_entries": sum(1 for e in entries if e.state == "OPEN"),
           "done": sum(1 for e in entries if e.state == "DONE"),
           "entries_total": len(entries)}
    return out


def claims_in(path: pathlib.Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    found = {}
    for key, (pat, _desc) in CLAIMS.items():
        m = re.search(pat, text, re.I)
        if m:
            found[key] = int(m.group(1))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("reports", nargs="*", help="report files to check")
    a = ap.parse_args()
    live = live_counts()
    print("  LIVE RECORD, recomputed now from the task-list markers:")
    for k, v in live.items():
        print(f"    {k:16s} {v}")
    print()
    paths = [pathlib.Path(p) for p in a.reports] or sorted(
        (REPO / "experimental_notes").glob("Morning_Report_2026-11-1*.md"))
    rows = []
    for p in paths:
        c = claims_in(p)
        if not c:
            print(f"  {p.name}: no machine-checkable claim found")
            continue
        gen = "_GENERATED" in p.name
        agree = (c.get("decisions_need_you", -1) + c.get("outstanding", -1)
                 == live["derived_items"]) \
            if {"decisions_need_you", "outstanding"} <= set(c) else None
        rows.append((p.name, gen, c, agree))
        print(f"  {p.name}  [{'GENERATED' if gen else 'narrated'}]")
        for k, v in c.items():
            print(f"      claims {k:20s} {v}")
        if agree is not None:
            print(f"      decisions + outstanding = {c['decisions_need_you'] + c['outstanding']}"
                  f"   live derived items = {live['derived_items']}   "
                  f"{'AGREES' if agree else 'DISAGREES'}")
    print()
    narrated = [r for r in rows if not r[1] and r[3] is not None]
    generated = [r for r in rows if r[1] and r[3] is not None]
    print(f"  narrated documents checked : {len(narrated)}, "
          f"agreeing with the live record: {sum(1 for r in narrated if r[3])}")
    print(f"  generated documents checked: {len(generated)}, "
          f"agreeing: {sum(1 for r in generated if r[3])}")
    print()
    print("  ★ A FRESHLY RENDERED GENERATED DOCUMENT AGREES BY CONSTRUCTION, so its")
    print("    score is not evidence of anything. The claim B167 needs is about DECAY:")
    print("    a narrated document frozen at a moment against a record that moves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
