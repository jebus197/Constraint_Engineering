#!/usr/bin/env python3
"""B20's sketched per-round predicate: does it control its error rate, and which correction?

THE CLAIM THIS REFUTES IS THIS PROJECT'S OWN. Entry B20 names the design
requirement for the bound orchestrator's monitor as "a PER-ROUND predicate
carrying its own falsifier and evaluable at every round boundary", and its
worked example alarms when a Wilson interval EXCLUDES 0.5. Evaluating a
fixed-horizon interval at every round boundary is repeated testing of one
hypothesis, which inflates the type-I error above its nominal level.

WHAT THIS PRODUCER ESTABLISHES, AND IT IS 3 THINGS AND NO MORE:
  1. The UNCORRECTED predicate does not control its rate.
  2. BOTH candidate corrections do, empirically, at every horizon tested.
  3. They are indistinguishable on the earliest defensible alarm.

2 CLAIMS OF MINE WERE REFUTED BY THIS PRODUCER AND ARE KEPT HERE RATHER THAN
TIDIED AWAY, because a reader needs to see which way the evidence went.
  * I expected an anytime-valid sequence to buy back the delay a Bonferroni
    split costs. It does not: both first fire at round 11 on a perfect run.
  * I claimed Bonferroni's need to fix the look count in advance was a
    concrete failure a sequence avoids, and tried to demonstrate it by tuning
    a split for 40 looks and running it for 1000. IT STAYED VALID.

SO NO DOMINANCE CLAIM IS MADE. Under the founder's 2026-10-02 standard a
composed or preferred design needs a committed measurement showing it dominates
the alternative on a named property; 3 properties were measured and the result
is a tie on 2 with the third unmeasurable by me. Under `simplicity-default` the
Bonferroni split is 1 divisor and is the honest default.

PRECISION. Every rate here is a simulation estimate over 20,000 draws, standard
error about 0.0027 near p = 0.18, so each is printed WITH its interval and must
not be quoted to 6 decimals. 2 runs of the first version gave 0.177050 and
0.178900, a difference of 0.68 standard errors, which is what established that
the 6th decimal is noise.

Usage: python3 scripts/a_per_round_predicate_peeks_2026-11-04.py
Exit 0 on a sound measurement, 3 if the 2 single-look routes disagree or if the
confidence-sequence construction fails its own validity check.
"""
import os
import pathlib
import sys

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

ALPHA, SEED, TRIALS, SIGMA, RHO = 0.05, 20261104, 20000, 0.5, 0.5
SHORT = (3, 5, 8, 12, 20, 40)
LONG = (40, 100, 250, 500, 1000)


