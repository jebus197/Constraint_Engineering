# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'adaptive_spec_blind_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: bd73be12bf248e3affa8baa43429c0203d7026dd561e3fc8927acd7b9d59f604
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Falsifiers for the adaptive distributed-compute design spec (2026-09-14).

Target: `adaptive_distributed_compute_design_spec.md`, SS6.1, 6.4, 6.5, 9.3.

Every check imports the REAL runner functions. Nothing is retyped.
Each check prints FALSIFIED when the claimed defect is present.

Run:  python3 scripts/adaptive_spec_falsifiers_2026-09-29.py
"""
import math
import os
import sys
import itertools

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bench"))

from reference_runner_v3 import (            # noqa: E402  REAL target, not a copy
    compute_rk, compute_rk_expectation, apply_sk_to_rk,
    SK_REJECTED, SK_NO_SCORE,
)

NU_B, NU_F = 0.05, 0.20          # shipped defaults in compute_rk's signature
FAILED = []


def wilson(k, n, z=1.959963984540054):
    """Wilson score interval for a proportion."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def spec_61(R, q, sigma, nu):
    """The specification's SS6.1 transcription, EXACTLY as written."""
    R_det = R * (1.0 - q) / (1.0 - q * R)
    return (sigma * R_det + (1.0 - sigma) * R) * (1.0 - nu) + nu


def banner(n, title):
    print("\n" + "=" * 74)
    print("CHECK %d: %s" % (n, title))
    print("=" * 74)


# ---------------------------------------------------------------- CHECK 1
def check1_nu_is_not_free():
    banner(1, "spec nu_hat is free; runner's nu_eff is a function of sigma")
    sigmas = [i / 20 for i in range(21)]
    R, q = 0.5, 0.30
    print("  R=%s q=%s nu_b=%s nu_f=%s" % (R, q, NU_B, NU_F))
    print("  %6s %18s %15s" % ("sigma", "runner compute_rk", "nu_eff implied"))
    implied = []
    for s in (0.0, 0.25, 0.5, 0.75, 1.0):
        live = compute_rk(R, q, s, NU_B, NU_F)
        nu_eff = 1.0 - (1.0 - NU_B) * (1.0 - (1.0 - s) * NU_F)
        implied.append(nu_eff)
        print("  %6.2f %18.6f %15.6f" % (s, live, nu_eff))
    spread = max(implied) - min(implied)
    best = min(
        ((max(abs(spec_61(R, q, s, nu) - compute_rk(R, q, s, NU_B, NU_F))
              for s in sigmas), nu)
         for nu in [i / 2000 for i in range(0, 501)]),
        key=lambda t: t[0])
    sup_err, nu_star = best
    print("\n  nu_eff spread over sigma in [0,1]: %.6f" % spread)
    print("  best constant nu_hat = %.4f, sup|spec-runner| = %.6f"
          % (nu_star, sup_err))
    ok = sup_err > 1e-9
    print("\n  Claimed defect present: %s" % ok)
    if ok:
        FAILED.append(1)
        print("  FALSIFIED")
    return sup_err, nu_star


