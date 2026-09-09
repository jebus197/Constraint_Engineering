#!/usr/bin/env python3
"""What actually catches CC1's self-inflicted defects: a mechanism, or the founder?

The founder asks whether the mechanism discussed for stopping repeated mistakes
was ever built. Before designing one it is worth knowing what the current
catchers are, because a new mechanism aimed at the wrong catcher is an addition
that nothing reaches -- the failure mode the additive standard names.

SOURCE AND ITS LIMITS, STATED FIRST. The sample is the defects CC1 introduced and
that were then caught, over 2026-09-08 and 2026-09-09, as recorded in the commit
messages of 3c4987d, 01906cc, 57d5a0e and 9e3dfe9 and in the operational tracker.
Two limits follow and neither is small:

  1. IT IS A CAUGHT-ONLY SAMPLE. Defects nothing caught cannot appear in it, so
     every rate here is conditioned on being caught and says nothing about how
     many were missed. This is the same selection trap the project already
     recorded when a similarity accuracy was computed over only the pairs a model
     was willing to label.
  2. THE CLASSIFICATION IS CC1'S OWN. Assigning a catcher to a defect is a
     judgement, and it is CC1 judging its own record. An independent reviewer
     might allocate several of these differently.

So this is an ORDER-OF-MAGNITUDE instrument for choosing where to put a guard,
not a measurement of CC1's error rate. The rate travels with this script per
`measured-rate-travels-with-its-script`.

Two tools per proportion: statsmodels for the intervals, mpmath for a
closed-form Wilson that shares none of statsmodels' code.
"""
from __future__ import annotations

import collections

import mpmath as mp
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint

# (short name, catcher, the evidence it is recorded in)
# catcher is one of:
#   SUITE    -- pytest went red
#   LINT     -- a linter or checker refused
#   FOUNDER  -- George caught it
#   SELF     -- CC1's own later check or P-pass caught it, unprompted
DEFECTS = [
    ("_record_recovery_ran never fired",            "SELF",    "tracker 2026-09-08 03:10 pointer"),
    ("duration scan double-counted the archive",    "SELF",    "tracker 2026-09-08 03:10 pointer"),
    ("pipeline exit code read 0 while pytest 1",    "SELF",    "tracker 2026-09-08 03:10 pointer"),
    ("39.35% pooled HIL baseline was a mixture",    "FOUNDER", "tracker 2026-09-08 04:45 pointer"),
    ("module-level panel_cwd fallback",             "SUITE",   "tracker 2026-09-08 04:45 pointer"),
    ("reading sk_result inside _apply_routing",     "SUITE",   "tracker 2026-09-08 04:45 pointer"),
    ("timestamp understated by 607 minutes",        "FOUNDER", "session record 2026-09-08"),
    ("target-mutation p-value anti-conservative",   "SELF",    "commit 01906cc"),
    ("committed .py snapshots read as source",      "SUITE",   "commit 01906cc"),
    ("scan-scope sweep was itself bounded",         "SELF",    "commit 57d5a0e"),
    ("memory ledger drift, 139 vs 138",             "SUITE",   "commit 9e3dfe9"),
    ("memory index entry 198 chars over 150",       "SUITE",   "commit 9e3dfe9"),
    ("tracker cited a file by bare name",           "SUITE",   "commit 9e3dfe9"),
    ("memory index over its line headroom",         "SUITE",   "commit 9e3dfe9"),
    ("v1.7 substring filter matched its target",    "SELF",    "commit 9e3dfe9"),
    ("'push is blocked' -- stale, never retested",  "FOUNDER", "session record 2026-09-09"),
    ("remote recovery conclusion was wrong",        "FOUNDER", "session record 2026-09-09"),
    ("the 4 skips answered before the run landed",  "SELF",    "session record 2026-09-09"),
    ("note vagueness: hedge and category noun",     "LINT",    "commit 57d5a0e"),
]


def wilson_mp(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(1 - (1 - conf) / 2)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    centre = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    half = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return float(centre - half), float(centre + half)


def main() -> int:
    n = len(DEFECTS)
    by = collections.Counter(c for _, c, _ in DEFECTS)
    print(f"Caught defects in the sample: {n}\n")
    print(f"{'catcher':<10}{'count':>6}{'share':>9}   Wilson 95% [statsmodels]      mpmath agrees")
    for catcher in ("SUITE", "SELF", "FOUNDER", "LINT"):
        k = by[catcher]
        lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
        lo_m, hi_m = wilson_mp(k, n)
        agree = abs(lo_w - lo_m) < 1e-12 and abs(hi_w - hi_m) < 1e-12
        print(f"{catcher:<10}{k:>6}{k/n:>9.1%}   [{lo_w:>6.1%}, {hi_w:>6.1%}]              {agree}")

    mech = by["SUITE"] + by["LINT"]
    lo_w, hi_w = proportion_confint(mech, n, alpha=0.05, method="wilson")
    lo_c, hi_c = proportion_confint(mech, n, alpha=0.05, method="beta")
    lo_m, hi_m = wilson_mp(mech, n)
    print(f"\nCaught by a MECHANISM (suite or lint): {mech} of {n} = {mech/n:.1%}")
    print(f"    Wilson 95%          [statsmodels] : [{lo_w:.1%}, {hi_w:.1%}]")
    print(f"    Wilson 95%          [mpmath     ] : [{lo_m:.1%}, {hi_m:.1%}]   agree={abs(lo_w-lo_m)<1e-12}")
    print(f"    Clopper-Pearson 95% [statsmodels] : [{lo_c:.1%}, {hi_c:.1%}]")

    f = by["FOUNDER"]
    lo_w2, hi_w2 = proportion_confint(f, n, alpha=0.05, method="wilson")
    print(f"\nReached the FOUNDER before anything caught it: {f} of {n} = {f/n:.1%}")
    print(f"    Wilson 95% [{lo_w2:.1%}, {hi_w2:.1%}]")

    # Is "mechanism catches more than the founder" distinguishable from chance,
    # among the defects caught by exactly one of those two? Exact binomial, and
    # the same question posed to Fisher on the 2x2 as an independent check.
    pair = mech + f
    p_exact = sps.binomtest(mech, pair, 0.5, alternative="greater").pvalue
    odds, p_fisher = sps.fisher_exact([[mech, f], [f, mech]], alternative="greater")
    print(f"\nAmong the {pair} caught by mechanism-or-founder, mechanism took {mech}.")
    print(f"    exact binomial vs 50/50 [scipy]      : p = {p_exact:.4g}")
    print(f"    Fisher on the mirrored table [scipy] : p = {p_fisher:.4g}, odds {odds:.3g}")

    print("\nWHAT THIS DOES AND DOES NOT SUPPORT")
    print("  Supports: a mechanism is already the most common catcher, so the")
    print("  marginal value of a NEW mechanism is lower than it looks, and the")
    print("  gap worth closing is the specific class the suite cannot see.")
    print("  Does NOT support: any claim about defects nothing caught, which by")
    print("  construction cannot appear here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
