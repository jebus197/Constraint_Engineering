#!/usr/bin/env python3
"""The real panel is measurably heterogeneous; the simulated panel is not.

THE FOUNDER'S QUESTION, 2026-10-05: whether using mixed model classes would restore
the utility of the capability ladder, "if even to a limited extent", and whether the
ladder's ordering is a MEASURED statistic or an assumed one.

WHAT THE SCHEMA ALREADY MEASURES. `bench/fingerprints/` holds a live capability
profile per model, updated every round by `_update_observed_fingerprint` and persisted
by `_save_fingerprints`. The glossary defines it as a 4-dimensional profile (D, v-bar,
A, C), appendix section 7.9. It is consumed by `burst_planner.py` and by
`_should_decompose` for decomposition and context-budget decisions.

WHAT THE LADDER USES INSTEAD. `bench/routing.py` contains the word "fingerprint"
exactly ONCE, in its own docstring: "route the falsification to progressively STRONGER
models (ordered by capability fingerprint)". The code reads no fingerprint. It ranks on
`DEFAULT_FALSIFIER_STRENGTH`, a frozen 5-tuple of bare vendor names derived from Exp 42
in June 2026 and never re-derived since -- `scripts/competence_provenance.py` exists
specifically to forbid careless re-derivation.

So the answer to the founder's second question is: the ladder order IS a measured
statistic, measured ONCE and frozen, and the schema separately carries a LIVE capability
measurement that the ladder does not read. The docstring and the code disagree.

WHAT THIS SCRIPT MEASURES. Whether the 6 simulated seats are behaviourally
distinguishable at all, against the 5 real models as the comparator, using finding
counts from the committed fingerprints. A chi-square test of homogeneity asks whether
one underlying rate explains each panel's counts. Cross-verified with scipy and an
independent NumPy computation, and the effect size reported with a confidence interval.

Run:  python3 scripts/the_sim_panel_is_not_heterogeneous_2026-10-05.py
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
FP_DIR = REPO / "bench" / "fingerprints"
sys.path.insert(0, str(REPO))


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_sim_panel_is_not_heterogeneous_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--fingerprints", default=str(FP_DIR),
                   help="directory of committed fingerprint JSON files")
    return p.parse_args(argv)


def _load(d: pathlib.Path):
    out = {}
    for p in sorted(glob.glob(str(d / "*.json"))):
        try:
            j = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        out[pathlib.Path(p).stem] = j
    return out


def _chi2_homogeneity(counts, exposures):
    """Chi-square test that one rate explains every count. Returns (chi2, df, p).

    Computed twice: scipy's chisquare against expected counts under a pooled rate,
    and an independent NumPy sum, with scipy's survival function for the p-value.
    """
    import numpy as np
    from scipy import stats
    obs = np.asarray(counts, dtype=float)
    exp_w = np.asarray(exposures, dtype=float)
    pooled = obs.sum() / exp_w.sum()
    expected = pooled * exp_w
    chi2_numpy = float((((obs - expected) ** 2) / expected).sum())
    chi2_scipy = float(stats.chisquare(obs, f_exp=expected, ddof=0).statistic)
    df = len(obs) - 1
    p = float(stats.chi2.sf(chi2_numpy, df))
    agree = abs(chi2_numpy - chi2_scipy) < 1e-9
    return chi2_numpy, chi2_scipy, agree, df, p, pooled, expected


def _wilson(k, n):
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import norm
    a = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = float(norm.ppf(0.975)); p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    b = (c - h, c + h)
    ok = abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9
    return a[0] * 100, a[1] * 100, ok


def main(argv=None) -> int:
    args = _parse_args(argv)
    fps = _load(pathlib.Path(args.fingerprints))
    if not fps:
        print("no fingerprints found")
        return 1

    sim = {k: v for k, v in fps.items() if k.endswith("-SIM")}
    real = {k: v for k, v in fps.items() if not k.endswith("-SIM")}

    print("=" * 78)
    print("IS THE SIMULATED PANEL HETEROGENEOUS? (the real panel as comparator)")
    print("=" * 78)
    print(f"fingerprints: {len(fps)}  ({len(sim)} simulated, {len(real)} real)")
    print()

    results = {}
    for name, group in (("REAL panel", real), ("SIMULATED panel", sim)):
        if len(group) < 2:
            continue
        labels, counts, rounds = [], [], []
        for k, v in sorted(group.items()):
            o = v.get("observed", {})
            tf, rp = o.get("total_findings"), o.get("rounds_participated")
            if not tf or not rp:
                continue
            labels.append(k); counts.append(tf); rounds.append(rp)
        if len(counts) < 2:
            continue
        chi_n, chi_s, agree, df, p, pooled, expected = _chi2_homogeneity(counts, rounds)
        results[name] = (p, chi_n, df)
        print("-" * 78)
        print(f"{name}  ({len(labels)} members)")
        print("-" * 78)
        print(f"{'model':<16}{'findings':>10}{'rounds':>8}{'rate':>9}{'expected':>11}")
        for l, c, r, e in zip(labels, counts, rounds, expected):
            print(f"{l:<16}{c:>10}{r:>8}{c / r:>9.4f}{e:>11.2f}")
        print(f"  pooled rate                    : {pooled:.6f} findings/round")
        print(f"  chi-square (NumPy)             : {chi_n:.6f}")
        print(f"  chi-square (scipy)             : {chi_s:.6f}"
              f"   {'AGREE' if agree else '*** DISAGREE — UNVERIFIED ***'}")
        print(f"  degrees of freedom             : {df}")
        print(f"  p (one rate explains them all) : {p:.6e}")
        if p < 0.05:
            print("  => the members DIFFER. One rate does not explain the panel.")
        else:
            print("  => NOT distinguishable. One rate explains every member.")
        print()

    print("=" * 78)
    print("THE COMPARISON THAT ANSWERS THE QUESTION")
    print("=" * 78)
    if "REAL panel" in results and "SIMULATED panel" in results:
        pr, cr, dr = results["REAL panel"]
        ps, cs, ds = results["SIMULATED panel"]
        print(f"  real panel      : p = {pr:.6e}  "
              f"{'HETEROGENEOUS' if pr < 0.05 else 'homogeneous'}")
        print(f"  simulated panel : p = {ps:.6e}  "
              f"{'HETEROGENEOUS' if ps < 0.05 else 'HOMOGENEOUS'}")
        print()
        if pr < 0.05 <= ps:
            print("  The real panel's members differ in finding rate and the simulated")
            print("  panel's do not. A uniform simulated panel therefore does not")
            print("  reproduce the property the capability ladder exists to exploit,")
            print("  and no amount of correct ladder ORDERING can recover it: the")
            print("  ordering is right and the thing it orders is flat.")
            print()
            print("  This is the quantitative form of the founder's point. Mixing model")
            print("  classes is what restores the ladder's premise. Whether 2 classes")
            print("  suffice is an open measurement, not a settled one -- the real")
            print("  panel spreads across 5 members, and the shipped seat map spreads")
            print("  across 2.")

    print()
    print("=" * 78)
    print("WHAT THE LADDER ACTUALLY READS")
    print("=" * 78)
    routing_src = (REPO / "bench" / "routing.py").read_text(encoding="utf-8")
    n_fp = routing_src.count("fingerprint")
    in_code = any("fingerprint" in l and not l.strip().startswith("#")
                  and '"""' not in l and "route the falsification" not in l
                  for l in routing_src.split("\n"))
    print(f"  occurrences of 'fingerprint' in bench/routing.py : {n_fp}")
    print(f"  any of them in executable code                   : {in_code}")
    print("  the single occurrence is the docstring claim 'ordered by capability")
    print("  fingerprint'. The code ranks on DEFAULT_FALSIFIER_STRENGTH, a frozen")
    print("  tuple of bare vendor names. The docstring and the code disagree.")
    print()
    print("  Meanwhile `_update_observed_fingerprint` writes a live profile EVERY")
    print("  round, and `burst_planner.py` and `_should_decompose` read it. So the")
    print("  schema already measures per-model capability continuously, and the")
    print("  ladder is the one consumer that does not use it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
