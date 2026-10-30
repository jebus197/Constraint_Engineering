#!/usr/bin/env python3
"""Which questions are owed, to whom, enumerated from the register.

WHY THIS SCRIPT EXISTS. Task entry B51 records that explanations are owed to the
founder and gives a figure for how many. That figure had NO producer: it came
from searching the word "explain" anywhere in a ticket's text. The entry itself
records the predicate over-matching by 1, and a later check found it worse than
that -- it covers 1 of the 11 live questions, missing 10. A number quoted to him
with no script behind it is a claim about evidence rather than evidence, which is
`measured-rate-travels-with-its-script` in his own words.

THE SOUND BASIS IS THE REGISTER'S OWN `qs` KIND, which exists because he ruled on
2026-10-19 that a question carries its own hashed identity. A question's
resolution is an ANSWER, not a build, and the 2 directions travel opposite ways:
he answers mine, I answer his. So the useful report is not a count of questions
but a SPLIT BY DIRECTION, because one side is work owed by the assistant and the
other is a decision owed by him, and conflating them is how 7 of his questions
came to be filed as debts HE owed.

HOW DIRECTION IS DERIVED, and it is derived rather than remembered. His questions
reach the register as annotations on a file in his `Responses/` directory, so
their anchor names that file. Mine are raised from chat, whose anchor begins
`chat#`, or against a repository artefact. Checked against all 11 live questions
on 2026-10-30: the predicate reproduces the hand classification exactly, 7 his and
4 mine.

AN EMPTY ANCHOR IS REPORTED, NOT DEFAULTED, and that is deliberate. 1 of the 11
carries no anchor at all and would fall through to "mine" by accident rather than
by the rule. Task C18's ruling is that an identity absent from the tables must be
LOUD and never defaulted, so an unattributable question is counted separately and
named. Silently assigning it would make the 2 totals add up and mean nothing.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: An anchor beginning with one of these does NOT name one of his response files.
#: Kept as data so a new source of assistant-raised questions is a 1-line change.
_NOT_HIS_PREFIXES = ("chat#", "experimental_notes/", "bench/", "scripts/", "docs/")


def classify(anchor: str) -> str:
    """"his", "mine" or "unattributed", from the anchor alone."""
    a = (anchor or "").strip()
    if not a:
        return "unattributed"
    if a.startswith(_NOT_HIS_PREFIXES):
        return "mine"
    return "his"


def collect() -> dict:
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TicketStore
    s = TicketStore()
    s.load()
    out = {"his": [], "mine": [], "unattributed": []}
    for t in s.live():
        if t.kind != "qs":
            continue
        out[classify(t.anchor or "")].append({
            "tid": t.tid,
            "status": t.status,
            "asked": t.ruled or "",
            "anchor": t.anchor or "",
            "task_ref": t.task_ref or "",
            "title": (t.title or "").strip(),
        })
    for k in out:
        out[k].sort(key=lambda r: (r["asked"], r["tid"]))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Which questions are owed, to whom, enumerated from the register.")
    ap.add_argument("--json", action="store_true", help="emit the split as JSON")
    args = ap.parse_args(argv)

    g = collect()
    n = sum(len(v) for v in g.values())
    if args.json:
        print(json.dumps({"total": n, **g}, indent=2))
        return 0

    print(f"== {n} live question(s) in the register ==\n")
    LABEL = {
        "his": "HIS QUESTIONS, which the assistant owes an ANSWER",
        "mine": "THE ASSISTANT'S QUESTIONS, which he owes a RULING",
        "unattributed": "UNATTRIBUTABLE: no anchor, so direction cannot be derived",
    }
    for key in ("his", "mine", "unattributed"):
        rows = g[key]
        print(f"{LABEL[key]}: {len(rows)}")
        for r in rows:
            where = r["anchor"].split("#")[0] if r["anchor"] else "(no anchor)"
            ref = f" [{r['task_ref']}]" if r["task_ref"] else ""
            print(f"   qs:{r['tid']}  asked {r['asked'] or '?':10s} {where[:44]:44s}{ref}")
            print(f"       {r['title'][:96]}")
        print()

    if g["unattributed"]:
        print("THE UNATTRIBUTABLE ONES ARE NOT COUNTED ON EITHER SIDE, on task C18's")
        print("ruling that an absent identity must be loud rather than defaulted.")
        print("Give each an anchor through `TicketStore.propose_from_chat`, which")
        print("derives one, and it will classify itself.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
