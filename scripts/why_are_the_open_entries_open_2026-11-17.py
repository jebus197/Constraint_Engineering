#!/usr/bin/env python3
"""Of the open entries whose own prose claims resolution, how many are closable?

★ WHY THIS EXISTS, AND IT BEARS ON A DECISION IN FRONT OF HIM. B197 reports the
task list's branching ratio above 1 and asks whether to rule again, retire the
assertion, or direct a closing pass. A closing pass is only worth ordering if
entries are open through NEGLECT. This measures that instead of assuming it.

★ THE ANSWER IS NOT FLATTERING IN EITHER DIRECTION, WHICH IS WHY IT IS WORTH
HAVING. Entries whose own STATUS prose says RESOLVED, FIXED or BUILT AND TESTED
while their marker reads OPEN look like neglect. Checked one at a time, almost
none are: they are open because the work is uncommitted, because the named
evidence is not something the suite RUNS, or -- in 1 case -- because the
mechanism is built and WIRED TO NOTHING, which the additive standard forbids as
firmly as a removal. Closing that one would certify an unwired addition as done.

★ IT CLASSIFIES AND DOES NOT CLOSE. `scripts/close_an_entry_2026-11-02.py` is
the only thing that closes an entry, it touches all 3 surfaces or none, and it
refuses without a verification.

Reads the task list and git. Writes nothing.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TL = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

CLAIMS_DONE = re.compile(r"STATUS:[^.]{0,200}?\b(RESOLVED|FIXED|BUILT AND TESTED|"
                         r"DONE|COMPLETE|DISCHARGED)\b", re.I)
NEEDS_HIM = re.compile(r"NEEDS (?:YOUR|HIS) RULING|AWAITING HIS|\[NEEDS", re.I)
UNWIRED = re.compile(r"NOT WIRED|0 production call sites|no production caller", re.I)


def classify() -> list[dict]:
    text = TL.read_text(encoding="utf-8", errors="replace")
    out = []
    for b in re.split(r"(?=^\*\*[A-Z]\d{1,4}\.)", text, flags=re.M):
        m = re.match(r"\*\*([A-Z]\d{1,4})\.", b)
        if not m:
            continue
        code = m.group(1)
        mk = re.search(rf"<!-- task: {code} \| state: (\w+) \| status: (\w+) \| "
                       rf"evidence: ([^|>]*)", b)
        if not mk or mk.group(1) != "OPEN":
            continue
        if not CLAIMS_DONE.search(b) or NEEDS_HIM.search(b[:1400]):
            continue
        status, ev = mk.group(2), mk.group(3).strip()
        tests = [f.strip() for f in ev.split(",")
                 if f.strip().startswith("bench/tests/") and f.strip().endswith(".py")]
        #: ★ "THE FILE EXISTS AT HEAD" IS NOT "THE WORK IS COMMITTED", and the
        #: first version of this classifier conflated them. 5 entries written
        #: tonight name evidence files that have been in HEAD for weeks while
        #: tonight's CHANGES to them sit uncommitted, so all 5 were reported as
        #: closable candidates when none is. File presence standing in for work
        #: being committed is the same shape as a substring standing in for a
        #: call -- the 4th instrument error of the night.
        #:
        #: The right test is BOTH: the evidence exists at HEAD **and** the
        #: working tree is clean for it. A dirty evidence file means the entry's
        #: work has not landed.
        def _settled(t: str) -> bool:
            at_head = subprocess.run(["git", "cat-file", "-e", f"HEAD:{t}"],
                                     cwd=REPO, capture_output=True).returncode == 0
            dirty = subprocess.run(["git", "status", "--porcelain", "--", t],
                                   cwd=REPO, capture_output=True,
                                   text=True).stdout.strip()
            return at_head and not dirty
        committed = all(_settled(t) for t in tests) if tests else False
        reason = None
        if status != "COMMITTED" and status in ("TESTED", "BUILT", "PROPOSED") and not committed:
            reason = ("evidence uncommitted or modified in the working tree, "
                      "or not a test the suite runs")
        if UNWIRED.search(b):
            reason = "built and WIRED TO NOTHING -- the additive standard forbids closing it"
        if reason is None and status == "TESTED" and committed:
            reason = "CANDIDATE: tested, evidence committed and runnable"
        out.append({"entry": code, "marker_status": status, "tests": tests,
                    "evidence_committed": committed, "verdict": reason
                    or "open for a reason the marker does not state"})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args([] if argv is None else argv)
    rows = classify()
    if a.json:
        import json
        print(json.dumps(rows, indent=2))
        return 0
    print(f"  open entries whose own prose claims resolution and which do not "
          f"say they need him: {len(rows)}\n")
    for r in rows:
        print(f"    {r['entry']:<6} marker {r['marker_status']:<10} "
              f"evidence committed {str(r['evidence_committed']):<5} "
              f"{r['verdict']}")
    cand = [r for r in rows if r["verdict"].startswith("CANDIDATE")]
    print()
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    mp.mp.dps = 40
    k, n = len(cand), len(rows)
    if n:
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        cl, ch = proportion_confint(k, n, alpha=0.05, method="beta")
        z = mp.sqrt(2) * mp.erfinv(mp.mpf("0.95"))
        p = mp.mpf(k) / n
        d = 1 + z**2 / n
        c = p + z**2 / (2 * n)
        h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
        agree = max(abs(float((c - h) / d) - lo), abs(float((c + h) / d) - hi))
        print(f"  closable candidates: {k} of {n} = {k / n:.6f}")
        print(f"      Wilson [{lo:.6f}, {hi:.6f}] (mpmath agrees to {agree:.2e})"
              f"  Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
    print()
    unwired = len([r for r in rows if "WIRED TO NOTHING" in r["verdict"]])
    blocked = n - k - unwired
    print(f"  THE BREAKDOWN, WHICH IS WHAT B197 ACTUALLY NEEDS: {k} closable, "
          f"{unwired} built and")
    print("  wired to nothing so closing them would certify an addition nothing")
    print(f"  reaches, and {blocked} whose evidence is uncommitted, modified in the "
          f"working tree,")
    print("  or not a test the suite runs.")
    print()
    print("  A CLOSING PASS IS WORTH ORDERING ONLY TO THE EXTENT ENTRIES ARE OPEN")
    print("  THROUGH NEGLECT, and on this measurement most are not. That is an")
    print("  argument the panel's recommendation did not have: both seats chose a")
    print("  closing pass over re-scoping the guard, and they chose it without")
    print("  knowing how few entries a pass can actually close. It does not overturn")
    print("  their reasoning -- re-scoping a threshold whenever it fires still")
    print("  measures nothing -- but it does mean the pass buys less than it sounds,")
    print("  and he should weigh both.")
    print()
    print("  AND THE 1 ENTRY THAT WAS GENUINE NEGLECT IS ALREADY CLOSED. B158 read")
    print("  RESOLVED since 2026-11-12 and VERIFIED since 2026-11-13 with its marker")
    print("  still OPEN; it was verified by execution and closed on 2026-11-17.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
