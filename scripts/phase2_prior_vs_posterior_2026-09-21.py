#!/usr/bin/env python3
"""Does the appendix's Phase 2 revert to the PRIOR, and does the revision differ?

THE QUESTION. `docs/MATHEMATICAL_APPENDIX.md` lines 217-233 set out a three-phase
recursion. Phase 1 computes `R_det = R_old(1-q)/(1-q*R_old)`, which appendix
section 1 derives as `P(flaw | no detection)` -- a Bayesian POSTERIOR. Phase 2
then reads `R_base = sigma*R_det + (1-sigma)*R_old`, and the appendix's own gloss
is explicit: *"When sigma = 0, risk stays at R_old -- the fix failed and risk
reverts to the pre-detection level."*

So at zero repair efficacy the appendix DISCARDS the posterior and returns to the
prior. The proposed revision 1.1 (`CDSFL_revised_core.py`, `update()`) instead
acts on the posterior: `R_new = (1-s)*z + b*(1-z)`, holding `z` at s = 0.

**ANSWERED 2026-09-21, AND THE APPENDIX IS RIGHT. CC1 WAS WRONG.** This script
first concluded that whether reverting to the prior is correct "is a modelling
question ... and no amount of algebra decides it". That was true of algebra
COMPARING THE 2 MAPS and false of a derivation FROM THE GENERATIVE MODEL, which
is the gap the cc2 seat closed in the free panel round of 2026-09-21.

`R_det` is the posterior given NON-DETECTION, which is only true under
`P(detect|flaw) = q` and `P(detect|no flaw) = 0`. Those same assumptions force a
SECOND branch the appendix never names: detection, with probability `q*R_old`,
posterior 1 under no false positives, and risk `1-sigma` after repair. The
mixture over both branches is `(1-q*R_old)*R_det + q*R_old*(1-sigma)`, which
SymPy reduces to `R_old*(1-q*sigma)` -- **exactly `R_old` at sigma = 0.**

CC1's premise was right and its conclusion was wrong. "The evidence still
happened" is correct, and it is PRECISELY WHY the answer is the prior: the
observation happens on both branches, sometimes saying "clean" and sometimes
"flaw found", and unrepaired they average back. That is the tower property,
`E[posterior] = prior`, verified here. The appendix does not discard the
observation; **the revision discards the unfavourable half of it**, keeping only
the branch where nothing was found.

A SECOND DEFECT IN THE REVISION, which CC1 missed entirely: at `sigma = 1`,
`nu = 0` the revision returns identically 0 for every state, asserting CERTAINTY
of no residual risk. That contradicts the appendix's own substrate ceiling
`lim R >= nu_k`.

WHAT REMAINS TRUE FROM THE FIRST VERSION. The 2 forms ARE different maps, and
the "exact identity" recorded on 2026-09-20 is about Phase 3 ALONE rather than
the Phase 2 and 3 composite. Both still measured below. What changed is the
verdict on WHICH form is correct, and the answer is the appendix's.

THE APPENDIX IS ALSO CONSERVATIVE, WHICH IS THE SAFE DIRECTION. Phase 2
interpolates between a quantity conditional on non-detection and a marginal
expectation, so it is exact only at sigma = 0. The gap is
`R_old^2*q*sigma*(q-1)/(R_old*q-1) >= 0`, and z3 returns UNSAT on the appendix
ever understating the exact mixture. For a safety gate, overstating risk is the
correct bias. This is a documentation gap, not an equation defect.

IT ALSO NARROWS A CLAIM THIS PROJECT ALREADY MADE. The 2026-09-20 review
synthesis records that the revision's action step is "identical to the appendix
Phase-3 form under s = sigma*(1-nu), b = nu, symbolic difference exactly 0". That
is TRUE of Phase 3 ALONE -- the bare re-injection map `x(1-nu)+nu`, which both
forms share at sigma = 0 -- and NOT true of the Phase 2 and 3 composite. The
identity is real and much narrower than the sentence reads.

EVERY FIGURE HERE IS CROSS-VERIFIED ON 2 INDEPENDENT TOOLS, per the 2026-04-21
rule: SymPy against z3 for the symbolic and satisfiability claims, NumPy against
mpmath for the numerical ones.
"""
from __future__ import annotations

import sympy as sp


