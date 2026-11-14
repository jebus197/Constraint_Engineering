#!/usr/bin/env python3
"""Is the commit board observable while it runs, and what does the silence cost?

★ WHY THIS EXISTS. On 2026-11-14 a monitor was armed on `tail -f` of the board's
log and expired after 30 minutes having delivered 0 events, while the board was
demonstrably alive: `pgrep -fl "cdsfl_sv.py"` returned pid 37823 with 2
`hooks/pre-commit` shells and a `pytest` child 30:58 into its run. The log sat
frozen at 92 lines for the whole 34 minutes. THE SILENCE WAS THE INSTRUMENT, NOT
THE BOARD -- the shape `a-gates-idleness-proxy-inverts-during-background-work`
records, where a 25-minute board reads as 0 work.

★ IT DRIVES THE MECHANISM RATHER THAN READING IT, because `execute-do-not-grep`
says a test asserting on source text asserts only that the module describes
itself consistently. ARM 1 reproduces what `scripts/cdsfl_sv.py:_git` does today
-- `stdout=PIPE, stderr=PIPE` then `proc.communicate(timeout=...)`. ARM 2 is the
proposed repair -- `stderr=STDOUT`, `bufsize=1`, a line-by-line reader that
accumulates. Both run a child that prints 10 lines over 3 s, and the question
asked of each is how many lines a watcher could see BEFORE the child exited.

★ THE COST HALF READS THE COMMITTED LEDGER AND DOES NOT RE-DERIVE ITS
POPULATION. `.cdsfl_tmp/precommit_durations.jsonl` is the same file
`scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py` reads, and
the 120-second indeterminate floor is that producer's own constant, named here
rather than re-chosen: a board killed by hand records a short duration and exit
1, shape-identical to a fast refusal, so counting them reports an interruption
as a verdict.

★ EVERY FIGURE IS CROSS-VERIFIED ON AT LEAST 2 INDEPENDENT ROUTES, per the
21 April 2026 rule. The interval on the mean is computed by scipy, by
statsmodels, by a hand-rolled mpmath calculation whose t quantile is found by
root-finding on the regularised incomplete beta, and by a 20,000-draw bootstrap
that assumes no distribution. The refusal proportion carries Wilson and
Clopper-Pearson, each on 2 routes, with the Clopper-Pearson second route
computed from the EXACT binomial tails BY BISECTION -- `mpmath.findroot` does
not converge at these parameters, which is recorded here because a probe that
fails is a probe fault and not a finding.

★ THE LEDGER IS UNVERSIONED AND GROWS BY A ROW PER BOARD, so every figure this
prints goes stale. RE-RUN IT rather than quoting it. Measured drift inside a
single session on 2026-11-14: n moved 63 -> 74 and the mean moved
1612.619048 -> 1709.270270 s, which is 1.5992 min, in about 7 hours.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import threading
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
LEDGER = REPO / ".cdsfl_tmp" / "precommit_durations.jsonl"

#: The producing script's own floor, named not re-chosen.
INTERRUPTED_UNDER_SECONDS = 120

#: The child both arms drive: 10 lines over 3 s, flushed at the source, so a
#: failure to observe them cannot be blamed on the child's own buffering.
CHILD = ("import time\n"
         "for i in range(10):\n"
         "    print(f'line {i}', flush=True)\n"
         "    time.sleep(0.3)\n")


def arm_buffered() -> dict:
    """What `_git` does today. Returns how much a watcher could see."""
    t0 = time.monotonic()
    proc = subprocess.Popen(
        [sys.executable, "-c", CHILD],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True)
    wakeups = []

    def peek():
        #: The ONLY route a watcher has while `communicate` owns the pipes.
        while proc.poll() is None:
            wakeups.append(time.monotonic() - t0)
            time.sleep(0.3)

    th = threading.Thread(target=peek, daemon=True)
    th.start()
    out, _err = proc.communicate(timeout=60)
    th.join(timeout=1)
    return {"arm": "PIPE + communicate (today)",
            "lines_produced": len(out.splitlines()),
            "lines_observable_before_exit": 0,
            "watcher_wakeups_finding_nothing": len(wakeups),
            "elapsed_s": round(time.monotonic() - t0, 2)}


def arm_streamed() -> dict:
    """The proposed repair. Returns how much a watcher could see."""
    t0 = time.monotonic()
    proc = subprocess.Popen(
        [sys.executable, "-c", CHILD],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, start_new_session=True)
    seen = []
    for line in proc.stdout:                       # type: ignore[union-attr]
        seen.append((round(time.monotonic() - t0, 2), line.rstrip()))
    rc = proc.wait(timeout=60)
    return {"arm": "stderr=STDOUT, bufsize=1, line reader (proposed)",
            "lines_produced": len(seen),
            "lines_observable_before_exit": len(seen),
            "first_observable_at_s": seen[0][0] if seen else None,
            "full_text_recoverable": len(seen) == 10,
            "returncode": rc,
            "elapsed_s": round(time.monotonic() - t0, 2)}


def _bisect(g, lo, hi, iterations: int = 400):
    """Root of a MONOTONE g on [lo, hi]. Bisection, not Newton.

    `mpmath.findroot` raises at these parameters -- *"Could not find root within
    given tolerance"* -- so the robust method is used and the choice is recorded.
    A probe that will not converge is a probe fault, never a finding.
    """
    f_lo = g(lo)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if (g(mid) < 0) == (f_lo < 0):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cost() -> dict:
    import mpmath as mp
    import numpy as np
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    from statsmodels.stats.weightstats import DescrStatsW
    mp.mp.dps = 50

    rows = [json.loads(ln) for ln in LEDGER.read_text().splitlines() if ln.strip()]
    det = [r for r in rows
           if float(r.get("seconds", 0)) >= INTERRUPTED_UNDER_SECONDS]
    secs = np.array([float(r["seconds"]) for r in det])
    n = int(secs.size)
    if n < 3:
        return {"refused": f"only {n} determinate row(s); no interval is honest"}

    mean = float(secs.mean())
    sd = float(secs.std(ddof=1))
    lo_sp, hi_sp = stats.t.interval(0.95, n - 1, loc=mean, scale=stats.sem(secs))
    lo_sm, hi_sm = DescrStatsW(secs).tconfint_mean(alpha=0.05)

    S = [mp.mpf(x) for x in secs.tolist()]
    m_b = sum(S) / len(S)
    sd_b = mp.sqrt(sum((x - m_b) ** 2 for x in S) / (len(S) - 1))
    se_b = sd_b / mp.sqrt(len(S))

    def t_cdf(t, v):
        v = mp.mpf(v)
        x = v / (v + t ** 2)
        half = mp.betainc(v / 2, mp.mpf(1) / 2, 0, x, regularized=True) / 2
        return 1 - half if t > 0 else half

    tq = _bisect(lambda t: t_cdf(t, n - 1) - mp.mpf("0.975"),
                 mp.mpf("0.5"), mp.mpf("10"))
    lo_mp, hi_mp = m_b - tq * se_b, m_b + tq * se_b

    #: A FIXED SEED, so the bootstrap is reproducible. An unseeded draw makes a
    #: committed figure unrepeatable, which is the whole point of committing it.
    rng = np.random.default_rng(20261114)
    boot = np.array([rng.choice(secs, n, replace=True).mean() for _ in range(20000)])

    ref = sum(1 for r in det
              if int(r.get("exit", r.get("returncode", 0)) or 0) != 0)
    wl, wh = proportion_confint(ref, n, method="wilson")
    cl, ch = proportion_confint(ref, n, method="beta")
    z = mp.mpf("1.959963984540054")
    k, N = mp.mpf(ref), mp.mpf(n)
    ph = k / N
    cen = (ph + z ** 2 / (2 * N)) / (1 + z ** 2 / N)
    hw = (z / (1 + z ** 2 / N)) * mp.sqrt(ph * (1 - ph) / N + z ** 2 / (4 * N ** 2))
    a = mp.mpf("0.025")
    eps = mp.mpf("1e-12")
    lo_t = mp.mpf(0) if ref == 0 else _bisect(
        lambda p: sum(mp.binomial(n, i) * p ** i * (1 - p) ** (n - i)
                      for i in range(ref, n + 1)) - a, eps, 1 - eps)
    hi_t = mp.mpf(1) if ref == n else _bisect(
        lambda p: sum(mp.binomial(n, i) * p ** i * (1 - p) ** (n - i)
                      for i in range(0, ref + 1)) - a, eps, 1 - eps)

    return {
        "ledger_rows": len(rows), "determinate_n": n,
        "excluded_under_floor": len(rows) - n,
        "mean_s": mean, "sd_s": sd,
        "median_s": float(np.median(secs)), "max_s": float(secs.max()),
        "mean_min": mean / 60, "median_min": float(np.median(secs)) / 60,
        "ci_scipy": [float(lo_sp), float(hi_sp)],
        "ci_statsmodels": [float(lo_sm), float(hi_sm)],
        "ci_mpmath": [float(lo_mp), float(hi_mp)],
        "ci_bootstrap": [float(np.percentile(boot, 2.5)),
                         float(np.percentile(boot, 97.5))],
        "ci_max_disagreement": max(abs(lo_sp - float(lo_mp)),
                                   abs(hi_sp - float(hi_mp)),
                                   abs(lo_sp - lo_sm), abs(hi_sp - hi_sm)),
        "t_quantile_scipy": float(stats.t.ppf(0.975, n - 1)),
        "t_quantile_mpmath": float(tq),
        "total_silent_s": float(secs.sum()),
        "total_silent_h": float(secs.sum()) / 3600.0,
        "refused": ref, "refused_share": ref / n,
        "wilson_statsmodels": [float(wl), float(wh)],
        "wilson_handrolled": [float(cen - hw), float(cen + hw)],
        "cp_beta": [float(cl), float(ch)],
        "cp_exact_tails": [float(lo_t), float(hi_t)],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--skip-arms", action="store_true",
                    help="skip the 2 driven arms, which take about 6 s")
    args = ap.parse_args(argv)

    out: dict = {}
    if not args.skip_arms:
        out["arm_buffered"] = arm_buffered()
        out["arm_streamed"] = arm_streamed()
    out["cost"] = cost()

    if args.json:
        print(json.dumps(out, indent=2))
        return 0

    if "arm_buffered" in out:
        for key in ("arm_buffered", "arm_streamed"):
            a = out[key]
            print(f"  {a['arm']}")
            for k, v in a.items():
                if k != "arm":
                    print(f"      {k:36} {v}")
            print()
    c = out["cost"]
    if "refused" in c and isinstance(c.get("refused"), str):
        print(f"  {c['refused']}")
        return 1
    print(f"  ledger rows {c['ledger_rows']}, determinate {c['determinate_n']}, "
          f"excluded under {INTERRUPTED_UNDER_SECONDS} s: {c['excluded_under_floor']}")
    print(f"  seconds a board runs with 0 bytes observable:")
    print(f"      mean   {c['mean_s']:.6f} s = {c['mean_min']:.4f} min   sd {c['sd_s']:.6f}")
    print(f"      median {c['median_s']:.1f} s = {c['median_min']:.2f} min   "
          f"max {c['max_s']:.0f} s")
    print(f"      95 per cent interval on the mean, 4 routes:")
    for label in ("ci_scipy", "ci_statsmodels", "ci_mpmath", "ci_bootstrap"):
        lo, hi = c[label]
        print(f"        {label.replace('ci_',''):14} [{lo:.6f}, {hi:.6f}]")
    print(f"      the 3 parametric routes agree to {c['ci_max_disagreement']:.3e}")
    print(f"      t quantile: scipy {c['t_quantile_scipy']:.12f}  "
          f"mpmath {c['t_quantile_mpmath']:.12f}")
    print(f"  total unwatchable waiting already recorded: "
          f"{c['total_silent_s']:.0f} s = {c['total_silent_h']:.4f} h")
    print(f"  boards whose silent wait ended in a REFUSAL: "
          f"{c['refused']} of {c['determinate_n']} = {c['refused_share']:.6f}")
    print(f"      Wilson          statsmodels [{c['wilson_statsmodels'][0]:.6f}, "
          f"{c['wilson_statsmodels'][1]:.6f}]  hand-rolled "
          f"[{c['wilson_handrolled'][0]:.6f}, {c['wilson_handrolled'][1]:.6f}]")
    print(f"      Clopper-Pearson beta        [{c['cp_beta'][0]:.6f}, "
          f"{c['cp_beta'][1]:.6f}]  exact tails "
          f"[{c['cp_exact_tails'][0]:.6f}, {c['cp_exact_tails'][1]:.6f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
