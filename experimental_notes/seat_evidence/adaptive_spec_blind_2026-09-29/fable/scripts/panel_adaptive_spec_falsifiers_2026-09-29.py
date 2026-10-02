# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'adaptive_spec_blind_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e5cfc3f0c2416f0f37798668413691d450e7046905e627e37e961564bd9488a9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Falsifiers for the adaptive distributed-compute design spec (2026-09-14).

Panel seat: fable (blind round, 2026-09-29).

Each check compares the specification's OWN transcriptions (SS6.1, SS6.2, SS6.4,
SS9.3) against the shipped implementation bench.reference_runner_v3.compute_rk
/ compute_rk_expectation / apply_sk_to_rk, or against a derivation executed
here with SymPy / statsmodels. PASS means "the finding it supports is
demonstrated". Exit non-zero if any demonstration fails to reproduce.

Sampling caveat (per the brief): all grid/sample rates below are properties of
a UNIFORM grid or uniform random draw over the unit cube. The operationally
relevant distribution of (R, q, sigma) is NOT known; no archived distribution
was substituted for it. Rates carry Wilson 95% intervals.
"""
import math
import os
import sys
import itertools

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bench.reference_runner_v3 import (  # noqa: E402
    compute_rk, compute_rk_expectation, apply_sk_to_rk, SK_NO_SCORE,
)

FAILURES = []


def check(name, ok, detail):
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}: {detail}")
    if not ok:
        FAILURES.append(name)


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def spec_61_rnext(R, q, sigma, nu):
    """The spec's own SS6.1 transcription: free sigma-hat and nu-hat."""
    R_det = R * (1 - q) / (1 - q * R)  # spec has NO denominator guard
    return (sigma * R_det + (1 - sigma) * R) * (1 - nu) + nu


def nu_eff(sk, nu_b=0.05, nu_f=0.20):
    return 1.0 - (1.0 - nu_b) * (1.0 - (1.0 - sk) * nu_f)


# F1: SS6.1 transcription equals compute_rk ONLY under the sk-coupled nu_eff;
# the spec presents nu as a free calibrated parameter.
grid = [i / 10 for i in range(1, 10)]
max_dev_coupled = 0.0
for R, q, s in itertools.product(grid, grid, grid):
    dev = abs(spec_61_rnext(R, q, s, nu_eff(s)) - compute_rk(R, q, s))
    max_dev_coupled = max(max_dev_coupled, dev)
check("F1a spec form == compute_rk when nu-hat = nu_eff(sigma)",
      max_dev_coupled < 1e-12, f"max |diff| = {max_dev_coupled:.2e} over 729 pts")

best_const, best_max = None, float("inf")
for nuh in [i / 100 for i in range(0, 41)]:
    m = max(abs(spec_61_rnext(R, q, s, nuh) - compute_rk(R, q, s))
            for R, q, s in itertools.product(grid, grid, grid))
    if m < best_max:
        best_max, best_const = m, nuh
n_pts, n_big = 0, 0
for R, q, s in itertools.product(grid, grid, grid):
    n_pts += 1
    if abs(spec_61_rnext(R, q, s, best_const) - compute_rk(R, q, s)) > 0.01:
        n_big += 1
lo, hi = wilson(n_big, n_pts)
check("F1b best constant nu-hat still mispredicts compute_rk",
      best_max > 0.05,
      f"best constant nu-hat={best_const}, max |diff|={best_max:.4f}; "
      f"|diff|>0.01 at {n_big}/{n_pts} grid pts "
      f"(rate {n_big/n_pts:.3f}, Wilson95 [{lo:.3f},{hi:.3f}]) [uniform grid]")

check("F1c nu_eff spans [0.05, 0.24] as sigma goes 1->0 (defaults)",
      abs(nu_eff(1.0) - 0.05) < 1e-15 and abs(nu_eff(0.0) - 0.24) < 1e-15,
      f"nu_eff(sk=1)={nu_eff(1.0):.4f}, nu_eff(sk=0)={nu_eff(0.0):.4f}")

