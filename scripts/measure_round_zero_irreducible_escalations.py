#!/usr/bin/env python3
"""The queue alarm was RIGHT, and softening it would have buried a real fault.

FOUNDER DECISION 6 asked what the alarm does. Answering that question refuted
CC1's own recommendation, which had been to soften it from HALT to veto-only.

WHY THE RECOMMENDATION WAS WRONG. `build_irreducible_queue_alarm`'s own docstring
records that a pure veto -- "returned not converged from the convergence checker and
nothing else" -- is the worst available response, because it names no cause, hands
over no evidence, and lets the loop burn its round budget against a fault no round
can fix. It was suppressed twice on 2026-08-01 by raising the bound, and it was
RIGHT BOTH TIMES. The current HALT/NOTIFY/ATTACH form exists precisely to stop an
alarm that only obstructs from being switched off. Reverting it to veto-only would
have re-created the failure it was built to end.

WHAT THE ALARM ACTUALLY CAUGHT, from the evidence bundle it attached to exp55:

    sk_states_in_queue      : ['(none)']
    items_without_falsifier : 6 of 7
    every item              : status OPEN, open_since_round 0

Findings were entering the IRREDUCIBLE queue at ROUND 0. `irreducible_escalation`
is set in one place only (reference_runner_v3.py, the `else` branch after the full
routing ladder is exhausted), and at round 0 the ladder cannot have been exhausted
in any meaningful sense: no S_k state exists for any queued item, so no fix was ever
evaluated. That is not irreducibility. It is findings that were never processed,
labelled as findings no machine could process.

The target was prose (614 bytes). The runner's own comment on the neighbouring line
records the historical version of this: "Until 2026-08-01 that was false on every
prose target -- no model was ever given the target." The A-list prose fixes landed
before exp55 ran on 2026-08-23, so either they do not cover this path or the ladder
genuinely exhausts at round 0 on short prose. Which of those it is, is the actual
open question, and it is the thing that has blocked the runway for 12 days.

THE ALARM IS THEREFORE LEFT EXACTLY AS IT IS. This script exists so the finding
travels and so nobody -- including a later CC1 -- re-proposes softening it without
reading what it caught.

Run: python3 scripts/measure_round_zero_irreducible_escalations.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from statsmodels.stats.proportion import proportion_confint

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def _walk(obj, key):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            yield from _walk(v, key)
    elif isinstance(obj, list):
        for i in obj:
            yield from _walk(i, key)


def main() -> int:
    argparse.ArgumentParser(description=__doc__.split("\n")[0]).parse_args()

    alarms, at_round_zero, no_sk = [], 0, 0
    for path in sorted(LOGS.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue
        for a in _walk(doc, "irreducible_queue_alarm"):
            if not isinstance(a, dict):
                continue
            key = (path.parent.name, a.get("round"), a.get("count"))
            if key in {(x[0], x[1], x[2]) for x in alarms}:
                continue
            alarms.append((path.parent.name, a.get("round"), a.get("count"),
                           a.get("bound"), a.get("sk_states_in_queue"),
                           a.get("items_without_falsifier")))

    n = len(alarms)
    print("Irreducible-queue alarms in the archive")
    print("=" * 62)
    print(f"  distinct alarm events: {n}")
    for run, rnd, count, bound, sk, nofals in alarms:
        print(f"    {run}")
        print(f"      round {rnd}, queue {count} against bound {bound}, "
              f"S_k states {sk}, items without a falsifier {nofals}")
        if rnd == 0:
            at_round_zero += 1
        if sk in (["(none)"], "(none)", None, []):
            no_sk += 1
    if n:
        for label, k in (("fired at ROUND 0", at_round_zero),
                         ("with NO S_k state for any queued item", no_sk)):
            lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
            print(f"\n  {label}: {k} of {n} = {100*k/n:.1f}%  "
                  f"Wilson [{100*lo:.1f}%, {100*hi:.1f}%]")
        print("\n  A queue item with no S_k state was never evaluated for a fix.")
        print("  At round 0 the routing ladder cannot have been exhausted.")
        print("  The alarm is naming an instrument fault, which is its job.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
