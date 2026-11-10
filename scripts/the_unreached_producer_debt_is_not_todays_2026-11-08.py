#!/usr/bin/env python3
"""A 3rd date-scoped guard would close 19 producers and leave 229.

HIS INSTRUCTION, 2026-11-08: *"extend the reached-producers rule to today's date
and commit"*, which is the fix I proposed to him. This measures that proposal
before building it, and the measurement says the SHAPE is wrong even though the
direction is right.

THE RULE AT ISSUE. `bench/tests/test_tonights_producers_are_reached_2026-11-03.py`
states it: a measurement producer that nothing EXECUTES is the
addition-nothing-reaches half of `additive-standard`, which this project has
confirmed 11 times. That guard is scoped to producers dated 2026-11-03, and a
sibling covers 2026-11-02.

WHAT IS MEASURED HERE. Every script in `scripts/` whose NAME carries a date,
excluding mutation harnesses for the reason the 2026-11-03 guard gives --
a harness invokes pytest, so running it from inside the suite recurses. A
producer counts as REACHED when its stem appears in any file under
`bench/tests/`, which is the same predicate the existing guards use.

THE RESULT, AND IT IS THE ARGUMENT AGAINST A 3RD DATED GUARD. 2026-11-08 is not
an outlier and the debt is not new: 2026-09-20 carries more unreached producers
than today does, and 37 of 46 dates carry at least 1. Closing today alone leaves
the rest, and a guard per date is precisely the pattern that let the debt recur
to a 3rd date.

SO THE FIX IS COMPOSED, AND THE COMPOSITION ADVANTAGE IS NAMED, which is what
his composability standard requires rather than the weak claim that 2 fixes can
coexist:
  * The DATE-SCOPED half pins today's SET. A named producer cannot silently
    stop being run, which a count alone would permit.
  * The DATE-INDEPENDENT RATCHET pins the GLOBAL COUNT. The debt cannot grow on
    any other date, which the dated guard alone permits -- it is blind to 36
    other dates.
  * Neither half does both: a set without a ratchet leaves 229 unguarded, and a
    ratchet without a set permits swapping one unreached producer for another at
    a constant total.

★ THIS SCRIPT COUNTS ITSELF, AND THAT IS NOT A FLAW TO HIDE. Writing it moved
the figure from 246 of 556 to 247 of 557, because it is a dated producer that no
test reached at the moment it was written. The same self-counting shape made the
closing report's commit figure go stale the instant the report was committed. A
measurement whose population includes the measurement cannot carry a live
number, so this one is always printed FROM THE TREE rather than quoted from
memory, and the ratchet below is pinned AFTER the listing rather than before it.

Exit 0 always: this reports. The ratchet that GATES is
`bench/tests/test_the_producer_debt_cannot_grow_2026-11-08.py`.
"""
from __future__ import annotations

import argparse
import collections
import math
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
DATED = re.compile(r"_(20\d\d-\d\d-\d\d)\.py$")
#: Excluded for the reason the 2026-11-03 guard gives for its own 2: a mutation
#: harness invokes pytest, so a test running it would recurse.
HARNESS = re.compile(r"mutations?_20\d\d-\d\d-\d\d\.py$")


def survey(repo: pathlib.Path = REPO):
    """(reached, unreached, by_date) over dated producers. The REACHED predicate
    is the one the existing guards use: the stem appears in any test file."""
    tests = [t.read_text(encoding="utf-8", errors="replace")
             for t in sorted((repo / "bench/tests").glob("*.py"))]
    by_date: dict = collections.defaultdict(lambda: [0, 0])
    reached, unreached = [], []
    for p in sorted((repo / "scripts").glob("*.py")):
        m = DATED.search(p.name)
        if not m or HARNESS.search(p.name):
            continue
        hit = any(p.stem in txt for txt in tests)
        (reached if hit else unreached).append(p.name)
        by_date[m.group(1)][0 if hit else 1] += 1
    return reached, unreached, dict(by_date)


def interval(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 independent routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p, d = k / n, 1 + stats.norm.ppf(0.975) ** 2 / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    cl = float(stats.beta.ppf(0.025, k, n - k + 1)) if k else 0.0
    ch = float(stats.beta.ppf(0.975, k + 1, n - k)) if k != n else 1.0

    def bi(a, b, y):
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(240):
            mid = (lo + hi) / 2
            if mpmath.betainc(a, b, 0, mid, regularized=True) < y:
                lo = mid
            else:
                hi = mid
        return float((lo + hi) / 2)

    ml = bi(k, n - k + 1, mpmath.mpf("0.025")) if k else 0.0
    mh = bi(k + 1, n - k, mpmath.mpf("0.975")) if k != n else 1.0
    return ((wl, wh), (float(c - hw), float(c + hw)), (cl, ch), (ml, mh))


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    reached, unreached, by_date = survey()
    n = len(reached) + len(unreached)
    k = len(unreached)
    print(f"dated producers, mutation harnesses excluded : {n}")
    print(f"  reached by at least 1 test                 : {len(reached)}")
    print(f"  reached by NOTHING                         : {k}")
    (wl, wh), (al, ah), (cl, ch), (ml, mh) = interval(k, n)
    print(f"\n  unreached: {k} of {n} = {k / n:.6f}")
    print(f"    Wilson [{wl:.6f}, {wh:.6f}] statsmodels")
    print(f"    Wilson [{al:.6f}, {ah:.6f}] written-out algebra, "
          f"agree to {max(abs(wl - al), abs(wh - ah)):.2e}")
    print(f"    Clopper-Pearson [{cl:.6f}, {ch:.6f}] scipy beta quantile")
    print(f"    Clopper-Pearson [{ml:.6f}, {mh:.6f}] mpmath incomplete beta, "
          f"agree to {max(abs(cl - ml), abs(ch - mh)):.2e}")
    with_debt = sum(1 for v in by_date.values() if v[1])
    print(f"\n  dates carrying ANY unreached producer: {with_debt} of {len(by_date)}")
    print(f"\n  worst 8 dates by unreached count:")
    _by = sorted(by_date.items(), key=lambda x: -x[1][1])
    for dt, (r, u) in _by[:8]:
        print(f"    {dt}  reached {r:3d}  unreached {u:3d}  "
              f"({u / (r + u):.4f} of {r + u})")
    if len(_by) > 8:
        print(f"    ... and {len(_by) - 8} more date(s) withheld, carrying "
              f"{sum(v[1] for _d, v in _by[8:])} further unreached producer(s)")
    today = by_date.get("2026-11-08", [0, 0])
    print(f"\n  2026-11-08 alone: {today[1]} unreached of {sum(today)}")
    print(f"  CLOSING TODAY ALONE WOULD LEAVE {k - today[1]} unreached on "
          f"{with_debt - (1 if today[1] else 0)} other date(s),")
    print(f"  which is why the fix is composed rather than a 3rd dated guard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
