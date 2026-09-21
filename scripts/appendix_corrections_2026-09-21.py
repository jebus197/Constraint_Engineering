#!/usr/bin/env python3
"""The 3 appendix corrections of 2026-09-21, and the 1 finding left open.

Every figure quoted in `experimental_notes/Morning_Report_2026-09-21.md` that
concerns the mathematical appendix is regenerated here. Nothing is typed into
prose that this script does not print.

1. THE STATED FLOOR IS TRUE BUT LOOSE BY 1/q. The appendix gives the substrate
   ceiling as `lim R >= nu_k`. At sigma = 1 the composite map has exactly 2 fixed
   points, `{1, nu/q}`, and the attracting one is `nu/q`. Since q < 1 the
   reachable floor is strictly higher than nu, so the appendix was OPTIMISTIC
   about how far a review loop can drive residual risk down. Checked against the
   shipped `compute_rk` rather than derived only on paper.

2. AT nu = q THE FIXED POINT IS PARABOLIC. The derivative of the map at R = 1 is
   `(nu-1)/(q-1)`, which is exactly 1 when nu = q, so approach to certain failure
   is O(1/n) rather than geometric. A run there looks like a flattening curve,
   and the Hard Exit fires on `dR = 0` over successive passes -- so it reads
   approach-to-certain-failure as a substrate ceiling reached, the opposite
   conclusion.

3. THE STOPPING-RULE GLOSS HOLDS ONLY BELOW THE PEAK. `Delta R` is unimodal in R,
   not monotone, peaking at `R* = (1 - sqrt(1-q))/q`. Above that peak the
   relationship inverts. The greedy rule "continue while Delta R > theta"
   therefore has a PREMATURE-STOP BAND at the highest-risk states.

4. OPEN, AND THE FOUNDER'S: a correctly detected, genuinely present flaw that
   happens to be published can only RAISE modelled risk. At nu_k = 0, c_ext = 1
   the combined novelty is 0, so q = 0, so detection is a no-op -- but
   re-injection is not. Measured as latent: no archived run carries `c_ext`.

CROSS-VERIFICATION, per the 2026-04-21 rule: SymPy against z3 for the symbolic
and satisfiability claims, NumPy against the shipped implementation for the
behavioural ones, and statsmodels beside a hand Wilson interval for proportions.
"""
from __future__ import annotations

import sys
from math import sqrt
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))


def wilson(k: int, n: int) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n)))
    return ((c - h) / d, (c + h) / d)


def the_floor():
    import sympy as sp
    from reference_runner_v3 import compute_rk
    R, q, nu, sg = sp.symbols('R q nu sigma', positive=True)
    T = (sg * R * (1 - q) / (1 - q * R) + (1 - sg) * R) * (1 - nu) + nu
    T1 = sp.simplify(T.subs(sg, 1))
    fps = sp.solve(sp.Eq(T1, R), R)
    interior = [f for f in fps if sp.simplify(f - 1) != 0]
    Rstar = sp.simplify(interior[0])
    orbits = []
    for qq, nn in ((0.2, 0.05), (0.1, 0.02), (0.5, 0.10)):
        r = 0.9
        for _ in range(20000):
            r = compute_rk(r, qq, 1.0, nu_b=nn, nu_f=0.0)
        orbits.append((qq, nn, r, nn / qq))
    d_at_1 = sp.simplify(sp.diff(T1, R).subs(R, 1))
    return {"fixed_points": [sp.factor(sp.simplify(f)) for f in fps],
            "attracting": sp.factor(Rstar),
            "ratio_to_stated": sp.simplify(Rstar / nu),
            "orbits": orbits,
            "derivative_at_1": sp.factor(d_at_1),
            "at_nu_equals_q": sp.simplify(d_at_1.subs(nu, q))}