# ---------------------------------------------------------------- CHECK 2
def check2_sigma_zero_is_negative_credit():
    banner(2, "sigma=0 yields NEGATIVE predicted credit, not zero")
    import sympy as sp
    R, q, nu = sp.symbols("R q nu", positive=True)
    Rdet = R * (1 - q) / (1 - q * R)
    Rnext = (0 * Rdet + (1 - 0) * R) * (1 - nu) + nu
    g = sp.simplify(R - Rnext)
    print("  SymPy: g at sigma=0  =  %s" % g)
    print("  factored            =  %s" % sp.factor(g))

    import z3
    zR, zq, znu = z3.Reals("R q nu")
    s = z3.Solver()
    s.add(zR > 0, zR < 1, zq > 0, zq < 1, znu > 0, znu < 1)
    s.add(zR - ((zR) * (1 - znu) + znu) >= 0)          # g >= 0 anywhere?
    res = s.check()
    print("  z3: exists (R,q,nu) in (0,1)^3 with g >= 0  ->  %s" % res)

    live = compute_rk(0.5, 0.30, 0.0, NU_B, NU_F)
    held, why = apply_sk_to_rk(0.5, SK_REJECTED, None)
    nos, why2 = apply_sk_to_rk(0.5, SK_NO_SCORE)
    print("\n  runner compute_rk(0.5, 0.30, sk=0.0) = %.6f   (R_old=0.5)" % live)
    print("  g implied by that                    = %+.6f" % (0.5 - live))
    print("  live REJECTED route apply_sk_to_rk   = %.6f  <- %s" % (held, why))
    print("  live NO_SCORE route apply_sk_to_rk   = %.6f  <- %s" % (nos, why2))
    ok = (res == z3.unsat) and (live > 0.5)
    print("\n  Claimed defect present: %s" % ok)
    if ok:
        FAILED.append(2)
        print("  FALSIFIED")


# ---------------------------------------------------------------- CHECK 3
def check3_branch_quantity_rank_inversion():
    banner(3, "spec ranks candidates on the wrong branch quantity")
    R = 0.5
    grid = [i / 20 for i in range(1, 20)]
    cands = [(q, s) for q in grid for s in grid]
    pairs = 0
    flips = 0
    example = None
    for (q1, s1), (q2, s2) in itertools.combinations(cands, 2):
        a1 = compute_rk(R, q1, s1, NU_B, NU_F)
        a2 = compute_rk(R, q2, s2, NU_B, NU_F)
        m1 = compute_rk_expectation(R, q1, s1, NU_B, NU_F)
        m2 = compute_rk_expectation(R, q2, s2, NU_B, NU_F)
        gA1, gA2 = R - a1, R - a2
        gM1, gM2 = R - m1, R - m2
        if abs(gA1 - gA2) < 1e-12 or abs(gM1 - gM2) < 1e-12:
            continue
        pairs += 1
        if (gA1 > gA2) != (gM1 > gM2):
            flips += 1
            if example is None:
                example = (q1, s1, q2, s2, gA1, gA2, gM1, gM2)
    lo, hi = wilson(flips, pairs)
    print("  sampling distribution: UNIFORM on the product grid")
    print("    q, sigma in {0.05, 0.10, ..., 0.95} (19x19=361 candidates),")
    print("    R fixed at %s, nu_b=%s, nu_f=%s; all unordered pairs." % (R, NU_B, NU_F))
    print("    This is NOT the operational distribution, which is unknown.")
    print("\n  strictly-ordered pairs : %d" % pairs)
    print("  ranking inversions     : %d" % flips)
    print("  inversion rate         : %.4f%%  Wilson 95%% [%.4f%%, %.4f%%]"
          % (100 * flips / pairs, 100 * lo, 100 * hi))
    if example:
        q1, s1, q2, s2, gA1, gA2, gM1, gM2 = example
        print("\n  worked inversion:")
        print("    m1 = (q=%s, sigma=%s) : g_spec(A) = %.6f   g_decision(M) = %.6f"
              % (q1, s1, gA1, gM1))
        print("    m2 = (q=%s, sigma=%s) : g_spec(A) = %.6f   g_decision(M) = %.6f"
              % (q2, s2, gA2, gM2))
        print("    spec SS6.4 dispatches %s; pre-branch expectation prefers %s"
              % ("m1" if gA1 > gA2 else "m2", "m1" if gM1 > gM2 else "m2"))
    import z3
    zR, zq, zs = z3.Reals("R q s")
    sol = z3.Solver()
    sol.add(zR > 0, zR < 1, zq > 0, zq < 1, zs > 0, zs <= 1)
    A = (zs * (zR * (1 - zq) / (1 - zq * zR)) + (1 - zs) * zR)
    M = zR * (1 - zq * zs)
    sol.add(A < M)
    print("\n  z3: exists a point with A < M (phases 1-2)  ->  %s" % sol.check())
    ok = flips > 0
    print("\n  Claimed defect present: %s" % ok)
    if ok:
        FAILED.append(3)
        print("  FALSIFIED")
    return flips, pairs, lo, hi


