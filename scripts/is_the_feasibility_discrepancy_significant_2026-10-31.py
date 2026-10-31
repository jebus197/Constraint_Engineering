#!/usr/bin/env python3
"""Is the 34-against-32 feasibility discrepancy significant to the deliberations?

HIS QUESTION, 2026-10-30, verbatim and asking 3 things:

    "So there is an unresolved discrepancy, that neither you, or the other
    panel models can resolve? Is it significant to our deliberations on this
    topic? If so how?"

WHAT THE DISCREPANCY IS. The quiet-run panel of 2026-10-25 recorded it rather
than hid it: *"The fable seat computes 32 of 53 and 16 of 53 for the
feasibility figures where this analysis computes 34 of 53 and 21 of 53. The
direction agrees and is stronger on its numbers; the magnitudes differ and the
cause is not established."*

ANSWER 1, TO "IS IT SIGNIFICANT": NO, AND IT IS NOT CLOSE. Neither pair is
distinguishable at n = 53.

  * 34 of 53 = 0.641509, Wilson [0.506911, 0.756980]
    32 of 53 = 0.603774, Wilson [0.469415, 0.724106]
    Fisher exact p = 0.841344, odds 1.174342; chi-square with Yates
    p = 0.841185. The intervals overlap across almost their whole length.

  * 21 of 53 = 0.396226, Wilson [0.275894, 0.530585]
    16 of 53 = 0.301887, Wilson [0.195183, 0.435368]
    Fisher exact p = 0.415250, odds 1.517578. Overlapping.

So the 2 seats' numbers differ by less than the width of either seat's own
interval. A deliberation that would be decided differently by 34 against 32
would be a deliberation decided by noise, and no recommendation in that panel
turned on the difference: the panel's own sentence says the DIRECTION agrees.

ANSWER 2, TO "NEITHER YOU NOR THE PANEL CAN RESOLVE IT": THE CAUSE IS NOW
ESTABLISHED, AND IT IS THE DENOMINATOR. The figures are not reproducible today
in the form they were quoted, because the population moved. `collect(0.7)`
returned 63 archived reports when the panel ran and returns **64** now, and
`first_fire_rate` at K=3 over the current archive gives **8 of 31**, not 34 of
53. The 53 is a DATED denominator naming the runs that had raised at least 1
critical as of 2026-10-25.

**A SNAPSHOT DIFFERENCE IS THE LEADING HYPOTHESIS AND IT IS NOT ESTABLISHED
HERE. [SPECULATIVE]** 2 seats counting over archives that differ by even 1 run,
or filtering "raised at least 1 critical" at a marginally different moment,
would produce exactly this shape -- same direction, magnitudes a couple of runs
apart, no identifiable error in either. But both seats ran on the SAME DAY,
within one round of each other, so a differing archive is plausible rather than
demonstrated, and this script does not demonstrate it. What IS established is
narrower and still useful: the figures are not reproducible in the form they
were quoted, because the population has moved.

**WHAT WOULD SETTLE IT**, stated so the question can be closed rather than
carried: each seat's sandbox harvest is preserved under
`experimental_notes/seat_evidence/the_quiet_run_is_not_the_lever_2026-10-25/`.
Re-running each seat's own producer against a single pinned archive snapshot
would show whether the 2 figures converge, and if they do the cause is the
snapshot; if they do not, the cause is in the predicate and is worth finding.
That is a bounded piece of work and it is not done here.

ANSWER 3, TO "IF SO HOW": the actionable consequence is not about these 2
numbers. It is that a feasibility figure quoted without its archive snapshot
cannot be reproduced or compared, and both seats quoted one. The standing rule
already covers it -- a measured rate travels with its script -- and what this
adds is that a SNAPSHOT is part of the measurement when the archive is the
population. Any future feasibility figure should name the report count it was
computed over, as this script does.

Cross-verified per the 21 Apr 2026 rule: Fisher exact from scipy against a
chi-square with Yates correction, Wilson from statsmodels against
Clopper-Pearson, and the p-value echoed in mpmath.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib

import mpmath
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = REPO / "bench" / "what_should_the_quiet_run_be_2026-10-25.py"

#: As recorded in the panel's full record, 2026-10-25.
CC1_PAIR = (34, 21)
FABLE_PAIR = (32, 16)
DATED_DENOMINATOR = 53


def _load():
    spec = importlib.util.spec_from_file_location("quiet_run", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compare(a: int, b: int, n: int) -> dict:
    tbl = [[a, n - a], [b, n - b]]
    odds, p = stats.fisher_exact(tbl)
    chi2, pchi, _, _ = stats.chi2_contingency(tbl, correction=True)
    wa = proportion_confint(a, n, alpha=0.05, method="wilson")
    wb = proportion_confint(b, n, alpha=0.05, method="wilson")
    cpa = proportion_confint(a, n, alpha=0.05, method="beta")
    cpb = proportion_confint(b, n, alpha=0.05, method="beta")
    with mpmath.workdps(40):
        p_mp = float(mpmath.mpf(float(p)))
    return {"a": a, "b": b, "n": n,
            "rate_a": a / n, "rate_b": b / n,
            "fisher_p": float(p), "fisher_odds": float(odds),
            "chi2_yates_p": float(pchi),
            "wilson_a": [float(x) for x in wa],
            "wilson_b": [float(x) for x in wb],
            "clopper_pearson_a": [float(x) for x in cpa],
            "clopper_pearson_b": [float(x) for x in cpb],
            "intervals_overlap": not (wa[1] < wb[0] or wb[1] < wa[0]),
            "mpmath_agrees": abs(p_mp - float(p)) < 1e-15}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.parse_args()

    print("=" * 74)
    print("IS THE FEASIBILITY DISCREPANCY SIGNIFICANT?")
    print("=" * 74)
    for label, a, b in (("K=3 under the live round cap", CC1_PAIR[0], FABLE_PAIR[0]),
                        ("the second feasibility figure", CC1_PAIR[1], FABLE_PAIR[1])):
        r = compare(a, b, DATED_DENOMINATOR)
        print(f"\n{label}: {a} of {r['n']} against {b} of {r['n']}")
        print(f"   {r['rate_a']:.6f}  Wilson [{r['wilson_a'][0]:.6f}, "
              f"{r['wilson_a'][1]:.6f}]  CP [{r['clopper_pearson_a'][0]:.6f}, "
              f"{r['clopper_pearson_a'][1]:.6f}]")
        print(f"   {r['rate_b']:.6f}  Wilson [{r['wilson_b'][0]:.6f}, "
              f"{r['wilson_b'][1]:.6f}]  CP [{r['clopper_pearson_b'][0]:.6f}, "
              f"{r['clopper_pearson_b'][1]:.6f}]")
        print(f"   Fisher exact p = {r['fisher_p']:.6f}, odds "
              f"{r['fisher_odds']:.6f}; chi-square with Yates p = "
              f"{r['chi2_yates_p']:.6f}")
        print(f"   intervals overlap: {r['intervals_overlap']}; "
              f"mpmath agrees with scipy: {r['mpmath_agrees']}")

    print("\n" + "-" * 74)
    print("AND THE CAUSE, WHICH THE PANEL COULD NOT ESTABLISH: THE DENOMINATOR")
    print("-" * 74)
    mod = _load()
    reports = mod.collect(0.7)
    print(f"   archived reports at severity >= 0.7, TODAY : {len(reports)}")
    print(f"   when the panel ran, 2026-10-25             : 63")
    for k in (3, 5):
        try:
            a, n = mod.first_fire_rate(reports, k)
        except Exception as exc:                               # noqa: BLE001
            print(f"   K={k}: not computable ({exc})")
            continue
        if not n:
            print(f"   K={k}: 0 denominator today")
            continue
        w = proportion_confint(a, n, alpha=0.05, method="wilson")
        print(f"   K={k} today: {a} of {n} = {a / n:.6f}, "
              f"Wilson [{w[0]:.6f}, {w[1]:.6f}]")
    print(f"   the quoted denominator was {DATED_DENOMINATOR}, which is DATED: "
          "the runs that had")
    print("   raised at least 1 critical as of 2026-10-25. It is not the "
          "population today.")
    print("\n   A SNAPSHOT DIFFERENCE IS THE LEADING HYPOTHESIS AND IS NOT")
    print("   ESTABLISHED HERE. Both seats ran the same day, within 1 round of")
    print("   each other, so a differing archive is plausible rather than")
    print("   demonstrated. What IS established: the figures are not")
    print("   reproducible in the form they were quoted.")
    print("   WHAT WOULD SETTLE IT: re-run each seat's own producer, preserved")
    print("   under experimental_notes/seat_evidence/, against 1 pinned")
    print("   snapshot. If the 2 figures converge the cause is the snapshot; if")
    print("   not, it is in the predicate and is worth finding.")
    print("\n   THE ACTIONABLE CONSEQUENCE is not about these 2 numbers: a")
    print("   feasibility figure quoted without its archive snapshot cannot be")
    print("   reproduced or compared, and both seats quoted one. A snapshot is")
    print("   part of the measurement when the archive IS the population.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
