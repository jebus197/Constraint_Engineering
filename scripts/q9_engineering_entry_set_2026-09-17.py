#!/usr/bin/env python3
"""Which supplementary entries go to the panel under Question 9. Read-only.

The founder approved Question 9 on 2026-09-17: dispatch the engineering entries
of the supplementary list now, and hold A19 until the new material on the
mathematical model has been reviewed. The set is DERIVED here from 3 committed
records rather than typed into the brief:

  1. the 59 ids in the table under "# SUPPLEMENTARY LIST" in the master task list;
  2. the 7 ids the approved plan holds for the founder by category, read from its
     "DECISION <n>. <id>" lines in Task_List_59_Decision_2026-09-12.md;
  3. the 31 ids panel round 16 reviewed that same morning, read from the "The 31
     entries:" line of its committed brief.

R10 and R11 are then held beside A19, because each bears directly on the
mathematical model: R10 is the reading behind the references selection, and R11
answers ruling 4.3 with `gamma_input`. Whether they should go to the panel after
all is the founder's verdict, item 12(a) of the 2026-09-17 action list.

Prints the figures the brief declares. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TASK_LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
DECISIONS = REPO / "experimental_notes" / "Task_List_59_Decision_2026-09-12.md"
ROUND16 = REPO / "experimental_notes" / "panel_briefs" / "Overclaiming_Entries_Brief_2026-09-17.md"
MODEL_BOUND = ("R10", "R11")
ID = r"[A-Z]\d+[a-z]?"


def supplementary_ids() -> list[str]:
    lines = TASK_LIST.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("# SUPPLEMENTARY LIST"))
    return [m.group(1) for line in lines[start:] if (m := re.match(rf"^\| `({ID})` \|", line))]


def held_ids() -> list[str]:
    return re.findall(rf"^DECISION \d+\. ({ID})[,.]", DECISIONS.read_text(encoding="utf-8"), re.M)


def round16_ids() -> list[str]:
    m = re.search(r"^The \d+ entries: (.+)\.$", ROUND16.read_text(encoding="utf-8"), re.M)
    return [x.strip() for x in m.group(1).split(",")]


def entry_set() -> dict:
    supp, held, r16 = supplementary_ids(), held_ids(), round16_ids()
    after_held = [s for s in supp if s not in held]
    reviewed = [s for s in after_held if s in r16]
    remaining = [s for s in after_held if s not in r16]
    model_bound = [s for s in remaining if s in MODEL_BOUND]
    return {"supplementary": supp, "held": held, "round16": r16, "reviewed_by_round16": reviewed,
            "model_bound": model_bound, "set": [s for s in remaining if s not in MODEL_BOUND]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Derive the Question 9 engineering entry set. Read-only.")
    ap.add_argument("--json", action="store_true", help="print the full derivation as JSON")
    args = ap.parse_args()
    e = entry_set()
    if args.json:
        print(json.dumps(e, indent=2))
        return 0
    print(f"supplementary entries: {len(e['supplementary'])}")
    print(f"held for the founder by category: {len(e['held'])} ({', '.join(e['held'])})")
    print(f"reviewed by panel round 16: {len(e['reviewed_by_round16'])} of its {len(e['round16'])}")
    print(f"held because the claim is about the model: {len(e['model_bound'])} ({', '.join(e['model_bound'])})")
    print(f"entries under review: {len(e['set'])}")
    print(" ".join(e["set"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
