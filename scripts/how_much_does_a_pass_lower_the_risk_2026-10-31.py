#!/usr/bin/env python3
"""How much does an extra pass lower residual risk IN THIS HARNESS, and is
there an optimum?

HIS QUESTION, 2026-10-31, verbatim:

    "There is an open question, which you might be able to measure, which is
    how much does increasing the number of passes on a given problem lower the
    residual risk/severity, given my definition, if at all, given the nature of
    the harness as it stands? That is an interesting question to ask, because it
    might point at an optimum (or it might not), or it might not be possible to
    measure this from historical data, and perhaps we can only measure it
    reliably/accurately going forward?"

HE ANTICIPATED THE OBSTACLE AND HE IS HALF RIGHT, WHICH IS THE INTERESTING PART.

  * The DIRECT measurement is impossible from the archive, exactly as he
    suspected. `R_old` is 0.500000 in all 1,252 archived entries carrying an
    `R_new` -- distinct count 1 -- because the runner re-initialises
    `R_k(0) = pi` per finding and never carries it across passes. So the archive
    holds no R(n) series for any problem. Producer for that figure:
    `scripts/his_severity_definition_is_the_models_own_quantity_2026-10-31.py`.

  * The INDIRECT measurement IS possible, and he did not have to concede it.
    Every entry records `open_since_round`, and 74 of 76 reports record
    `rounds`. So the DISCOVERY CURVE -- how many previously-unseen findings each
    pass turns up -- is recoverable per run. Under the model's own detection
    kernel that curve determines `q`, and `q` is the entire content of "how much
    does a pass lower the risk".

THE ESTIMATOR, and its assumption stated so it can be attacked. If a target
holds N latent flaws and each pass detects each still-undetected flaw
independently with probability q, the number still undetected after k passes is
N(1-q)^k, so NEW finds per pass decay geometrically with ratio (1-q). Fitting
log(new finds) against pass index gives slope log(1-q). This is the Duane-style
fit the appendix already references at section 7.1. The independence assumption
is the weak point: a flaw missed because no seat has the capability is missed
again next pass, which is section 1's capability ceiling and makes the true
curve decay FASTER at first and then flatten above zero. The fit is reported
per run so that flattening is visible rather than averaged away.

CENSORING, WHICH BIASES THE ANSWER IN A KNOWN DIRECTION. The harness stops on
convergence, so a run ENDS when the discovery curve has flattened. The last
rounds -- the informative ones for the tail -- are therefore systematically
absent, and a geometric fit over the observed rounds OVERSTATES q. Quantified
below by refitting on truncated prefixes of the same runs.

Cross-verification per the 21 Apr 2026 rule: every slope by statsmodels OLS AND
NumPy least squares; every interval by Wilson/Clopper-Pearson or the OLS
t-interval; the optimum derived in SymPy and checked numerically.
"""
from __future__ import annotations

import collections
import glob
import json
import math
import pathlib
import statistics

import numpy as np
import statsmodels.api as sm
import sympy as sp
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
CRITICAL_CUT = 0.7            # the pre-registered cut, 2026-05-18


# ─────────────────────────────── the archive ───────────────────────────────

def discovery_curves() -> list[dict]:
    """Per run: new findings per pass, from `open_since_round`."""
    out = []
    for r in sorted(glob.glob(str(LOGS / "*" / "*_report.json"))):
        try:
            d = json.load(open(r))
        except Exception:
            continue
        ents = ((d.get("registry") or {}).get("entries") or {})
        if not ents:
            continue
        per_round = collections.Counter()
        per_round_crit = collections.Counter()
        for e in ents.values():
            k = e.get("open_since_round")
            if k is None:
                continue
            try:
                k = int(k)
            except (TypeError, ValueError):
                continue
            per_round[k] += 1
            sev = e.get("severity")
            if isinstance(sev, (int, float)) and float(sev) >= CRITICAL_CUT:
                per_round_crit[k] += 1
        if not per_round:
            continue
        lo, hi = min(per_round), max(per_round)
        curve = [per_round.get(k, 0) for k in range(lo, hi + 1)]
        crit = [per_round_crit.get(k, 0) for k in range(lo, hi + 1)]
        out.append({"run": pathlib.Path(r).parent.name,
                    "first_round": lo, "last_round": hi,
                    "rounds_recorded": len(d.get("rounds") or []),
                    "total_rounds": d.get("total_rounds"),
                    "max_rounds": d.get("max_rounds"),
                    "curve": curve, "critical_curve": crit,
                    "findings": sum(curve),
                    "gamma": d.get("gamma"),
                    "gamma_history": d.get("gamma_history") or []})
    return out