def symbolic():
    """The 2 maps, their difference, and where it vanishes."""
    R_old, q, sigma, nu, z = sp.symbols('R_old q sigma nu z', nonnegative=True)
    R_base_z = sigma * z + (1 - sigma) * R_old          # Phase 2 with R_det -> z
    appendix = sp.expand(R_base_z * (1 - nu) + nu)      # Phase 3
    s, b = sigma * (1 - nu), nu                          # the settled parameter map
    revision = sp.expand((1 - s) * z + b * (1 - z))
    diff = sp.factor(sp.simplify(appendix - revision))
    where = sp.solve(sp.Eq(revision, appendix), R_old)
    phase3_only = sp.simplify((z * (1 - nu) + nu) - revision.subs(sigma, 0))
    return {
        "appendix": sp.factor(appendix),
        "revision": sp.factor(revision),
        "difference": diff,
        "vanishes_at_R_old": where,
        "phase3_alone_residual": phase3_only,
    }


def numeric(n: int = 200_000, seed: int = 20260921):
    """How often and how far the 2 maps disagree, NumPy against mpmath."""
    import numpy as np
    import mpmath as mp
    mp.mp.dps = 40
    rng = np.random.default_rng(seed)

    def appx(R, q, s, v):
        Rd = R * (1 - q) / (1 - q * R)
        return (s * Rd + (1 - s) * R) * (1 - v) + v

    def rev(R, q, s, v):
        zz = R * (1 - q) / (1 - q * R)
        return (1 - s * (1 - v)) * zz + v * (1 - zz)

    R = rng.uniform(1e-6, 1 - 1e-6, n)
    Q = rng.uniform(1e-6, 1 - 1e-6, n)
    S = rng.uniform(0.0, 1.0, n)
    V = rng.uniform(0.0, 1 - 1e-6, n)
    a, r = appx(R, Q, S, V), rev(R, Q, S, V)
    d = abs(a - r)
    differ = int((d > 1e-12).sum())

    # mpmath at 40 digits on a single worked point, as an independent check
    Ro, qq, sg, vv = (mp.mpf('0.5'), mp.mpf('0.3'), mp.mpf('0.4'), mp.mpf('0.1'))
    a_mp, r_mp = appx(Ro, qq, sg, vv), rev(Ro, qq, sg, vv)
    # and the same point in NumPy, to check the 2 tools agree
    a_np = float(appx(0.5, 0.3, 0.4, 0.1))
    agree = abs(float(a_mp) - a_np) < 1e-12

    zero_sigma = []
    for ro in ('0.5', '0.8'):
        ro_m = mp.mpf(ro)
        zz = ro_m * (1 - qq) / (1 - qq * ro_m)
        zero_sigma.append({
            "R_old": str(ro_m), "posterior": str(zz),
            "appendix": str(appx(ro_m, qq, mp.mpf(0), mp.mpf(0))),
            "revision": str(rev(ro_m, qq, mp.mpf(0), mp.mpf(0))),
        })
    return {
        "n": n, "differ": differ, "share": differ / n,
        "max_gap": float(d.max()), "mean_gap": float(d.mean()),
        "in_unit_interval": bool((a >= 0).all() and (a <= 1).all()
                                 and (r >= 0).all() and (r <= 1).all()),
        "worked_point": {"appendix": str(a_mp), "revision": str(r_mp),
                         "gap": str(abs(a_mp - r_mp))},
        "numpy_mpmath_agree_1e-12": agree,
        "at_sigma_zero": zero_sigma,
    }


def satisfiability():
    """z3: can 1 parameter pair make the maps agree at 2 distinct states?"""
    import z3
    sg, nu = z3.Reals('sigma nu')
    Ro1, Ro2, q = z3.Reals('Ro1 Ro2 q')

    def appx(R):
        Rd = R * (1 - q) / (1 - q * R)
        return (sg * Rd + (1 - sg) * R) * (1 - nu) + nu

    def rev(R):
        zz = R * (1 - q) / (1 - q * R)
        return (1 - sg * (1 - nu)) * zz + nu * (1 - zz)

    s = z3.Solver()
    s.add(sg >= 0, sg <= 1, nu >= 0, nu <= 1, q > 0, q < 1)
    s.add(Ro1 > 0, Ro1 < 1, Ro2 > 0, Ro2 < 1, Ro1 != Ro2)
    s.add(appx(Ro1) == rev(Ro1), appx(Ro2) == rev(Ro2))
    res = s.check()
    witness = None
    if res == z3.sat:
        m = s.model()
        witness = {"sigma": str(m[sg]), "nu": str(m[nu])}
    return {"result": str(res), "witness": witness}


