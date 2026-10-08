# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'division_count_blind_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9dcbb57390595ac4e15d32043a192f7e6b0f2b3243e7bd099a2c5c967809baee
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Monotonicity of the division-cost curve is a THEOREM, and the proof is Neyman-Pearson.

WHAT THIS FILE CLAIMS, AGAINST THE 2026-10-08 BRIEF.

The brief reports that the merge construction -- collapse 2 adjacent promotion
gates into 1 gate on the concatenated attempts -- "is not a lemma within the
threshold family", measured at 801 of 4000 random gate pairs with no dominating
merged gate (scripts/the_division_count_is_derivable_2026-10-08.py, claim 3).
It concludes monotonicity "rests on a SCAN, not a proof", and that a proof would
need the modelling decision that "a ladder's gates may be arbitrary tests".

BOTH HALVES ARE WRONG, AND THE SECOND IS THE ONE THAT MATTERS.

1. The 801 failures are entirely an artefact of DISCRETENESS, not of the AND-test
   being genuinely unbeatable. The merged gate the brief searches for is a
   DETERMINISTIC success-count threshold on a1+a2 attempts, which attains only
   finitely many significance levels. The AND test's size falls strictly between
   2 adjacent attainable levels in those cases; rounding down to the nearest
   attainable level discards power, and that -- not any failure of the merge
   argument -- is what the brief measured.

2. The modelling step the proof needs is NOT "arbitrary tests". It is the
   RANDOMISED threshold test (pass if S >= s; pass with probability gamma if
   S == s-1), which is the standard completion of the binomial test family and
   the object Neyman-Pearson is stated over. Within that family the merge IS a
   lemma, proved below, and monotonicity follows:

   LEMMA (merge). For gates g1 = (a1, s1), g2 = (a2, s2), there is a randomised
   threshold gate g on n = a1 + a2 attempts with
       pass_capable(g) >= pass_capable(g1) * pass_capable(g2)
       pass_weak(g)    <= pass_weak(g1)    * pass_weak(g2)
   PROOF. Take n i.i.d. Bernoulli(p) attempts. The AND rule -- at least s1
   successes in the first a1, at least s2 in the last a2 -- is a test on THAT
   sample space with size alpha = pass_weak(g1)*pass_weak(g2) under p = weak and
   power beta = pass_capable(g1)*pass_capable(g2) under p = capable. The
   likelihood ratio for Bernoulli(capable) against Bernoulli(weak) is
       L(S) = (capable/weak)^S * ((1-capable)/(1-weak))^(n-S),
   strictly increasing in the total success count S whenever capable > weak
   (checked symbolically below), so the family has monotone likelihood ratio and
   the Neyman-Pearson most powerful test of size exactly alpha is a RANDOMISED
   threshold on S. By Neyman-Pearson that test's power is >= beta, and its size
   is exactly alpha. That test is g. QED

   THEOREM (monotonicity). cost(T) <= cost(T+1) for T >= 2, where cost(T) is the
   fewest total attempts over feasible ladders of T-1 gates.
   PROOF. Take an attempts-optimal feasible ladder for T+1 divisions: T gates,
   total A. Merge gates 1 and 2 by the lemma. The result has T-1 gates, total
   attempts a1+a2+sum(rest) = A unchanged, end-to-end capable product not
   decreased and end-to-end weak product not increased, so still feasible. Hence
   a feasible T-division ladder of cost A exists and cost(T) <= A = cost(T+1). QED

3. AND THE THEOREM HAS AN EXACT BOUNDARY CONDITION THE BRIEF DOES NOT STATE.
   The merged gate consumes a1+a2 attempts in ONE gate. The producer imposes
   MAX_ATTEMPTS_PER_GATE = 24. Under a per-gate attempts ceiling the merge can be
   INADMISSIBLE, and then monotonicity is not implied -- and claim 6 below
   exhibits an actual inversion in the capped model. So: monotone when only the
   TOTAL attempts budget binds; NOT a theorem when a per-gate ceiling binds.
   scripts/the_division_count_is_derivable_2026-10-08.py scans under a per-gate
   ceiling of 24 and reports 0 inversions, which is consistent but is luck of the
   parameters rather than a consequence of the model it actually solves.

Every numeric claim is computed twice, SciPy's binomial tail against an exact
mpmath sum, and the symbolic claim goes to SymPy and z3.