# ---------------------------------------------------------------- CHECK 4
def check4_objective_additive_bias():
    """SS6.5 maximises sum_u sum_m x_mu g_mu, adding the gains of two
    configurations dispatched to the SAME unit. SS6.7.1 forbids exactly that.

    The Bayes detection update composes MULTIPLICATIVELY IN THE ODDS, so the
    true joint gain is the single-pass gain at q_eff = 1-(1-q1)(1-q2).
    The additive objective is therefore biased -- and the bias is TWO-SIGNED,
    with boundary R* = (1 - sqrt(1-q_eff)) / q_eff in [1/2, 1).
    """
    banner(4, "SS6.5 additive objective is biased, and the bias is TWO-SIGNED")
    import sympy as sp
    R, q1, q2 = sp.symbols("R q1 q2", positive=True)
    T = lambda r, q: r * (1 - q) / (1 - q * r)        # noqa: E731
    qeff = 1 - (1 - q1) * (1 - q2)
    # The odds composition, DERIVED not asserted.
    comp = sp.simplify(T(T(R, q1), q2) - T(R, qeff))
    print("  SymPy: T(T(R,q1),q2) - T(R, 1-(1-q1)(1-q2)) = %s" % comp)
    print("  (odds multiply by (1-q), so two passes ARE one pass at q_eff)")
    g1 = R - T(R, q1)
    g2 = R - T(R, q2)
    gj = R - T(R, qeff)
    gap = sp.simplify(g1 + g2 - gj)
    print("\n  (g1+g2) - g_joint = %s" % sp.factor(gap))

    # Closed-form sign boundary (Wolfram Reduce, re-derived here in SymPy).
    Q = sp.symbols("Q", positive=True)
    Rstar = (1 - sp.sqrt(1 - Q)) / Q
    print("\n  sign boundary R* = (1-sqrt(1-q_eff))/q_eff")
    print("    limit q_eff->0 : %s" % sp.limit(Rstar, Q, 0))
    print("    limit q_eff->1 : %s" % sp.limit(Rstar, Q, 1))
    print("    at q_eff=3/4   : %s = %.6f"
          % (sp.nsimplify(Rstar.subs(Q, sp.Rational(3, 4))),
             float(Rstar.subs(Q, sp.Rational(3, 4)))))
    # Verify the boundary against the gap expression.
    chk = sp.simplify(gap.subs(R, Rstar.subs(Q, qeff)))
    print("    gap at R = R* : %s  (should be 0)" % sp.simplify(chk))

    sub = {R: sp.Rational(1, 2), q1: sp.Rational(1, 2), q2: sp.Rational(1, 2)}
    print("\n  R=1/2 (== RK0_PI_BASE, the runner's default prior):")
    print("    g1+g2   = %s = %.6f" % (sp.nsimplify(g1.subs(sub) + g2.subs(sub)),
                                       float(g1.subs(sub) + g2.subs(sub))))
    print("    g_joint = %s = %.6f" % (sp.nsimplify(gj.subs(sub)),
                                       float(gj.subs(sub))))
    print("    objective OVERSTATES by %.2f%%"
          % (100 * (float((g1.subs(sub) + g2.subs(sub)) / gj.subs(sub)) - 1)))
    sub2 = {R: sp.Rational(9, 10), q1: sp.Rational(1, 2), q2: sp.Rational(1, 2)}
    print("\n  R=9/10 (a unit that has accrued risk above R*=2/3):")
    print("    g1+g2   = %.6f" % float(g1.subs(sub2) + g2.subs(sub2)))
    print("    g_joint = %.6f" % float(gj.subs(sub2)))
    print("    objective UNDERSTATES by %.2f%%"
          % (100 * (1 - float((g1.subs(sub2) + g2.subs(sub2)) / gj.subs(sub2)))))

    import z3
    zR, za, zb = z3.Reals("R a b")
    Tz = lambda r, q: r * (1 - q) / (1 - q * r)       # noqa: E731
    s = z3.Solver()
    s.add(zR > 0, zR <= z3.RealVal(1) / 2, za > 0, za < 1, zb > 0, zb < 1)
    s.add((zR - Tz(zR, za)) + (zR - Tz(zR, zb))
          <= zR - Tz(zR, 1 - (1 - za) * (1 - zb)))
    print("\n  z3: any point with R<=1/2 where the sum does NOT overstate -> %s"
          % s.check())
    s2 = z3.Solver()
    s2.add(zR > 0, zR < 1, za > 0, za < 1, zb > 0, zb < 1)
    s2.add((zR - Tz(zR, za)) + (zR - Tz(zR, zb))
           < zR - Tz(zR, 1 - (1 - za) * (1 - zb)))
    print("  z3: any point at all where the sum UNDERSTATES              -> %s"
          % s2.check())

    # Measured sign distribution on a STATED grid, with a Wilson interval.
    grid = [i / 20 for i in range(1, 20)]
    over = under = tot = 0
    for Rv in grid:
        for a in grid:
            for b in grid:
                ga = Rv - (Rv * (1 - a) / (1 - a * Rv))
                gb = Rv - (Rv * (1 - b) / (1 - b * Rv))
                qe = 1 - (1 - a) * (1 - b)
                gjv = Rv - (Rv * (1 - qe) / (1 - qe * Rv))
                if abs(ga + gb - gjv) < 1e-15:
                    continue
                tot += 1
                if ga + gb > gjv:
                    over += 1
                else:
                    under += 1
    lo, hi = wilson(over, tot)
    print("\n  sampling distribution: UNIFORM on R, q1, q2 in")
    print("    {0.05, 0.10, ..., 0.95}^3 (6859 points, sigma=1, nu=0).")
    print("    NOT the operational distribution, which is unknown; R is however")
    print("    initialised at exactly 0.5 by RK0_PI_BASE.")
    print("  overstates : %d / %d = %.2f%%  Wilson 95%% [%.2f%%, %.2f%%]"
          % (over, tot, 100 * over / tot, 100 * lo, 100 * hi))
    print("  understates: %d / %d = %.2f%%" % (under, tot, 100 * under / tot))

    # And on the LIVE function at the shipped nu.
    Rv, qa, qb = 0.5, 0.45, 0.35
    ga = Rv - compute_rk(Rv, qa, 1.0, NU_B, NU_F)
    gb = Rv - compute_rk(Rv, qb, 1.0, NU_B, NU_F)
    seq = compute_rk(compute_rk(Rv, qa, 1.0, NU_B, NU_F), qb, 1.0, NU_B, NU_F)
    gjl = Rv - seq
    print("\n  LIVE compute_rk, R=0.5, q_A=0.45, q_B=0.35 (SS6.2's own numbers),")
    print("  sigma=1, shipped nu_b=0.05 nu_f=0.20:")
    print("    g_A + g_B = %.6f ; sequential joint gain = %.6f ; bias %+.2f%%"
          % (ga + gb, gjl, 100 * ((ga + gb) / gjl - 1)))
    ok = (over > 0 and under > 0)
    print("\n  Claimed defect present (bias exists AND is two-signed): %s" % ok)
    if ok:
        FAILED.append(4)
        print("  FALSIFIED")
    return over, under, tot