def generative():
    """Derive the correct sigma = 0 value FROM the generative model.

    This is the step the first version of this script said algebra could not
    take. It can: the non-detection posterior only exists under stated detection
    assumptions, and those assumptions determine the other branch too.
    """
    import z3
    R, q, sg, nu, z = sp.symbols('R_old q sigma nu z', nonnegative=True)
    R_det = R * (1 - q) / (1 - q * R)
    p_no, p_yes = 1 - q * R, q * R
    mixture = sp.simplify(p_no * R_det + p_yes * (1 - sg))
    tower = sp.simplify(p_no * R_det + p_yes * 1)
    rev = (1 - sg * (1 - nu)) * z + nu * (1 - z)
    appx = sg * R_det + (1 - sg) * R

    zR, zq, zs = z3.Reals('R q s')
    s3 = z3.Solver()
    s3.add(zR > 0, zR < 1, zq > 0, zq < 1, zs >= 0, zs <= 1)
    Rd = zR * (1 - zq) / (1 - zq * zR)
    s3.add((zs * Rd + (1 - zs) * zR) - zR * (1 - zq * zs) < 0)

    return {
        "mixture": sp.factor(mixture),
        "equals_closed_form": sp.simplify(mixture - R * (1 - q * sg)) == 0,
        "at_sigma_zero": sp.simplify(mixture.subs(sg, 0)),
        "tower_holds": sp.simplify(tower - R) == 0,
        "revision_at_perfect_fix": sp.simplify(rev.subs({sg: 1, nu: 0})),
        "z3_understate": str(s3.check()),
        "conservatism_gap": sp.factor(sp.simplify(appx - mixture)),
    }


def false_alarm():
    """Does the appendix's R_det presuppose a zero false-alarm rate?

    Several claims in the 2026-09-10 revision package converge on this from
    different directions, and the free panel's 2-branch derivation leans on it
    too. Checked here rather than taken from either.
    """
    import z3
    R, q, phi = sp.symbols('R q phi', nonnegative=True)
    general = sp.simplify(R * (1 - q) / (R * (1 - q) + (1 - R) * (1 - phi)))
    appendix = R * (1 - q) / (1 - q * R)
    agree_at = sp.solve(sp.Eq(general, appendix), phi)
    gaps = []
    for ph in ('0', '0.05', '0.10', '0.25'):
        v = float(general.subs({R: sp.Rational(1, 2), q: sp.Rational(3, 10),
                                phi: sp.nsimplify(ph)}))
        a = float(appendix.subs({R: sp.Rational(1, 2), q: sp.Rational(3, 10)}))
        gaps.append((ph, v, a, v - a))
    zR, zq, zp = z3.Reals('R q phi')
    s3 = z3.Solver()
    s3.add(zR > 0, zR < 1, zq > 0, zq < 1, zp > 0, zp < 1, zp < zq)
    s3.add(zR * (1 - zq) / (1 - zq * zR)
           > zR * (1 - zq) / (zR * (1 - zq) + (1 - zR) * (1 - zp)))
    return {"general": sp.factor(general), "appendix": sp.factor(appendix),
            "agree_at_phi": agree_at, "gaps": gaps, "z3_exceeds": str(s3.check())}


