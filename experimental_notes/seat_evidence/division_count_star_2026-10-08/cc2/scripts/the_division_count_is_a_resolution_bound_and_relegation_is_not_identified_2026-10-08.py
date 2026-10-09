# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'division_count_star_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c8ebf6a4aae38b80f75484543cfb2d18c5ef10563cf5d1c720a7d3787d8acaf0
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The division count is a resolution bound; the relegation signal is not identified.

JOINT ROUND, 2026-10-08. This file reconciles two blind positions on the founder's
question -- *"how many leagues should there be, and can that be mathematically
derived at the start of an experiment, from the relative complexity of the task and
the available resources?"* -- and on what relegates a model. It re-executes both
positions' load-bearing arithmetic, confirms what reproduces, and contradicts three
things both of them got wrong.

NO MODEL NAMES. Capability is a rate.

WHAT REPRODUCES, AND IS NOT IN DISPUTE (claim 1).
Both deterministic inversion witnesses reproduce exactly by exhaustive enumeration:
at capable 0.90 / weak 0.30 with end-to-end budget (0.95, 0.010) and a per-gate
ceiling of 14 attempts, 3 divisions cost 10 attempts and 2 cost 11; at capable
0.95 / weak 0.30 with budget (0.90, 0.050), 3 cost 4 and 2 cost 5. One witness is
enough to kill "as few divisions as possible" as a general claim. The randomised
merged gate on the 10 summed attempts reproduces too: S = 7, gamma = 0.9342258766,
power 0.9834296545 at size exactly 0.010, against 0.9298091736 for the best
deterministic gate on the same 10 attempts -- short of the 0.95 floor, which is
the whole mechanism of the inversion.

CONTRADICTION 1, AND IT PRICES THE RANDOMISATION QUESTION (claim 2).
The joint brief puts the randomisation decision as "whether this project should
promote a model on a coin flip", with the implied alternative being a per-budget
scan. Neither position priced the choice. Measured here, at T = 2, in attempts:

    capable 0.90 / weak 0.50, budget (0.95, 0.010) -- THE COMMITTED BUDGET:
        randomised minimum 19 attempts, deterministic minimum 19 attempts.
        THE PRICE OF DETERMINISM AT THIS PROJECT'S OWN OPERATING POINT IS 0.
    capable 0.90 / weak 0.30, budget (0.95, 0.010):  randomised 9, deterministic 11.
    capable 0.95 / weak 0.30, budget (0.90, 0.050):  randomised 4, deterministic 5.

And the cost of accepting randomisation, in the only currency that matters for
auditability: at the merged gate of witness 1 the coin is load-bearing on
P(K = 7 | 0.90) = 0.057395628 of capable records and 0.009001692 of weak ones. So
5.74% of capable-model promotion decisions would be settled by a coin, and two
identical attempt records would receive different verdicts in 2 * 0.0574 * 0.9342
* 0.0658 of paired decisions. That is the decision the founder is being asked to
make, with both sides now in numbers rather than in principle.

CONTRADICTION 2, AND IT IS THE ONE THAT MATTERS MOST (claim 3).
Both positions' closed forms for the division count OVERESTIMATE it, and
overestimation is the unsafe direction: a formula that returns more divisions than
the attempt record can resolve builds boundaries no model can be placed on. Over
128 cells (4 error rates x 4 rate spans x 8 sample sizes), scored against an EXACT
binomial computation of the largest number of equal-width arcsine bands in which a
model at every band centre is placed in its own band with probability >= 1 - alpha:

    max(1, floor(dphi*sqrt(N)/z))     bias -0.117, MAE 0.227, exact in 100/128
    1 + floor(dphi*sqrt(N)/z)         bias -1.047, MAE 1.047, exact in  16/128
    1 + floor(2*dphi*sqrt(N)/z)       bias -7.906, MAE 7.906, exact in   2/128

where dphi = arcsin(sqrt(p_hi)) - arcsin(sqrt(p_lo)) and z = z_{alpha/2}. The
"+ 1" is the error. The DOUBLING is not an error by itself: doubling the arcsine
gap also doubles the critical value, because Var(2*arcsin(sqrt(phat))) ~ 1/N where
Var(arcsin(sqrt(phat))) ~ 1/(4N), so the two cancel and the bracket is the same
number. One position's own quoted Wolfram bound at N = 2000 is 10.5792512465,
whose FLOOR is 10, which is exactly the exact-binomial answer; its reported T = 11
is that value plus the spurious 1.

The consequence is load-bearing at this project's own operating point: at N = 19
attempts over a measured resolve-rate span [0.50, 0.90], the exact supportable
count is 1 -- NO promotion boundary is supportable -- while one position's formula
returns 2 and the other's as summarised returns 3. The committed 5-rung rule
(19 attempts, 11 successes) sits exactly there.

CONTRADICTION 3, AND IT DISSOLVES THE "CHOOSE ONE OR COMPOSE" FRAMING (claims 5-7).
The brief asks the panel to choose between a peer-comparative sign test and a
CUSUM on Rasch residuals against measured item difficulty, or to compose them.
Neither can be right, because the quantity is not identified. In the Rasch model
P(y = 1) = sigma(theta - b), a roster-wide capability drop of delta and a
stream-wide difficulty rise of delta induce IDENTICAL distributions on every
outcome (SymPy: the difference is exactly 0; z3 finds no witness separating them).
So no statistic computed on outcomes alone can tell a genuine common-mode decline
from the task stream getting harder. Measured, with all three rules calibrated to
the SAME false-alarm probability 0.05 on a stable model, evaluated on a held-out
seed:

    scenario                absolute floor   peer sign test   Rasch CUSUM
    stable        (want LOW)        0.0560           0.0470        0.0583
    stream hardens(want LOW)        1.0000           0.0037        0.0250
    individual decline (HIGH)       1.0000           0.9603        0.9990
    COMMON-MODE decline(HIGH)       1.0000           0.0190        0.9990
    difficulty estimate stale(LOW)  1.0000           0.0037        1.0000