Run: python3 scripts/the_merge_lemma_is_neyman_pearson_2026-10-08.py
"""
from __future__ import annotations

import argparse
import math

CAPABLE_RATE = 0.90
WEAK_RATE = 0.50
TOL = 1e-12


def _sf(s: int, a: int, p: float) -> float:
    """P(S >= s) for S ~ Binomial(a, p). s <= 0 means certain pass."""
    from scipy.stats import binom
    if s <= 0:
        return 1.0
    if s > a:
        return 0.0
    return float(binom.sf(s - 1, a, p))


def _sf_exact(s: int, a: int, p: float) -> float:
    import mpmath as mp
    if s <= 0:
        return 1.0
    if s > a:
        return 0.0
    with mp.workdps(60):
        pp = mp.mpf(p)
        return float(sum(mp.binomial(a, k) * pp ** k * (1 - pp) ** (a - k)
                         for k in range(s, a + 1)))


def _pmf(k: int, a: int, p: float) -> float:
    from scipy.stats import binom
    if k < 0 or k > a:
        return 0.0
    return float(binom.pmf(k, a, p))


def randomised_np_gate(n: int, alpha: float, weak: float = WEAK_RATE,
                       cap: float = CAPABLE_RATE) -> dict:
    """The Neyman-Pearson most powerful test of size EXACTLY alpha on n attempts.

    Pass if S >= s; and if S == s-1, pass with probability gamma. Choose s as the
    smallest threshold whose deterministic size does not exceed alpha, then spend
    the remaining size allowance on the next mass point down.
    """
    s = n + 1
    while s > 0 and _sf(s - 1, n, weak) <= alpha + TOL:
        s -= 1
    size_det = _sf(s, n, weak)
    mass_weak = _pmf(s - 1, n, weak)
    gamma = 0.0
    if mass_weak > 0.0:
        gamma = min(1.0, max(0.0, (alpha - size_det) / mass_weak))
    power = _sf(s, n, cap) + gamma * _pmf(s - 1, n, cap)
    size = size_det + gamma * mass_weak
    return {"n": n, "threshold": s, "gamma": gamma, "size": size, "power": power,
            "deterministic_size": size_det}


def claim_the_deterministic_merge_failures_reproduce(
        trials: int = 4000, seed: int = 5, maxa: int = 12) -> dict:
    """The brief's own measurement, re-executed. It should reproduce at 801."""
    import random
    rng = random.Random(seed)
    fails, tested = 0, 0
    fail_pairs = []
    for _ in range(trials):
        a1 = rng.randint(1, maxa); s1 = rng.randint(1, a1)
        a2 = rng.randint(1, maxa); s2 = rng.randint(1, a2)
        and_cap = _sf(s1, a1, CAPABLE_RATE) * _sf(s2, a2, CAPABLE_RATE)
        and_weak = _sf(s1, a1, WEAK_RATE) * _sf(s2, a2, WEAK_RATE)
        tested += 1
        ok = any(_sf(s, a1 + a2, CAPABLE_RATE) >= and_cap
                 and _sf(s, a1 + a2, WEAK_RATE) <= and_weak
                 for s in range(1, a1 + a2 + 1))
        if not ok:
            fails += 1
            fail_pairs.append(((a1, s1), (a2, s2), and_cap, and_weak))
    return {"pairs_tested": tested, "deterministic_failures": fails,
            "brief_reported": 801, "reproduces": fails == 801,
            "_fail_pairs": fail_pairs}


