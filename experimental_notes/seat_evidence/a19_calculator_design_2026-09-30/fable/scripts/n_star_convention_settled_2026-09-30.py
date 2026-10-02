# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 23581c0e05b4b41cc3461b9d07a6422466ea31251f11071a4945170b9450cd28
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q6 of the 2026-09-30 A19 calculator brief: settle n* = (a/theta)^(1/gamma).

THE QUESTION. A prior round reported that `_estimate_gamma` fits the CUMULATIVE
curve, making n* = (a(1-gamma)/theta)^(1/gamma) = 1.6447 rather than 9.3805,
but could not locate the fitting code to decide whether a = 4.89 is a
cumulative or a rate coefficient.

THE FITTING CODE IS FOUND AND EXECUTED HERE: `bench/decay_analysis.py`, whose
`fit_duane` fits `_duane_cumulative(n, alpha, gamma) = alpha * n**gamma` to
`np.cumsum(rounds_data)` with scipy curve_fit, and whose own line ~176 states
the intensity `lambda(n) = alpha*gamma*n^(gamma-1)`. So in the ONLY code in
this repository that produces an `a` at all:

    * `alpha` IS A CUMULATIVE COEFFICIENT: N(1) = alpha (predicted cumulative
      findings after round 1), NOT a rate coefficient.
    * `gamma` THERE IS THE CUMULATIVE EXPONENT gamma_d, where the RUNNER's
      `_estimate_gamma` (reference_runner_v3.py:3190) returns gamma_r = 1 - beta
      for the SAME beta. The two "gammas" in this project are OPPOSITE
      conventions: gamma_r = 1 - gamma_d.

WHAT THIS SCRIPT EXECUTES
  CHK-1  reproduce the archived fit (alpha=4.8969, gamma_d=0.7417) from its own
         rounds_data [5,3,3,3,2] with scipy curve_fit; cross-check with sympy
         and mpmath.
  CHK-2  show alpha is cumulative: fitted N(1) = alpha.
  CHK-3  run the RUNNER's `_estimate_gamma` on the same series and show it
         returns approximately 1 - gamma_d, i.e. the OTHER convention.
  CHK-4  sweep the whole decay_analysis.json for any single fit pairing
         (4.89 +/- 0.01, 0.709 +/- 0.01): the master-list pair does not exist
         as one record, so its provenance is mixed.
  CHK-5  the three n* candidates, sympy AND mpmath:
           claimed  (a/th)^(1/g)            = 9.3805   solves th = a*n^-g,
                    a RATE model no fitter in this repo produces;
           CC2      (a(1-g)/th)^(1/g)       = 1.6447   correct ONLY if g is
                    runner-convention (rate exponent g_r = 0.709);
           decay    (a*g/th)^(1/(1-g))      = 71.7...  correct if g is the
                    decay-convention cumulative exponent g_d = 0.709.
  CHK-6  the data refute 1.6447 empirically: the series that carries
         alpha=4.8969 still yields 2 novel findings in round 5.

Writes nothing. Runs in seconds. No model dispatched.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import numpy as np                                   # noqa: E402
import sympy as sp                                   # noqa: E402
from mpmath import mp, mpf                           # noqa: E402
from scipy.optimize import curve_fit                 # noqa: E402

mp.dps = 30