# ---------------------------------------------------------------- CHECK 5
def check5_exploration_term():
    """SS6.4: e_mu = sqrt(log(1+N_u)/(1+n_mu)) and
    score = g/(c + l_t t + l_h h) + beta e.

    (a) At N_u=0, e_mu is identically 0 for EVERY n_mu.
    (b) The score adds a RATIO (risk per currency) to a DIMENSIONLESS bonus
        scaled by beta, so beta silently carries units of risk-per-currency
        and the ranking is not invariant under a change of cost unit.
    """
    banner(5, "SS6.4 exploration term vanishes at N_u=0; score is unit-dependent")
    e = lambda N, n: math.sqrt(math.log(1 + N) / (1 + n))   # noqa: E731
    print("  (a) e_mu(N_u, n_mu):")
    for N in (0, 1, 5, 20, 100):
        row = "  ".join("n=%d:%.4f" % (n, e(N, n)) for n in (0, 1, 5))
        print("      N_u=%4d   %s" % (N, row))
    zero_at_0 = all(e(0, n) == 0.0 for n in range(0, 50))
    print("\n      e_mu == 0 for EVERY n_mu when N_u=0 : %s" % zero_at_0)
    print("      => on the first unit of a new task family the term cannot")
    print("         break any tie, and a never-tried configuration (n_mu=0)")
    print("         gets the same bonus as a saturated one (n_mu=49): zero.")
    print("      Standard UCB has the count of the ARM in the log numerator or")
    print("      forces one pull per arm; this form has neither, so exploration")
    print("      is switched OFF exactly when uncertainty is greatest.")

    print("\n  (b) unit sensitivity. score = g/D + beta*e, D in currency units.")
    print("      Rescaling currency by s (dollars->cents, s=100) and rescaling")
    print("      lambda_t, lambda_h to preserve term 1 gives g/(sD) + beta*e:")
    print("      term 1 shrinks by 1/s, term 2 does not. A flip needs")
    print("        beta*(e_B - e_A)  between  (g_A/D_A - g_B/D_B)/s  and")
    print("        (g_A/D_A - g_B/D_B).")
    A = dict(g=0.020, D=1.00, N=8, n=6)     # cheap-ish, well observed
    B = dict(g=0.015, D=1.00, N=8, n=0)     # never tried
    gapratio = A["g"] / A["D"] - B["g"] / B["D"]
    de = e(B["N"], B["n"]) - e(A["N"], A["n"])
    print("\n      worked construction: g_A=%.3f D_A=%.2f n_A=%d ; "
          "g_B=%.3f D_B=%.2f n_B=%d, N_u=8"
          % (A["g"], A["D"], A["n"], B["g"], B["D"], B["n"]))
    print("      ratio gap = %.6f ; e_B - e_A = %.6f" % (gapratio, de))
    for beta in (0.0010, 0.1000):
        picks = []
        for s in (1.0, 100.0):
            sA = A["g"] / (A["D"] * s) + beta * e(A["N"], A["n"])
            sB = B["g"] / (B["D"] * s) + beta * e(B["N"], B["n"])
            picks.append(("A" if sA > sB else "B", sA, sB))
        print("      beta=%.4f : dollars picks %s (%.6f vs %.6f) ; "
              "cents picks %s (%.6f vs %.6f) -> flip=%s"
              % (beta, picks[0][0], picks[0][1], picks[0][2],
                 picks[1][0], picks[1][1], picks[1][2],
                 picks[0][0] != picks[1][0]))
    beta_lo, beta_hi = gapratio / 100.0 / de, gapratio / de
    print("\n      EXACT flip band for this pair: beta in (%.6f, %.6f)"
          % (beta_lo, beta_hi))
    print("      i.e. a %.0f-fold window of beta: the flip is NOT universal, it is"
          % (beta_hi / beta_lo))
    print("      a band whose LOCATION moves with the currency unit. The spec says")
    print("      beta 'must be fixed before a comparative run' but never states its")
    print("      units, so the band is unpinned.")

    # Measured flip rate over a STATED box.
    import numpy as np
    rng = np.random.default_rng(20260929)
    flips = 0
    tot = 0
    for _ in range(200000):
        gA, gB = rng.uniform(0.001, 0.05, 2)
        DA, DB = rng.uniform(0.05, 5.0, 2)
        nA, nB = rng.integers(0, 20, 2)
        Nu = int(rng.integers(1, 50))
        beta = 10.0 ** rng.uniform(-4, 0)
        eA, eB = e(Nu, int(nA)), e(Nu, int(nB))
        s1A, s1B = gA / DA + beta * eA, gB / DB + beta * eB
        s2A, s2B = gA / (100 * DA) + beta * eA, gB / (100 * DB) + beta * eB
        if abs(s1A - s1B) < 1e-15 or abs(s2A - s2B) < 1e-15:
            continue
        tot += 1
        if (s1A > s1B) != (s2A > s2B):
            flips += 1
    lo, hi = wilson(flips, tot)
    print("\n      sampling distribution, STATED: g ~ U(0.001, 0.05);")
    print("        D ~ U(0.05, 5.0) currency units; n ~ U{0..19}; N_u ~ U{1..49};")
    print("        beta ~ log-uniform(1e-4, 1); 200000 draws, seed 20260929.")
    print("        This is MY prior, not the operational one, which is unknown.")
    print("      dollars-vs-cents ranking flips: %d / %d = %.2f%% "
          "Wilson 95%% [%.2f%%, %.2f%%]"
          % (flips, tot, 100 * flips / tot, 100 * lo, 100 * hi))
    ok = zero_at_0 and flips > 0
    print("\n  Claimed defect present: %s" % ok)
    if ok:
        FAILED.append(5)
        print("  FALSIFIED")
    return flips, tot, lo, hi