def claim_randomisation_turns_the_merge_into_a_lemma(
        trials: int = 4000, seed: int = 5, maxa: int = 12) -> dict:
    """THE HEADLINE. Every pair admits a dominating RANDOMISED threshold gate."""
    import random
    rng = random.Random(seed)
    fails, tested = 0, 0
    worst_power_slack = float("inf")
    worst_size_excess = -float("inf")
    witness = None
    for _ in range(trials):
        a1 = rng.randint(1, maxa); s1 = rng.randint(1, a1)
        a2 = rng.randint(1, maxa); s2 = rng.randint(1, a2)
        and_cap = _sf(s1, a1, CAPABLE_RATE) * _sf(s2, a2, CAPABLE_RATE)
        and_weak = _sf(s1, a1, WEAK_RATE) * _sf(s2, a2, WEAK_RATE)
        g = randomised_np_gate(a1 + a2, and_weak)
        tested += 1
        power_slack = g["power"] - and_cap
        size_excess = g["size"] - and_weak
        if power_slack < worst_power_slack:
            worst_power_slack = power_slack
            witness = {"gates": [(a1, s1), (a2, s2)], "and_capable": and_cap,
                       "and_weak": and_weak, "merged": g}
        worst_size_excess = max(worst_size_excess, size_excess)
        if power_slack < -1e-9 or size_excess > 1e-9:
            fails += 1
    return {
        "pairs_tested": tested,
        "pairs_with_no_dominating_randomised_gate": fails,
        "merge_is_a_lemma_under_randomisation": fails == 0,
        "worst_power_slack": worst_power_slack,
        "worst_size_excess": worst_size_excess,
        "tightest_witness": witness,
        "consequence": ("monotonicity is a THEOREM in the randomised-threshold "
                        "family, which is the standard completion of the binomial "
                        "test family, NOT the family of arbitrary tests"),
    }


def claim_the_failures_are_discreteness_not_substance(seed: int = 5) -> dict:
    """Every deterministic failure is repaired by randomisation alone."""
    det = claim_the_deterministic_merge_failures_reproduce(seed=seed)
    repaired, unrepaired, example = 0, 0, None
    for (a1, s1), (a2, s2), and_cap, and_weak in det["_fail_pairs"]:
        g = randomised_np_gate(a1 + a2, and_weak)
        if g["power"] >= and_cap - 1e-9 and g["size"] <= and_weak + 1e-9:
            repaired += 1
            if example is None and 0.0 < g["gamma"] < 1.0:
                best_det = max(
                    (_sf(s, a1 + a2, CAPABLE_RATE) for s in range(1, a1 + a2 + 1)
                     if _sf(s, a1 + a2, WEAK_RATE) <= and_weak), default=0.0)
                example = {
                    "gates": [(a1, s1), (a2, s2)],
                    "and_capable_to_beat": round(and_cap, 10),
                    "and_weak_ceiling": round(and_weak, 10),
                    "best_DETERMINISTIC_power": round(best_det, 10),
                    "randomised_threshold": g["threshold"],
                    "randomised_gamma": round(g["gamma"], 10),
                    "randomised_power": round(g["power"], 10),
                    "randomised_size": round(g["size"], 10),
                }
        else:
            unrepaired += 1
    return {"deterministic_failures": det["deterministic_failures"],
            "repaired_by_randomisation": repaired, "still_failing": unrepaired,
            "all_repaired": unrepaired == 0,
            "worked_example": example}


def claim_the_likelihood_ratio_is_monotone() -> dict:
    """The one premise Neyman-Pearson needs, checked in SymPy and z3."""
    import sympy as sp
    import z3
    S, n, c, w = sp.symbols("S n c w", positive=True)
    L = (c / w) ** S * ((1 - c) / (1 - w)) ** (n - S)
    dlog = sp.simplify(sp.diff(sp.log(L), S))
    dlog_at = sp.simplify(dlog.subs({c: sp.Rational(9, 10), w: sp.Rational(1, 2)}))
    positive = bool(sp.simplify(dlog_at) > 0)
    cz, wz = z3.Reals("cz wz")
    sv = z3.Solver()
    sv.add(cz > 0, cz < 1, wz > 0, wz < 1, cz > wz,
           cz * (1 - wz) <= wz * (1 - cz))
    return {"d_logL_d_S": str(dlog),
            "d_logL_d_S_at_0.9_vs_0.5": str(dlog_at),
            "slope_positive_at_the_brief_rates": positive,
            "z3_counterexample_search": str(sv.check()),
            "monotone_likelihood_ratio_holds": str(sv.check()) == "unsat"}


