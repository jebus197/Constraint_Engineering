#!/usr/bin/env python3
"""Scope for decisions 16 and 32, and why 32's stated population does not reproduce.

DECISION 16 -- the 133 unadjudicated similarity pairs. Ruled: no adjudication is
needed; supply the 17 missing fixes, repair the 11 equipment cases, record the 4
containments. Measured scope today, from the committed adjudicator's own dry run:

    unadjudicated pairs                 133
    code targets, in scope               90
    exam targets, need the off-repo store 43

The 43 cannot proceed while the answer-key store is held for the founder's return,
so the workable population is 90. Supplying a fix is per-item authoring, not a
sweep, and it is NOT started -- named here rather than left implied.

DECISION 32 -- the materiality review of "findings against TRUE claims", stated as
11 in Exp 49, 6 in Exp 48, and Exp 47's 2 HIL residuals. THAT POPULATION DOES NOT
REPRODUCE. Measured from the run reports, which are what executed:

    exp47  70 entries   REFUTED 2   irreducible 3
    exp48  37 entries   REFUTED 2   irreducible 1
    exp49  38 entries   REFUTED 0   irreducible 0

Exp 49 carries 0 refuted findings and 0 irreducible items, against a claimed 11.
The figures 11/6/2 appear in exactly 2 places -- one tracker line and the decisions
file that copied it from that line -- with no post-mortem, no artefact and no
script behind them. That is the shape `measured-rate-travels-with-its-script`
exists to catch, and it is the second such figure found today (the other was "37
finding IDs to relabel", which also did not reproduce).

There is an innocent reading and it is probably the right one: for an EXAM target,
"a finding against a TRUE claim" is decided against the ANSWER KEY, not against the
run's status field. So the number may be real and simply uncheckable from the
reports alone -- which means decision 32 needs the answer-key store, and is
therefore blocked behind the same held work as the 43 exam pairs above.

Either way the honest position is the same: 32 cannot be drafted from what is
readable today, and the 11/6/2 figures must not be quoted until something
reproduces them.

Run: python3 scripts/scope_remaining_adjudication_and_materiality.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

from statsmodels.stats.proportion import proportion_confint

REPO = Path(__file__).resolve().parents[1]


def _entries(run_glob: str):
    for d in sorted((REPO / "bench" / "logs").glob(run_glob)):
        for p in sorted(d.glob("*.json")):
            try:
                doc = json.loads(p.read_text())
            except Exception:
                continue
            stack = [doc]
            while stack:
                o = stack.pop()
                if isinstance(o, dict):
                    if isinstance(o.get("entries"), dict) and o["entries"]:
                        return d.name, o["entries"]
                    stack.extend(o.values())
                elif isinstance(o, list):
                    stack.extend(o)
    return None, None


def main() -> int:
    argparse.ArgumentParser(description=__doc__.split("\n")[0]).parse_args()

    print("DECISION 16 — adjudication scope (from the committed adjudicator)")
    r = subprocess.run(["python3", str(REPO / "scripts" / "adjudicate_by_repair.py"),
                        "--dry-run"], capture_output=True, text=True, cwd=str(REPO))
    for line in r.stdout.strip().split("\n")[-4:]:
        print("   ", line.strip())

    print("\nDECISION 32 — the claimed population, re-measured")
    claimed = {"exp47": 2, "exp48": 6, "exp49": 11}
    for exp, claim in claimed.items():
        name, ents = _entries(f"{exp}_*")
        if not ents:
            print(f"    {exp}: no entries block found")
            continue
        st = Counter(e.get("status") for e in ents.values() if isinstance(e, dict))
        refuted = st.get("REFUTED", 0)
        irred = sum(1 for e in ents.values()
                    if isinstance(e, dict) and e.get("irreducible_escalation"))
        n = len(ents)
        lo, hi = proportion_confint(refuted, n, alpha=0.05, method="wilson")
        print(f"    {exp}: {n} entries | REFUTED {refuted} "
              f"({100*refuted/n:.1f}%, Wilson [{100*lo:.1f}%, {100*hi:.1f}%]) "
              f"| irreducible {irred} | CLAIMED {claim}")
    print("\n  exp49 carries 0 refuted and 0 irreducible against a claimed 11.")
    print("  The figures 11/6/2 have no artefact behind them and must not be")
    print("  quoted until something reproduces them. Most likely they are decided")
    print("  against the ANSWER KEY, which is held -- so 32 is blocked on that.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
