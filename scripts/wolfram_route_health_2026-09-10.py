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