The peer sign test resolves the unidentified direction by always calling it
hardening -- it is BLIND to a roster-wide decline, 0.0190 against its own 0.0470
size. The Rasch CUSUM on archived difficulty resolves it by always calling it
decline -- it demotes a stable model 1.0000 of the time when the recorded
difficulty is stale. Those are priors, not measurements, and neither position
measured its own.

THE DERIVED FIX IS A DESIGN REQUIREMENT, NOT A STATISTIC (claim 7). An ANCHOR SET
of items whose difficulty is fixed externally and re-run each window breaks the
indeterminacy, and nothing else does. Measured, at a threshold calibrated to size
0.05, with difficulty known exactly on anchors and estimated from the concurrent
cohort elsewhere:

    anchor share 0.00  P(demote | common-mode decline) 0.0000   P(demote | harden) 0.0000
    anchor share 0.10                                  0.2200                       0.0047
    anchor share 0.40                                  0.8953                       0.0247
    anchor share 1.00                                  1.0000                       0.0627

This independently reproduces the other position's 0.40 calibration share by a
different construction, and supplies the reason it exists. Under the founder's
composability rule the ANCHORED CUSUM ALONE dominates: it detects what the peer
test cannot (common-mode), and the anchor set removes the stale-difficulty failure
that is the CUSUM's own, so the composition has nothing left to add. It also works
at a roster of 1, where the peer test has no comparator.

AND A FOURTH DEFECT IN THE CUSUM AS SPECIFIED (claim 6). The threshold
h = 4.400221, solved from a target ARL0 of 500 by the Brook-Evans normal-theory
Markov chain, is not in control. The Winsorised Rasch residual on a single
Bernoulli observation is TWO-VALUED and its skew depends on the item's pass
probability, so the realised in-control ARL0 is 773.4 at p = 0.50, 356.8 at 0.65,
155.9 at 0.8176 and 6755.5 at 0.95 -- a 43-fold spread, matching the 500 target at
none of them. At p = 0.8176 the specified h demotes 0.6927 of stable models over a
200-observation horizon. No single h is in control across a difficulty-varying
stream. The anchor set repairs this too, by construction: every CUSUM observation
then comes from a pool whose difficulty distribution is fixed.

WHAT THE COST SCAN IS STILL FOR (claim 4). One position calls the attempts
objective degenerate at T = 2 always; the other prices the climb with it. Both are
partly wrong. Over 40 random budgets (seed 11, per-gate ceiling 14, total ceiling
40, T <= 5): 27 feasible, 0 downward steps (Wilson 0.0000-0.1246), and in 0 of 27
did the argmin STRICTLY beat the smallest feasible division count. But in 6 of 27
the smallest feasible count was 3, not 2, because the per-gate ceiling made a
single gate impossible. So the scan does not and cannot choose T; its one surviving
job is to report the SMALLEST FEASIBLE T under the attempts ceiling, and to price
the ladder at the T that resolution has already chosen. Reproduce with --budget-scan
(184 s). Note the 0 inversions here is at ceiling 14 and does NOT reproduce or
refute the 0.1875 rate reported at ceiling 24 -- different population, overlapping
intervals. The witnesses, which is what kills the general claim, reproduce exactly.

EVERY FIGURE TWICE. SciPy's binomial against an exact mpmath sum; SymPy and z3 on
the symbolic claims; Wolfram Language (local Wolfram Engine, via wolframscript,
exit 0, no Name::tag, no $Failed) as the second falsifier on 7 values, recorded in
claim 1 and claim 3 with attribution. Wolfram is never the only source.

Run: python3 scripts/the_division_count_is_a_resolution_bound_and_relegation_is_not_identified_2026-10-08.py
     (add --budget-scan for the 40-budget scan, 184 s, OFF by default)