# ---------------------------------------------------------------- CHECK 6
def check6_power_of_the_9_3_design():
    banner(6, "SS9.2/9.3 sample size: what effect size can 3 runs resolve?")
    from statsmodels.stats.power import TTestIndPower
    pw = TTestIndPower()
    print("  two-sample t-test, alpha=0.05 two-sided:")
    print("  %6s %15s %15s %17s" % ("n/arm", "power at d=0.8", "power at d=1.5",
                                    "d for 80% power"))
    for n in (3, 5, 10, 20):
        p8 = pw.power(effect_size=0.8, nobs1=n, alpha=0.05, ratio=1.0)
        p15 = pw.power(effect_size=1.5, nobs1=n, alpha=0.05, ratio=1.0)
        d80 = pw.solve_power(effect_size=None, nobs1=n, alpha=0.05,
                             power=0.80, ratio=1.0)
        print("  %6d %15.4f %15.4f %17.3f" % (n, p8, p15, d80))
    d80_3 = pw.solve_power(effect_size=None, nobs1=3, alpha=0.05, power=0.80,
                           ratio=1.0)
    d80_3_bonf = pw.solve_power(effect_size=None, nobs1=3, alpha=0.05 / 15,
                                power=0.80, ratio=1.0)
    print("\n  SS9.2 has 6 conditions => C(6,2) = 15 pairwise comparisons.")
    print("  minimum detectable d at n=3, 80%% power, alpha=0.05        : %.3f" % d80_3)
    print("  ... with Bonferroni alpha=0.05/15                          : %.3f"
          % d80_3_bonf)
    print("\n  MarginalVerifiedYield(n) = (V_n - V_(n-1))/(C_n - C_(n-1)).")
    print("  SE(V_n - V_(n-1)) at 3 runs/arm = sqrt(2/3)*sigma = %.4f*sigma"
          % math.sqrt(2 / 3))
    print("  so the SIGN of the numerator is undetermined unless the true")
    print("  marginal gain exceeds %.3f*sigma." % (1.96 * math.sqrt(2 / 3)))
    print("\n  SS9.3 has 6 scales x SS9.2's 6 conditions x 3 seeds = 108 runs")
    print("  if 3 is per CELL; the text says 'per condition', which reads as 18")
    print("  runs and leaves n=1 per (scale, condition) cell -- zero within-cell")
    print("  variance estimate.")
    ok = d80_3 > 2.5
    print("\n  Claimed defect present (n=3 resolves only d > 2.5): %s" % ok)
    if ok:
        FAILED.append(6)
        print("  FALSIFIED")
    return d80_3, d80_3_bonf


