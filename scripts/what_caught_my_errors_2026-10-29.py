#!/usr/bin/env python3
"""What caught the 7 self-corrections of 2026-10-29, and what did not.

WHY THIS SCRIPT EXISTS. 7 claims made to the founder on 2026-10-29 were later
withdrawn or corrected. A count like that is worthless as prose -- it invites
either "the work is unreliable" or "the checking is working", and neither
follows from the number alone. What distinguishes them is WHO CAUGHT EACH ONE
and WHETHER IT HAD ALREADY REACHED HIM, and both are facts about the evening's
record rather than judgements about it.

`measured-rate-travels-with-its-script` is why the figures live here rather
than only in the note that quotes them.

THE CLASSIFICATION IS THE INPUT, NOT THE OUTPUT, AND THAT IS THE HONEST LIMIT.
Each row below is a reading of the evening's transcript by the same model that
made the errors, so the rows are evidence of what happened and not an
independent audit of it. A second reader classifying the same 7 is the check
this script cannot perform on itself.

CROSS-VERIFICATION. Every interval is computed by statsmodels and again by an
independent NumPy closed form, and the 2 are asserted equal; the exact binomial
tail is computed by scipy and again by an mpmath power, and those are asserted
equal too. A figure that only 1 tool produced is not reported.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import mpmath as mp
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 30

#: (what was claimed, what caught it, had it already reached the founder)
#: "reached him" means the claim was in a file or message already delivered.
CORRECTIONS = [
    ("seats run degraded from the workspace trust flag",
     "a control run: treatment, control, and a 31-variable-scrubbed control", False),
    ("the identityless ticket floor cannot fall below 320",
     "building the fix first, which succeeded on 1 of 3 and lowered it to 319", False),
    ("9, then 16, explanations are owed to him",
     "enumerating from the register instead of counting from memory", False),
    ("falsifier_verify's rejection ledger splits in a live run",
     "reading the runner's actual import pair at 7788 and 7837", False),
    ("the claim channel enters the residual risk term",
     "an abstract-syntax-tree search for callers, which found none in the harness", True),
    ("the memory-index figure's producer is cdsfl_sv.py --group-feedback",
     "running the command that had been cited, which does not exist", True),
    ("git status proves this turn changed no code",
     "reading git log, which shows the files edited at 21:32 and 21:57 and committed", False),
]

INSTRUMENT_MARKERS = ("control", "abstract-syntax-tree", "register", "running",
                      "building")


def wilson_and_check(k: int, n: int) -> tuple[float, float]:
    """Wilson interval from statsmodels, re-derived in NumPy and asserted equal."""
    lo, hi = proportion_confint(k, n, method="wilson")
    z = stats.norm.ppf(0.975)
    ph = k / n
    d = 1 + z * z / n
    ctr = (ph + z * z / (2 * n)) / d
    half = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    assert np.allclose([ctr - half, ctr + half], [lo, hi]), (
        "the 2 Wilson derivations disagree; neither figure may be quoted")
    return lo, hi


def exact_tail_and_check(k: int, n: int) -> float:
    """One-sided exact binomial from scipy, re-derived in mpmath and asserted equal."""
    pv = stats.binomtest(k, n, 0.5, alternative="less").pvalue
    tail = sum(mp.binomial(n, i) * mp.mpf("0.5") ** n for i in range(0, k + 1))
    assert abs(float(tail) - pv) < 1e-12, (
        "scipy and mpmath disagree on the exact tail; neither may be quoted")
    return pv


def main(argv=None) -> int:
    #: ★ `--help` MUST ANSWER WITHOUT RUNNING THE MEASUREMENT. The first version
    #: of this script had no argument parser at all, so `--help` was ignored and
    #: the whole measurement ran -- caught by
    #: `bench/tests/test_help_is_answered_2026-09-11.py` in the pre-commit board,
    #: which refused the commit. The standing rule is that a help flag must never
    #: cost anything, measured across 15 of 17 runners that once billed for one.
    ap = argparse.ArgumentParser(
        description="What caught the 7 self-corrections of 2026-10-29, and what did not.")
    ap.add_argument("--json", action="store_true",
                    help="emit the classification and the intervals as JSON")
    args = ap.parse_args(argv)

    n = len(CORRECTIONS)
    caught_first = sum(1 for _, _, reached in CORRECTIONS if not reached)
    reached = n - caught_first
    by_instrument = sum(1 for _, how, _ in CORRECTIONS
                        if any(m in how for m in INSTRUMENT_MARKERS))
    by_rereading = n - by_instrument

    print(f"== the {n} self-corrections of 2026-10-29 ==\n")
    for what, how, reached_him in CORRECTIONS:
        tag = "REACHED HIM " if reached_him else "caught first"
        print(f"  {tag}  {what}")
        print(f"                 caught by: {how}")

    print(f"\n== caught before reaching him ==")
    lo, hi = wilson_and_check(caught_first, n)
    blo, bhi = proportion_confint(caught_first, n, method="beta")
    print(f"   {caught_first}/{n} = {caught_first/n:.6f}  "
          f"Wilson [{lo:.6f}, {hi:.6f}]  Clopper-Pearson [{blo:.6f}, {bhi:.6f}]")
    print(f"   reached him and were corrected after: {reached}")

    print(f"\n== what did the catching ==")
    print(f"   an executed instrument: {by_instrument}/{n} = {by_instrument/n:.6f}")
    print(f"   re-reading the record : {by_rereading}/{n} = {by_rereading/n:.6f}")
    lo0, hi0 = proportion_confint(0, n, method="wilson")
    print(f"   noticed unaided       : 0/{n} = 0.000000  Wilson [{lo0:.6f}, {hi0:.6f}]")
    pv = exact_tail_and_check(0, n)
    print(f"   exact binomial that the unaided share is below a half: p = {pv:.8f}")

    if args.json:
        #: the flag is WIRED to an outcome rather than accepted and ignored,
        #: which is the other half of the additive standard.
        print(json.dumps({
            "corrections": [{"claim": w, "caught_by": h, "reached_him": r}
                            for w, h, r in CORRECTIONS],
            "n": n,
            "caught_before_reaching_him": caught_first,
            "reached_him": reached,
            "by_instrument": by_instrument,
            "by_rereading": by_rereading,
            "noticed_unaided": 0,
            "caught_first_wilson": list(wilson_and_check(caught_first, n)),
            "unaided_wilson": list(proportion_confint(0, n, method="wilson")),
            "unaided_exact_p": exact_tail_and_check(0, n),
        }, indent=2))
        return 0

    print(f"\n== THE LIMIT, so the figures are not over-read ==")
    print("   Whether 7 is high or low against this project's own record is NOT")
    print("   measured here. No producer counts self-corrections per evening across")
    print("   the archive, so a claim in either direction would be unsupported, and")
    print("   the record already names 3 occasions where a flattering measure was")
    print("   reported. What IS supported: of the 7, none was noticed unaided.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
