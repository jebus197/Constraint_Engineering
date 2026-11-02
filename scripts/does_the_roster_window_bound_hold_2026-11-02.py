#!/usr/bin/env python3
"""Does the roster-scaled convergence window actually bound spurious convergence?

THE DESIGN UNDER TEST. `experimental_notes/seat_evidence/
dynamic_roster_and_derived_ladder_2026-10-07/cc2/bench/degraded_convergence_2026-10-07.py`
is a CC2 seat design that has sat UNADOPTED since 2026-10-07. It claims the live
`_check_gamma_alt_convergence` in `bench/reference_runner_v3.py` is ROSTER-BLIND:
its count side -- K consecutive rounds with 0 new criticals -- gets easier as the
roster shrinks, because fewer seats generate fewer findings, and the gate cannot
see the difference.

Its repair is `K_required = ceil(K * n_dec / n_live)`, claimed SUFFICIENT AT EVERY
intra-round correlation and tight at independence. THAT IS A MATHEMATICAL CLAIM AND
`fff-sympy` BINDS: a mathematical claim that has not been SymPy-verified is
unverified, so it is verified here before any verdict is recorded on the design.

THE DERIVATION BEING CHECKED, in the design's own terms. Seats in a round share a
per-round latent factor u; given u they are conditionally independent with
probability p(u), and E[p(u)] = q.

    A(n) := E_u[(1 - p(u))^n]        # P(a round of n seats is quiet)
    f(n) := -ln A(n)

A(n) = E[exp(n * ln(1-p))] is the moment generating function of X := ln(1-p) <= 0,
so ln A(n) is a cumulant generating function and is CONVEX in n. Hence f is
CONCAVE with f(0) = 0, so f(n)/n is NON-INCREASING, so for n_live < n_dec:

    f(n_dec)/f(n_live) <= n_dec/n_live

and therefore the integer window ceil(K * n_dec/n_live) is at least the exact
requirement K * f(n_dec)/f(n_live). THE 3 STEPS CHECKED SEPARATELY, because the
chain is only as good as its weakest link and the last one carries a hidden
precondition.

★ THE HIDDEN PRECONDITION, which the design's docstring does NOT state. Dividing
by f(n_live) requires f(n_live) > 0, i.e. A(n_live) < 1, i.e. P(p > 0) > 0. If the
panel can never produce a critical at all then every round is quiet by
construction, no window separates the cases, and the ratio is 0/0. That is a real
boundary and it is tested rather than assumed away.

NO FIGURE HERE IS A CLAIM ABOUT THE PROJECT'S OWN CORRELATION. The design is
explicit that the intra-round correlation has never been measured here; the whole
point of the bound is that it does not need to be. This script tests the BOUND, not
the parameter.
"""
from __future__ import annotations

import argparse
import math
import pathlib

import numpy as np
import sympy as sp

rng = np.random.default_rng(20261102)


def banner(s: str) -> None:
    print("=" * 74)
    print(s)
    print("=" * 74)


# ───────────────────── STEP 1: SymPy, the CGF is convex ─────────────────────
def step1_cgf_convex() -> bool:
    """ln A(n) convex in n, on an explicit 2-point mixture, symbolically."""
    n, p1, p2, w = sp.symbols("n p1 p2 w", positive=True)
    # A(n) = w*(1-p1)^n + (1-w)*(1-p2)^n, a genuine 2-point latent mixture.
    A = w * (1 - p1) ** n + (1 - w) * (1 - p2) ** n
    lnA = sp.log(A)
    d2 = sp.simplify(sp.diff(lnA, n, 2))

    # Convexity of a log-MGF is standard; here it is CHECKED by showing the
    # second derivative is a variance, which is non-negative by construction.
    # Substituting a1 = (1-p1)^n, a2 = (1-p2)^n, L1 = ln(1-p1), L2 = ln(1-p2):
    a1, a2, L1, L2, ww = sp.symbols("a1 a2 L1 L2 ww", positive=True)
    num = (ww * a1 * L1 ** 2 + (1 - ww) * a2 * L2 ** 2) / (ww * a1 + (1 - ww) * a2)
    mean = (ww * a1 * L1 + (1 - ww) * a2 * L2) / (ww * a1 + (1 - ww) * a2)
    variance_form = sp.simplify(num - mean ** 2)

    # d2 should equal that variance form under the substitution.
    subbed = sp.simplify(
        d2.subs({(1 - p1) ** n: a1, (1 - p2) ** n: a2, w: ww})
        - variance_form.subs({L1: sp.log(1 - p1), L2: sp.log(1 - p2)})
    )
    # Verify numerically rather than trusting the symbolic rearrangement alone.
    worst = 0.0
    for _ in range(4000):
        vals = {p1: rng.uniform(1e-4, 0.999), p2: rng.uniform(1e-4, 0.999),
                w: rng.uniform(0.001, 0.999), n: rng.uniform(0.1, 40.0)}
        got = float(d2.subs(vals))
        worst = min(worst, got) if got < worst else worst
    print(f"  symbolic d2/dn2 ln A(n) minus its variance form : "
          f"{'0' if subbed == 0 else sp.srepr(subbed)[:40]}")
    print(f"  most negative d2/dn2 over 4,000 random draws    : {worst:.6e}")
    ok = worst >= -1e-9
    print(f"  CONVEX (d2 >= 0 everywhere sampled)             : {ok}")
    return ok


