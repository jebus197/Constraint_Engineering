# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 95e656fa6ae26e3d2a6db39f87491d31e8854b60b5ddd39f2f47af213bd3faff
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Measure the intra-round correlation of per-seat finding production.

WHY THIS EXISTS. The spurious-convergence factor for a shrinking roster moves by
7.7915x across a plausible correlation range
(`bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py`), and
this project has never measured the correlation. It is an EMPIRICAL quantity, not
one anyone has to assume: every archived report records, per round, which seats
answered and how many findings each produced.

WHAT IT DOES NOT DECIDE. The roster-scaled convergence window in
`bench/degraded_convergence_2026-10-07.py` does NOT depend on this number:
independence is the worst case (f(n) = -ln E[(1-p)^n] is concave through the
origin, so f(n_dec)/f(n_live) <= n_dec/n_live), and the window is derived from it.
Measuring rho can only RELAX that window. So this script sets how much the repair
over-corrects, and how urgent it was -- not whether it is correct.

THE ESTIMATOR. For each round r with n_r responding seats, let X_ri = 1 if seat i
produced at least one NEW CRITICAL finding that round. Treat the round as a
cluster. The intraclass correlation is estimated by the standard
method-of-moments / ANOVA estimator for binary clustered data (Fleiss 1981;
Ridout, Demetrio & Firth 1999, "Estimating intraclass correlation for binary
data", Biometrics 55:137-148):

    p_hat = sum_r sum_i X_ri / sum_r n_r
    MSB   = sum_r n_r (p_r - p_hat)^2 / (R - 1)        between-cluster
    MSW   = sum_r sum_i (X_ri - p_r)^2 / (N - R)       within-cluster
    rho   = (MSB - MSW) / (MSB + (n_0 - 1) MSW)

with n_0 = (N - sum_r n_r^2 / N) / (R - 1) the usual unequal-cluster-size
correction. A negative estimate is reported as measured and NOT clamped to 0,
because clamping hides the case where rounds are LESS alike than chance -- which
would mean the shrinking-roster factor is WORSE than the independence bound, and
is the one result that would refute the derivation's claim that independence is
the worst case.

Bootstrap over ROUNDS (the clusters), not over seats, because seats within a
round are the thing whose dependence is being estimated.

THE SEVERITY CAVEAT, STATED BECAUSE IT CHANGES THE ANSWER. The gate's count side
runs on NEW CRITICAL findings from the settled, verifier-filtered series. Archived
`rounds[*].per_model` records ALL-SEVERITY finding counts. Those are different
quantities and the all-severity correlation is an upper bound on nothing in
particular -- it is a DIFFERENT number, reported as such. A report carrying
per-seat novel-critical counts is what this script actually wants;
`--field` selects it where present.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random


def icc_binary(clusters):
    """Fleiss/ANOVA intraclass correlation for binary data in unequal clusters.

    `clusters` is a list of lists of 0/1. Returns (rho, p_hat, R, N, n_0).
    """
    clusters = [c for c in clusters if len(c) >= 2]
    R = len(clusters)
    if R < 2:
        return (float("nan"), float("nan"), R, 0, float("nan"))
    N = sum(len(c) for c in clusters)
    tot = sum(sum(c) for c in clusters)
    p_hat = tot / N
    n0 = (N - sum(len(c) ** 2 for c in clusters) / N) / (R - 1)
    msb = sum(len(c) * (sum(c) / len(c) - p_hat) ** 2 for c in clusters) / (R - 1)
    msw_num = sum(sum((x - sum(c) / len(c)) ** 2 for x in c) for c in clusters)
    msw = msw_num / (N - R) if N > R else 0.0
    den = msb + (n0 - 1) * msw
    rho = (msb - msw) / den if den != 0 else float("nan")
    return (rho, p_hat, R, N, n0)


def bootstrap_ci(clusters, reps=4000, seed=20261007, alpha=0.05):
    """Percentile CI, resampling ROUNDS (the clusters) with replacement."""
    rnd = random.Random(seed)
    vals = []
    n = len(clusters)
    for _ in range(reps):
        samp = [clusters[rnd.randrange(n)] for _ in range(n)]
        r = icc_binary(samp)[0]
        if not math.isnan(r):
            vals.append(r)
    if not vals:
        return (float("nan"), float("nan"))
    vals.sort()
    lo = vals[int(alpha / 2 * len(vals))]
    hi = vals[min(len(vals) - 1, int((1 - alpha / 2) * len(vals)))]
    return (lo, hi)


def clusters_from_report(path, field):
    """One cluster per round: [1 if seat produced >=1 finding else 0, ...].

    A seat that did NOT respond is EXCLUDED from its round's cluster rather than
    recorded as a 0. A seat that was never asked produced no findings for a
    transport reason, not a review reason, and scoring it 0 would manufacture
    exactly the correlation this script exists to measure.
    """
    try:
        d = json.load(open(path))
    except Exception:
        return []
    out = []
    for r in d.get("rounds", []) or []:
        if not isinstance(r, dict):
            continue
        per = r.get(field) or r.get("per_model") or {}
        if not isinstance(per, dict) or not per:
            continue
        responded = set(r.get("models_responded") or per.keys())
        cl = [1 if (per.get(m) or 0) > 0 else 0 for m in sorted(per) if m in responded]
        if len(cl) >= 2:
            out.append(cl)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="logs/**/*report*.json")
    ap.add_argument("--field", default="per_model_novel_critical",
                    help="per-seat NEW CRITICAL counts; falls back to per_model "
                         "(all-severity), which is a DIFFERENT quantity")
    a = ap.parse_args()

    paths = sorted(glob.glob(a.glob, recursive=True))
    clusters, used = [], []
    for p in paths:
        c = clusters_from_report(p, a.field)
        if c:
            clusters.extend(c)
            used.append((p, len(c)))

    print("== intra-round correlation of per-seat finding production ==")
    print(f"   reports matched : {len(paths)}")
    print(f"   reports usable  : {len(used)}")
    for p, n in used:
        print(f"      {n} round(s)  {p}")
    if len(clusters) < 2:
        print("   INSUFFICIENT DATA: fewer than 2 usable rounds.")
        print("   rho is UNMEASURED, and the roster-scaled window does not depend")
        print("   on it (independence is the worst case). Re-run against the full")
        print("   logs/ archive, not a staged subset.")
        return 2

    rho, p_hat, R, N, n0 = icc_binary(clusters)
    lo, hi = bootstrap_ci(clusters)
    print(f"   rounds (clusters) : {R}")
    print(f"   seat-rounds       : {N}")
    print(f"   mean n_0          : {n0:.4f}")
    print(f"   p_hat (seat-round production rate): {p_hat:.6f}")
    print(f"   rho_hat           : {rho:.6f}")
    print(f"   bootstrap 95% CI  : [{lo:.6f}, {hi:.6f}]  (resampling ROUNDS)")
    print()
    print("   READ THIS BEFORE QUOTING THE NUMBER:")
    print(f"   * {R} clusters is far too few for a usable interval; the CI above")
    print("     will be wide and should be reported with it, never alone.")
    if a.field == "per_model_novel_critical" and not any(
            "per_model_novel_critical" in json.dumps(json.load(open(p)))[:200000]
            for p, _ in used[:1]):
        print("   * the NEW-CRITICAL field was ABSENT, so this is the ALL-SEVERITY")
        print("     correlation. The gate's count side runs on new criticals. These")
        print("     are different quantities and this is NOT a substitute.")
    print("   * rho was NOT clamped. A negative estimate would mean rounds are less")
    print("     alike than chance, which is the one result that would refute the")
    print("     claim that independence bounds the shrinking-roster factor.")
    print()
    print("   WHAT TO RECORD GOING FORWARD, so this is measurable properly: write")
    print("   per-seat NOVEL CRITICAL counts into rounds[*].per_model_novel_critical")
    print("   alongside the existing all-severity per_model. One extra dict per")
    print("   round makes rho a measured quantity instead of an assumed one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