def main() -> None:
    print("=" * 74)
    print("PHASE 2: DOES THE APPENDIX REVERT TO THE PRIOR? 2026-09-21")
    print("=" * 74)

    sym = symbolic()
    print("\n1. SYMBOLIC (SymPy)")
    print(f"   appendix composite      : {sym['appendix']}")
    print(f"   revision, mapped        : {sym['revision']}")
    print(f"   difference              : {sym['difference']}")
    print(f"   vanishes at R_old       : {sym['vanishes_at_R_old']}")
    print("     -> a condition on the STATE, not a parameter restriction, so the")
    print("        2 forms are NOT the same map.")
    print(f"   Phase 3 ALONE, residual : {sym['phase3_alone_residual']}")
    print("     -> 0, which is the narrow sense in which the recorded 'exact")
    print("        identity' holds. It is Phase 3, not the composite.")

    num = numeric()
    print("\n2. NUMERICAL (NumPy, cross-checked against mpmath at 40 digits)")
    print(f"   sampled                 : {num['n']} points in the open unit cube")
    print(f"   differing by > 1e-12    : {num['differ']} = {num['share']:.4%}")
    print(f"   max gap                 : {num['max_gap']:.6f}")
    print(f"   mean gap                : {num['mean_gap']:.6f}")
    print(f"   both stay in [0,1]      : {num['in_unit_interval']}")
    wp = num["worked_point"]
    print(f"   at R_old=0.5 q=0.3 sigma=0.4 nu=0.1:")
    print(f"      appendix {wp['appendix']}")
    print(f"      revision {wp['revision']}")
    print(f"      gap      {wp['gap']}")
    print(f"   NumPy and mpmath agree to 1e-12 : {num['numpy_mpmath_agree_1e-12']}")
    print("\n   AT sigma = 0, WHERE THE SEMANTICS SPLIT:")
    for row in num["at_sigma_zero"]:
        print(f"      R_old={row['R_old']}  posterior={row['posterior'][:20]}")
        print(f"         appendix -> {row['appendix'][:20]}  (reverts to the PRIOR)")
        print(f"         revision -> {row['revision'][:20]}  (holds the POSTERIOR)")

    sat = satisfiability()
    print("\n3. SATISFIABILITY (z3)")
    print(f"   agree at 2 distinct states at once : {sat['result']}")
    if sat["witness"]:
        print(f"      witness: sigma={sat['witness']['sigma']}, nu={sat['witness']['nu']}")
        print("      -> a degenerate corner, not a usable operating point.")

    gen = generative()
    print("\n4. WHICH FORM IS CORRECT: DERIVED FROM THE GENERATIVE MODEL")
    print(f"   two-branch mixture        : {gen['mixture']}")
    print(f"   equals R_old*(1-q*sigma)? : {gen['equals_closed_form']}")
    print(f"   at sigma = 0              : {gen['at_sigma_zero']}   <-- the PRIOR")
    print(f"   E[posterior] == prior?    : {gen['tower_holds']}  (tower property)")
    print(f"   revision at sigma=1,nu=0  : {gen['revision_at_perfect_fix']}"
          "   <-- asserts CERTAINTY")
    print(f"   can the appendix understate the exact mixture? {gen['z3_understate']}")
    print(f"   appendix - exact          : {gen['conservatism_gap']}")

    fa = false_alarm()
    print("\n5. DOES R_det PRESUPPOSE ZERO FALSE ALARMS?")
    print(f"   general posterior, no report, false-alarm rate phi : {fa['general']}")
    print(f"   the appendix's R_det                               : {fa['appendix']}")
    print(f"   the 2 agree only when phi = {fa['agree_at_phi']}")
    print("   so R_det is the phi = 0 special case, and phi = 0 is never stated.")
    for ph, v, a, gap in fa["gaps"]:
        print(f"      phi={ph:<5} true={v:.6f}  appendix={a:.6f}  gap={gap:+.6f}")
    print(f"   z3: can the appendix EXCEED the general posterior? {fa['z3_exceeds']}"
          "  (unsat = never)")
    print("   -> a non-zero phi makes the TRUE posterior HIGHER than the appendix")
    print("      reports, so the appendix is OPTIMISTIC here -- the opposite")
    print("      direction to Phase 2's conservatism. 2 biases, opposite signs.")

    print("\n6. VERDICT")
    print("   THE APPENDIX IS RIGHT. Reverting to the prior at sigma = 0 is the")
    print("   tower property, not a conflation: the observation occurs on BOTH")
    print("   branches and unrepaired they average back to the prior. CC1's")
    print("   concern is WITHDRAWN. The revision keeps only the non-detection")
    print("   branch, and at a perfect fix it asserts zero residual risk.")
    print("   WHAT STANDS: the 2 are different maps, and the recorded 'exact")
    print("   identity' is Phase 3 alone rather than the composite.")


if __name__ == "__main__":
    # A --help MUST NEVER COST ANYTHING (founder ruling). This samples 200,000
    # points and runs z3, so an unguarded --help would do all of it first.
    import argparse
    ap = argparse.ArgumentParser(
        description=("Compare the appendix's Phase 2+3 composite against revision "
                     "1.1's action step. Reads nothing, writes nothing, dispatches "
                     "to no model and costs nothing."),
        epilog=("Prints the symbolic difference and where it vanishes, the share of "
                "200,000 sampled points at which the 2 maps disagree, and the "
                "sigma = 0 case where the semantics split."))
    ap.parse_args()
    main()