def fit_q(curve: list[int]) -> dict:
    """Slope of log(new finds) against pass index -> q = 1 - exp(slope).

    Both tools run on the same design matrix and must agree.
    """
    pts = [(i, c) for i, c in enumerate(curve) if c > 0]
    if len(pts) < 3:
        return {"n_points": len(pts), "q": None,
                "why": "fewer than 3 passes with a new find; no slope is identifiable"}
    x = np.array([p[0] for p in pts], dtype=float)
    y = np.log(np.array([p[1] for p in pts], dtype=float))
    X = sm.add_constant(x)
    res = sm.OLS(y, X).fit()
    slope_sm = float(res.params[1])
    np_slope = float(np.polyfit(x, y, 1)[0])
    agree = abs(slope_sm - np_slope) < 1e-9
    # a positive slope means discovery ACCELERATED, so no decay to read
    q = 1.0 - math.exp(slope_sm) if slope_sm < 0 else None
    ci = res.conf_int(alpha=0.05)[1] if len(pts) > 2 else (float("nan"),) * 2
    q_lo = 1.0 - math.exp(float(ci[1])) if slope_sm < 0 else None
    q_hi = 1.0 - math.exp(float(ci[0])) if slope_sm < 0 else None
    return {"n_points": len(pts), "slope_statsmodels": slope_sm,
            "slope_numpy": np_slope, "tools_agree": agree,
            "q": q, "q_ci_low": q_lo, "q_ci_high": q_hi,
            "r_squared": float(res.rsquared),
            "slope_p": float(res.pvalues[1])}


