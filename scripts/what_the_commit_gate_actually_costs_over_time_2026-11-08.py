"""What has the commit gate actually cost, over more than 1 run? B81.

HIS RULING, 2026-11-08: *"Add the guard, but make sure it contains a check for
why the commit is failing and so that it gives the reason for the failure, if
not already done. stm"*

WHAT WAS ALREADY DONE, REPORTED BECAUSE HIS OWN WORDS INVITE IT. The
reason-giving half is largely in place: `hooks/pre-commit` already extracts the
failing tests and prints them to stderr, so a refusal from a red guard already
says which guard. What was NOT in place is a refusal from the LIMIT, because
there was no limit to refuse from.

THE DEFECT THIS CLOSES. The hook recorded its duration by OVERWRITING a single
scratch number, so the gate had no cost HISTORY at all. Every statement about
what it costs came from 1 number describing the last run, and the limit stated
in the hook's own header -- 11 minutes, so 660 seconds -- could not be checked
against anything. Measured from this session's own boards, the gate ran 652,
683 and 698 seconds, so it sits ON that line rather than inside it.

AND THE OUTCOME IS NOW RECORDED BESIDE THE DURATION, which is the half worth
having. A refusal leaves NO trace in the repository: that is why this session's
own refusal count had to be reported as session-observed rather than derived,
and why `scripts/how_many_commits_and_how_many_refusals_2026-11-08.py` says so
in its own output. The ledger records the trap's exit code, so the refusal rate
becomes derivable from the next run onward.

WHAT THIS DOES NOT DO, AND WHY NOT. It does not refuse. B81's guard fails when
the gate exceeds its stated limit, and the gate is AT that limit today, so a
refusing guard would block every commit until the guard set is split into a
commit-time tier and a periodic one. That split, and the bound it is split
against, are **B103** -- which is his decision and which the decisions file
itself records as 1 decision wearing 2 numbers. So this collects the evidence
B103 needs without pre-empting it.

THE LEDGER IS UNTRACKED, DELIBERATELY. A tracked ledger written from a
pre-commit hook lands AFTER the commit it describes, so every commit would
leave the tree dirty and the history would trail by 1. Where it should finally
live is part of the same decision.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
if not REPO.is_dir():
    REPO = pathlib.Path(__file__).resolve().parents[1]

LEDGER = REPO / ".cdsfl_tmp/precommit_durations.jsonl"
#: The hook's own header states a per-commit gate costing 11 minutes, so 660 s.
#: Read from prose rather than from a constant, which is itself part of B81:
#: a limit that exists only as a sentence cannot be enforced.
STATED_LIMIT_SECONDS = 11 * 60


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


def rows(path: pathlib.Path = LEDGER) -> list[dict]:
    """Every well-formed ledger row. A malformed line is skipped, not fatal."""
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict) and isinstance(d.get("seconds"), int):
            out.append(d)
    return out


#: ★ A KILLED BOARD IS NOT A FAST REFUSAL, and the ledger CANNOT tell them
#: apart. Added 2026-11-08, hours after the ledger itself, because the 4th row
#: ever written was a board interrupted by hand and it recorded
#: `{"seconds":12,"exit":1}` -- byte-identical in shape to a gate that refused
#: quickly. The hook sees only the exit code of a pytest whose process was
#: killed, which is 1, the same code a genuine test failure gives.
#:
#: SO THE SHORT ROWS ARE SEPARATED RATHER THAN DROPPED OR COUNTED. Dropping
#: them would hide a real fast refusal if one ever occurred; counting them
#: inflated "over the stated limit" from 4 of 4 to 4 of 5 and the standard
#: deviation from 36 seconds to 315. Both are reported, labelled, and the
#: headline figure uses the completed runs.
#:
#: THE THRESHOLD IS DERIVED FROM THE MECHANISM, NOT CHOSEN. The gate's cheap
#: phase alone takes minutes; a run ending inside 120 seconds did not reach
#: the board at all, so it cannot be a verdict about the board's cost. It is
#: reported as INDETERMINATE, which is what this project's own rule requires
#: of a measurement that did not happen.
INTERRUPTED_UNDER_SECONDS = 120


def split_rows(rs: list[dict]) -> tuple[list[dict], list[dict]]:
    """(completed, indeterminate). A short run is not evidence about cost."""
    done = [r for r in rs if r["seconds"] >= INTERRUPTED_UNDER_SECONDS]
    short = [r for r in rs if r["seconds"] < INTERRUPTED_UNDER_SECONDS]
    return done, short


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    # ★ FOLDED IN 2026-11-09 FROM A DUPLICATE I SHOULD NOT HAVE WRITTEN.
    # `scripts/what_does_the_gate_actually_cost_2026-11-09.py` was written that
    # night to answer the same question this script already answered, without
    # checking whether an instrument existed -- the failure recorded as
    # use-the-instrument-that-exists, 4 of 11 on 2026-10-12. Its 2 unique
    # contributions are kept here and the duplicate is retired: a one-sided
    # t-test against the stated limit, and a projection for added guard work.
    #
    # WHY --max-seconds EXISTS. This script's headline proportion pools every
    # recorded board, and from 2026-11-09 the ledger holds 2 DIFFERENT gate
    # configurations -- 128 guard files and 232. Pooling them measures 2 things
    # at once, which is the ecological confound corrected elsewhere in this
    # project, and it is why the pooled standard deviation jumped to 430.7 s.
    # The flag bounds the sample to one configuration so the test speaks for
    # one gate. It does NOT change the proportion above, which is deliberately
    # a census of everything recorded.
    ap.add_argument("--max-seconds", type=float, default=None,
                    help="restrict the t-test sample to boards at or under "
                         "this duration, to keep 1 gate configuration")
    ap.add_argument("--add-seconds", type=float, default=None,
                    help="project this much extra guard work on top of the mean")
    args = ap.parse_args()

    rs = rows()
    print(f"the gate's stated limit, from its own header : "
          f"{STATED_LIMIT_SECONDS} s (11 minutes)")
    print(f"ledger rows recorded                         : {len(rs)}")
    if not rs:
        print()
        print("  NO HISTORY YET, AND THAT IS THE EXPECTED STATE ON THE FIRST RUN.")
        print("  The ledger is written by `hooks/pre-commit`'s exit trap, so the")
        print("  first row appears after the next commit attempt. This prints 0")
        print("  rather than inventing a distribution from the single scratch")
        print("  number, which is the whole defect B81 names: 1 number is not a")
        print("  history, and a limit with nothing to check against is not a limit.")
        print(f"  Spool path: {LEDGER}")
        return 0

    rs_all = rs
    rs, short = split_rows(rs_all)
    if short:
        print(f"\n  INDETERMINATE, EXCLUDED FROM EVERY FIGURE BELOW: "
              f"{len(short)} row(s) under {INTERRUPTED_UNDER_SECONDS} s "
              f"({', '.join(str(r['seconds']) + ' s' for r in short)}). A board "
              f"killed by hand records a short duration and exit 1, which is "
              f"shape-identical to a fast refusal -- the hook sees only the "
              f"exit code of a pytest whose process was killed. Counting them "
              f"would be reporting an interruption as a verdict.")
    if not rs:
        print(f"\n  NO COMPLETED RUN IS RECORDED YET, so nothing is claimed "
              f"about the gate's cost. {len(rs_all)} row(s) exist and all are "
              f"indeterminate.")
        return 0
    secs = [r["seconds"] for r in rs]
    over = [r for r in rs if r["seconds"] > STATED_LIMIT_SECONDS]
    refused = [r for r in rs if r.get("exit") not in (0, None)]

    print(f"\n  seconds: min {min(secs)}  median "
          f"{statistics.median(secs):.1f}  max {max(secs)}")
    if len(secs) > 1:
        print(f"  standard deviation: {statistics.stdev(secs):.1f}")

    # ── IS THE MEAN SIGNIFICANTLY OVER THE STATED LIMIT? ────────────────────
    sample = [s for s in secs
              if args.max_seconds is None or s <= args.max_seconds]
    if args.max_seconds is not None:
        print(f"\n  t-test sample bounded to <= {args.max_seconds:.0f} s: "
              f"{len(sample)} of {len(secs)} board(s), so it speaks for 1 gate "
              f"configuration rather than pooling 2")
    if len(sample) >= 2:
        n_s = len(sample)
        mean_s = statistics.fmean(sample)
        sd_s = statistics.stdev(sample)
        se_s = sd_s / (n_s ** 0.5)
        tstat = (mean_s - STATED_LIMIT_SECONDS) / se_s if se_s else float("nan")
        print(f"\n  mean {mean_s:.6f} s over n={n_s}, sd {sd_s:.6f}")
        print(f"  one-sided t against {STATED_LIMIT_SECONDS} s: "
              f"t = {tstat:.6f}, df = {n_s - 1}")
        p_sp = p_mp = None
        try:
            from scipy import stats as _st
            p_sp = float(_st.t.sf(tstat, df=n_s - 1))
            lo, hi = _st.t.interval(0.95, n_s - 1, loc=mean_s, scale=se_s)
            print(f"  95% t-interval on the mean: [{lo:.6f}, {hi:.6f}] s -- the "
                  f"limit lies "
                  f"{'INSIDE' if lo <= STATED_LIMIT_SECONDS <= hi else 'OUTSIDE'}"
                  f" it")
        except ImportError:
            pass
        try:
            import mpmath as _mp
            _mp.mp.dps = 40
            nu = _mp.mpf(n_s - 1)
            xx = nu / (nu + _mp.mpf(tstat) ** 2)
            p_mp = float(_mp.betainc(nu / 2, _mp.mpf(0.5), 0, xx,
                                     regularized=True) / 2)
        except ImportError:
            pass
        if p_sp is not None and p_mp is not None:
            print(f"  p = {p_sp:.6f} (scipy)  {p_mp:.6f} (mpmath betainc)  "
                  f"agree={abs(p_sp - p_mp) < 1e-9}")
            print(f"  -> {'REJECT' if p_sp < 0.05 else 'CANNOT REJECT'} the null "
                  f"that this gate sits at or below its stated limit")
        else:
            print("  p NOT COMPUTED on 2 routes, so under the cross-check rule "
                  "nothing is claimed from it")

    if args.add_seconds is not None and sample:
        base = statistics.fmean(sample)
        total = base + args.add_seconds
        print(f"\n  projection: {base:.2f} + {args.add_seconds:.2f} = "
              f"{total:.2f} s = {total / 60:.2f} min, which is "
              f"{total / STATED_LIMIT_SECONDS:.6f} x the stated limit")

    for label, k in (("over the stated limit", len(over)),
                     ("refused the commit", len(refused))):
        n = len(rs)
        (wl, wh), (cl, ch), diff = _iv(k, n)
        print(f"\n  {label}: {k} of {n} = {k / n:.6f}")
        print(f"    Wilson [{wl:.6f}, {wh:.6f}]  "
              f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
        print(f"    the 2 routes of each agree to {diff:.2e}")

    print()
    if over:
        print(f"  THE GATE EXCEEDS ITS OWN STATED LIMIT on {len(over)} of "
              f"{len(rs)} recorded run(s). That is the condition B81's guard "
              f"would refuse on, and it is NOT refused here, because the split "
              f"into a commit-time tier and a periodic tier is B103 and the "
              f"bound is his to set.")
    else:
        print(f"  Every recorded run is inside the stated limit. On this "
              f"evidence a refusing guard would not fire -- but {len(rs)} "
              f"run(s) is a small history, and the interval above is the "
              f"honest statement rather than the point estimate.")
    print(f"\n  A REFUSAL USED TO LEAVE NO TRACE AT ALL, which is why this "
          f"session's refusal count had to be session-observed. From the first "
          f"row onward it is derivable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