# ──────────── STEP 2: NumPy, f(n)/n non-increasing on many mixtures ────────────
def step2_ratio_nonincreasing() -> tuple[bool, float]:
    """f(n)/n non-increasing, over a wide family of latent distributions."""
    worst = 0.0
    checked = 0
    for _ in range(3000):
        k = rng.integers(1, 6)                      # 1..5 point latent mixture
        ps = rng.uniform(1e-5, 0.9995, size=k)
        ws = rng.dirichlet(np.ones(k))

        def f(nn: float) -> float:
            A = float(np.sum(ws * (1.0 - ps) ** nn))
            return -math.log(A)

        ns = np.arange(1, 25, dtype=float)
        r = np.array([f(x) / x for x in ns])
        d = np.diff(r)
        worst = max(worst, float(d.max()))
        checked += len(d)
    ok = worst <= 1e-9
    print(f"  comparisons of f(n)/n vs f(n+1)/(n+1)           : {checked:,}")
    print(f"  largest INCREASE found in f(n)/n                : {worst:.6e}")
    print(f"  NON-INCREASING                                  : {ok}")
    return ok, worst


# ────── STEP 3: the window is sufficient, and never under-corrects ──────
def step3_window_sufficient() -> tuple[bool, int, float]:
    """ceil(K*n_dec/n_live) >= K*f(n_dec)/f(n_live), and the slack is >= 0."""
    K_VALUES = (2, 3, 4, 5)
    violations = 0
    trials = 0
    min_slack = math.inf
    tight_at_independence = []
    for _ in range(3000):
        k = rng.integers(1, 6)
        ps = rng.uniform(1e-5, 0.9995, size=k)
        ws = rng.dirichlet(np.ones(k))
        n_dec = int(rng.integers(2, 13))
        n_live = int(rng.integers(1, n_dec + 1))

        def f(nn: int) -> float:
            return -math.log(float(np.sum(ws * (1.0 - ps) ** nn)))

        fl = f(n_live)
        if fl <= 0.0:                     # the hidden precondition; see step 4
            continue
        exact = f(n_dec) / fl
        for K in K_VALUES:
            trials += 1
            required = math.ceil(K * n_dec / n_live)
            slack = required - K * exact
            min_slack = min(min_slack, slack)
            if slack < -1e-9:
                violations += 1
        # at independence the ratio should equal n_dec/n_live exactly
        if k == 1:
            tight_at_independence.append(abs(exact - n_dec / n_live))

    ok = violations == 0
    print(f"  (K, roster) combinations tested                 : {trials:,}")
    print(f"  violations of the bound                         : {violations}")
    print(f"  minimum slack (required - exact)                : {min_slack:.6e}")
    if tight_at_independence:
        print(f"  max |exact - n_dec/n_live| at independence      : "
              f"{max(tight_at_independence):.6e}  (tight, as claimed)")
    print(f"  SUFFICIENT AT EVERY SAMPLED CORRELATION         : {ok}")
    return ok, violations, min_slack


# ────── STEP 4: the precondition the design does not state ──────
def step4_precondition() -> bool:
    """f(n_live) = 0 when the panel can never produce a critical: 0/0."""
    ws, ps = np.array([1.0]), np.array([0.0])      # q = 0 exactly
    A = float(np.sum(ws * (1.0 - ps) ** 5))
    f5 = -math.log(A)
    degenerate = abs(f5) < 1e-15
    print(f"  with q = 0 exactly, A(5) = {A:.1f} and f(5) = {f5:.1f}")
    print(f"  the exact requirement is therefore 0/0          : {degenerate}")
    print("  CONSEQUENCE: no window separates a quiet healthy panel from a")
    print("  quiet dead one when NO seat can ever produce a critical. The")
    print("  design's n_live == 0 guard does NOT cover this -- the roster is")
    print("  full and the finding rate is 0. It is a REAL boundary, and the")
    print("  docstring states neither it nor a guard for it.")
    return degenerate


def main() -> int:
    # ★ ARGPARSE IS NOT DECORATION HERE. Without it, `--help` fell through and ran
    # the whole measurement, which the suite refuses: a flag must never trigger
    # the work it is asking about. Same family as the standing rule that a
    # `--help` must never cost money.
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.strip().splitlines()[0] if __doc__ else None)
    ap.parse_args()
    banner("STEP 1 (SymPy)  the log-MGF is convex, so f = -ln A is concave")
    s1 = step1_cgf_convex()
    print()
    banner("STEP 2 (NumPy)  a concave f with f(0)=0 has non-increasing f(n)/n")
    s2, _ = step2_ratio_nonincreasing()
    print()
    banner("STEP 3 (NumPy)  ceil(K*n_dec/n_live) bounds the exact requirement")
    s3, viol, slack = step3_window_sufficient()
    print()
    banner("STEP 4          the precondition the design omits")
    s4 = step4_precondition()
    print()
    banner("VERDICT ON THE DERIVATION")
    all_ok = s1 and s2 and s3 and s4
    print(f"  step 1 convexity          : {'HOLDS' if s1 else 'FAILS'}")
    print(f"  step 2 ratio monotonicity : {'HOLDS' if s2 else 'FAILS'}")
    print(f"  step 3 window sufficiency : {'HOLDS' if s3 else 'FAILS'}"
          f"  ({viol} violations, min slack {slack:.3e})")
    print(f"  step 4 omitted precondition reproduced : "
          f"{'YES' if s4 else 'NO'}")
    print()
    if all_ok:
        print("  THE DERIVATION IS SOUND AS STATED, with 1 unstated precondition")
        print("  (a panel with a 0 critical rate) that the design's own guards do")
        print("  not cover. The bound never under-corrects, so adopting it cannot")
        print("  weaken the gate -- which is the property that matters for a")
        print("  pre-registered threshold.")
    else:
        print("  AT LEAST 1 STEP FAILED. The design's claim does not survive and")
        print("  must not be adopted on the strength of its docstring.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
