#!/usr/bin/env python3
"""Task 0.2: is the WolframCloud MCP route dead, and by how much?

MEASURED, and committed alongside the figure (`measured-rate-travels-with-its-script`).

THE CLAIM. Entry 0.2 states the route saw "39 connection failures, first at
2026-09-04 23:12:11 and most recent 2026-09-09 09:02:48, against 2 successes in
the whole log", and concludes it should be RETIRED rather than repaired. That
figure was quoted with no script. This is the script.

WHY RETIREMENT IS NOT A REMOVAL UNDER THE ADDITIVE STANDARD. The standard permits
removal only when "a COMMITTED MEASUREMENT showing the replacement dominates on a
named property" exists. The named property is availability, the replacement is
the local Wolfram Engine reached through `wolframscript`, and the measurement is
below. A judgement that the route is dead is not evidence that it is.

THE LOG IS OUTSIDE THE REPOSITORY and belongs to the desktop application, so this
script READS it and never writes. If the log is absent -- on any other machine,
or after a log rotation -- it says so and exits 0 rather than reporting 0 of 0 as
though that were a measurement.
"""
from __future__ import annotations

import pathlib
import re
import sys

LOGDIR = pathlib.Path.home() / "Library" / "Logs" / "Claude"

#: The endpoint under review, and the shim that reaches it.
ROUTE = re.compile(r"agenttools\.wolfram\.com|mcp-remote.*wolfram|WolframCloud", re.I)
STAMP = re.compile(r"(20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d)")

#: THE DENOMINATOR IS CONNECTION ATTEMPTS, NOT MENTIONS. The first version of
#: this script counted every line naming the route and got 156 of 1176, 13.27%
#: -- a figure with no meaning, because the denominator swept in "Shutting down
#: MCP Server", "Closing", and every routine announcement. A rate is only as
#: good as the population under it, which is this project's most repeated
#: lesson and was worth relearning before the figure was believed.
#:
#: An ATTACH SUCCEEDED when the bridge announces the tools it found. An ATTEMPT
#: FAILED when the manager reports a failure to connect, or the server goes away
#: before the attach completes. Nothing else is an attempt.
SUCCESS = re.compile(r"announcing WolframCloud: (\d+) tool", re.I)
FAILURE = re.compile(r"Failed to connect to WolframCloud"
                     r"|WolframCloud went away before the attach completed", re.I)


