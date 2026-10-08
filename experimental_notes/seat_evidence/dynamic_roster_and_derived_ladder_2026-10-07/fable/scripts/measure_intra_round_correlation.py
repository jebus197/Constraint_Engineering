# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4e14b113b64aeffec423614e6c2b007ff9f5518f9cd0c64cbc6014282560e770
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Measure the intra-round correlation of per-seat critical production from the
archive -- the parameter the 2026-10-07 hazard analysis flags as never measured.

The quantity: within a round every seat receives a byte-identical brief, so
whether seat s produces >= 1 critical-severity finding in round r is plausibly
correlated across seats. The spurious-convergence fold 8.49986 (6 seats -> 4)
assumes independence; the fold at the TRUE correlation is what sets the
urgency of the degradation-aware gate (not its necessity -- z3 settles that).

Data: every archived report whose `rounds[*]` carry both `models_responded`
and per-finding `model_id` + `severity` (31 such reports found 2026-10-08).
X[r,s] = 1 iff seat s produced >= 1 finding with severity >=
CRITICAL_SEVERITY_THRESHOLD (0.7, the runner's operational threshold) in round
r. Rounds with < 2 responders are uninformative for a within-round statistic
and are skipped, and that skip is logged, not silent.

Estimator: the one-way ANOVA intraclass correlation ICC(1) over rounds as
groups (unbalanced form with k0 the mean-square group size correction),
pooled across runs; a pairwise-phi average is printed beside it as a second,
model-free view. Negative estimates are reported as computed -- clamping would
manufacture the favourable answer.
"""
from __future__ import annotations

import glob
import json
import os
import sys

CRITICAL_SEVERITY_THRESHOLD = 0.7   # mirrors bench/reference_runner_v3.py:8301


def harvest(root: str = "bench/logs"):
    rows, skipped_rounds, reports = [], 0, 0
    for p in sorted(glob.glob(os.path.join(root, "**", "*.json"), recursive=True)):
        try:
            if os.path.getsize(p) > 20_000_000:
                continue
            with open(p) as f:
                d = json.load(f)
        except Exception:
            continue
        rounds = d.get("rounds") if isinstance(d, dict) else None
        if not (isinstance(rounds, list) and rounds
                and isinstance(rounds[0], dict)
                and "models_responded" in rounds[0]):
            continue
        reports += 1
        for r in rounds:
            seats = sorted(set(r.get("models_responded") or []))
            if len(seats) < 2:
                skipped_rounds += 1
                continue
            crit_by_seat = {s: 0 for s in seats}
            for fnd in (r.get("findings") or []):
                m = fnd.get("model_id") or fnd.get("model")
                if m in crit_by_seat and (fnd.get("severity") or 0.0) >= \
                        CRITICAL_SEVERITY_THRESHOLD:
                    crit_by_seat[m] = 1
            rows.append((p, r.get("round"), [crit_by_seat[s] for s in seats]))
    return rows, skipped_rounds, reports


def icc1(groups):
    """One-way ANOVA ICC(1), unbalanced. groups: list of lists of 0/1."""
    N = sum(len(g) for g in groups)
    K = len(groups)
    if K < 2 or N <= K:
        return None
    grand = sum(sum(g) for g in groups) / N
    ssb = sum(len(g) * (sum(g) / len(g) - grand) ** 2 for g in groups)
    ssw = sum(sum((x - sum(g) / len(g)) ** 2 for x in g) for g in groups)
    msb = ssb / (K - 1)
    msw = ssw / (N - K)
    k0 = (N - sum(len(g) ** 2 for g in groups) / N) / (K - 1)
    denom = msb + (k0 - 1) * msw
    return (msb - msw) / denom if denom else None


def pairwise_phi(groups):
    """Mean product-moment correlation over all within-round seat pairs,
    computed on the pooled pair observations (x_i, x_j)."""
    import itertools
    xs, ys = [], []
    for g in groups:
        for a, b in itertools.combinations(g, 2):
            xs.append(a), ys.append(b)
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    vx = sum((x - mx) ** 2 for x in xs) / n
    vy = sum((y - my) ** 2 for y in ys) / n
    return cov / (vx * vy) ** 0.5 if vx and vy else None


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "bench/logs"
    rows, skipped, reports = harvest(root)
    groups = [g for _, _, g in rows]
    print(f"reports with usable rounds: {reports}")
    print(f"rounds used: {len(groups)}   rounds skipped (<2 responders): {skipped}")
    if not groups:
        print("no data -- cannot estimate; this is the honest null result")
        return 1
    rate = sum(sum(g) for g in groups) / sum(len(g) for g in groups)
    print(f"per-seat-per-round P(>=1 critical): {rate:.4f} "
          f"(the hazard analysis assumed 0.3)")
    r_icc = icc1(groups)
    r_phi = pairwise_phi(groups)
    print(f"ICC(1) intra-round correlation: "
          f"{'undefined' if r_icc is None else round(r_icc, 4)}")
    print(f"pairwise-phi (second view):     "
          f"{'undefined' if r_phi is None else round(r_phi, 4)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