DECAY = REPO / "bench/results/round_robin_phase2/decay_analysis.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    failures = 0

    def check(label, ok):
        nonlocal failures
        print(("PASS  " if ok else "FAIL  ") + label)
        if not ok:
            failures += 1

    d = json.loads(DECAY.read_text())

    # ---- CHK-1: reproduce the archived fit from its own data ---------------
    rec = d["per_task"][51]["models"]["deepseek"]
    rounds = rec["rounds_data"]
    want_a = rec["duane"]["params"]["alpha"]
    want_g = rec["duane"]["params"]["gamma"]
    cum = np.cumsum(rounds).astype(float)
    x = np.arange(1, len(cum) + 1, dtype=float)
    popt, _ = curve_fit(lambda n, a, g: a * np.power(n, g), x, cum,
                        p0=[cum[-1], 0.5], maxfev=10000)
    a_fit, g_fit = float(popt[0]), float(popt[1])
    print(f"CHK-1 rounds_data={rounds} cumulative={cum.tolist()}")
    print(f"      archived (alpha, gamma_d) = ({want_a}, {want_g})")
    print(f"      re-fit   (alpha, gamma_d) = ({a_fit:.4f}, {g_fit:.4f})")
    check("archived Duane fit reproduces to 4 dp",
          abs(a_fit - want_a) < 5e-4 and abs(g_fit - want_g) < 5e-4)

    # ---- CHK-2: alpha is the CUMULATIVE coefficient ------------------------
    n1_pred = a_fit * 1.0 ** g_fit
    print(f"CHK-2 fitted N(1) = alpha = {n1_pred:.4f}; observed cumsum[0] = {cum[0]}")
    check("alpha = fitted CUMULATIVE at round 1 (a cumulative coefficient, "
          "not a rate coefficient)", abs(n1_pred - a_fit) < 1e-12)

    # ---- CHK-3: the runner's gamma is the OPPOSITE convention --------------
    from reference_runner_v3 import _estimate_gamma
    g_runner = _estimate_gamma(list(rounds), min_rounds=3)
    print(f"CHK-3 runner _estimate_gamma(same series) = {g_runner:.4f}; "
          f"1 - gamma_d(curve_fit) = {1 - g_fit:.4f}")
    check("runner gamma sits near 1-gamma_d and far from gamma_d: the two "
          "conventions are opposite", abs(g_runner - (1 - g_fit)) < 0.15
          and abs(g_runner - g_fit) > 0.25)

    # ---- CHK-4: the pair (4.89, 0.709) exists in NO single fit -------------
    pairs = []
    for t in d["per_task"]:
        for mname, m in t["models"].items():
            p = (m.get("duane") or {}).get("params") or {}
            if "alpha" in p:
                pairs.append((p["alpha"], p["gamma"], t["task_id"], mname))
    hits = [p for p in pairs if abs(p[0] - 4.89) < 0.01 and abs(p[1] - 0.709) < 0.01]
    near_a = [p for p in pairs if abs(p[0] - 4.89) < 0.01]
    near_g = [p for p in pairs if abs(p[1] - 0.709) < 0.01]
    print(f"CHK-4 fits scanned: {len(pairs)}; pairing both 4.89 and 0.709: "
          f"{len(hits)}")
    print(f"      alpha~4.89 alone: {[(p[2], p[3], p[0], p[1]) for p in near_a]}")
    print(f"      gamma~0.709 alone: {[(p[2], p[3], p[0], p[1]) for p in near_g]}")
    check("the master-list pair (a=4.89, gamma=0.709) is NOT a single archived "
          "fit -- its two halves come from different records", len(hits) == 0)

    # ---- CHK-5: the three n* candidates, 2 tools each -----------------------
    a_s, g_s, th = sp.Rational(489, 100), sp.Rational(709, 1000), sp.Integer(1)
    cand = {
        "claimed (a/th)^(1/g)": (a_s / th) ** (1 / g_s),
        "CC2 (a(1-g)/th)^(1/g)": (a_s * (1 - g_s) / th) ** (1 / g_s),
        "decay-correct (a*g/th)^(1/(1-g))": (a_s * g_s / th) ** (1 / (1 - g_s)),
    }
    ref = {"claimed (a/th)^(1/g)": "9.3805",
           "CC2 (a(1-g)/th)^(1/g)": "1.6447",
           "decay-correct (a*g/th)^(1/(1-g))": None}
    a_m, g_m = mpf("4.89"), mpf("0.709")
    m_vals = {
        "claimed (a/th)^(1/g)": a_m ** (1 / g_m),
        "CC2 (a(1-g)/th)^(1/g)": (a_m * (1 - g_m)) ** (1 / g_m),
        "decay-correct (a*g/th)^(1/(1-g))": (a_m * g_m) ** (1 / (1 - g_m)),
    }
    for k, v in cand.items():
        v_sp = float(sp.N(v, 20))
        v_mp = float(m_vals[k])
        print(f"CHK-5 {k} = {v_sp:.4f} (sympy) / {v_mp:.4f} (mpmath)")
        check(f"sympy == mpmath for {k}", abs(v_sp - v_mp) < 1e-9)
        if ref[k]:
            check(f"reproduces the prior round's {ref[k]}",
                  abs(v_sp - float(ref[k])) < 5e-4)
    # Verify by SUBSTITUTION (symbolic solve on n^(709/1000) would expand a
    # degree-1000 polynomial): each candidate must zero its own equation.
    n = sp.Symbol("n", positive=True)
    rate_decay = sp.diff(a_s * n ** g_s, n)            # a*g*n^(g-1)
    resid1 = sp.N(rate_decay.subs(n, cand["decay-correct (a*g/th)^(1/(1-g))"]) - th, 30)
    check("substituting (a*g/th)^(1/(1-g)) into d/dn[a*n^g] = theta zeroes it",
          abs(float(resid1)) < 1e-20)
    rate_claimed = a_s * n ** (-g_s)                   # the model the claimed
    resid2 = sp.N(rate_claimed.subs(n, cand["claimed (a/th)^(1/g)"]) - th, 30)
    check("substituting (a/th)^(1/g) into a*n^-g = theta zeroes it  [a RATE "
          "model NO fitter in this repo produces]", abs(float(resid2)) < 1e-20)
    resid3 = sp.N(rate_decay.subs(n, cand["claimed (a/th)^(1/g)"]) - th, 30)
    check("the claimed 9.3805 does NOT satisfy the fitted model's own "
          "stopping equation (residual is far from 0)", abs(float(resid3)) > 0.5)

    # ---- CHK-6: the fit's own data refute n* = 1.6447 -----------------------
    print(f"CHK-6 marginal novelty by round for the alpha=4.8969 series: {rounds}")
    check("round 5 still yields >= 2 novel findings, so 'marginal < 1/round "
          "after 1.64 rounds' is false on the fit's own data",
          rounds[4] >= 2)
    n_star_fit = (a_fit * g_fit) ** (1 / (1 - g_fit))
    lam5 = a_fit * g_fit * 5 ** (g_fit - 1)
    print(f"      fitted intensity at n=5: {lam5:.4f}/round (observed 2); "
          f"intensity reaches 1/round at n = {n_star_fit:.1f}")
    check("fitted intensity at the last observed round is still > 1/round, "
          "consistent with the correct n* being far beyond 10", lam5 > 1.0)

    print(f"\n{'ALL CHECKS PASS' if failures == 0 else str(failures) + ' CHECK(S) FAILED'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