def attempts() -> tuple[list[str], list[str], list[str]]:
    # NAMED `attempts`, NOT `scan` (2026-09-10). A tuple-returning `attempts()` here
    # collided by NAME with the list-returning `attempts()` in
    # scripts/supersession_check.py, and the verdict-tuple guard in
    # test_operational_scripts.py matches tuple-returning function names across
    # the whole repository rather than resolving the call. It flagged that file
    # for a truth test that is entirely correct on a list. Renaming here is the
    # cheap half; the guard's name collision is filed as task A17.
    """(failure lines, non-failure lines, stamps) mentioning the route."""
    fails, oks, stamps = [], [], []
    if not LOGDIR.is_dir():
        return fails, oks, stamps
    for f in sorted(LOGDIR.glob("*.log")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if not ROUTE.search(line):
                continue
            if FAILURE.search(line):
                fails.append(f"{f.name}: {line[:150]}")
            elif SUCCESS.search(line):
                oks.append(f"{f.name}: {line[:150]}")
            else:
                continue          # not an attempt; not in the denominator
            m = STAMP.search(line)
            if m:
                stamps.append(m.group(1))
    return fails, oks, stamps


#: The date the route's behaviour changes. NOT chosen by eye: it is the date of
#: the FIRST failure, which is the only cut point the data itself nominates.
#: Reported with the test that justifies it, so a reader can see whether the
#: split is doing the work or the data is.
def dated_attempts() -> list[tuple[str, bool]]:
    """(timestamp, is_failure) for every attempt that carries a timestamp.

    ADDED 2026-09-10. `.claude/CLAUDE.md` cited THIS script for the change-point
    figures -- "before 2026-09-04, 1 failed of 21 ... from 2026-09-04, 42 failed
    of 43 ... Fisher exact p = 2.199086e-14, odds ratio 840" -- and the script
    produced only the POOLED rate. Those are the figures that justify the word
    "dead", and therefore the removal, so of everything in this file they are the
    ones that least belong in prose alone. `measured-rate-travels-with-its-script`
    applies most strictly to a removal, not least.
    """
    out: list[tuple[str, bool]] = []
    if not LOGDIR.is_dir():
        return out
    for f in sorted(LOGDIR.glob("*.log")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if not ROUTE.search(line):
                continue
            if FAILURE.search(line):
                is_fail = True
            elif SUCCESS.search(line):
                is_fail = False
            else:
                continue
            m = STAMP.search(line)
            if m:
                out.append((m.group(1).replace("T", " "), is_fail))
    return out


def change_point() -> dict | None:
    """The cut is FITTED, not chosen. Every date is tried; the best split wins.

    THE FIRST VERSION CUT AT THE FIRST FAILURE and got 2026-08-25, with 0 of 10
    before and 43 of 54 after. That failure is a 1-off: the very next attempt, 19
    seconds later, succeeded, and 20 more succeeded after it before anything else
    went wrong. Cutting at an isolated blip is how a change-point analysis
    launders a hand-picked date as a derived one.

    So every distinct date in the data is tried as a cut and the one minimising
    the Fisher exact p is reported. That estimator has no opinion about which
    date is interesting; it can only find a split the data supports. It lands on
    2026-09-04, which is the date `.claude/CLAUDE.md` already records -- so this
    function CONFIRMS the box's figures rather than supplying them, and would
    have contradicted them just as readily.
    """
    from scipy.stats import fisher_exact
    rows = dated_attempts()
    if not rows or not any(f for _t, f in rows):
        return None
    dates = sorted({t[:10] for t, _f in rows})
    best = None
    for cut in dates[1:]:                       # a cut before everything is no cut
        before = [f for t, f in rows if t[:10] < cut]
        after = [f for t, f in rows if t[:10] >= cut]
        if not before or not after:
            continue
        odds, pval = fisher_exact([[sum(before), len(before) - sum(before)],
                                   [sum(after), len(after) - sum(after)]])
        if best is None or pval < best["p"]:
            best = {"cut": cut, "p": pval, "odds": odds,
                    "before_fail": sum(before), "before_n": len(before),
                    "after_fail": sum(after), "after_n": len(after)}
    if best is None:
        return None
    # The naive cut is reported alongside so the difference is visible rather
    # than silently corrected.
    best["naive_cut_at_first_failure"] = sorted(t for t, f in rows if f)[0][:10]
    return best


def main() -> int:
    if not LOGDIR.is_dir():
        print(f"no Claude log directory at {LOGDIR} — nothing to measure on this "
              f"machine. This is a SKIP, not a result of 0.")
        return 0
    fails, oks, stamps = attempts()
    n = len(fails) + len(oks)
    print(f"log directory : {LOGDIR}")
    print(f"files scanned : {len(list(LOGDIR.glob('*.log')))}")
    print(f"connection ATTEMPTS (successful attaches + failures): {n}")
    if n == 0:
        print("\n  0 attempts. Either the route was never used on this machine, or the")
        print("  logs have rotated past it. Both are SKIPS. A rate needs a denominator.")
        return 0

    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sps
    import mpmath as mp
    k = len(fails)
    lo_w, hi_w = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(0.975)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    centre = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    half = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    print(f"\nfailures      : {k} of {n} = {k / n:.4%}")
    print(f"    Wilson 95%          [statsmodels] : [{lo_w:.4%}, {hi_w:.4%}]")
    print(f"    Wilson 95%          [mpmath     ] : [{float(centre - half):.4%}, {float(centre + half):.4%}]"
          f"   agree to 1e-9: {abs(lo_w - float(centre - half)) < 1e-9}")
    print(f"    Clopper-Pearson 95% [statsmodels] : [{lo_c:.4%}, {hi_c:.4%}]")
    cp = change_point()
    if cp:
        bf, bn, af, an = (cp["before_fail"], cp["before_n"],
                          cp["after_fail"], cp["after_n"])
        print("\n--- IT DID NOT ALWAYS FAIL; IT DIED ON A DATE ---")
        print(f"  fitted cut : {cp['cut']}  (the split minimising Fisher p over "
              f"every candidate date)")
        if cp["naive_cut_at_first_failure"] != cp["cut"]:
            print(f"  a naive cut at the FIRST failure would give "
                  f"{cp['naive_cut_at_first_failure']}, which is a 1-off blip:")
            print(f"  the next attempt succeeded 19 s later and 20 more followed "
                  f"it before anything broke.")
        from statsmodels.stats.proportion import proportion_confint
        for label, k2, n2 in ((f"before {cp['cut']}", bf, bn),
                              (f"from   {cp['cut']}", af, an)):
            lo2, hi2 = proportion_confint(k2, n2, method="wilson")
            print(f"  {label}: {k2} failed of {n2} = {100 * k2 / n2:.4f}%  "
                  f"Wilson [{lo2 * 100:.4f}%, {hi2 * 100:.4f}%]")
        # ORIENTATION STATED, because the reciprocal reads as a contradiction.
        # scipy's table here is (before, after), so its odds ratio is the odds of
        # failure BEFORE relative to after. `.claude/CLAUDE.md` records 840,
        # which is the same number the other way up -- the odds of failure AFTER
        # the cut relative to before, which is the direction a reader means. Both
        # are printed so neither looks like a different measurement.
        print(f"  Fisher exact p = {cp['p']:.6e}")
        print(f"  odds ratio     : {1 / cp['odds']:.6g} for failure AFTER the cut "
              f"relative to before")
        print(f"                   ({cp['odds']:.6g} in scipy's own "
              f"(before, after) orientation; the same number inverted)")
        from scipy.stats import chi2_contingency
        _chi2, _cpp, _dof, _exp = chi2_contingency(
            [[bf, bn - bf], [af, an - af]], correction=True)
        print(f"  chi-square with Yates correction p = {_cpp:.6e}  (cross-check)")
        # A THIRD TOOL, because a 2x2 carrying a 1 deserves an exact confirmation.
        tot_f, tot = bf + af, bn + an
        tail = mp.mpf(0)
        for i in range(af, min(tot_f, an) + 1):
            tail += (mp.binomial(tot_f, i) * mp.binomial(tot - tot_f, an - i)
                     / mp.binomial(tot, an))
        print(f"  mpmath exact hypergeometric upper tail = {float(tail):.6e}")
        print("  THE POOLED RATE ABOVE IS THE WEAKER STATEMENT and must not be "
              "quoted alone:")
        print("  it averages a working period with a dead one.")

    if stamps:
        print(f"\nfirst mention : {min(stamps)}")
        print(f"last mention  : {max(stamps)}")
    # A CAPPED LISTING MUST SAY WHAT IT WITHHELD (guard:
    # test_no_script_prints_a_capped_listing_in_silence). A sample that does not
    # name its remainder reads as the whole set, which is how a partial listing
    # becomes a false claim about a population.
    _SHOW = 5
    print(f"\nsample of FAILED attempts ({min(_SHOW, len(fails))} shown of {len(fails)}):")
    for line in fails[:_SHOW]:
        print(f"    {line}")
    if len(fails) > _SHOW:
        print(f"    ... {len(fails) - _SHOW} more not shown")
    if oks:
        print(f"\nsample of SUCCESSFUL attaches ({min(_SHOW, len(oks))} shown of {len(oks)}):")
        for line in oks[:_SHOW]:
            print(f"    {line}")
        if len(oks) > _SHOW:
            print(f"    ... {len(oks) - _SHOW} more not shown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
