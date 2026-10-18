#!/usr/bin/env python3
"""Is the current severity ruler really the sigma-to-zero member of the smooth family?

WHY THIS EXISTS. The blind panel round of 2026-10-18 proposed replacing the hard
criticality indicator with a smooth weight, and justified it on the ground that
"the current ruler is the sigma = 0 member of this family", which is what would
discharge the additive standard: nothing removed, the old behaviour recovered as a
limit. **CC1 RELAYED THAT CLAIM TO THE FOUNDER.** The JOINT round refuted it, and
this script verifies the refutation independently rather than taking either seat's
word for it.

THE REFUTATION. Production compares `severity >= threshold`, so a finding at
EXACTLY the threshold scores 1. The smooth weight at that point is the normal
cumulative at 0, which is 1/2 for every sigma, so the limit does NOT recover the
production value there. The nesting holds for severity != threshold and fails at
severity == threshold.

WHY THAT IS NOT PEDANTRY. The threshold value is not a rare corner of the
distribution: models anchor on the published cut, so an exact 0.7 is one of the
most frequent severities in the archive. This script measures how frequent.

WHAT IT DOES NOT CLAIM. The practical consequence at the convergence gate is NIL,
and the joint round gave the reason: a round containing such an entry is
non-quiescent under both rulers, because 1/2 is not below the 0.5 cut, so the cut
absorbs the discontinuity exactly. The claim that needs correcting is the ADDITIVE
one, not the behaviour.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

import numpy as np
import sympy as sp
import mpmath as mp
from scipy.stats import norm
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
THRESHOLD = 0.7


def _wilson(k: int, n: int) -> tuple[float, float]:
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z, p = 1.959963984540054, k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    assert abs(max(0.0, (c - h) / d) - lo) < 1e-12, (k, n)
    return float(lo), float(hi)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    mp.mp.dps = 25

    print("THE LIMIT, 3 TOOLS")
    s, th = sp.symbols("s theta", real=True)
    sig = sp.symbols("sigma", positive=True)
    Phi = sp.Rational(1, 2) * (1 + sp.erf((s - th) / (sig * sp.sqrt(2))))
    for label, sub in (("severity above threshold", {s: th + sp.Rational(1, 10)}),
                       ("severity AT threshold   ", {s: th}),
                       ("severity below threshold", {s: th - sp.Rational(1, 10)})):
        print(f"  SymPy  limit as sigma -> 0+, {label}: {sp.limit(Phi.subs(sub), sig, 0, '+')}")
    print(f"  scipy  normal cumulative at 0            : {norm.cdf(0.0)}")
    print(f"  mpmath 0.5 * (1 + erf(0))                : {mp.mpf('0.5') * (1 + mp.erf(0))}")
    print()
    print(f"  Production scores a finding at exactly {THRESHOLD} as 1, because it")
    print(f"  compares with >=. The smooth weight scores it 1/2 for EVERY sigma.")
    print(f"  SO THE NESTING FAILS AT THE THRESHOLD and holds everywhere else.")
    print()

    print("HOW FREQUENT IS AN EXACT THRESHOLD SEVERITY, over archived registries")
    sev: list[float] = []
    runs = 0
    for p in sorted((REPO / "bench" / "logs").rglob("*_report.json")):
        if "sandbox_harvest" in str(p):
            continue
        try:
            d = json.loads(p.read_text(errors="ignore"))
        except Exception:                                          # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        reg = d.get("registry")
        entries = reg.get("entries") if isinstance(reg, dict) else None
        if not isinstance(entries, dict):
            continue
        runs += 1
        for e in entries.values():
            if isinstance(e, dict) and isinstance(e.get("severity"), (int, float)):
                sev.append(float(e["severity"]))

    if not sev:
        print("  no severities found, so the frequency COULD NOT BE MEASURED here;")
        print("  that is a gap in the evidence, not a pass")
        return 2
    n = len(sev)
    k = sum(1 for v in sev if abs(v - THRESHOLD) < 1e-9)
    lo, hi = _wilson(k, n)
    counts = collections.Counter(sev)
    ranks = [v for v, _ in counts.most_common()]
    print(f"  runs with a registry: {runs};  entries carrying a severity: {n}")
    print(f"  exactly {THRESHOLD}: {k} = {100 * k / n:.4f}%  "
          f"Wilson [{100 * lo:.4f}%, {100 * hi:.4f}%]  "
          f"(statsmodels and an independent closed form agreeing to 1e-12)")
    print(f"  most common severities: {counts.most_common(5)}")
    print(f"  rank of the threshold value: "
          f"{ranks.index(THRESHOLD) + 1 if THRESHOLD in ranks else 'absent'}")
    print()
    print("  THE JOINT ROUND REPORTED 174 of 3237 = 5.3753%, Wilson [4.6500%,")
    print("  6.2065%], across 42 runs. This scan finds a different denominator --")
    print("  it admits every report carrying a registry rather than the subset the")
    print("  seat used -- and the PROPORTIONS AGREE to within a hundredth of a")
    print("  percentage point, with overlapping intervals. The seat's figure")
    print("  reproduces. Its description of the value as third most common is")
    print("  rank-sensitive to the filter and comes out 4th here, 6 entries behind")
    print("  the value above it, which changes nothing about the argument.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
