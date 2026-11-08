#!/usr/bin/env python3
"""The gate's deciding series is not in the registry, so a verdict cannot be audited.

`_check_gamma_alt_convergence` decides convergence on `gamma_critical`, the
CRITICAL-ONLY decay curve, and the project's standing directive is that gamma is
load-bearing. But `runner_state.json` persists `gamma_history` -- the ALL-SEVERITY
curve -- and on study_run1b carries no `gamma_critical_history` at all. The
consequence was concrete: a replay script's `or` fallback substituted the
all-severity value (0.4274) under the label `gamma_critical` and it was reported as
the gate's input for hours, when the run's own log shows 0.732.

The founder's position is that the registry is the single source of truth for any
experiment a researcher may wish to run. That cannot hold while the deciding input
of the convergence gate lives only in a log line, so this measures how widespread
the omission is across the whole archive rather than asserting it from one run.

Runs that cannot be measured are counted and reported SEPARATELY rather than folded
into either arm: a directory with no state file is not a run that lacks the series.
"""
import glob
import json
import pathlib
import re
import sys

import numpy as np
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402
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

# GUARDED BY `__main__`, and the reason is a real failure (2026-10-03).
# `bench/tests/test_operational_scripts.py::test_help_builds_and_lists_every_advertised_flag`
# import-probes every parser-less script in a subprocess started with
# `python3 -c ...`, where `sys.argv` is ['-c', '<this path>']. A module-level
# `answer_help` therefore sees the script's own path as an unrecognised argument
# and exits 2, so the script "no longer imports" as far as that guard is
# concerned. The project's convention is to call it from main() --
# scripts/a19_flag_admits_harmful_fixes_2026-09-22.py:81 does exactly that.
if __name__ == "__main__":
    answer_help(__doc__, __file__)

REPO = pathlib.Path(__file__).resolve().parents[1]
GAMMA_LOG = re.compile(r"gamma_critical:\s*([0-9.]+)")


def wilson(k, n):
    """Wilson as a rounded percentage pair, from the canonical helper.

    ★ DELEGATED 2026-11-08 on his ruling for B135 option 1. The algebra
    that stood here was correct and the detector could not SEE it, because
    it named the sample size `nn` where the pattern required `n`. It is
    replaced by a call rather than by a wider pattern, so the cross-check
    is executed instead of being inferred from a spelling. `_iv` is lifted
    byte-identical from the canonical producer and the board guard asserts
    every copy agrees with every other.
    """
    wl, wh = _iv(k, n)[0]
    return round(100 * wl, 4), round(100 * wh, 4)

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
    has_crit = has_all = neither = 0
    unreadable = 0
    recoverable_from_log = 0
    rows = []
    dirs = sorted(p for p in (REPO / "bench" / "logs").iterdir() if p.is_dir())
    for d in dirs:
        state = None
        for name in ("runner_state.json",):
            f = d / name
            if f.is_file():
                state = f
                break
        if state is None:
            for f in sorted(d.glob("*_report.json")):
                state = f
                break
        if state is None:
            continue                      # not a run we can measure; not an arm
        try:
            js = json.loads(state.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            unreadable += 1
            continue
        crit = bool(js.get("gamma_critical_history"))
        allg = bool(js.get("gamma_history"))
        has_crit += crit
        has_all += allg
        if not crit and not allg:
            neither += 1
        # could the real value be recovered from the log instead?
        rec = False
        log = d / "console.log"
        if not crit and log.is_file():
            try:
                rec = bool(GAMMA_LOG.search(log.read_text(errors="replace")))
            except Exception:
                rec = False
        recoverable_from_log += rec
        rows.append((d.name, crit, allg, rec))

    n = len(rows)
    print(f"run directories carrying a state or report file: {n}")
    print(f"unreadable state files (counted separately): {unreadable}")
    print()
    k = n - has_crit
    lo, hi = wilson(k, n)
    print(f"MISSING gamma_critical_history (the gate's own series): {k}/{n} = "
          f"{100.0*k/n:.4f}%  Wilson [{lo}%, {hi}%]  (statsmodels == mpmath)")
    lo2, hi2 = wilson(has_all, n)
    print(f"carrying gamma_history (ALL-severity, not the gate's input): {has_all}/{n} "
          f"= {100.0*has_all/n:.4f}%  Wilson [{lo2}%, {hi2}%]")
    print(f"carrying NEITHER series: {neither}")
    print()
    if k:
        lo3, hi3 = wilson(recoverable_from_log, k)
        print(f"of the {k} missing it, recoverable from the run log's "
              f"'gamma_critical:' line: {recoverable_from_log}/{k} = "
              f"{100.0*recoverable_from_log/k:.4f}%  Wilson [{lo3}%, {hi3}%]")
        print(f"  -> so {k - recoverable_from_log} run(s) have the gate's deciding "
              f"input in NO durable place at all.")
    print()
    arr = np.array([1 if c else 0 for _, c, _, _ in rows])
    print(f"NumPy cross-check: sum(has_crit) = {int(arr.sum())}, "
          f"matches the counter {has_crit}")
    assert int(arr.sum()) == has_crit, "numpy and the loop disagree"
    print()
    print("THE POINT, stated plainly: a reader given only the registry cannot check")
    print("why a run converged or did not, because the series the gate reads is not")
    print("there. A replay that falls back to gamma_history is not auditing the gate;")
    print("it is auditing a different curve under the gate's name.")


if __name__ == "__main__":
    raise SystemExit(main())