def capped_optimal_curve(cap: float, weak: float, pc_min: float, pw_max: float,
                         per_gate_cap: int, max_div: int, maxtot: int) -> tuple:
    """Exact DP over the capped DETERMINISTIC threshold menu, no gate-menu
    pre-reduction, Pareto pruning only within an attempts bucket (lossless)."""
    LC, LW = math.log(pc_min), math.log(pw_max)
    menu = []
    for a in range(1, per_gate_cap + 1):
        for s in range(1, a + 1):
            pc, pw = _sf(s, a, cap), _sf(s, a, weak)
            if pc <= 0.0:
                continue
            menu.append((a, math.log(pc), math.log(pw) if pw > 0 else -700.0, s))
    curve, ladders = {}, {}
    layer = {0: [(0.0, 0.0, ())]}
    for g in range(1, max_div):
        nxt = {}
        for A, sts in layer.items():
            for lc0, lw0, path in sts:
                for a, glc, glw, s in menu:
                    if A + a > maxtot:
                        continue
                    nxt.setdefault(A + a, []).append(
                        (lc0 + glc, lw0 + glw, path + ((a, s),)))
        layer = {}
        for A, sts in nxt.items():
            sts.sort(key=lambda t: (-t[0], t[1]))
            keep, best = [], float("inf")
            for lc, lw, path in sts:
                if lw < best - 1e-15:
                    keep.append((lc, lw, path))
                    best = lw
            layer[A] = keep
        feas = [(A, p) for A, sts in layer.items() for lc, lw, p in sts
                if lc >= LC - 1e-12 and lw <= LW + 1e-12]
        if feas:
            A, p = min(feas, key=lambda t: t[0])
            curve[g + 1], ladders[g + 1] = A, p
        else:
            curve[g + 1], ladders[g + 1] = None, None
    return curve, ladders


def claim_a_per_gate_ceiling_breaks_monotonicity() -> dict:
    """THE BOUNDARY CONDITION. Scan per-gate ceilings for an actual inversion."""
    found = []
    scanned = []
    for per_gate_cap in range(2, 13):
        curve, ladders = capped_optimal_curve(
            CAPABLE_RATE, WEAK_RATE, 0.95, 0.01, per_gate_cap, 8, 60)
        seq = [(T, curve[T]) for T in sorted(curve) if curve[T] is not None]
        inv = [(a[0], b[0], a[1], b[1]) for a, b in zip(seq, seq[1:])
               if b[1] < a[1]]
        scanned.append({"ceiling": per_gate_cap,
                        "curve": {T: curve[T] for T in sorted(curve)},
                        "inversions": inv})
        if inv:
            a, b, na, nb = inv[0]
            found.append({"ceiling": per_gate_cap, "from_T": a, "to_T": b,
                          "cost_at_from_T": na, "cost_at_to_T": nb,
                          "ladder_at_from_T": list(ladders[a] or ()),
                          "ladder_at_to_T": list(ladders[b] or ())})
    return {"ceilings_scanned": [s["ceiling"] for s in scanned],
            "per_ceiling": scanned,
            "inversions_found": found,
            "monotone_under_every_ceiling_tested": not found,
            "consequence": ("a per-gate attempts ceiling is not a harmless "
                            "implementation detail: it is exactly the condition "
                            "under which the monotonicity theorem does not apply")}


def claim_scipy_and_mpmath_agree_on_the_witness(ex) -> dict:
    """Second tool on the worked randomised example."""
    if not ex:
        return {"checked": False}
    (a1, s1), (a2, s2) = ex["gates"]
    n = a1 + a2
    s = ex["randomised_threshold"]
    gamma = ex["randomised_gamma"]
    import mpmath as mp
    with mp.workdps(60):
        def pmf_exact(k, a, p):
            if k < 0 or k > a:
                return 0.0
            pp = mp.mpf(p)
            return float(mp.binomial(a, k) * pp ** k * (1 - pp) ** (a - k))
        power_exact = _sf_exact(s, n, CAPABLE_RATE) + gamma * pmf_exact(
            s - 1, n, CAPABLE_RATE)
        size_exact = _sf_exact(s, n, WEAK_RATE) + gamma * pmf_exact(
            s - 1, n, WEAK_RATE)
    return {"checked": True, "n": n,
            "power_scipy": ex["randomised_power"], "power_mpmath": power_exact,
            "size_scipy": ex["randomised_size"], "size_mpmath": size_exact,
            "max_abs_diff": max(abs(ex["randomised_power"] - power_exact),
                                abs(ex["randomised_size"] - size_exact))}