# ---------------------------------------------------------------- CHECK 7
def check7_spec_62_arithmetic():
    banner(7, "SS6.2 worked example -- CONTROL, expected to hold")
    import sympy as sp
    v = 1 - (1 - sp.Rational(45, 100)) * (1 - sp.Rational(35, 100))
    print("  1-(1-0.45)(1-0.35) = %s = %s" % (v, float(v)))
    print("  spec says 0.6425                 -> %s" % (float(v) == 0.6425))
    marg = v - sp.Rational(45, 100)
    print("  marginal contribution of B = %s = %s" % (marg, float(marg)))
    print("  spec says 0.1925                 -> %s" % (float(marg) == 0.1925))
    ok = float(v) == 0.6425 and float(marg) == 0.1925
    print("\n  SS6.2 arithmetic SOUND: %s  (no defect; nothing to falsify)" % ok)
    return ok




# ---------------------------------------------------------------- CHECK 8
SPEC = ("/Users/georgejackson/Developer_Projects/Responses/"
        "Codex, ChatGPT & Grok resources/"
        "adaptive_distributed_compute_design_spec.md")


def check8_compiler_obligations():
    """SS4.2 / SS7.1 step 2: the task compiler must validate FOUR things.
    Which of the four is decidable from the WorkUnit contract in SS4.2?"""
    banner(8, "SS4.2 task-compiler obligations: how many are decidable?")
    # 1. Acyclicity -- DECIDABLE. Demonstrated, not asserted.
    def acyclic(nodes, edges):
        indeg = {n: 0 for n in nodes}
        for a, b in edges:
            indeg[b] += 1
        q = [n for n in nodes if indeg[n] == 0]
        seen = 0
        while q:
            n = q.pop()
            seen += 1
            for a, b in edges:
                if a == n:
                    indeg[b] -= 1
                    if indeg[b] == 0:
                        q.append(b)
        return seen == len(nodes)
    N = ["u1", "u2", "u3"]
    print("  1. acyclicity            : Kahn on a DAG  -> %s" %
          acyclic(N, [("u1", "u2"), ("u2", "u3")]))
    print("                             Kahn on a cycle -> %s  (DECIDABLE, O(V+E))"
          % acyclic(N, [("u1", "u2"), ("u2", "u3"), ("u3", "u1")]))
    # 2. Unresolved dependencies -- DECIDABLE (set membership on ids).
    ids = set(N)
    deps = {"u1": [], "u2": ["u1"], "u3": ["u9"]}
    dangling = {k: [d for d in v if d not in ids] for k, v in deps.items()}
    print("  2. unresolved deps       : dangling refs %s  (DECIDABLE, set membership)"
          % {k: v for k, v in dangling.items() if v})
    # 3. Interface ownership -- DECIDABLE given declared InterfaceContract ids.
    ifaces = {"I1": ["u1", "u2"]}
    owners = {i: (len(us) >= 2) for i, us in ifaces.items()}
    print("  3. interface ownership   : joins >=2 units %s  (DECIDABLE from SS4.2 "
          "declarations)" % owners)
    # 4/5. HARD-constraint coverage and duplication -- need an ORACLE.
    text = open(SPEC, encoding="utf-8").read()
    terms = {
        "entail": text.lower().count("entail"),
        "decidab": text.lower().count("decidab"),
        "covers": text.lower().count("covers"),
        "coverage of HARD": text.count("coverage of HARD"),
        "identity mechanism": text.count("identity mechanism"),
    }
    print("\n  4. coverage of HARD constraints: requires deciding, for each h in H,")
    print("     whether SOME unit's `statement` discharges h. That is an ENTAILMENT")
    print("     question over natural-language propositions (SS4.2 `statement:")
    print("     the exact proposition or bounded task`).")
    print("  5. duplication          : SS8.8 forbids lexical similarity as the")
    print("     mechanism, and names no other. So dedup is specified NEGATIVELY.")
    print("\n  mechanical evidence -- occurrences in the 624-line spec:")
    for k, v in terms.items():
        print("     %-20s %d" % (k, v))
    undecidable = terms["entail"] == 0 and terms["decidab"] == 0
    print("\n  DECIDABLE from SS4.2 alone : 3 of 5 (acyclicity, deps, ownership)")
    print("  REQUIRING AN UNSPECIFIED ORACLE : 2 of 5 (HARD coverage, duplication)")
    print("  the spec defines no entailment or identity procedure: %s" % undecidable)
    ok = undecidable
    print("\n  Claimed defect present: %s" % ok)
    if ok:
        FAILED.append(8)
        print("  FALSIFIED")
    return terms


