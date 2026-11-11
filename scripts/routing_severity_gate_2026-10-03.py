#!/usr/bin/env python3
"""Does routing serve only criticals while A4 counts every severity?

`_apply_routing` (bench/reference_runner_v3.py:8609) skips any entry below
CRITICAL_SEVERITY_THRESHOLD. `unverified_critical_count` (:2747) has had NO
severity gate since founder ruling 23 (2026-09-06). If both hold, a finding
below 0.7 can never be served a falsifier, can never be released by the
`exhausted` valve (which also gates at 0.7), and is counted against A4 for the
life of the run.

This measures the association on a FINISHED run's registry rather than reading
the source: routed (has a routing_history) against severity >= 0.7.
"""
import argparse, json, pathlib
import numpy as np
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.contingency_tables import Table2x2
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
    ap.add_argument("--state", default=None)
    a = ap.parse_args()

    if getattr(a, "state", None) is None:
        ap.error("--state is required")

    d = json.loads(pathlib.Path(a.state).read_text(errors="replace"))
    entries = (d.get("registry") or {}).get("entries") or {}

    rows = []
    for cid, e in entries.items():
        sev = float(e.get("severity") or 0.0)
        rh = e.get("routing_history")
        routed = bool(rh)
        rows.append((cid, sev, sev >= CRIT, routed))

    crit_routed = sum(1 for _, _, c, r in rows if c and r)
    crit_unrouted = sum(1 for _, _, c, r in rows if c and not r)
    sub_routed = sum(1 for _, _, c, r in rows if not c and r)
    sub_unrouted = sum(1 for _, _, c, r in rows if not c and not r)

    print(f"entries: {len(rows)}")
    print()
    print("                      routed   not routed")
    print(f"  severity >= {CRIT}      {crit_routed:5d}   {crit_unrouted:9d}")
    print(f"  severity <  {CRIT}      {sub_routed:5d}   {sub_unrouted:9d}")
    print()

    # Fisher exact, two tools
    table = [[crit_routed, crit_unrouted], [sub_routed, sub_unrouted]]
    odds_sp, p_sp = sps.fisher_exact(table)
    print(f"  scipy Fisher exact : p = {p_sp:.6e}  OR = {odds_sp}")
    try:
        t2 = Table2x2(np.array(table) + 0.5)   # Haldane correction for a zero cell
        print(f"  statsmodels Table2x2 (Haldane-corrected) OR = "
              f"{t2.oddsratio:.6f}, 95% CI {tuple(round(x,6) for x in t2.oddsratio_confint())}")
    except Exception as exc:
        print(f"  statsmodels Table2x2 unavailable: {exc}")

    # the decisive proportion: of SUB-critical entries, how many were ever routed?
    n_sub = sub_routed + sub_unrouted
    if n_sub:
        # * DELEGATED 2026-11-08, as above. The printed `(statsmodels ==
        # mpmath)` claim stays backed by the helper's own returned gap.
        (lo, hi), _cp, _gap = _iv(sub_routed, n_sub)
        assert _gap < 1e-9, "statsmodels and mpmath disagree on Wilson"
        print()
        print(f"  SUB-CRITICAL entries ever routed: {sub_routed}/{n_sub} = "
              f"{100.0*sub_routed/n_sub:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]"
              f"  (statsmodels == mpmath)")

    # and the A4 blockers specifically
    print()
    print("  THE A4 BLOCKERS (UNCONFIRMED, no resolved falsifier):")
    for cid, e in sorted(entries.items()):
        if e.get("status") != "UNCONFIRMED":
            continue
        sev = float(e.get("severity") or 0.0)
        rh = e.get("routing_history")
        print(f"    {cid}  sev={sev:.2f}  {'>=0.7' if sev>=CRIT else '< 0.7'}  "
              f"routing_history={'present len '+str(len(rh)) if rh else 'ABSENT'}")


if __name__ == "__main__":
    raise SystemExit(main())
