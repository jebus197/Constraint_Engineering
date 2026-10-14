#!/usr/bin/env python3
"""For each PARKED item, has the founder already ruled on it?

HIS QUESTION, 2026-10-13: *"Did I not rule on these already? Also what about
the items listed as 'parked' here. There doesn't seem much reason to ignore
them. Give me a fresh morning report of anything still requiring my ruling.
Check first if I haven't ruled on them already."*

WHY THIS IS A SCRIPT AND NOT A JUDGEMENT. The previous morning report listed 6
decisions and 21 parked items. He annotated all 6 the same day, and the report
that is still on his Desktop is the one his annotations were written ONTO, so
re-reading it shows the questions and not their answers. Deciding by memory
which of the 21 he has since ruled on is exactly the operation this project has
recorded going wrong: a rate or a status asserted from recollection rather than
derived from the record.

HOW A MATCH IS ESTABLISHED, AND WHAT IT DELIBERATELY WILL NOT DO. Each parked
heading is reduced to the IDENTIFIERS it carries -- task codes (A17, A18, V9,
W1), finding codes (C0040, C0001) and numbered entries (10.2). An annotation of
his counts as bearing on a parked item only when it carries the same
identifier, or when the parked file's own text says the item is closed. A bare
topic word is NOT enough: "panel" or "logs" appears across most of the corpus
and would match everything, which is the shape of the defect recorded in
`feedback_check_the_whole_set`. So this script UNDER-reports rather than over-
reports, and the residue it cannot decide is listed for reading rather than
silently classed either way.

Usage: python3 scripts/has_he_already_ruled_on_the_parked_2026-10-13.py
"""
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
MARKERS = REPO / "scripts" / "task_list_markers.py"

#: Parked items whose premise was refuted BY EXECUTION on 2026-10-13, each with
#: the evidence that refuted it. Listed rather than inferred, because "I checked
#: and it is stale" is a claim about evidence until the evidence is named.
VERIFIED_STALE = {
    "The triage script cannot see an entry that says":
        "scripts/blocker_triage.decision_required exists and fires on the A8 "
        "shape; 27 tests green",
    "the Claude CLI login has expired":
        "cc2 answered twice on 2026-10-12 (127 and 98 tool calls, ok=True) in "
        "bench/logs/clear_the_outstanding_2026-10-12 and its joint round",
}

#: Shapes that identify a specific item. Deliberately narrow.
IDENT_RE = re.compile(
    r"\b(?:[A-Z]\d{1,3}(?:/[A-Z]\d{1,3})?|C\d{4}|W\d|V\d{1,2}|\d{1,2}\.\d{1,2})\b")

#: Phrases in the PARKED file's own text that mark an item as already settled.
CLOSED_MARKERS = ("SUPERSEDED", "RESOLVED", "NOTHING LEFT TO RULE ON",
                  "SAME DECISION AS", "IS CLOSED", "NOT A BLOCKER",
                  "on the founder's instruction", "do not answer this heading")


def parked_items():
    """(heading, body) for every '## ' heading in the parked file."""
    if not PARKED.is_file():
        return []
    text = PARKED.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"^## ", text, flags=re.M)[1:]
    out = []
    for p in parts:
        lines = p.splitlines()
        out.append((lines[0].strip(), "\n".join(lines[1:])))
    return out


def task_states() -> dict:
    """ident -> (state, status) from the master task list, via its own parser."""
    spec = importlib.util.spec_from_file_location("tlm", MARKERS)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tlm"] = mod
    spec.loader.exec_module(mod)
    return {e.ident: (e.state, e.status) for e in mod.parse_entries(TASKLIST)}


def annotations():
    """Every annotation the founder wrote, through the canonical reader."""
    r = subprocess.run([sys.executable, str(READER), "--json"],
                       capture_output=True, text=True, cwd=str(REPO))
    if r.returncode != 0:
        return []
    d = json.loads(r.stdout)
    return d.get("annotations", [])