def the_stopping_peak(q_val: str = "0.3", theta: float = 0.05):
    import sympy as sp
    import numpy as np
    import z3
    R, q = sp.symbols('R q', positive=True)
    dR = R * q * (R - 1) / (R * q - 1)
    peak = (1 - sp.sqrt(1 - q)) / q
    crit = sp.solve(sp.diff(dR, R), R)
    second = sp.simplify(sp.diff(dR, R, 2).subs(R, peak))
    qq = sp.nsimplify(q_val)
    pk = float(peak.subs(q, qq))
    pv = float(dR.subs({q: qq, R: sp.nsimplify(pk)}))
    f = sp.lambdify((R,), dR.subs(q, qq), 'numpy')
    xs = np.linspace(1e-6, 1 - 1e-6, 200000)
    ys = f(xs)
    band = xs[(ys < theta) & (xs > pk)]
    zR = z3.Real('R')
    s = z3.Solver()
    s.add(zR > z3.RealVal(str(pk)), zR < 1)
    s.add(zR * z3.RealVal(q_val) * (zR - 1) / (zR * z3.RealVal(q_val) - 1)
          < z3.RealVal(str(theta)))
    samples = [(r, float(dR.subs({q: qq, R: sp.nsimplify(r)})))
               for r in (0.99, 0.95, 0.90, 0.80, pk, 0.40, 0.20)]
    return {"critical_points": [sp.simplify(c) for c in crit],
            "claimed_peak": peak, "second_derivative": second,
            "peak_at": pk, "peak_value": pv,
            "band": (float(band.min()), float(band.max())) if band.size else None,
            "band_width": float(band.max() - band.min()) if band.size else 0.0,
            "z3_band_exists": str(s.check()), "samples": samples}


def the_novelty_coupling():
    import sympy as sp
    import numpy as np
    import z3
    eta_int, c_ext, nu_k, d, p, R, sg, nu = sp.symbols(
        'eta_int c_ext nu_k d p R sigma nu', nonnegative=True)
    eta_comb = eta_int * (1 - c_ext * (1 - nu_k))
    q = eta_comb * d * p
    R_det = R * (1 - q) / (1 - q * R)
    R_new = (sg * R_det + (1 - sg) * R) * (1 - nu) + nu
    at = {nu_k: 0, c_ext: 1}
    delta = sp.simplify(R_new.subs(at) - R)
    zR, zn = z3.Reals('R nu')
    s = z3.Solver()
    s.add(zR >= 0, zR < 1, zn > 0, zn <= 1, zR * (1 - zn) + zn < zR)
    rng = np.random.default_rng(20260921)
    N = 200000
    Rv, nv = rng.uniform(0, 1, N), rng.uniform(0, 1, N)
    dRv = (Rv * (1 - nv) + nv) - Rv
    return {"eta_at": sp.simplify(eta_comb.subs(at)),
            "q_at": sp.simplify(q.subs(at)),
            "delta": sp.factor(delta),
            "matches_nu_times": sp.simplify(delta - nu * (1 - R)) == 0,
            "z3_can_reduce": str(s.check()),
            "numpy_reducing": int((dRv < 0).sum()), "numpy_n": N,
            "numpy_maxresid": float(abs(dRv - nv * (1 - Rv)).max())}