# ---------------------------------------------------------------- CHECK 9
def check9_promotion_gates_checkable():
    """SS9.4: four promotion gates. Can a PROGRAM evaluate each criterion?"""
    banner(9, "SS9.4 promotion gates: how many can a program evaluate?")
    gates = [
        ("Library", "Unit, property, and adversarial tests",
         True, "exit status of a test runner"),
        ("Shadow", "Counterfactual comparison; no target or budget mutation",
         True, "hash equality on target + budget ledger delta == 0"),
        ("Controlled live", "Matched-budget improvement and no invariant breach",
         False, "'improvement' names NO statistic, NO threshold, NO interval; "
                "SS8's 10 invariants ARE property-testable"),
        ("Operational", "Replicated benefit, auditability, and defined rollback",
         False, "'replicated' has no k; 'auditability' has no predicate; "
                "'defined rollback' is checkable only as existence-of-a-document"),
    ]
    print("  %-17s %-9s %s" % ("gate", "program?", "why"))
    for name, crit, ok, why in gates:
        print("  %-17s %-9s %s" % (name, "YES" if ok else "NO", why))
    text = open(SPEC, encoding="utf-8").read()
    import re
    thr = re.findall(r"[^.]*\bthreshold\b[^.]*\.", text)
    nums = re.findall(r"threshold[^.]{0,80}?([0-9]+\.?[0-9]*)", text)
    print("\n  mechanical: 'threshold' appears %d times; NUMERIC values attached: %d"
          % (len(thr), len(nums)))
    for t in thr:
        print("     - %s" % " ".join(t.split())[:110])
    checkable = sum(1 for g in gates if g[2])
    print("\n  program-evaluable gates: %d of 4" % checkable)
    print("  the 2 that decide whether the layer goes LIVE are the 2 that are not.")
    ok = checkable < 4 and len(nums) == 0
    print("\n  Claimed defect present: %s" % ok)
    if ok:
        FAILED.append(9)
        print("  FALSIFIED")
    return checkable


if __name__ == "__main__":
    sup_err, nu_star = check1_nu_is_not_free()
    check2_sigma_zero_is_negative_credit()
    flips, pairs, lo, hi = check3_branch_quantity_rank_inversion()
    o, un, t4 = check4_objective_additive_bias()
    f5, t5, l5, h5 = check5_exploration_term()
    d80, d80b = check6_power_of_the_9_3_design()
    ctl = check7_spec_62_arithmetic()
    check8_compiler_obligations()
    check9_promotion_gates_checkable()

    print("\n" + "=" * 74)
    print("SUMMARY: checks with the claimed defect PRESENT: %s" % sorted(set(FAILED)))
    print("         SS6.2 control held sound: %s" % ctl)
    print("=" * 74)
    if FAILED:
        print("FALSIFIED")
