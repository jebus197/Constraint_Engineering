#!/usr/bin/env python3
"""Is the introduction rate `b` estimable AT DETECTABLE SCOPE from data already on disk?

Panel round 4, Q4. fable (round 3) claimed YES: fit constant-plus-decay against
pure decay on the per-round novel-critical series, because at steady state
detections per round equal `b` exactly. cgpt/ds/cx said NO without a paired
action cohort. This script RUNS the fit fable named, on the archive fable named.

MODELS, per run, t = 0..T-1, n_t = novel critical findings in round t:
    M0 (pure decay)          n_t ~ Poisson(A * r^t)
    M1 (constant-plus-decay) n_t ~ Poisson(b + A * r^t)
M1 nests M0 at b=0. Because b sits on the boundary under H0, the LRT null
distribution is the 50:50 mixture chi2_0 : chi2_1 (Self & Liang 1987), so the
p-value is HALF the chi2_1 tail. Both fits are MLE; every optimiser result is
cross-checked by an independent coarse grid search sharing no code path.

SCOPE CAVEAT, stated up front: this estimates b at DETECTABLE scope only.
A flaw class with detection probability ~0 never enters n_t, so no fit on n_t
can see it. That is fable's own second claim and it is conceded, not contested.

Run:  python3 scripts/b_fit_novel_decay_2026-09-20.py
"""
from __future__ import annotations

import glob
import json
import os
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 60_000_000
MIN_LEN = 6  # a 2-vs-3 parameter comparison on <6 points is noise


def collect():
    out = []
    for f in sorted(glob.glob(str(ROOT / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > MAX_BYTES:
            continue
        try:
            d = json.load(open(f, errors="ignore"))
        except Exception:
            continue
        found = []

        def walk(o):
            if isinstance(o, dict):
                h = o.get("novel_critical_history")
                if isinstance(h, list) and h and all(isinstance(x, int) for x in h):
                    found.append(h)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(d)
        if found:
            out.append((Path(f).parent.name, max(found, key=len)))
    return out


def nll_m0(theta, n):
    A, r = theta
    if A < 0 or not (0.0 < r < 1.0):
        return 1e18
    lam = np.maximum(A * r ** np.arange(len(n)), 1e-12)
    return float(np.sum(lam - n * np.log(lam)))


def nll_m1(theta, n):
    b, A, r = theta
    if b < 0 or A < 0 or not (0.0 < r < 1.0):
        return 1e18
    lam = np.maximum(b + A * r ** np.arange(len(n)), 1e-12)
    return float(np.sum(lam - n * np.log(lam)))


def fit(n):
    n = np.asarray(n, float)
    starts0 = [[n[0] + 0.5, 0.7], [max(n.mean(), 0.5), 0.9], [n.max() + 1, 0.5]]
    starts1 = [[0.1, n[0] + 0.5, 0.7],
               [max(n[-3:].mean(), 0.01), max(n[0] - n[-3:].mean(), 0.5), 0.6],
               [n.mean() / 2 + 0.01, n.max() + 1, 0.5]]
    best0 = min((minimize(nll_m0, x0, args=(n,), method="Nelder-Mead",
                          options={"xatol": 1e-8, "fatol": 1e-10, "maxiter": 4000})
                 for x0 in starts0), key=lambda r: r.fun)
    best1 = min((minimize(nll_m1, x0, args=(n,), method="Nelder-Mead",
                          options={"xatol": 1e-8, "fatol": 1e-10, "maxiter": 4000})
                 for x0 in starts1), key=lambda r: r.fun)
    return best0, best1


def grid_check(n, nll, dims):
    """Independent coarse grid search: no optimiser, no shared path."""
    n = np.asarray(n, float)
    if dims == 2:
        pts = ((A, r) for A in np.linspace(0.1, n.max() + 5, 60)
               for r in np.linspace(0.05, 0.99, 60))
    else:
        pts = ((b, A, r) for b in np.linspace(0, max(n.mean(), 2), 25)
               for A in np.linspace(0.1, n.max() + 5, 25)
               for r in np.linspace(0.05, 0.99, 25))
    return min(nll(th, n) for th in pts)


def main() -> int:
    series = collect()
    long_runs = [(name, s) for name, s in series if len(s) >= MIN_LEN]
    print(f"Archived runs with novel_critical_history : {len(series)}")
    print(f"Runs with >= {MIN_LEN} rounds (fittable)       : {len(long_runs)}")
    print()
    print(f"{'run':46s} {'T':>3s} {'b_hat':>7s} {'p(LRT)':>8s} {'AIC0-AIC1':>9s} grid_ok")
    rows = []
    for name, s in long_runs:
        best0, best1 = fit(s)
        ll0, ll1 = -best0.fun, -best1.fun
        lrt = max(0.0, 2 * (ll1 - ll0))
        p = 0.5 * chi2.sf(lrt, df=1)  # boundary mixture
        d_aic = (2 * 2 + 2 * best0.fun) - (2 * 3 + 2 * best1.fun)
        g0 = grid_check(s, nll_m0, 2)
        g1 = grid_check(s, nll_m1, 3)
        ok = (best0.fun <= g0 + 1e-6) and (best1.fun <= g1 + 1e-6)
        b_hat = best1.x[0]
        rows.append((name, len(s), b_hat, p, d_aic, ok))
        print(f"{name:46s} {len(s):3d} {b_hat:7.3f} {p:8.4f} {d_aic:9.2f} {ok}")

    sig = [r for r in rows if r[3] < 0.05 and r[4] > 0]
    print()
    print(f"Runs where constant-plus-decay beats pure decay (p<0.05 AND AIC): "
          f"{len(sig)}/{len(rows)}")
    if sig:
        bs = sorted(r[2] for r in sig)
        print(f"b_hat over those runs: min={bs[0]:.3f} median={bs[len(bs)//2]:.3f} "
              f"max={bs[-1]:.3f}")
    print()
    print("Second instrument, tail mean of last 4 rounds (steady-state detections = b):")
    # STATE THE REMAINDER (2026-09-24). A list cut to 5 under a heading that reads
    # as complete is a silent falsehood: a reader cannot tell 5 runs from 50.
    _ranked = sorted(long_runs, key=lambda x: -len(x[1]))
    for name, s in _ranked[:5]:
        tail = s[-4:]
        print(f"  {name:46s} T={len(s):3d} tail={tail} mean={np.mean(tail):.2f}")
    if len(_ranked) > 5:
        print(f"  ... and {len(_ranked) - 5} further run(s) not shown, of {len(_ranked)} total")
    print()
    verdict = "ESTIMABLE" if sig else "NOT SEPARABLE ON THIS ARCHIVE"
    print(f"VERDICT at detectable scope: {verdict}")
    print("Scope caveat: undetectable classes never enter n_t (fable's own limit),")
    print("and b_hat counts NOVEL CRITICALS PER ROUND -- the detected part of")
    print("introduction only. It is an instrument, not the parameter.")
    return 0


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    raise SystemExit(main())