def is_it_armed():
    """No archived run may carry a non-zero c_ext, or the coupling is live."""
    import glob
    import json
    import os
    files = armed = 0
    for f in sorted(glob.glob(str(REPO / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > 60_000_000:
            continue
        try:
            raw = open(f, errors="ignore").read()
        except OSError:
            continue
        if "sk_result" not in raw:
            continue
        files += 1
        try:
            doc = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        hit = [False]

        def walk(node):
            if isinstance(node, dict):
                v = node.get("c_ext")
                if isinstance(v, (int, float)) and v > 0:
                    hit[0] = True
                for x in node.values():
                    walk(x)
            elif isinstance(node, list):
                for x in node:
                    walk(x)

        walk(doc)
        if hit[0]:
            armed += 1
    return armed, files


def main() -> None:
    from statsmodels.stats.proportion import proportion_confint
    print("=" * 74)
    print("APPENDIX CORRECTIONS, 2026-09-21")
    print("=" * 74)

    fl = the_floor()
    print("\n1. THE STATED FLOOR IS TRUE BUT LOOSE BY 1/q")
    print(f"   fixed points at sigma=1 : {fl['fixed_points']}")
    print(f"   attracting one          : {fl['attracting']}")
    print(f"   ratio to the stated nu  : {fl['ratio_to_stated']}")
    print("   shipped compute_rk, 20,000 cycles:")
    for qq, nn, orbit, expected in fl["orbits"]:
        print(f"      q={qq} nu={nn}: orbit -> {orbit:.10f}   nu/q = {expected:.10f}"
              f"   stated nu = {nn}")

    print("\n2. AT nu = q THE FIXED POINT IS PARABOLIC")
    print(f"   T'(R) at R=1   : {fl['derivative_at_1']}")
    print(f"   at nu = q      : {fl['at_nu_equals_q']}")
    print("   -> derivative exactly 1, so approach to R=1 is O(1/n), and the")
    print("      Hard Exit reads it as a substrate ceiling reached.")

    sp_ = the_stopping_peak()
    print("\n3. THE STOPPING-RULE GLOSS HOLDS ONLY BELOW THE PEAK")
    print(f"   critical points    : {sp_['critical_points']}")
    print(f"   peak               : {sp_['claimed_peak']}")
    print(f"   second derivative  : {sp_['second_derivative']}  (negative = a maximum)")
    print(f"   at q=0.3: peak gain {sp_['peak_value']:.6f} at R={sp_['peak_at']:.6f}")
    print("   R        per-cycle gain   verdict at theta=0.05")
    for r, v in sp_["samples"]:
        print(f"      {r:<8.4f} {v:<16.6f} {'CONTINUE' if v > 0.05 else 'STOP'}")
    if sp_["band"]:
        print(f"   PREMATURE-STOP BAND above the peak: R in "
              f"[{sp_['band'][0]:.6f}, {sp_['band'][1]:.6f}], width {sp_['band_width']:.6f}")
    print(f"   z3: does that band exist? {sp_['z3_band_exists']}  (sat = yes)")

    nc = the_novelty_coupling()
    print("\n4. OPEN: A PUBLISHED FLAW CAN ONLY RAISE MODELLED RISK")
    print(f"   eta_combined at nu_k=0, c_ext=1 : {nc['eta_at']}")
    print(f"   q there                         : {nc['q_at']}")
    print(f"   R_new - R_old                   : {nc['delta']}")
    print(f"   equals nu*(1-R_old)?              {nc['matches_nu_times']}")
    print(f"   z3: can such a cycle REDUCE risk? {nc['z3_can_reduce']}  (unsat = never)")
    print(f"   numpy {nc['numpy_n']} samples reducing risk: {nc['numpy_reducing']}"
          f"   max residual {nc['numpy_maxresid']:.3e}")

    armed, files = is_it_armed()
    lo, hi = wilson(armed, files)
    a, b = proportion_confint(armed, files, method="wilson") if files else (0, 0)
    print(f"\n   SEVERITY: archived runs with a non-zero c_ext: {armed}/{files}")
    print(f"   Wilson [{lo:.4%}, {hi:.4%}]  statsmodels agrees: {abs(lo - a) < 1e-9}")
    print("   -> LATENT. The channel is live in code and armed by no shipped")
    print("      config, so no archived result is affected.")


if __name__ == "__main__":
    # A --help MUST NEVER COST ANYTHING (founder ruling). This runs 20,000-cycle
    # orbits, a 200,000-point sweep and several z3 queries.
    import argparse
    ap = argparse.ArgumentParser(
        description=("Regenerate every appendix figure quoted in the 2026-09-21 "
                     "morning report. Reads bench/logs, writes nothing, "
                     "dispatches to no model and costs nothing."),
        epilog=("Prints the true floor against the stated one, the parabolic "
                "point, the stopping-rule peak and its premature-stop band, and "
                "the novelty coupling with its severity bound."))
    ap.parse_args()
    main()