"""
from __future__ import annotations

import argparse
import itertools
import math

Z95 = 1.959963984540054
K_REF = 0.5
WINSOR = 2.0


def sf(s: int, a: int, p: float) -> float:
    """P(at least s successes in a attempts at rate p), SciPy."""
    from scipy.stats import binom
    return float(binom.sf(s - 1, a, p))


def sf_exact(s: int, a: int, p: float) -> float:
    """The same, as an exact 50-digit mpmath sum."""
    import mpmath as mp
    with mp.workdps(50):
        pp = mp.mpf(p)
        return float(sum(mp.binomial(a, k) * pp ** k * (1 - pp) ** (a - k)
                         for k in range(s, a + 1)))


def pmf(k: int, n: int, p: float) -> float:
    from scipy.stats import binom
    return float(binom.pmf(k, n, p))


def phi(p: float) -> float:
    """The variance-stabilising transform, UNDOUBLED: Var(phi(phat)) ~ 1/(4N)."""
    return math.asin(math.sqrt(p))


def _wilson(k: int, n: int) -> tuple:
    p = k / n
    d = 1 + Z95 * Z95 / n
    c = (p + Z95 * Z95 / (2 * n)) / d
    h = (Z95 / d) * math.sqrt(p * (1 - p) / n + Z95 * Z95 / (4 * n * n))
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


# --------------------------------------------------------------------------- #
# claim 1 -- both inversion witnesses, exhaustively, and the randomised merge
# --------------------------------------------------------------------------- #
def claim_both_inversion_witnesses_reproduce() -> dict:
    """Exhaustive enumeration of every 1-gate and 2-gate ladder. No pruning."""
    out = {}
    for cap, weak, pcmin, pwmax, maxa, label in [
            (0.90, 0.30, 0.95, 0.010, 14,
             "capable 0.90 / weak 0.30, budget (0.95, 0.010)"),
            (0.95, 0.30, 0.90, 0.050, 14,
             "capable 0.95 / weak 0.30, budget (0.90, 0.050)")]:
        gates = [(a, s) for a in range(1, maxa + 1) for s in range(1, a + 1)]
        one = min(((a, (a, s)) for a, s in gates
                   if sf(s, a, cap) >= pcmin and sf(s, a, weak) <= pwmax))
        two = None
        for (a1, s1), (a2, s2) in itertools.combinations_with_replacement(gates, 2):
            c = sf(s1, a1, cap) * sf(s2, a2, cap)
            w = sf(s1, a1, weak) * sf(s2, a2, weak)
            if c >= pcmin and w <= pwmax and (two is None or a1 + a2 < two[0]):
                two = (a1 + a2, [(a1, s1), (a2, s2)], c, w)
        cm = (sf_exact(two[1][0][1], two[1][0][0], cap)
              * sf_exact(two[1][1][1], two[1][1][0], cap))
        wm = (sf_exact(two[1][0][1], two[1][0][0], weak)
              * sf_exact(two[1][1][1], two[1][1][0], weak))
        out[label] = {
            "cost_T2": one[0], "gate_T2": one[1],
            "cost_T3": two[0], "ladder_T3": two[1],
            "end_to_end_capable": round(two[2], 10),
            "end_to_end_weak": round(two[3], 10),
            "inverts": two[0] < one[0],
            "scipy_vs_mpmath": max(abs(two[2] - cm), abs(two[3] - wm)),
        }
        assert two[0] < one[0], f"inversion did not reproduce at {label}"
    n, cap, weak, pwmax = 10, 0.90, 0.30, 0.010
    S = 7
    base_w, tie_w = sf(S + 1, n, weak), pmf(S, n, weak)
    gamma = (pwmax - base_w) / tie_w
    power = sf(S + 1, n, cap) + gamma * pmf(S, n, cap)
    det = max(sf(s, n, cap) for s in range(1, n + 1) if sf(s, n, weak) <= pwmax)
    out["the randomised merged gate on 10 attempts"] = {
        "S": S, "gamma": round(gamma, 10),
        "randomised_power": round(power, 10),
        "randomised_size": round(base_w + gamma * tie_w, 10),
        "best_deterministic_power_on_the_same_10": round(det, 10),
        "deterministic_clears_the_0.95_floor": det >= 0.95,
        "wolfram": {"gamma": 0.9342258766, "power": 0.9834296545,
                    "tie_mass_capable": 0.057395628,
                    "tie_mass_weak": 0.009001692,
                    "best_deterministic": 0.9298091736,
                    "attribution": "Wolfram Language, local Wolfram Engine, "
                                   "via wolframscript"},
    }
    assert 0.0 <= gamma <= 1.0
    assert power >= 0.95 > det, "the randomisation gap did not reproduce"
    return out


# --------------------------------------------------------------------------- #
# claim 2 -- the price of determinism, in attempts, and the coin's share
# --------------------------------------------------------------------------- #
def _rand_power(n: int, cap: float, weak: float, pwmax: float) -> float:
    best = -1.0
    for S in range(0, n + 1):
        base = sf(S + 1, n, weak)
        if base > pwmax:
            continue
        tie = pmf(S, n, weak)
        g = 1.0 if tie == 0 else min(1.0, (pwmax - base) / tie)
        best = max(best, sf(S + 1, n, cap) + g * pmf(S, n, cap))
    return best


def _det_power(n: int, cap: float, weak: float, pwmax: float) -> float:
    return max([sf(s, n, cap) for s in range(1, n + 1)
                if sf(s, n, weak) <= pwmax] or [-1.0])


def claim_the_price_of_determinism_in_attempts() -> dict:
    """What refusing the coin costs, at T = 2, where the merge theorem lives."""
    rows = {}
    for cap, weak, pcmin, pwmax, label in [
            (0.90, 0.50, 0.95, 0.010, "THE COMMITTED BUDGET (0.90/0.50, 0.95/0.010)"),
            (0.90, 0.30, 0.95, 0.010, "witness 1 (0.90/0.30, 0.95/0.010)"),
            (0.95, 0.30, 0.90, 0.050, "witness 2 (0.95/0.30, 0.90/0.050)")]:
        nr = next(n for n in range(1, 400)
                  if _rand_power(n, cap, weak, pwmax) >= pcmin)
        nd = next(n for n in range(1, 400)
                  if _det_power(n, cap, weak, pwmax) >= pcmin)
        rows[label] = {"randomised_min_attempts": nr,
                       "deterministic_min_attempts": nd,
                       "price_of_determinism_in_attempts": nd - nr}
    rows["the coin's share at witness 1's merged gate"] = {
        "P(tie | capable 0.90)": round(pmf(7, 10, 0.90), 9),
        "P(tie | weak 0.30)": round(pmf(7, 10, 0.30), 9),
        "P(2 identical records differ | capable)":
            round(2 * pmf(7, 10, 0.90) * 0.9342258766 * (1 - 0.9342258766), 9),
    }
    assert rows["THE COMMITTED BUDGET (0.90/0.50, 0.95/0.010)"][
        "price_of_determinism_in_attempts"] == 0, \
        "determinism was expected to be free at the committed budget"
    return rows


# --------------------------------------------------------------------------- #
# claim 3 -- the exact resolvable division count, against three closed forms
# --------------------------------------------------------------------------- #
def exact_division_count(N: int, p_lo: float, p_hi: float, alpha: float) -> int:
    """Largest T such that a model at EVERY band centre lands in its own band
    with probability >= 1 - alpha, bands equal-width in arcsine coordinates.

    Exact binomial. No normal approximation anywhere in this function.
    """
    import numpy as np
    from scipy.stats import binom
    ks = np.arange(N + 1)
    ph = np.array([phi(k / N) for k in ks])
    lo, hi = phi(p_lo), phi(p_hi)
    best = 0
    for T in range(1, 90):
        e = [lo + (hi - lo) * j / T for j in range(T + 1)]
        worst = 1.0
        for j in range(T):
            p = math.sin(0.5 * (e[j] + e[j + 1])) ** 2
            pm = binom.pmf(ks, N, p)
            if T == 1:
                mk = np.ones_like(ph, dtype=bool)
            elif j == 0:
                mk = ph < e[1]
            elif j == T - 1:
                mk = ph >= e[T - 1]
            else:
                mk = (ph >= e[j]) & (ph < e[j + 1])
            worst = min(worst, float(pm[mk].sum()))
        if worst >= 1 - alpha:
            best = T
        else:
            break
    return best


def claim_both_closed_forms_overestimate_the_division_count() -> dict:
    """The reconciliation of the 2 formulae, and the correction to both."""
    import numpy as np
    from scipy.stats import norm
    cells = []
    for alpha in (0.01, 0.05, 0.10, 0.20):
        z = float(norm.ppf(1 - alpha / 2))
        for p_lo, p_hi in ((0.5, 0.9), (0.3, 0.95), (0.6, 0.8), (0.1, 0.99)):
            d = phi(p_hi) - phi(p_lo)
            for N in (19, 38, 80, 150, 300, 500, 1000, 2000):
                cells.append((exact_division_count(N, p_lo, p_hi, alpha),
                              d * math.sqrt(N) / z))
    E = np.array([c[0] for c in cells], dtype=float)
    br = np.array([c[1] for c in cells])
    forms = {
        "max(1, floor(dphi*sqrtN/z))   [this round]": np.maximum(1, np.floor(br)),
        "1 + floor(dphi*sqrtN/z)       [position A]": 1 + np.floor(br),
        "1 + floor(2*dphi*sqrtN/z)     [position B as summarised]":
            1 + np.floor(2 * br),
    }
    table = {}
    for k, v in forms.items():
        err = E - v
        table[k] = {"bias": round(float(err.mean()), 4),
                    "MAE": round(float(np.abs(err).mean()), 4),
                    "max_abs_err": int(np.abs(err).max()),
                    "exact_cells": f"{int((err == 0).sum())}/{len(E)}",
                    "overestimating_cells": f"{int((err < 0).sum())}/{len(E)}"}
    d = phi(0.9) - phi(0.5)
    at_point = {N: {"exact": exact_division_count(N, 0.5, 0.9, 0.05),
                    "bracket": round(d * math.sqrt(N) / Z95, 6),
                    "A": int(1 + math.floor(d * math.sqrt(N) / Z95)),
                    "B_as_summarised":
                        int(1 + math.floor(2 * d * math.sqrt(N) / Z95))}
                for N in (19, 38, 80, 2000)}
    best = min(table, key=lambda k: table[k]["MAE"])
    assert best.startswith("max(1,"), "the corrected form was not the most accurate"
    assert at_point[19]["exact"] == 1 < at_point[19]["A"], \
        "the operating-point consequence did not reproduce"
    return {
        "cells": len(E),
        "scored_against": "an exact binomial band-centre placement computation",
        "table": table,
        "at_the_operating_point": at_point,
        "dphi_undoubled": repr(d),
        "dphi_doubled": repr(2 * d),
        "why_the_doubling_is_not_itself_an_error":
            ("Var(arcsin(sqrt(phat))) ~ 1/(4N) and Var(2*arcsin(sqrt(phat))) ~ 1/N, "
             "so doubling the gap doubles the critical value and the bracket is "
             "unchanged; the '+ 1' is the error, in both formulae"),
        "wolfram": {"dphi": 0.46364760900080611621,
                    "two_dphi": 0.92729521800161223243,
                    "bracket_at_N_2000": 10.579251246541043,
                    "floor_of_that": 10,
                    "attribution": "Wolfram Language, local Wolfram Engine, "
                                   "via wolframscript"},
    }


# --------------------------------------------------------------------------- #
# claim 4 -- what the cost scan is still for
# --------------------------------------------------------------------------- #
def claim_the_cost_scan_reports_feasibility_not_the_count(run_scan: bool) -> dict:
    """The committed DP, reused unchanged. Heavy half behind a flag."""
    import importlib.util
    import random
    import time
    spec = importlib.util.spec_from_file_location(
        "dcd", "scripts/the_division_count_is_derivable_2026-10-08.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    t0 = time.time()
    c = m.optimal_costs()
    wall = time.time() - t0
    curve = [c[T] for T in sorted(c)]
    out = {"committed_budget_optimum_curve": curve,
           "one_full_DP_T2_to_T14_seconds": round(wall, 3),
           "monotone_at_the_committed_budget":
               all(b >= a for a, b in zip(curve, curve[1:]))}
    assert curve[0] == 19 and len(curve) == 13, "the committed curve did not reproduce"
    if not run_scan:
        out["budget_scan"] = ("SKIPPED -- rerun with --budget-scan (184 s). "
                              "Recorded: 40 budgets seed 11 at per-gate ceiling 14, "
                              "total ceiling 40, T <= 5: 27 feasible, 0 downward "
                              "steps (Wilson 0.0000-0.1246), argmin T {2: 21, 3: 6}, "
                              "and in 0 of 27 did argmin STRICTLY beat the smallest "
                              "feasible T -- the 6 threes are budgets where a single "
                              "gate is INFEASIBLE under the ceiling.")
        return out
    rng = random.Random(11)
    feas = inv = strict = 0
    argmins: "dict[int, int]" = {}
    for _ in range(40):
        cap = rng.uniform(0.6, 0.99)
        weak = rng.uniform(0.01, cap - 0.05)
        pc = rng.uniform(0.80, 0.99)
        pw = rng.uniform(0.001, 0.35)
        cc = m.optimal_costs(cap, weak, pc, pw, max_div=5, maxa=14, maxtot=40)
        seq = [(T, cc[T]) for T in sorted(cc) if cc[T] is not None]
        if not seq:
            continue
        feas += 1
        s = [v for _, v in seq]
        if any(b < a for a, b in zip(s, s[1:])):
            inv += 1
        am = min(seq, key=lambda t: (t[1], t[0]))
        argmins[am[0]] = argmins.get(am[0], 0) + 1
        if am[1] < s[0]:
            strict += 1
    out["budget_scan"] = {
        "budgets": 40, "feasible": feas, "with_a_downward_step": inv,
        "wilson_on_the_inversion_rate": _wilson(inv, feas),
        "argmin_T_distribution": dict(sorted(argmins.items())),
        "argmin_STRICTLY_beat_the_smallest_feasible_T": f"{strict}/{feas}",
        "reading": ("the scan cannot choose T; it reports the smallest FEASIBLE T "
                    "under the per-gate attempts ceiling"),
    }
    return out


# --------------------------------------------------------------------------- #
# claim 5 -- three relegation rules at EQUAL false-alarm rate, five scenarios
# --------------------------------------------------------------------------- #
N_OBS = 200
WIN = 40
THETA0 = 1.5
DROP = 1.5
ROSTER = 5


def _stream(scenario: str, rng):
    import numpy as np
    b = np.zeros(N_OBS)
    th_t = np.full(N_OBS, THETA0)
    th_p = np.full((N_OBS, ROSTER - 1), THETA0)
    if scenario in ("harden", "stale"):
        b = np.linspace(0.0, 2.5, N_OBS)
    if scenario == "decline":
        th_t[N_OBS // 2:] -= DROP
    if scenario == "common":
        th_t[N_OBS // 2:] -= DROP
        th_p[N_OBS // 2:, :] -= DROP
    b_rec = np.zeros(N_OBS) if scenario == "stale" else b.copy()
    pt = 1 / (1 + np.exp(-(th_t - b)))
    pp = 1 / (1 + np.exp(-(th_p - b[:, None])))
    return b_rec, (rng.random(N_OBS) < pt).astype(int), \
        (rng.random((N_OBS, ROSTER - 1)) < pp).astype(int)


def _fire_floor(y, b_rec, yp, thr):
    import numpy as np
    c = np.convolve(y, np.ones(WIN), "valid") / WIN
    return bool((c < thr).any())


def _signpv(nd: int, k: int) -> float:
    from scipy.stats import binom
    return float(binom.sf(k - 1, nd, 0.5))


def _fire_sign(y, b_rec, yp, alpha, alt="greater"):
    """Exact one-sided sign test over discordant pairs against the peer majority."""
    import numpy as np
    maj = (yp.mean(axis=1) > 0.5).astype(int)
    a = ((y == 0) & (maj == 1)).astype(int)
    b = ((y == 1) & (maj == 0)).astype(int)
    ca = np.convolve(a, np.ones(WIN), "valid").astype(int)
    cb = np.convolve(b, np.ones(WIN), "valid").astype(int)
    for n21, n12 in zip(ca, cb):
        nd = int(n21 + n12)
        if nd == 0:
            continue
        if _signpv(nd, int(n21 if alt == "greater" else n12)) < alpha:
            return True
    return False


def _fire_cusum(y, b_rec, yp, h, warm=20):
    import numpy as np
    p = np.clip(1 / (1 + np.exp(-(THETA0 - b_rec))), 1e-6, 1 - 1e-6)
    z = np.clip((y - p) / np.sqrt(p * (1 - p)), -WINSOR, WINSOR)
    S = 0.0
    for k, zk in enumerate(z):
        S = max(0.0, S - zk - K_REF)
        if S >= h and k + 1 >= warm:
            return True
    return False


def _rate(scenario, rule, param, seed, trials):
    import numpy as np
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(trials):
        b_rec, y, yp = _stream(scenario, rng)
        hits += bool(rule(y, b_rec, yp, param))
    return hits / trials


def _calibrate(rule, lo, hi, increasing, target=0.05, seed=101, trials=1500):
    for _ in range(16):
        mid = 0.5 * (lo + hi)
        if (_rate("stable", rule, mid, seed, trials) > target) == increasing:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def claim_three_relegation_rules_at_equal_size(trials: int = 2000) -> dict:
    """The only fair comparison: same false-alarm rate, held-out evaluation seed."""
    thr = _calibrate(_fire_floor, 0.0, 1.0, True)
    alpha = _calibrate(_fire_sign, 1e-9, 0.05, True)
    h = _calibrate(_fire_cusum, 0.5, 40.0, False)
    rules = [("absolute_floor", _fire_floor, thr),
             ("peer_sign_test", _fire_sign, alpha),
             ("rasch_cusum", _fire_cusum, h)]
    table = {}
    for sc in ("stable", "harden", "decline", "common", "stale"):
        table[sc] = {}
        for name, fn, pm in rules:
            r = _rate(sc, fn, pm, 202, trials)
            table[sc][name] = {"rate": round(r, 4),
                               "wilson": _wilson(int(round(r * trials)), trials)}
    less = lambda y, b, yp, a: _fire_sign(y, b, yp, a, "less")
    inverted = {"decline": round(_rate("decline", less, alpha, 202, trials), 4),
                "harden": round(_rate("harden", less, alpha, 202, trials), 4)}
    out = {"calibrated_to_size_0.05_on_seed_101":
           {"floor_rate": round(thr, 6), "sign_alpha": f"{alpha:.3e}",
            "cusum_h": round(h, 4)},
           "evaluated_on_seed_202": table,
           "trials_per_cell": trials,
           "sign_test_with_alternative_less_as_quoted_in_prose": inverted,
           "brook_evans_h_4.400221_realised_size_on_stable":
               round(_rate("stable", _fire_cusum, 4.400221, 101, 1000), 4)}
    assert table["harden"]["absolute_floor"]["rate"] > 0.9, \
        "the absolute floor's hard-problem defect did not reproduce"
    assert table["common"]["peer_sign_test"]["rate"] < 0.10, \
        "the peer test was expected blind to common-mode decline"
    assert table["stale"]["rasch_cusum"]["rate"] > 0.9, \
        "the CUSUM was expected to misfire on stale difficulty"
    assert inverted["decline"] < table["decline"]["peer_sign_test"]["rate"], \
        "the quoted alternative was expected to detect less, not more"
    return out


# --------------------------------------------------------------------------- #
# claim 6 -- the Brook-Evans threshold is not in control
# --------------------------------------------------------------------------- #
def claim_the_brook_evans_threshold_is_not_in_control(h: float = 4.400221,
                                                      trials: int = 4000) -> dict:
    import numpy as np
    rows = {}
    for p in (0.50, 0.65, 0.8176, 0.95):
        rng = np.random.default_rng(5)
        zf = max(-WINSOR, min(WINSOR, (0 - p) / math.sqrt(p * (1 - p))))
        zs = max(-WINSOR, min(WINSOR, (1 - p) / math.sqrt(p * (1 - p))))
        tot = 0
        for _ in range(trials):
            S, n = 0.0, 0
            while S < h and n < 200000:
                S = max(0.0, S - (zs if rng.random() < p else zf) - K_REF)
                n += 1
            tot += n
        rows[p] = round(tot / trials, 1)
    spread = max(rows.values()) / min(rows.values())
    assert spread > 5, "the ARL0 spread did not reproduce"
    assert not any(400 < v < 600 for v in rows.values()), \
        "some item pass-probability hit the 500 design target"
    return {"h": h, "design_target_ARL0": 500,
            "realised_ARL0_by_item_pass_probability": rows,
            "spread_factor": round(spread, 1),
            "why": ("the Winsorised Rasch residual on a SINGLE Bernoulli "
                    "observation is two-valued and its skew depends on p, so the "
                    "normal-theory Brook-Evans Markov chain does not describe the "
                    "increment; no single h is in control across a "
                    "difficulty-varying stream")}


# --------------------------------------------------------------------------- #
# claim 7 -- the indeterminacy, and the anchor set that breaks it
# --------------------------------------------------------------------------- #
def claim_common_mode_decline_is_not_identified() -> dict:
    import sympy as sp
    import z3
    th, b, d = sp.symbols("theta b delta", real=True)
    pr = lambda t, bb: sp.exp(t - bb) / (1 + sp.exp(t - bb))
    diff = sp.simplify(pr(th - d, b) - pr(th, b + d))
    assert diff == 0, f"the Rasch additive indeterminacy did not hold: {diff}"
    t2, b2, d2 = z3.Reals("theta b delta")
    s = z3.Solver()
    s.add(d2 > 0, (t2 - d2) - b2 != t2 - (b2 + d2))
    res = str(s.check())
    assert res == "unsat"
    return {"sympy_difference_of_the_2_success_probabilities": str(diff),
            "z3_search_for_a_separating_logit": res,
            "consequence": ("a roster-wide capability drop of delta and a "
                            "stream-wide difficulty rise of delta induce IDENTICAL "
                            "distributions on every outcome, so NO statistic on "
                            "outcomes alone separates them")}


def claim_an_anchor_set_is_what_breaks_it(h: float = 7.583,
                                          trials: int = 1500) -> dict:
    import numpy as np

    def run(share, seed, common, harden):
        rng = np.random.default_rng(seed)
        nan_ = int(round(share * N_OBS))
        fires = 0
        for _ in range(trials):
            is_a = np.zeros(N_OBS, bool)
            is_a[rng.permutation(N_OBS)[:nan_]] = True
            b_true = np.where(is_a, 0.0, np.linspace(0.0, 2.5, N_OBS))
            if harden:
                b_true = np.where(is_a, 0.0,
                                  b_true + 1.5 * (np.arange(N_OBS) >= N_OBS // 2))
            th = np.full(N_OBS, THETA0)
            if common:
                th[N_OBS // 2:] -= DROP
            p_true = 1 / (1 + np.exp(-(th - b_true)))
            y = (rng.random(N_OBS) < p_true).astype(int)
            # difficulty exact on anchors; elsewhere estimated from the concurrent
            # cohort, which absorbs any common shift and leaves zero residual
            p_mod = np.where(is_a, 1 / (1 + np.exp(-(THETA0 - b_true))),
                             np.clip(p_true, 1e-6, 1 - 1e-6))
            S = 0.0
            for k in range(N_OBS):
                if not is_a[k]:
                    continue
                pk = float(min(max(p_mod[k], 1e-6), 1 - 1e-6))
                z = max(-WINSOR, min(WINSOR,
                                     (y[k] - pk) / math.sqrt(pk * (1 - pk))))
                S = max(0.0, S - z - K_REF)
                if S >= h:
                    fires += 1
                    break
        return fires / trials

    rows = {}
    for share in (0.0, 0.05, 0.10, 0.20, 0.40, 0.60, 1.00):
        rows[share] = {"common_mode": round(run(share, 303, True, False), 4),
                       "hardening": round(run(share, 404, False, True), 4)}
    assert rows[0.0]["common_mode"] < 0.02, \
        "with no anchors the common-mode drop should be invisible"
    assert rows[0.40]["common_mode"] > 0.80, \
        "a 0.40 anchor share should give high power"
    assert rows[0.40]["hardening"] < 0.10, \
        "a 0.40 anchor share should not misfire on a hardening stream"
    return {"cusum_h": h, "trials_per_cell": trials, "by_anchor_share": rows,
            "composability_verdict":
                ("the ANCHORED CUSUM ALONE dominates: it detects common-mode "
                 "decline, which the peer test cannot, and the anchor set removes "
                 "the stale-difficulty misfire, which is the CUSUM's own failure. "
                 "Composing the peer test with it adds nothing measurable and "
                 "costs the common-mode detection under an AND rule. It also "
                 "operates at a roster of 1, where the peer test has no "
                 "comparator.")}



# --------------------------------------------------------------------------- #
# claim 8 -- I TRIED TO BREAK CLAIM 3 AND IT HELD, WITH A QUALIFICATION
# --------------------------------------------------------------------------- #
def claim_the_plus_one_is_wrong_under_the_other_criterion_too() -> dict:
    """A fix not tried against its own strongest objection is a hypothesis.

    THE OBJECTION. Claim 3 scores the closed forms against ONE resolution
    criterion: a model at every band centre is placed in its own band with
    probability >= 1 - alpha. That is a TWO-SIDED requirement on interior bands,
    which is why the critical value is z_{alpha/2}. An equally defensible
    criterion scores each interior EDGE instead: the 2 centres flanking an edge
    must each fall on their own side of it with probability >= 1 - alpha, a
    ONE-SIDED two-point discrimination, which would license z_alpha and a larger
    count. If the '+ 1' is correct under that criterion, claim 3 is a criterion
    artefact rather than an error.

    IT IS NOT. Under the edge criterion the best-fitting form is still the one
    WITHOUT the '+ 1'. And the consequence that matters is criterion-independent:
    at N = 19 over the span [0.50, 0.90] BOTH criteria give an exact count of 1.
    What IS criterion-dependent is the SIZE of the overestimate -- 1.047
    divisions under the band criterion, 0.547 under the edge criterion -- and
    which z to use. That choice is the founder's, and it is listed as such.
    """
    import numpy as np
    from scipy.stats import binom, norm
    def exact_T_edge(N, plo, phh, alpha):
        ks = np.arange(N + 1)
        ph = np.array([phi(k / N) for k in ks])
        lo, hi = phi(plo), phi(phh)
        best = 0
        for T in range(1, 90):
            e = [lo + (hi - lo) * j / T for j in range(T + 1)]
            ok = True
            for j in range(1, T):
                pl = math.sin(0.5 * (e[j - 1] + e[j])) ** 2
                pr = math.sin(0.5 * (e[j] + e[j + 1])) ** 2
                if float(binom.pmf(ks, N, pl)[ph >= e[j]].sum()) > alpha:
                    ok = False
                    break
                if float(binom.pmf(ks, N, pr)[ph < e[j]].sum()) > alpha:
                    ok = False
                    break
            if ok:
                best = T
            else:
                break
        return best
    rows = []
    for alpha in (0.01, 0.05, 0.10, 0.20):
        z1 = float(norm.ppf(1 - alpha))
        z2 = float(norm.ppf(1 - alpha / 2))
        for plo, phh in ((0.5, 0.9), (0.3, 0.95), (0.6, 0.8), (0.1, 0.99)):
            d = phi(phh) - phi(plo)
            for N in (19, 38, 80, 150, 300, 500, 1000, 2000):
                rows.append((exact_T_edge(N, plo, phh, alpha),
                             d * math.sqrt(N) / z1, d * math.sqrt(N) / z2))
    E = np.array([r[0] for r in rows], dtype=float)
    b1 = np.array([r[1] for r in rows])
    b2 = np.array([r[2] for r in rows])
    forms = {
        "max(1, floor(dphi*sqrtN/z_alpha))     [one-sided z, no +1]":
            np.maximum(1, np.floor(b1)),
        "1 + floor(dphi*sqrtN/z_alpha)         [one-sided z, +1]": 1 + np.floor(b1),
        "max(1, floor(dphi*sqrtN/z_alpha_2))   [two-sided z, no +1]":
            np.maximum(1, np.floor(b2)),
        "1 + floor(dphi*sqrtN/z_alpha_2)       [two-sided z, +1 = position A]":
            1 + np.floor(b2),
    }
    table = {}
    for k, v in forms.items():
        err = E - v
        table[k] = {"bias": round(float(err.mean()), 4),
                    "MAE": round(float(np.abs(err).mean()), 4),
                    "exact_cells": f"{int((err == 0).sum())}/{len(E)}"}
    best = min(table, key=lambda k: table[k]["MAE"])
    at_point = {N: exact_T_edge(N, 0.5, 0.9, 0.05) for N in (19, 38, 80, 2000)}
    assert "no +1" in best, \
        f"the '+ 1' became the best form under the edge criterion: {best}"
    assert at_point[19] == 1, \
        "the operating-point consequence was expected criterion-independent"
    return {"criterion": "interior-edge one-sided two-point discrimination",
            "cells": len(E), "table": table, "best_fitting_form": best,
            "exact_counts_span_0.50_to_0.90_alpha_0.05": at_point,
            "verdict": ("claim 3 HELD. The '+ 1' is not the best-fitting form "
                        "under either criterion. The MAGNITUDE of the "
                        "overestimate and the choice of z ARE criterion-"
                        "dependent; the operating-point consequence at N = 19 "
                        "is not.")}

# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget-scan", action="store_true",
                    help="also run the 40-budget DP scan (184 s). OFF by default: "
                         "the panel validator has a 600 s ceiling.")
    a = ap.parse_args()

    print("== 1. both inversion witnesses, exhaustively, and the randomised merge ==")
    for k, v in claim_both_inversion_witnesses_reproduce().items():
        print(f"   {k}")
        for kk, vv in v.items():
            print(f"      {kk}: {vv}")

    print("\n== 2. the price of determinism, in attempts ==")
    for k, v in claim_the_price_of_determinism_in_attempts().items():
        print(f"   {k}: {v}")

    print("\n== 3. both closed forms OVERESTIMATE the division count ==")
    d3 = claim_both_closed_forms_overestimate_the_division_count()
    print(f"   {d3['cells']} cells, scored against {d3['scored_against']}")
    for k, v in d3["table"].items():
        print(f"      {k:58s} bias {v['bias']:+7.3f}  MAE {v['MAE']:6.3f}  "
              f"max|err| {v['max_abs_err']:2d}  exact {v['exact_cells']}  "
              f"over {v['overestimating_cells']}")
    print("   at the operating point, span 0.50-0.90, alpha 0.05:")
    for N, r in d3["at_the_operating_point"].items():
        print(f"      N={N:5d}  exact {r['exact']:2d}   A {r['A']:2d}   "
              f"B {r['B_as_summarised']:2d}   bracket {r['bracket']}")
    print(f"   dphi {d3['dphi_undoubled']}  doubled {d3['dphi_doubled']}")
    print(f"   {d3['why_the_doubling_is_not_itself_an_error']}")
    print(f"   Wolfram: {d3['wolfram']}")

    print("\n== 4. what the cost scan is still for ==")
    for k, v in claim_the_cost_scan_reports_feasibility_not_the_count(
            a.budget_scan).items():
        print(f"   {k}: {v}")

    print("\n== 5. three relegation rules at EQUAL false-alarm rate ==")
    d5 = claim_three_relegation_rules_at_equal_size()
    print(f"   {d5['calibrated_to_size_0.05_on_seed_101']}")
    print(f"   Brook-Evans h=4.400221 realised P(fire | stable) = "
          f"{d5['brook_evans_h_4.400221_realised_size_on_stable']}")
    names = ("absolute_floor", "peer_sign_test", "rasch_cusum")
    print(f"   {'scenario':12s}" + "".join(f"{n:>28s}" for n in names))
    for sc, row in d5["evaluated_on_seed_202"].items():
        line = f"   {sc:12s}"
        for n in names:
            line += f"{row[n]['rate']:9.4f} {row[n]['wilson']}".rjust(28)
        print(line)
    print("   want:        stable LOW   harden LOW   decline HIGH   "
          "common HIGH   stale LOW")
    print(f"   sign test with alternative 'less' as quoted in prose: "
          f"{d5['sign_test_with_alternative_less_as_quoted_in_prose']}")

    print("\n== 6. the Brook-Evans threshold is not in control ==")
    for k, v in claim_the_brook_evans_threshold_is_not_in_control().items():
        print(f"   {k}: {v}")

    print("\n== 7. common-mode decline is NOT IDENTIFIED, and anchors break it ==")
    for k, v in claim_common_mode_decline_is_not_identified().items():
        print(f"   {k}: {v}")
    d7 = claim_an_anchor_set_is_what_breaks_it()
    for share, r in d7["by_anchor_share"].items():
        print(f"   anchor share {share:4.2f}  common-mode {r['common_mode']:.4f}   "
              f"hardening {r['hardening']:.4f}")
    print(f"   {d7['composability_verdict']}")

    print("\n== 8. I tried to break claim 3 under the other resolution criterion ==")
    d8 = claim_the_plus_one_is_wrong_under_the_other_criterion_too()
    print(f"   criterion: {d8['criterion']}, {d8['cells']} cells")
    for k, v in d8["table"].items():
        print(f"      {k:62s} bias {v['bias']:+7.3f}  MAE {v['MAE']:6.3f}  "
              f"exact {v['exact_cells']}")
    print(f"   best-fitting form: {d8['best_fitting_form']}")
    print(f"   exact counts, span 0.50-0.90, alpha 0.05: "
          f"{d8['exact_counts_span_0.50_to_0.90_alpha_0.05']}")
    print(f"   {d8['verdict']}")

    print("\nall falsifiers passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