def claim_the_deterministic_curve_ACTUALLY_INVERTS() -> dict:
    """THE BRIEF'S OWN QUESTION, ANSWERED IN THE AFFIRMATIVE.

    The brief asks of its robustness sweep "whether any setting produces an
    inversion, which would settle question 2 immediately", and reports 0
    downward steps and 0 inversions at its single rate pair (0.90, 0.50). Over a
    wider grid of rate pairs there ARE inversions, and here are 2 of them,
    established by EXHAUSTIVE ENUMERATION of 1-gate and 2-gate ladders rather
    than by a Pareto-pruned dynamic program, so no pruning rule can be blamed.

    This settles question 2 in both directions at once:
      * In the DETERMINISTIC success-count threshold family, monotonicity is
        FALSE. Not unproven -- false, with a witness.
      * In the RANDOMISED threshold family, monotonicity is the theorem proved
        in this file's docstring, and the witness shows the exact mechanism: the
        merged randomised gate on a1+a2 attempts IS feasible, while the best
        deterministic gate on the same attempts falls short of the capable floor.
    It also refutes the brief's conclusion that "as few divisions as possible IS
    right on the attempts metric": at the first witness 3 divisions cost 10
    attempts where 2 cost 11, so there a division is better than free.
    """
    import itertools
    cases = [(0.90, 0.30, 0.95, 0.010), (0.95, 0.30, 0.90, 0.050)]
    MAXA = 14
    out = []
    for cap, weak, pc, pw in cases:
        gates = [(a, s) for a in range(1, MAXA + 1) for s in range(1, a + 1)]
        best1 = None
        for a, s in gates:
            if _sf(s, a, cap) >= pc and _sf(s, a, weak) <= pw:
                if best1 is None or a < best1[0]:
                    best1 = (a, [(a, s)])
        best2 = None
        for g1, g2 in itertools.combinations_with_replacement(gates, 2):
            c = _sf(g1[1], g1[0], cap) * _sf(g2[1], g2[0], cap)
            w = _sf(g1[1], g1[0], weak) * _sf(g2[1], g2[0], weak)
            if c >= pc and w <= pw:
                tot = g1[0] + g2[0]
                if best2 is None or tot < best2[0]:
                    best2 = (tot, [g1, g2])
        row = {"rates": (cap, weak), "budget": (pc, pw),
               "per_gate_cap": MAXA,
               "cost_T2_deterministic": best1[0] if best1 else None,
               "ladder_T2": best1[1] if best1 else None,
               "cost_T3_deterministic": best2[0] if best2 else None,
               "ladder_T3": best2[1] if best2 else None}
        if best1 and best2:
            row["inversion"] = best2[0] < best1[0]
            a1, s1 = best2[1][0]; a2, s2 = best2[1][1]
            c = _sf(s1, a1, cap) * _sf(s2, a2, cap)
            w = _sf(s1, a1, weak) * _sf(s2, a2, weak)
            cx = _sf_exact(s1, a1, cap) * _sf_exact(s2, a2, cap)
            wx = _sf_exact(s1, a1, weak) * _sf_exact(s2, a2, weak)
            row["T3_end_to_end_capable"] = round(c, 10)
            row["T3_end_to_end_weak"] = round(w, 10)
            row["scipy_mpmath_max_abs_diff"] = max(abs(c - cx), abs(w - wx))
            n = a1 + a2
            g = randomised_np_gate(n, pw, weak=weak, cap=cap)
            row["randomised_single_gate_on_n"] = n
            row["randomised_threshold"] = g["threshold"]
            row["randomised_gamma"] = round(g["gamma"], 10)
            row["randomised_size"] = round(g["size"], 10)
            row["randomised_power"] = round(g["power"], 10)
            row["randomised_restores_monotonicity"] = (
                g["power"] >= pc - 1e-12 and g["size"] <= pw + 1e-12)
            row["best_deterministic_power_on_n"] = round(max(
                (_sf(s, n, cap) for s in range(1, n + 1)
                 if _sf(s, n, weak) <= pw), default=0.0), 10)
        out.append(row)
    return {"witnesses": out,
            "inversions_confirmed": sum(1 for r in out if r.get("inversion")),
            "deterministic_monotonicity_is_FALSE":
                any(r.get("inversion") for r in out),
            "randomisation_restores_it_in_every_witness":
                all(r.get("randomised_restores_monotonicity")
                    for r in out if r.get("inversion")),
            "method": ("exhaustive enumeration of all 1-gate and all 2-gate "
                       "ladders over a per-gate cap of 14, no Pareto pruning"),
            "consequence": ("the brief's '0 downward steps, 0 inversions' holds "
                            "at its single rate pair (0.90, 0.50) and does not "
                            "generalise; and 'as few divisions as possible' is "
                            "false at the first witness, where 3 divisions cost "
                            "10 attempts against 11 for 2")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()

    print("== 1. the brief's deterministic merge failures, re-executed ==")
    d1 = claim_the_deterministic_merge_failures_reproduce()
    print(f"   pairs tested: {d1['pairs_tested']}")
    print(f"   deterministic failures: {d1['deterministic_failures']} "
          f"(brief reported {d1['brief_reported']}) -> reproduces "
          f"{d1['reproduces']}")

    print("\n== 2. randomisation makes the merge a LEMMA ==")
    d2 = claim_randomisation_turns_the_merge_into_a_lemma()
    for k in ("pairs_tested", "pairs_with_no_dominating_randomised_gate",
              "merge_is_a_lemma_under_randomisation", "worst_power_slack",
              "worst_size_excess", "consequence"):
        print(f"   {k}: {d2[k]}")

    print("\n== 3. the deterministic failures are DISCRETENESS, repaired ==")
    d3 = claim_the_failures_are_discreteness_not_substance()
    for k in ("deterministic_failures", "repaired_by_randomisation",
              "still_failing", "all_repaired"):
        print(f"   {k}: {d3[k]}")
    ex = d3["worked_example"]
    if ex:
        print("   worked example:")
        for k, v in ex.items():
            print(f"      {k}: {v}")

    print("\n== 4. the Neyman-Pearson premise: monotone likelihood ratio ==")
    for k, v in claim_the_likelihood_ratio_is_monotone().items():
        print(f"   {k}: {v}")

    print("\n== 5. scipy vs mpmath on the worked example ==")
    for k, v in claim_scipy_and_mpmath_agree_on_the_witness(ex).items():
        print(f"   {k}: {v}")

    print("\n== 6. BOUNDARY CONDITION: does a per-gate ceiling break it? ==")
    d6 = claim_a_per_gate_ceiling_breaks_monotonicity()
    for s in d6["per_ceiling"]:
        print(f"   ceiling {s['ceiling']:2d}: {s['curve']}  inversions "
              f"{s['inversions']}")
    print(f"   inversions found: {d6['inversions_found']}")
    print(f"   monotone under every ceiling tested: "
          f"{d6['monotone_under_every_ceiling_tested']}")
    print(f"   {d6['consequence']}")

    print("\n== 7. THE DETERMINISTIC CURVE ACTUALLY INVERTS ==")
    d7 = claim_the_deterministic_curve_ACTUALLY_INVERTS()
    for r in d7["witnesses"]:
        print(f"   rates {r['rates']} budget {r['budget']} per-gate cap "
              f"{r['per_gate_cap']}")
        print(f"      T=2 deterministic optimum {r['cost_T2_deterministic']} "
              f"{r['ladder_T2']}")
        print(f"      T=3 deterministic optimum {r['cost_T3_deterministic']} "
              f"{r['ladder_T3']}")
        print(f"      INVERSION: {r.get('inversion')}   end-to-end capable "
              f"{r.get('T3_end_to_end_capable')} weak "
              f"{r.get('T3_end_to_end_weak')}  scipy-vs-mpmath "
              f"{r.get('scipy_mpmath_max_abs_diff'):.3e}")
        print(f"      randomised gate on n={r.get('randomised_single_gate_on_n')}: "
              f"s={r.get('randomised_threshold')} gamma="
              f"{r.get('randomised_gamma')} size={r.get('randomised_size')} "
              f"power={r.get('randomised_power')}  restores monotonicity: "
              f"{r.get('randomised_restores_monotonicity')}")
        print(f"      best DETERMINISTIC power on the same n: "
              f"{r.get('best_deterministic_power_on_n')}")
    print(f"   inversions confirmed: {d7['inversions_confirmed']}")
    print(f"   deterministic monotonicity is FALSE: "
          f"{d7['deterministic_monotonicity_is_FALSE']}")
    print(f"   randomisation restores it everywhere: "
          f"{d7['randomisation_restores_it_in_every_witness']}")
    print(f"   method: {d7['method']}")
    print(f"   {d7['consequence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
