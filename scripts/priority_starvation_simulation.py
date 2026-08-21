#!/usr/bin/env python3
"""Does clamping the similarity map fix R_k starvation on its own, or worsen it?

WHY THIS EXISTS
---------------
Commit 3660816 raised R_k FAIL in the feedback priority above near-duplicate,
overriding an invariant recorded as intentional in
`bench/tests/test_feedback_channel.py`. The justifying figures existed only in a
commit message and a test comment. An independent review (Fable 5, 2026-08-21)
called that out correctly: by this project's own standard an uncommitted
measurement cannot justify overriding a recorded design decision. This is that
measurement, committed and reproducible.

THE QUESTION
------------
`priority_score` ranks feedback for a limited prompt budget. Near-duplicate scores
`2.0 * similarity`; an R_k discrepancy scored `min(1.0, |delta|)`, typically <0.1.
CC2 measured the consequence: the R_k INCONSISTENT record fired in 20 of 170
exp44 files against a 31.7% FAIL rate.

The intuition is that repairing the similarity map fixes this by itself, because
the duplicate flood stops. THE INTUITION IS WRONG, and this shows why: at 98%
flagging the duplicate term is very nearly a CONSTANT and cancels out of the
ranking. Once flagging drops to ~21% it becomes DISCRIMINATING, so the minority
of findings carrying a duplicate flag outrank every R_k failure.

    python3 scripts/priority_starvation_simulation.py
"""
from __future__ import annotations

import random
import statistics as st

TOP_K = 10          # cfg.feedback_top_k
N_FINDINGS = 30     # a typical round
FAIL_RATE = 0.506   # measured on the corrected reader, exp44-49, 2026-08-21
MEDIAN_DELTA = 0.35 # typical |claimed - recomputed| when it is not a FAIL
TRIALS = 600
SEED = 11


def score(dup_sim, rk_fail, scheme):
    s = 2.0 * dup_sim if dup_sim is not None else 0.0
    if rk_fail:
        s += 2.5 if scheme == "new" else min(1.0, MEDIAN_DELTA)
    return s


def surfaced_fraction(dup_rate, scheme, seed):
    """Mean share of R_k-failing findings that make the top_k, over TRIALS rounds.

    Seeded per call so the two schemes see the IDENTICAL population: the only
    variable is the weighting.
    """
    rng = random.Random(seed)
    fracs = []
    for _ in range(TRIALS):
        round_items = []
        for i in range(N_FINDINGS):
            dup = rng.uniform(0.62, 0.79) if rng.random() < dup_rate else None
            rk_fail = rng.random() < FAIL_RATE
            round_items.append((i, dup, rk_fail))
        ranked = sorted(round_items, key=lambda t: -score(t[1], t[2], scheme))
        top = {i for i, _, _ in ranked[:TOP_K]}
        failing = [i for i, _, f in round_items if f]
        if failing:
            fracs.append(sum(1 for i in failing if i in top) / len(failing))
    return st.mean(fracs)


def main():
    print("Fraction of R_k-FAILING findings that reach the prompt\n")
    print(f"  top_k={TOP_K}  findings/round={N_FINDINGS}  FAIL rate={FAIL_RATE}  trials={TRIALS}\n")
    print(f"  {'duplicate flagging rate':34s} {'old weights':>12s} {'new weights':>12s}")
    print("  " + "-" * 60)
    for rate, label in ((0.98, "BEFORE the clamp (98% flagged)"),
                        (0.214, "AFTER the clamp (21.4% flagged)")):
        old = surfaced_fraction(rate, "old", SEED)
        new = surfaced_fraction(rate, "new", SEED)
        print(f"  {label:34s} {old*100:11.1f}% {new*100:11.1f}%")
    print("""
  READ THIS ROW-WISE, NOT COLUMN-WISE. The point is not that the new weights are
  better in the abstract. It is that repairing the similarity map MOVES the
  problem: under the old weights the share of R_k failures reaching a model FALLS
  once duplicates become rare, because a rare flag discriminates where a
  universal one cannot.""")


if __name__ == "__main__":
    main()
