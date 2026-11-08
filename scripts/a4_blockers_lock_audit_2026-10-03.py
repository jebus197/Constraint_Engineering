#!/usr/bin/env python3
"""Which locks hold each A4 blocker shut, for a finished run.

The A4 fail-safe (unverified_critical_count, reference_runner_v3.py:2747) blocks
the zero-critical streak while any UNCONFIRMED critical is pending. The only
escape is the `exhausted` valve, which needs THREE conditions at once:

    status in EXHAUSTED_ELIGIBLE_STATUSES  and  severity >= 0.7
    and  age >= exhausted_round_threshold  and  len(verdicts) > 0

This prints, per blocking entry, which of those are open and which are shut, so
a proposed threshold change can be judged against the entries it would have to
free rather than against the mechanism in the abstract.
"""
import argparse, json, pathlib
import numpy as np
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp
import math


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
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

        def f(x):
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
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)

VALVE = ("OPEN", "CONTESTED", "REOPENED", "CORROBORATED", "WITHHELD", "UNCONFIRMED")
CRIT = 0.7

def main() -> int:
    """★ THE BODY MOVED HERE ON 2026-11-08 SO THIS FILE CAN BE IMPORTED.

    It ran at module level, so importing it either handed argparse the
    importing process's argv and raised `SystemExit: 2`, or printed its whole
    report. B135's option 1 requires the shared interval helper to be EXECUTED
    by `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`, which
    imports every script defining one; an unimportable producer makes that
    helper unreachable. Command-line behaviour is unchanged and was asserted
    byte for byte against a baseline taken before the edit.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", default=None)
    ap.add_argument("--threshold", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=8)
    a = ap.parse_args()

    if getattr(a, "run", None) is None:
        ap.error("--run is required")

    run = pathlib.Path(a.run)
    d = json.loads((run / "runner_state.json").read_text(errors="replace"))
    entries = (d.get("registry") or {}).get("entries") or {}
    final_round = a.rounds - 1          # 0-based

    blockers = {cid: e for cid, e in entries.items()
                if e.get("status") == "UNCONFIRMED" and e.get("severity", 0) >= CRIT}

    print(f"run: {run.name}   entries: {len(entries)}   "
          f"final round_idx: {final_round}   threshold: {a.threshold}")
    print(f"A4 blockers (UNCONFIRMED and severity >= {CRIT}): {len(blockers)}")
    print()

    would_free_now, would_free_at_7, shut_by_reviews = [], [], []
    for cid, e in sorted(blockers.items()):
        lscr = e.get("last_status_change_round", 0)
        age = final_round - lscr
        nverd = len(e.get("verdicts", []) or [])
        l_status = e.get("status") in VALVE
        l_sev = e.get("severity", 0) >= CRIT
        l_age = age >= a.threshold
        l_rev = nverd > 0
        print(f"  {cid}  severity={e.get('severity'):.2f}  status={e.get('status')}")
        print(f"      last_status_change_round={lscr}  age at final round={age}")
        print(f"      verdicts={nverd}")
        print(f"      LOCKS -> status:{'OPEN' if l_status else 'SHUT'}  "
              f"severity:{'OPEN' if l_sev else 'SHUT'}  "
              f"age>={a.threshold}:{'OPEN' if l_age else 'SHUT'}  "
              f"has_reviews:{'OPEN' if l_rev else 'SHUT'}")
        freed = l_status and l_sev and l_age and l_rev
        freed_t7 = l_status and l_sev and (age >= final_round) and l_rev
        print(f"      valve fires as configured (T={a.threshold}): {freed}")
        print(f"      valve would fire at T={final_round}: {freed_t7}")
        print()
        if freed: would_free_now.append(cid)
        if freed_t7: would_free_at_7.append(cid)
        if not l_rev: shut_by_reviews.append(cid)

    n = len(blockers)
    print(f"SUMMARY over {n} blocker(s):")
    print(f"  freed as configured (T={a.threshold}) : {len(would_free_now)} {would_free_now}")
    print(f"  freed if T lowered to {final_round}        : {len(would_free_at_7)} {would_free_at_7}")
    print(f"  still shut by has_reviews         : {len(shut_by_reviews)} {shut_by_reviews}")
    print()

    if n:
        k = len(shut_by_reviews)
        # * DELEGATED 2026-11-08 on his ruling for B135 option 1. The algebra
        # that stood here was correct and the detector could not SEE it,
        # because it named the sample size `nn` where the pattern required
        # `n`. The printed claim `(statsmodels == mpmath)` is still BACKED:
        # `_iv` returns the larger of its 2 route disagreements and it is
        # asserted here, exactly as the inline assert did.
        (lo, hi), _cp, _gap = _iv(k, n)
        assert _gap < 1e-9, \
            "statsmodels and mpmath disagree on the Wilson interval"
        print(f"  shut by has_reviews: {k}/{n} = {100.0*k/n:.4f}%  "
              f"Wilson [{100*lo:.4f}%, {100*hi:.4f}%]  (statsmodels == mpmath)")

        ages = np.array([final_round - e.get("last_status_change_round", 0)
                         for e in blockers.values()])
        print(f"  ages (NumPy): min={ages.min()} max={ages.max()} "
              f"mean={ages.mean():.4f}")
        print(f"  threshold needed to free the OLDEST blocker: {ages.max()}")


if __name__ == "__main__":
    raise SystemExit(main())