try:
    spec_61_rnext(1.0, 1.0, 0.5, 0.05)
    guarded = False
except ZeroDivisionError:
    guarded = True
check("F1d spec SS6.1 has no denominator guard at qR=1 (compute_rk does)",
      guarded and compute_rk(1.0, 1.0, 0.5) <= 1.0,
      f"spec form raises ZeroDivisionError; compute_rk(1,1,0.5)="
      f"{compute_rk(1.0, 1.0, 0.5):.4f}")

# F2: SS6.1 closing claim: gate-failed candidate gets ZERO credit. Shipped:
# sk=0 on an applicable gate gives NEGATIVE credit; only NO_SCORE gives zero.
R0 = 0.5
r_fail = compute_rk(R0, 0.5, 0.0)
r_noscore, _ = apply_sk_to_rk(R0, SK_NO_SCORE)
check("F2 'zero credit' claim vs shipped S_k sink",
      r_fail > R0 and r_noscore == R0,
      f"gate-failed: R 0.5 -> {r_fail:.4f} (credit {R0-r_fail:+.4f}, NEGATIVE); "
      f"NO_SCORE: R 0.5 -> {r_noscore:.4f} (credit exactly 0)")

# F3: SS6.1's g ranks by the CONDITIONAL (gate) update; the canonical
# pre-dispatch quantity (appendix 2026-09-21/29; compute_rk_expectation) is
# the branch-weighted expectation. Demonstrate a ranking reversal on the
# SHIPPED functions.
R = 0.9
cand_X = dict(q=0.9, s=0.4)
cand_Y = dict(q=0.5, s=0.8)
gA = {k: R - compute_rk(R, c["q"], c["s"]) for k, c in
      (("X", cand_X), ("Y", cand_Y))}
gM = {k: R - compute_rk_expectation(R, c["q"], c["s"]) for k, c in
      (("X", cand_X), ("Y", cand_Y))}
reversal = (gA["X"] > gA["Y"]) and (gM["Y"] > gM["X"])
check("F3a ranking reversal: spec's g vs expectation-based g",
      reversal,
      f"g_spec: X={gA['X']:.4f} vs Y={gA['Y']:.4f}; "
      f"g_expect: X={gM['X']:.4f} vs Y={gM['Y']:.4f} (R=0.9; "
      f"X: q=0.9,s=0.4; Y: q=0.5,s=0.8)")

import random  # noqa: E402
rng = random.Random(20260929)
n_trials, n_rev = 0, 0
for _ in range(20000):
    Rr = rng.uniform(0.05, 0.99)
    q1, s1 = rng.random(), rng.random()
    q2, s2 = rng.random(), rng.random()
    a1 = Rr - compute_rk(Rr, q1, s1)
    a2 = Rr - compute_rk(Rr, q2, s2)
    m1 = Rr - compute_rk_expectation(Rr, q1, s1)
    m2 = Rr - compute_rk_expectation(Rr, q2, s2)
    n_trials += 1
    if (a1 - a2) * (m1 - m2) < 0:
        n_rev += 1
lo, hi = wilson(n_rev, n_trials)
check("F3b reversal rate (uniform draw; operational distribution UNKNOWN)",
      n_rev > 0,
      f"{n_rev}/{n_trials} = {n_rev/n_trials:.4f}, "
      f"Wilson95 [{lo:.4f},{hi:.4f}]")

g_cond = 0.99 - spec_61_rnext(0.99, 0.3, 1.0, 0.0)
check("F3c conditional gain at R=0.99,q=0.3 is 0.004225 (appendix figure)",
      abs(g_cond - 0.004225) < 1e-6,
      f"g_cond={g_cond:.6f} vs expectation-corner R*q={0.99*0.3:.4f} "
      f"(factor {0.99*0.3/g_cond:.1f}x)")