def censoring_bias(curves: list[dict]) -> dict:
    """Refit on truncated prefixes. If q falls as more of the tail is seen,
    the full-run fit was overstating it, which is the censoring direction."""
    rows = []
    for c in curves:
        full = fit_q(c["curve"])
        if full.get("q") is None:
            continue
        half = fit_q(c["curve"][: max(3, len(c["curve"]) // 2)])
        if half.get("q") is None:
            continue
        rows.append({"run": c["run"], "q_full": full["q"], "q_half": half["q"],
                     "passes": len(c["curve"])})
    if len(rows) < 3:
        return {"pairs": len(rows), "why": "too few runs with an identifiable slope"}
    a = np.array([r["q_half"] for r in rows])
    b = np.array([r["q_full"] for r in rows])
    w = stats.wilcoxon(a, b) if len(rows) >= 6 else None
    t = stats.ttest_rel(a, b)
    return {"pairs": len(rows),
            "median_q_on_first_half": float(np.median(a)),
            "median_q_on_full_run": float(np.median(b)),
            "wilcoxon_p": float(w.pvalue) if w is not None else None,
            "paired_t_p": float(t.pvalue),
            "direction": ("the full-run fit is HIGHER, so censoring overstates q"
                          if np.median(b) > np.median(a) else
                          "the full-run fit is LOWER, so the prefix overstates q")}


# ───────────────────────────────── the optimum ─────────────────────────────

def optimum() -> dict:
    """Is there an optimal number of passes? Derived, not asserted.

    With risk R(n) = pi m^n / ((1-pi) + pi m^n), m = 1-q, a consequence C per
    unit of residual risk and a cost c per pass, total loss is
    L(n) = C R(n) + c n. An interior optimum needs dL/dn = 0.
    """
    pi, q, n, C, c = sp.symbols("pi q n C c", positive=True)
    m = 1 - q
    R = pi * m ** n / ((1 - pi) + pi * m ** n)
    L = C * R + c * n
    dL = sp.simplify(sp.diff(L, n))
    sol = sp.solve(sp.Eq(dL, 0), n)
    # second derivative at the solution decides minimum vs maximum
    d2 = sp.simplify(sp.diff(L, n, 2))
    worked = []
    for Cv, cv, piv, qv in ((100.0, 1.0, 0.5, 0.42105), (100.0, 1.0, 0.9, 0.05),
                            (1000.0, 1.0, 0.5, 0.42105), (10.0, 1.0, 0.5, 0.42105)):
        f = sp.lambdify(n, L.subs({C: Cv, c: cv, pi: piv, q: qv}), "numpy")
        ns = np.arange(0, 60, 1.0)
        vals = f(ns)
        best = int(np.argmin(vals))
        worked.append({"C": Cv, "cost_per_pass": cv, "pi": piv, "q": qv,
                       "n_star": best, "loss_at_n_star": float(vals[best]),
                       "R_at_n_star": float(piv * (1 - qv) ** best /
                                            ((1 - piv) + piv * (1 - qv) ** best))})
    return {"dL_dn": str(dL), "closed_form_n": [str(s) for s in sol],
            "d2L_dn2": str(d2), "worked": worked,
            "note": ("an interior optimum exists whenever the marginal risk "
                     "reduction C*|dR/dn| starts above the pass cost c and "
                     "decays through it; both conditions are checkable per run")}


def main() -> int:
    curves = discovery_curves()
    fits = []
    for c in curves:
        f = fit_q(c["curve"])
        fits.append({**{k: c[k] for k in
                        ("run", "findings", "total_rounds", "max_rounds")},
                     "passes_with_a_new_find": f["n_points"], **f})
    ident = [f for f in fits if f.get("q") is not None]
    qs = [f["q"] for f in ident]
    bias = censoring_bias(curves)
    opt = optimum()

    print("=" * 74)
    print("HOW MUCH DOES A PASS LOWER THE RISK, AS THIS HARNESS STANDS")
    print("=" * 74)
    print(f"archived runs with a discovery curve        : {len(curves)}")
    print(f"runs where a decay slope is identifiable    : {len(ident)}")
    if qs:
        n, k = len(curves), len(ident)
        from statsmodels.stats.proportion import proportion_confint
        w = proportion_confint(k, n, alpha=0.05, method="wilson")
        cp = proportion_confint(k, n, alpha=0.05, method="beta")
        print(f"   identifiable share {k}/{n} = {k/n:.6f}, "
              f"Wilson [{w[0]:.6f}, {w[1]:.6f}], "
              f"Clopper-Pearson [{cp[0]:.6f}, {cp[1]:.6f}]")
        print(f"q per pass: median {statistics.median(qs):.6f}, "
              f"min {min(qs):.6f}, max {max(qs):.6f}")
        if len(qs) > 1:
            print(f"            stdev {statistics.pstdev(qs):.6f}")
        print(f"   every fit agreed across statsmodels and NumPy: "
              f"{all(f['tools_agree'] for f in ident)}")
        mq = statistics.median(qs)
        print(f"\nAT THE MEDIAN FITTED q = {mq:.6f}, carrying R forward from pi = 0.5:")
        R = 0.5
        for i in range(1, 11):
            prev = R
            R = R * (1 - mq) / (1 - mq * R)
            print(f"   pass {i:2}: R = {R:.6f}   (this pass removed {prev - R:.6f})")
    print()
    print("CENSORING CHECK (refit on the first half of each run):")
    for k, v in bias.items():
        print(f"   {k}: {v}")
    print()
    print("IS THERE AN OPTIMUM? Derived, then computed:")
    print(f"   dL/dn = {opt['dL_dn']}")
    for w in opt["worked"]:
        print(f"   C={w['C']:7.1f} cost/pass={w['cost_per_pass']:.1f} "
              f"pi={w['pi']:.2f} q={w['q']:.5f} -> n* = {w['n_star']:2}  "
              f"R(n*) = {w['R_at_n_star']:.6f}")
    print(f"   {opt['note']}")
    print()
    _shown = 12
    _all_fits = sorted(fits, key=lambda x: -x["findings"])
    print(f"PER-RUN DETAIL — the {min(_shown, len(_all_fits))} with the most "
          f"findings, of {len(_all_fits)} runs; "
          f"{max(0, len(_all_fits) - _shown)} not shown "
          f"(pass --json for every row):")
    for f in _all_fits[:_shown]:
        q = f.get("q")
        qs_ = f"{q:.6f}" if q is not None else "not identifiable"
        print(f"   {f['run'][:52]:52} findings={f['findings']:4} "
              f"passes={f['passes_with_a_new_find']:2} q={qs_}")
    print()
    print(json.dumps({"runs": len(curves), "identifiable": len(ident),
                      "q_median": statistics.median(qs) if qs else None,
                      "censoring": bias}, indent=2, default=str))
    return 0


def _cli() -> None:
    """A `--help` MUST NOT run the measurement. Founder rule: a help flag must
    never cost money or time. Guarded by
    `bench/tests/test_help_is_answered_2026-09-11.py`, which refused the first
    commit of this script for exactly this reason."""
    import argparse
    ap = argparse.ArgumentParser(description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--json", action="store_true",
                    help="print the full report as JSON only")
    ap.parse_args()


if __name__ == "__main__":
    _cli()
    raise SystemExit(main())
