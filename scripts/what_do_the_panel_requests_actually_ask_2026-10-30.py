#!/usr/bin/env python3
"""The 30 open panel-requested tickets, classified by his words and dated.

WHY THIS EXISTS, AND IT IS A DEFECT OF MINE. The morning report of 2026-10-30
told the founder that of 30 panel-labelled work tickets, 19 are unconditional
requests, 6 are conditional and 5 are not panel requests at all, that 11 trace
to a task entry of which 10 have every referenced entry closed (0.909091), and
that 94 panel records exist against those 30 requests. Searching the tree for a
producer of any of those figures returns nothing: `panel_requests_are_tracked_2026-10-20.py`
tracks the tickets and `work_remaining_section_2026-10-20.py` renders a section,
and neither computes a split, a traceability count or a record tally. So 10
figures reached him, and were then re-quoted twice in the consolidated file of
the same morning, as prose about evidence rather than evidence. The project's
own rule is that a measured count may be cited only if the script that produced
it is committed alongside it.

WHAT THIS DOES AND DOES NOT DO. It recomputes the request count, the 3-way
classification and the records-after-request tally, and it prints its rule so a
reader can disagree with the classification rather than having to trust it. It
does NOT trace a request to a task entry, because every one of these tickets
carries an empty `task_ref` and tracing needs the annotated passage at the
ticket's anchor, which must be read through
`scripts/read_founder_responses_2026-10-11.py` rather than by searching the
files. Until that is built, the 11-of-30 and 10-of-11 figures have no producer
and must not be quoted.

IT CLOSES NOTHING. `TicketStore.close` requires a verification per ticket, and
matching a record to a request needs both sides read. A script that closed 30
tickets on a date comparison would be the opposite of that discipline.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import sys

import mpmath as mp
import numpy as np
from scipy import stats as sst
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

EVIDENCE = REPO / "experimental_notes" / "evidence"

#: A CONDITION GATES THE REQUEST. Each is matched on his own sentence, so a
#: reader can see why an item was called conditional. "if" alone is deliberately
#: not enough -- "if you are unsure" gates the request, "if it works" does not
#: always -- so the markers are phrases rather than the bare conjunction.
CONDITIONAL = re.compile(
    r"\bif (?:you|there|that|this|it|not|necessary|unsure|any)\b"
    r"|\bif not already\b|\bunless\b|\bin case\b|\bwhere necessary\b"
    r"|\bas necessary\b|\bshould you\b|\bif in doubt\b", re.I)

#: AN INSTRUCTION TO ACT, as opposed to a question that mentions a panel. The
#: distinction matters because 1 of his annotations asks why a guard should need
#: a panel review at all, which is the opposite of commissioning one.
IMPERATIVE = re.compile(
    r"\bask (?:the panel|them|the free panel|the models)\b"
    r"|\bcheck (?:it |your work |this )?with\b|\bdiscuss\b"
    r"|\b(?:run|build|dispatch|set up|arrange) a (?:\d[ -])?(?:model )?panel\b"
    r"|\bput (?:it|this|that) to the panel\b|\bdo the work\b|\bdo it\b"
    r"|\badd it to\b|\bthen do\b|\bverdict\b|\bapprove", re.I)

PANEL = re.compile(r"\bpanel\b", re.I)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def classify(verbatim: str) -> tuple[str, str]:
    """(verdict, the sentence the verdict rests on).

    UNCONDITIONAL / CONDITIONAL / NOT-A-REQUEST. The sentence is returned so the
    classification is auditable: a reader can read the words it was decided on.
    """
    sents = _sentences(verbatim)
    panel_sents = [s for s in sents if PANEL.search(s)]
    basis = panel_sents[0] if panel_sents else (sents[0] if sents else verbatim)

    #: An imperative anywhere in the annotation commissions work, even when the
    #: panel is named in a different sentence of the same reply.
    has_imperative = bool(IMPERATIVE.search(verbatim))
    if not has_imperative:
        interrogative = basis.rstrip().endswith("?")
        if interrogative or not panel_sents:
            return "NOT-A-REQUEST", basis
    #: A condition is read from the imperative's own sentence where there is
    #: one, else from the panel sentence, so an unrelated conditional elsewhere
    #: in a long reply does not gate the request.
    imp_sents = [s for s in sents if IMPERATIVE.search(s)]
    scope = imp_sents[0] if imp_sents else basis
    if CONDITIONAL.search(scope):
        return "CONDITIONAL", scope
    return "UNCONDITIONAL", scope


#: HAND-READ CASES, AND THE RULE DISAGREES WITH 2 OF THEM. Recorded as a control
#: rather than as ground truth: these are 1 reader's reading, which is why the
#: producer reports DISAGREEMENT instead of publishing a corrected split. The
#: project's rule is that a finding is confirmed programmatically or by the human
#: in the loop, and a regex over his prose is neither once it is shown to misfire.
#:
#:   fd6bd113d263 -- the rule says UNCONDITIONAL because IMPERATIVE matched the
#:     word "verdict". His sentence is *"I can't offer a verdict"*: the match is
#:     INSIDE A NEGATION, which is the shape that once made a reader match
#:     NOT FALSIFIED as FALSIFIED and cost this project a convergence.
#:   5b46f40b7ddb -- the rule says CONDITIONAL on "Fix as necessary". The
#:     condition gates the FIX; the next sentence asks for a panel discussion
#:     unconditionally, so the scope was taken from the wrong clause.
#:
#: Both are SCOPE errors rather than vocabulary errors, so widening the patterns
#: would not fix them. A classification of his prose needs the prose read.
HAND_READ: dict[str, str] = {
    "fd6bd113d263": "NOT-A-REQUEST",
    "5b46f40b7ddb": "UNCONDITIONAL",
}


def panel_rounds() -> list[tuple[datetime.date, str]]:
    """(date, round name) for every mirrored panel round, from its parent dir."""
    out = []
    for d in sorted(EVIDENCE.glob("panel_records_*")):
        m = re.match(r"panel_records_(\d{4})-(\d{2})-(\d{2})$", d.name)
        if not m:
            continue
        day = datetime.date(*map(int, m.groups()))
        for r in sorted(p for p in d.iterdir() if p.is_dir()):
            out.append((day, r.name))
    return out


def requests() -> list[dict]:
    from bench.ticket_store import TicketStore
    s = TicketStore()
    out = []
    for t in s.all() if hasattr(s, "all") else s._by_tid.values():
        if t.kind != "wr" or str(t.status).upper() != "OPEN":
            continue
        if not str(t.title).startswith("PANEL REQUESTED"):
            continue
        verdict, basis = classify(t.verbatim)
        out.append({"tid": t.tid, "ruled": t.ruled, "anchor": t.anchor,
                    "task_ref": t.task_ref, "verdict": verdict,
                    "basis": basis[:200], "verbatim_len": len(t.verbatim)})
    return sorted(out, key=lambda x: (x["ruled"] or "", x["tid"]))


def report() -> dict:
    reqs = requests()
    rounds = panel_rounds()
    n = len(reqs)
    by = {}
    for r in reqs:
        by.setdefault(r["verdict"], []).append(r["tid"])
    #: records dated at or after each request, which is the only claim a date
    #: comparison supports: it does NOT say the record answers the request.
    for r in reqs:
        if r["ruled"]:
            d = datetime.date(*map(int, r["ruled"].split("-")))
            r["rounds_after"] = sum(1 for day, _ in rounds if day >= d)
        else:
            r["rounds_after"] = None
    dated = [r for r in reqs if r["ruled"]]
    res = {"requests": n, "rounds_mirrored": len(rounds),
           "by_verdict": {k: len(v) for k, v in sorted(by.items())},
           "tids_by_verdict": by,
           "task_ref_present": sum(1 for r in reqs if r["task_ref"]),
           "oldest": dated[0]["ruled"] if dated else None,
           "newest": dated[-1]["ruled"] if dated else None,
           "min_rounds_after": min(r["rounds_after"] for r in dated) if dated else None,
           "detail": reqs}
    #: THE CONTROL DECIDES WHETHER THE SPLIT MAY BE PUBLISHED AT ALL.
    disagree = []
    for tid, label in HAND_READ.items():
        got = next((r["verdict"] for r in reqs if r["tid"] == tid), None)
        if got is not None and got != label:
            disagree.append({"tid": tid, "rule_says": got, "read_as": label})
    res["hand_read_checked"] = len(HAND_READ)
    res["hand_read_disagreements"] = disagree
    res["split_publishable"] = not disagree

    if n and not disagree:
        k = len(by.get("UNCONDITIONAL", []))
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        cp = sst.binomtest(k, n).proportion_ci(confidence_level=0.95, method="exact")
        assert abs(float(mp.mpf(k) / mp.mpf(n)) - np.float64(k) / n) < 1e-12
        res["unconditional_share"] = {"k": k, "n": n, "p": k / n,
                                      "wilson": [lo, hi],
                                      "clopper_pearson": [cp.low, cp.high]}
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    ap.add_argument("--detail", action="store_true", help="print every request")
    args = ap.parse_args(argv)
    r = report()
    if args.json:
        print(json.dumps(r, indent=2, default=str))
        return 0
    print(__doc__.split("\n")[0])
    print("=" * 78)
    print(f"open panel-requested tickets : {r['requests']}")
    print(f"panel rounds mirrored        : {r['rounds_mirrored']}")
    print(f"tickets carrying a task_ref  : {r['task_ref_present']} "
          f"-> tracing to an entry needs the Responses reader, not this script")
    print(f"ruling dates                 : {r['oldest']} to {r['newest']}")
    print()
    if r["split_publishable"]:
        for k, v in r["by_verdict"].items():
            print(f"  {k:16s} {v:3d}")
    else:
        print("  THE 3-WAY SPLIT IS WITHHELD. The rule disagrees with a hand")
        print("  reading on "
              f"{len(r['hand_read_disagreements'])} of {r['hand_read_checked']} "
              "case(s) checked, and both are SCOPE")
        print("  errors that widening the patterns would not fix:")
        for d in r["hand_read_disagreements"]:
            print(f"    {d['tid']}: rule says {d['rule_says']}, "
                  f"read as {d['read_as']}")
        print("  What the rule still establishes is reported above and below:")
        print("  the request COUNT, the date range, that 0 carry a task_ref,")
        print("  and how many rounds are mirrored after each one.")
        print("  The earlier figures of 19, 6 and 5 have no producer and no")
        print("  recorded rule, so they cannot be checked either.")
    u = r.get("unconditional_share")
    if u:
        print(f"\n  unconditional share {u['k']}/{u['n']} = {u['p']:.6f}")
        print(f"    Wilson           [{u['wilson'][0]:.6f}, {u['wilson'][1]:.6f}]")
        print(f"    Clopper-Pearson  [{u['clopper_pearson'][0]:.6f}, "
              f"{u['clopper_pearson'][1]:.6f}]")
    print(f"\n  fewest rounds mirrored after any single request: {r['min_rounds_after']}")
    print("  A DATE COMPARISON SAYS ONLY THAT PANELS RAN AFTERWARDS. It does not")
    print("  say any of them answered the request, and nothing here is closed.")
    if args.detail:
        print("\n" + "-" * 78)
        for d in r["detail"]:
            print(f"  [{d['tid']}] {d['ruled']}  {d['verdict']}  "
                  f"rounds_after={d['rounds_after']}")
            print(f"      anchor: {d['anchor']}")
            print(f"      basis : {d['basis'][:140]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