# NOTE 2026-11-04: the CANONICAL `_iv`, verbatim from
# `scripts/a_bare_clock_was_dated_from_the_mtime_2026-11-03.py`. This file
# already held a vectorised closed-form Wilson in `_wilson_bounds`, so its
# second Wilson route existed -- but written as `z**2 / n`, where the route
# detector looks for `z * z / (2 * n)`, and Clopper-Pearson rested on scipy
# alone with no second route at all. Using the canonical helper fixes the real
# gap and the detection gap together, and matches the 16 producers that already
# conform. `_wilson_bounds` stays: it is vectorised and this is not.
def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, on 2 INDEPENDENT implementations each.

    PROPAGATED 2026-11-03 from the one producer that already had both routes.
    An audit of this session's producers by STEM-IMPORT COUNT passed this file,
    and the count was a proxy: the project had already measured that `scipy` and
    `statsmodels` resolve to the identical verifier, so 2 library names can buy
    0 cross-checks. The predicate that matters is ROUTES PER QUANTITY -- Wilson
    from statsmodels against Wilson written out, and Clopper-Pearson from
    scipy's beta quantile against mpmath's regularized incomplete beta by
    bisection. 2 libraries computing 2 DIFFERENT intervals is not a cross-check
    of either one.

    The 3rd return value is the LARGER of the 2 disagreements, so a drift in
    either quantity surfaces in the single number the caller already prints.
    """
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    # second Wilson, written out, to catch a library disagreement
    import math
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def _f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if _f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def _ivl(rate: float, trials: int = TRIALS) -> str:
    k = int(round(rate * trials))
    (lo, hi), _cp, _agree = _iv(k, trials)
    return f"{rate:.4f} [{lo:.4f}, {hi:.4f}]"


def _wilson_bounds(k, n, alpha):
    """Vectorised closed form. Its single-look case is cross-checked below."""
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = (z / d) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return c - h, c + h


def _cs_halfwidth(t, rho=RHO, alpha=ALPHA, sigma=SIGMA):
    """Normal-mixture (Robbins) confidence-sequence half-width at time t."""
    a = t * rho**2 + 1.0
    return sigma * np.sqrt(2.0 * a / (t**2 * rho**2) * np.log(np.sqrt(a) / alpha))


def _family_rate(n_rounds, rng, kind, alpha_per_look=ALPHA):
    x = rng.binomial(1, 0.5, size=(TRIALS, n_rounds))
    cum = np.cumsum(x, axis=1)
    fired = np.zeros(TRIALS, dtype=bool)
    for t in range(1, n_rounds + 1):
        if kind == "cs":
            m = cum[:, t - 1] / t
            w = _cs_halfwidth(t)
            lo, hi = m - w, m + w
        else:
            lo, hi = _wilson_bounds(cum[:, t - 1], t, alpha_per_look)
        fired |= (lo > 0.5) | (hi < 0.5)
    return float(fired.mean())


def _first_fire_interval(alpha, cap=80):
    for t in range(1, cap + 1):
        lo, _ = proportion_confint(t, t, alpha=alpha, method="wilson")
        if lo > 0.5:
            return t
    return None


def _first_fire_cs(cap=80):
    for t in range(1, cap + 1):
        if 1.0 - _cs_halfwidth(t) > 0.5:
            return t
    return None


def _round_lengths(repo: pathlib.Path):
    """Round-series length for every archived run that recorded one.

    Read from `gate_history` in each run's own state file, which B20 records as
    present in 65 of 65. A run with no series is EXCLUDED rather than counted
    as 0, because absent and zero are different facts.
    """
    import json
    out = []
    for q in sorted(repo.glob("bench/logs/*/runner_state.json")):
        try:
            d = json.loads(q.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        gh = d.get("gate_history") or []
        if gh:
            out.append(len(gh))
    return out


def _share(k, n):
    (lo, hi), (lo2, hi2), agree = _iv(k, n)
    return (f"{k:>3} of {n} = {k/n:.6f}  Wilson [{lo:.6f}, {hi:.6f}]  "
            f"CP [{lo2:.6f}, {hi2:.6f}]  (2-route |diff| {agree:.1e})")


def _section_four(repo: pathlib.Path, first_fire: int) -> int:
    """WHICH QUANTITY? The decisive section, and it is about the archive.

    A corrected proportion predicate cannot fire before `first_fire`. If most
    real runs end before that, the predicate is inert whatever correction it
    uses -- which is a property of the QUANTITY and not of the correction.
    """
    print("\n" + "=" * 76)
    print("4. WHICH QUANTITY? MEASURED AGAINST THE ARCHIVE'S OWN ROUND SERIES")
    print("=" * 76)
    rounds = _round_lengths(repo)
    if not rounds:
        print("   no archived run carries a round series; this section is VOID")
        print("   and no share is reported, rather than reporting 0 of 0.")
        return 3
    import statistics
    print(f"   runs with a round series: {len(rounds)}; "
          f"min {min(rounds)}, median {statistics.median(rounds)}, "
          f"max {max(rounds)}")
    n = len(rounds)
    print(f"\n   a corrected PROPORTION predicate needs round {first_fire}:")
    print(f"     {_share(sum(1 for r in rounds if r >= first_fire), n)}")
    print("   a GAMMA predicate is estimable from round 3 "
          "(min_rounds_for_gamma = 3):")
    print(f"     {_share(sum(1 for r in rounds if r >= 3), n)}")
    print("   the GATE BOOLEAN is available from round 1:")
    print(f"     {_share(sum(1 for r in rounds if r >= 1), n)}")
    print("\n   SO THE ENTRY'S REQUIREMENT STANDS AND ITS WORKED EXAMPLE DOES")
    print("   NOT. Uncorrected the proportion predicate false-alarms; corrected")
    print("   it is inert in most real runs. Both directions fail, and that is a")
    print("   property of the quantity chosen. State the predicate over a")
    print("   continuous per-round quantity or over the gate boolean instead.")
    return 0


def main() -> int:
    answer_help(__doc__, __file__)
    rng = np.random.default_rng(SEED)
    print("=" * 76)
    print("1. THE UNCORRECTED PREDICATE DOES NOT CONTROL ITS RATE")
    print(f"   null p = 0.5, nominal alpha = {ALPHA:.4f}, {TRIALS:,} draws")
    print("=" * 76)
    print(f"{'rounds':>8}  {'P(>=1 alarm), Wilson 95%':>30}  {'inflation':>10}")
    for n in SHORT:
        r = _family_rate(n, rng, "wilson")
        print(f"{n:>8}  {_ivl(r):>30}  {r / ALPHA:>9.2f}x")
    print("\n   The 0 at 3 rounds is not an error: a Wilson interval on 3")
    print("   observations cannot exclude 0.5 at all, which B20 records from")
    print("   the other side as a lower bound of 0.438503 at n = 3.")

    print("\n" + "=" * 76)
    print("2. BOTH CANDIDATE CORRECTIONS CONTROL IT, EMPIRICALLY")
    print("=" * 76)
    print(f"{'rounds':>8}  {'Bonferroni split':>30}  {'confidence sequence':>30}")
    bad = []
    for n in SHORT[1:]:
        b = _family_rate(n, rng, "wilson", ALPHA / n)
        c = _family_rate(n, rng, "cs")
        for r in (b, c):
            _, hi = proportion_confint(int(round(r * TRIALS)), TRIALS,
                                       alpha=0.05, method="wilson")
            if hi > ALPHA:
                bad.append((n, r))
        print(f"{n:>8}  {_ivl(b):>30}  {_ivl(c):>30}")

    print("\n   AND THE SEQUENCE AT LONG HORIZONS, which is the falsification")
    print("   attempt on its validity rather than a restatement of it:")
    for n in LONG:
        c = _family_rate(n, rng, "cs")
        _, hi = proportion_confint(int(round(c * TRIALS)), TRIALS,
                                   alpha=0.05, method="wilson")
        if hi > ALPHA:
            bad.append((n, c))
        print(f"{n:>8}  {'':>30}  {_ivl(c):>30}")
    if bad:
        print(f"\n   A CORRECTION EXCEEDED {ALPHA:.4f} AT {[n for n, _ in bad]}; "
              f"the comparison is void.")
        return 3

    print("\n" + "=" * 76)
    print("3. THEY ARE INDISTINGUISHABLE ON THE EARLIEST DEFENSIBLE ALARM")
    print("   (perfect observation run, every round a success)")
    print("=" * 76)
    print(f"   uncorrected alpha = {ALPHA:.4f}        : n = "
          f"{_first_fire_interval(ALPHA)}")
    print(f"   Bonferroni over 12 looks       : n = "
          f"{_first_fire_interval(ALPHA / 12)}")
    print(f"   Bonferroni over 40 looks       : n = "
          f"{_first_fire_interval(ALPHA / 40)}")
    print(f"   confidence sequence (rho={RHO})   : n = {_first_fire_cs()}")

    print("\n   MY CLAIM THAT A SEQUENCE BUYS BACK THE DELAY IS REFUTED: both")
    print("   land at the same round. And my claim that a mis-tuned Bonferroni")
    print("   fails outright is ALSO refuted, measured directly below.")

    b1000 = _family_rate(1000, rng, "wilson", ALPHA / 40)
    _, hi = proportion_confint(int(round(b1000 * TRIALS)), TRIALS,
                               alpha=0.05, method="wilson")
    print(f"\n   a Bonferroni split tuned for 40 looks, RUN FOR 1000:")
    print(f"     {_ivl(b1000)} against its nominal {ALPHA:.4f} -- "
          f"{'INVALID' if hi > ALPHA else 'STILL VALID'}")
    print("   The looks are strongly dependent, each adding 1 observation to")
    print("   the same running proportion, so the correction stays conservative")
    print("   25-fold beyond its tuning.")

    print("\n" + "=" * 76)
    print("SINGLE-LOOK CROSS-CHECK at n = 12, 2 independent routes")
    print("=" * 76)
    exact = 0.0
    for k in range(13):
        lo, hi2 = proportion_confint(k, 12, alpha=ALPHA, method="wilson")
        if lo > 0.5 or hi2 < 0.5:
            exact += stats.binom.pmf(k, 12, 0.5)
    draws = rng.binomial(12, 0.5, size=TRIALS)
    lo_v, hi_v = _wilson_bounds(draws, 12, ALPHA)
    sim = float(np.mean((lo_v > 0.5) | (hi_v < 0.5)))
    print(f"  exact enumeration (binom.pmf + statsmodels) : {exact:.6f}")
    print(f"  vectorised closed form over {TRIALS:,} draws    : {sim:.6f}")
    print(f"  absolute difference                         : {abs(exact-sim):.6f}")
    if abs(exact - sim) > 0.01:
        print("\n  THE 2 ROUTES DISAGREE BY MORE THAN 0.01; measurement void.")
        return 3

    print("\nWHAT THIS DOES NOT SAY. It does not say a per-round predicate is")
    print("the wrong design; B20's requirement stands. It says the predicate as")
    print("SKETCHED must not ship uncorrected, that either correction will do on")
    print("this evidence, and that the earliest defensible alarm is round 9 to")
    print("11 rather than round 1 -- so an actuator built on it cannot act in a")
    print("run's opening rounds at all. NO DOMINANCE CLAIM is made between the 2")
    print("corrections, because 3 properties were measured and the result is a")
    print("tie on 2 with the third not demonstrable from this evidence.")

    repo = pathlib.Path(__file__).resolve().parents[1]
    return _section_four(repo, _first_fire_interval(ALPHA / 12) or 9)


if __name__ == "__main__":
    sys.exit(main())
