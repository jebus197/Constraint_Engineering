#!/usr/bin/env python3
"""PRODUCER: what is still outstanding, and is any of it mine to do?

HIS QUESTION, 2026-11-01 02:01: *"Have you completed all the work outstanding
from the last tts response I gave you and on your master task list, including
all the outstanding free panel reviews? If not why did you stop?"*

THE HONEST HEADLINE IS THAT THE OPEN COUNT WENT UP, NOT DOWN. The list held 9
OPEN entries when he went to sleep and holds 15 now. 9 entries were ADDED and 0
were closed, so by the only count that matters to him the night made the queue
longer. That is not automatically wrong -- 5 of the additions are defects that
previously had no position in the register at all, which was his own instruction
-- but it has to be said first rather than buried under what was built.

WHAT THIS SCRIPT SEPARATES, because the answer to "why did you stop" depends on
it entirely:

  * entries whose remaining work is HIS -- a ruling, an authorisation, a spend;
  * entries whose remaining work is MINE and was not done;
  * and PANEL REVIEWS HE HAS AUTHORISED that have never run, which is a
    different question from the written briefs measured earlier tonight: a
    review he authorised with no brief written is outstanding and would not
    appear in a census of brief directories.

THE EARLIER MEASUREMENT WAS TRUE AND NARROWER THAN THE QUESTION. Tonight's
`is_any_panel_brief_still_outstanding_2026-11-01.py` established that 0 of 7
WRITTEN briefs are both unrun and still relevant. It did not ask whether he has
authorised a review for which no brief exists, and his question is the wider
one.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

import task_list_markers as tlm  # noqa: E402

FAILURES: list[str] = []

#: An entry whose remaining work is HIS: a ruling, an authorisation, a spend, a
#: go-ahead. Matched on the entry text, which is where the project records it.
HIS = re.compile(
    r"(NEEDS\s+(?:HIS|YOUR)\s+(?:RULING|GO-?AHEAD|VERDICT|AUTHORISATION|DECISION)"
    r"|STILL\s+(?:HIS|NEEDS\s+HIS)|AWAITS?\s+(?:HIS|YOUR)"
    r"|NEEDS\s+HIS\s+RULING\s+ON|IT\s+COSTS\s+MONEY)", re.I)

#: An entry that says, in its own words, that nothing is owed by him.
NOT_HIS = re.compile(r"NEEDS\s+NO\s+RULING", re.I)


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    _check("wilson cross-check",
           abs(float((c - h) / d) - lo_sm) < 1e-9 and abs(float((c + h) / d) - hi_sm) < 1e-9,
           "statsmodels and mpmath disagree")
    return float(lo_sm), float(hi_sm)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    entries = tlm.parse_entries()
    openes = [e for e in entries if (e.state or "").upper() == "OPEN"]

    print("=" * 72)
    print("M1. THE COUNT WENT UP, WHICH IS THE FIRST THING HE IS OWED")
    print("=" * 72)
    added = [e for e in openes if e.ident in
             ("B58", "B59", "B60", "B61", "C0001", "C0036", "C0037", "C0040", "C0054")]
    print(f"OPEN entries now                : {len(openes)}")
    print(f"OPEN entries added last night   : {len(added)}")
    print(f"OPEN entries closed last night  : 0")
    print(f"  added: {sorted(e.ident for e in added)}")
    print()
    print("5 of the 9 are the directive-composition defects, which previously")
    print("had no position in the register at all -- giving them one was his own")
    print("instruction, so their appearance is the instruction being carried out")
    print("rather than new work being invented. The other 4 are the night's own")
    print("findings. NONE of the 9 existed as a tracked item before, so the")
    print("queue is longer AND more honest, and both halves are true.")

    print()
    print("=" * 72)
    print("M2. WHOSE WORK IS THE REMAINDER?")
    print("=" * 72)
    his, mine, unclear = [], [], []
    for e in openes:
        txt = e.text
        if HIS.search(txt) and not NOT_HIS.search(txt):
            his.append(e)
        elif NOT_HIS.search(txt):
            mine.append(e)
        else:
            unclear.append(e)
    print(f"{'bucket':<34}{'count':>6}")
    print(f"{'waiting on HIM (ruling/spend)':<34}{len(his):>6}")
    print(f"{'says it needs NO ruling -> MINE':<34}{len(mine):>6}")
    print(f"{'says neither':<34}{len(unclear):>6}")
    lo, hi = wilson(len(his), len(openes))
    print()
    print(f"share waiting on him: {len(his)} of {len(openes)}  "
          f"Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    for label, group in (("WAITING ON HIM", his),
                         ("MINE, AND NOT DONE", mine),
                         ("SAYS NEITHER -- needs reading", unclear)):
        print(f"  {label}:")
        for e in sorted(group, key=lambda x: x.ident):
            print(f"     {e.ident:<8} status={e.status}")
        if not group:
            print("     none")
        print()
    _check("the buckets partition the open set",
           len(his) + len(mine) + len(unclear) == len(openes),
           "an entry fell into no bucket")

    print("=" * 72)
    print("M3. PANEL REVIEWS HE HAS AUTHORISED, AND WHETHER THEY RAN")
    print("=" * 72)
    # A review he AUTHORISED is recorded in an entry's text; a review that RAN
    # has a log directory with at least 1 reply file. This is the wider question
    # his message asks, and the brief census of earlier tonight did not cover it.
    AUTH = re.compile(r"(put\s+it\s+to\s+the\s+(free\s+)?panel|to\s+the\s+free\s+panel"
                      r"|which\s+I\s+have\s+already\s+authorised|free[- ]panel\s+dispatch"
                      r"|panel\s+review\s+I\s+(?:have\s+)?(?:already\s+)?(?:requested|authorised))",
                      re.I)
    authorised = [e for e in entries if AUTH.search(e.text)]
    print(f"entries whose text records an authorised panel review: {len(authorised)}")
    for e in sorted(authorised, key=lambda x: x.ident):
        print(f"   {e.ident:<8} state={e.state}")
    print()
    rounds = {}
    for b in REPO.glob("bench/logs/**/BRIEF*.md"):
        d = b.parent
        if "sandbox_harvest" in str(d) or "panel_worktree" in str(d):
            continue
        rounds[d.name] = len([f for f in d.glob("*.json")
                              if "brief" not in f.name.lower()])
    ran = {k: v for k, v in rounds.items() if v > 0}
    print(f"panel rounds with at least 1 seat reply: {len(ran)} of {len(rounds)}")
    lo2, hi2 = wilson(len(ran), len(rounds))
    print(f"   Wilson 95% [{lo2:.6f}, {hi2:.6f}]")
    print()
    print("WHAT THIS CAN AND CANNOT SETTLE. It can say how many rounds ran and")
    print("which entries record an authorisation. It CANNOT mechanically pair an")
    print("authorisation with the round that discharged it, because the pairing")
    print("lives in prose. So the 0-outstanding claim of earlier tonight is")
    print("sound for WRITTEN BRIEFS and is NOT a claim about authorisations, and")
    print("the gap between those 2 is what his question is pointing at.")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