def main() -> int:
    answer_help(__doc__, __file__)
    items = parked_items()
    anns = annotations()
    if not items:
        print("no parked items found; measurement void.")
        return 3
    if not anns:
        print("the reader returned no annotations; measurement void.")
        return 3

    ann_text = [(a.get("date", "?"), (a.get("text") or "")) for a in anns]
    print(f"parked headings: {len(items)}   annotations read: {len(anns)}")

    states = task_states()
    closed, ruled, undecided = [], [], []
    body_only = []
    for heading, body in items:
        # THE MARKER MUST BE IN THE HEADING, NOT MERELY SOMEWHERE IN THE ITEM.
        # A body mentioning "RESOLVED" about a NEIGHBOURING fact would
        # otherwise settle the item falsely. Attempted as a falsification on
        # 2026-10-13: 0 of 21 items match on the body alone, so the stricter
        # rule changes no current classification -- and it is applied anyway,
        # because the looser one would have been wrong the moment one did.
        if any(m in body and m not in heading for m in CLOSED_MARKERS):
            body_only.append(heading)
        if any(m in heading for m in CLOSED_MARKERS):
            closed.append((heading, "the item's own heading says so"))
            continue
        # THE TASK LIST IS THE SECOND SOURCE, and without it this script
        # reported 8 of 21 while the full analysis reported 14 -- so a figure
        # quoted to the founder had no producer, which is the defect
        # `measured-rate-travels-with-its-script` exists to prevent.
        # A COMPOUND IDENTIFIER IS SEVERAL IDENTIFIERS, and not splitting it
        # cost a figure. `IDENT_RE` matches "A13/A14" as ONE token, the task
        # list keys "A13" and "A14" separately, so the lookup missed and the
        # item read as unsettled -- this script reported 13 of 21 where the
        # full analysis reported 14, with A13/A14 the whole difference. Both
        # halves are DONE. Same shape as every other instrument defect of this
        # week: a predicate that fails to match what it should.
        _idents = [part for tok in IDENT_RE.findall(heading)
                   for part in tok.split("/")]
        done = [i for i in _idents
                if states.get(i, ("", ""))[0] in ("DONE", "WITHDRAWN")]
        if done:
            closed.append((heading,
                           f"task list: {done[0]} is {states[done[0]][0]}"))
            continue
        stale = [why for frag, why in VERIFIED_STALE.items() if frag in heading]
        if stale:
            closed.append((heading, f"refuted by execution: {stale[0]}"))
            continue
        idents = {i for i in IDENT_RE.findall(heading)}
        hits = []
        for date, txt in ann_text:
            for ident in idents:
                if re.search(r"\b" + re.escape(ident) + r"\b", txt):
                    hits.append((date, ident, txt[:150]))
                    break
        if hits:
            ruled.append((heading, hits))
        else:
            undecided.append((heading, sorted(idents)))

    print(f"\nSETTLED, AND BY WHAT                   : {len(closed)}")
    for h, why in closed:
        print(f"    [{why[:46]:<46}] {h[:62]}")
    print(f"\nitems matching a closed-marker in the BODY but not the heading: "
          f"{len(body_only)}")
    if body_only:
        print("  these would be FALSE POSITIVES under a looser rule:")
        for h in body_only:
            print(f"    {h[:88]}")
    print(f"\nHE HAS RULED, BY IDENTIFIER MATCH      : {len(ruled)}")
    for h, hits in ruled:
        print(f"    {h[:92]}")
        for date, ident, txt in hits[:2]:
            print(f"       {date} [{ident}] {txt}")
        # A LIST CUT TO N UNDER A COMPLETE-LOOKING HEADING IS A SILENT FALSEHOOD.
        if len(hits) > 2:
            print(f"       ... and {len(hits) - 2} further ruling(s) on this "
                  f"heading, of {len(hits)} total, not shown")
    print(f"\nNO RULING FOUND, NEEDS READING         : {len(undecided)}")
    for h, idents in undecided:
        print(f"    {h[:88]}   idents={idents or '(none)'}")

    n = len(items)
    k = len(closed) + len(ruled)
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo2 = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi2 = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    print(f"\nparked items already closed or ruled: {k} of {n} = {k/n:.4%}")
    print(f"  Wilson 95%          [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% [{lo2:.4%}, {hi2:.4%}]  (scipy.beta)")
    print("\nTHE RESIDUE IS WHAT STILL NEEDS HIM, and it is an UPPER BOUND:")
    print("  identifier matching under-reports, so an item listed as needing")
    print("  him may still carry a ruling phrased without its code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
