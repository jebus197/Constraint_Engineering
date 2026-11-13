#!/usr/bin/env python3
"""B103's rule says every guard since 2026-10-29 is on the gate. 32 are not.

`hooks/pre-commit` states the rule in its own prose, twice:

    "SO THE SCOPE IS THE GUARDS WRITTEN SINCE 2026-10-29"
    "B103's rule is that every guard written on or after 2026-10-29 goes on
     this gate"

★ AND THE FILE ALREADY RECORDS THIS FAILING ONCE. Against the 6 guards dated
2026-11-10 it says: "5 OF THEM WERE MINE TO ADD EARLIER THE SAME NIGHT AND WERE
NOT ADDED ... so each guarded a repair that this gate could not have caught
regressing. That is the 'a guard outside the gate' class the list already
records against test_blocker_triage, found there after 5 commits."

It has recurred, at 32 files, and they are not old ones: they include the
guards for repairs committed and staged TODAY.

★ WHY THIS IS NOT AN ARGUMENT FOR ADDING EVERY TEST FILE, which the same file
refutes at length. Adding the whole unreached set takes the gate from 312 s to
5,634 s, a factor of 18.05, and "a commit that takes an hour and a half is a
commit nobody makes". The rule is deliberately scoped to guards since
2026-10-29 precisely because that set is small and cheap. This script measures
the gap against THAT rule, not against the whole suite.

★ THE COST OF CLOSING IT IS NOT MEASURED HERE AND MUST NOT BE ASSUMED. The
file's own history is that a recommendation was once accepted on a figure
answering a different question -- "about 6 per cent" where the real answer was
1,705 per cent. Before these 32 are added, they must be RUN TOGETHER once and
the wall time reported, exactly as the 2026-10-31 addition of 29 files and the
2026-11-10 addition of 6 both did.
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent
if not (REPO / "hooks").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
CUTOFF = datetime.date(2026, 10, 29)   # B103's rule, quoted in hooks/pre-commit


def listed_guards() -> set[str]:
    pre = (REPO / "hooks" / "pre-commit").read_text(encoding="utf-8")
    m = re.search(r'GUARDS="(.*?)"', pre, re.S)
    if not m:
        raise SystemExit("hooks/pre-commit no longer defines GUARDS; this "
                         "script's whole premise is gone, which is a finding")
    return {l.strip() for l in m.group(1).splitlines() if l.strip()}


def dated_guards() -> dict[str, datetime.date]:
    out = {}
    for f in sorted((REPO / "bench" / "tests").glob("test_*.py")):
        d = re.search(r"_(\d{4})-(\d{2})-(\d{2})\.py$", f.name)
        if not d:
            continue
        when = datetime.date(int(d.group(1)), int(d.group(2)), int(d.group(3)))
        if when >= CUTOFF:
            out[f"bench/tests/{f.name}"] = when
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()
    listed, dated = listed_guards(), dated_guards()
    missing = sorted(p for p in dated if p not in listed)
    k, n = len(missing), len(dated)
    print(f"  GUARDS list                       : {len(listed)} files")
    print(f"  guards dated on or after {CUTOFF} : {n}")
    print(f"  NOT on the gate                   : {k} of {n} = {k / n:.6f}\n")

    import numpy as np
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    w1 = proportion_confint(k, n, method="wilson")
    p, z = k / n, 1.959963984540054
    den = 1 + z * z / n
    ctr, half = (p + z * z / (2 * n)) / den, \
        z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    cp1 = proportion_confint(k, n, method="beta")
    cp2 = (float(sbeta.ppf(0.025, k, n - k + 1)) if k else 0.0,
           float(sbeta.ppf(0.975, k + 1, n - k)) if k < n else 1.0)
    print(f"  Wilson statsmodels [{w1[0]:.6f}, {w1[1]:.6f}]")
    print(f"  Wilson closed form [{ctr-half:.6f}, {ctr+half:.6f}]  "
          f"agree {max(abs(w1[0]-(ctr-half)), abs(w1[1]-(ctr+half))):.3e}")
    print(f"  C-P    statsmodels [{cp1[0]:.6f}, {cp1[1]:.6f}]")
    print(f"  C-P    scipy.beta  [{cp2[0]:.6f}, {cp2[1]:.6f}]  "
          f"agree {max(abs(cp1[0]-cp2[0]), abs(cp1[1]-cp2[1])):.3e}\n")

    by_day: dict[datetime.date, int] = {}
    for pth in missing:
        by_day[dated[pth]] = by_day.get(dated[pth], 0) + 1
    print("  by date written:")
    for day in sorted(by_day):
        print(f"    {day}: {by_day[day]}")
    print("\n  ★ COST OF CLOSING THIS IS NOT MEASURED HERE. Run the 32 together")
    print("    once and report the wall time before adding them, as the")
    print("    2026-10-31 and 2026-11-10 additions both did.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