# F4: SS6.4 exploration term dead at cold start; score unbounded as cost->0.
e_cold = [math.sqrt(math.log(1 + 0) / (1 + n_mu)) for n_mu in (0, 5, 50)]
check("F4a e_mu = 0 for EVERY m when N_u = 0 (no cold-start exploration)",
      all(v == 0.0 for v in e_cold), f"e_mu at N_u=0: {e_cold}")
g_hat, lam_t, lam_h = 0.1, 1.0, 1.0
scores = [g_hat / (c + lam_t * 0.0 + lam_h * 0.0) for c in (1e-3, 1e-6, 1e-9)]
check("F4b score unbounded as c_mu -> 0 with t=h=0 (no floor specified)",
      scores[-1] > 1e7, f"scores at c=1e-3,1e-6,1e-9: {scores}")

# F5: SS9.3 power of 'at least three seeded runs per condition'.
try:
    from statsmodels.stats.power import TTestIndPower  # noqa: E402
    from statsmodels.stats.proportion import proportion_confint  # noqa: E402
    solver = TTestIndPower()
    mde = solver.solve_power(nobs1=3, alpha=0.05, power=0.8, ratio=1.0,
                             alternative="two-sided")
    mde_bonf = solver.solve_power(nobs1=3, alpha=0.05 / 5, power=0.8,
                                  ratio=1.0, alternative="two-sided")
    lo33, hi33 = proportion_confint(3, 3, method="wilson")
    check("F5a n=3/condition detects only enormous effects",
          mde > 2.5,
          f"MDE (Cohen's d, alpha=.05, power=.8) = {mde:.2f}; "
          f"Bonferroni over 5 control comparisons: d = {mde_bonf:.2f}")
    check("F5b a 3/3 proportion is uninformative",
          lo33 < 0.5,
          f"Wilson95 for 3/3 successes = [{lo33:.3f}, {hi33:.3f}]")
except ImportError:
    check("F5 statsmodels available", False, "statsmodels missing")

# F6: SS6.2 arithmetic exact (SOUND check), matches PAPER.md Part XIII form.
from fractions import Fraction  # noqa: E402
v = 1 - (1 - Fraction(45, 100)) * (1 - Fraction(35, 100))
check("F6 SS6.2 worked example exact",
      v == Fraction(257, 400) and v - Fraction(45, 100) == Fraction(77, 400),
      f"1-(0.55)(0.65) = {float(v)} (= 257/400); "
      f"increment {float(v-Fraction(45,100))} (= 77/400)")

# SymPy: the algebra behind F1/F3, derived not asserted.
import sympy as sp  # noqa: E402
Rs, qs, ss, nh, nb, nf = sp.symbols("R q s nu_hat nu_b nu_f", positive=True)
R_det = Rs * (1 - qs) / (1 - qs * Rs)
R_base = ss * R_det + (1 - ss) * Rs
nu_e = 1 - (1 - nb) * (1 - (1 - ss) * nf)
diff = sp.simplify((R_base * (1 - nh) + nh) - (R_base * (1 - nu_e) + nu_e))
check("SymPy: spec_form - runner_form == (nu_hat - nu_eff)(1 - R_base)",
      sp.simplify(diff - (nh - nu_e) * (1 - R_base)) == 0,
      f"factored: {sp.factor(diff)}")
gA_sym = sp.simplify(Rs - (ss * R_det + (1 - ss) * Rs))
check("SymPy: spec gain (nu=0) == s*q*R*(1-R)/(1-qR)  [ranks by sq/(1-qR)]",
      sp.simplify(gA_sym - ss * qs * Rs * (1 - Rs) / (1 - qs * Rs)) == 0,
      f"gA = {sp.factor(gA_sym)}")
gM_sym = sp.simplify(Rs - Rs * (1 - qs * ss))
check("SymPy: expectation gain (nu=0) == R*q*s  [ranks by sq]",
      sp.simplify(gM_sym - Rs * qs * ss) == 0, f"gM = {gM_sym}")

print()
if FAILURES:
    print(f"REFUTED-DEMONSTRATIONS: {FAILURES}")
    sys.exit(1)
print("ALL DEMONSTRATIONS REPRODUCED (exit 0)")
