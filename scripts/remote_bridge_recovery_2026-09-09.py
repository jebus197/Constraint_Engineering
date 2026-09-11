#!/usr/bin/env python3
"""Did the desktop app's remote session recover by itself after each forced restart?

Source: ~/Library/Logs/Claude/main.log, the app's own log. The rate travels with
this script per `measured-rate-travels-with-its-script`.

The question matters because the founder's working model is that the remote
session only comes back after physically returning to the machine. If the host
side in fact recovers unaided, the fault lies elsewhere and so does the remedy.

CORRECTED 2026-09-09 by the P-pass on the first version, which had 3 defects:

  1. THE RECOVERY WINDOW WAS UNBOUNDED. Each restart was paired with the FIRST
     "reconnected successfully" at any later time, so a reconnect 6.3 hours
     later -- exactly what would happen if the founder got home and interacted
     -- scored as "recovered unaided". That is the claim under test, so the
     instrument could not have refuted it. Now bounded, default 600 s, and the
     bound is reported alongside the answer.
  2. NO SESSION-IDENTITY CHECK. "reconnected successfully" was matched as a bare
     substring, so a different session reconnecting would have been credited to
     this one. Now the session id is captured and compared.
  3. A LOG WITH NO RESTART IN IT raised ZeroDivisionError instead of saying so.

The conclusion survived all 3: the 2 observed lags are 40 s and 75 s, so 2 of 2
still count as unaided recovery at every bound from 120 s upward. The conclusion
was never at risk; the instrument was, and an instrument that cannot fail its
own hypothesis is not evidence.

Two tools per proportion: statsmodels for the intervals, mpmath for a
closed-form Wilson sharing none of statsmodels' code.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import mpmath as mp
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint

LOG = Path.home() / "Library/Logs/Claude/main.log"
STAMP = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)")
QUIT = "Auto-restarting app after update"
BACK = re.compile(r"Session (\S+) reconnected successfully")
DEFAULT_WINDOW_S = 600.0


class NoRestarts(ValueError):
    """The log records no forced restart, so there is nothing to measure."""


def parse_events(text: str) -> tuple[list[dt.datetime], list[tuple[dt.datetime, str]]]:
    """Return (restart times, [(reconnect time, session id)])."""
    quits: list[dt.datetime] = []
    backs: list[tuple[dt.datetime, str]] = []
    for line in text.splitlines():
        m = STAMP.match(line)
        if not m:
            continue
        t = dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        if QUIT in line:
            quits.append(t)
            continue
        b = BACK.search(line)
        if b:
            backs.append((t, b.group(1)))
    return quits, backs


def recoveries(text: str, window_s: float = DEFAULT_WINDOW_S,
               session_id: str | None = None) -> list[tuple[dt.datetime, float | None, str | None]]:
    """For each restart, the lag to the first reconnect WITHIN window_s, or None.

    `session_id` restricts the match to one session; None accepts any, but the
    id that matched is returned so a caller can see what was credited.
    """
    quits, backs = parse_events(text)
    if not quits:
        raise NoRestarts("no 'Auto-restarting app after update' line in the log")
    out = []
    for q in quits:
        hit = None
        for t, sid in backs:
            if t < q:
                continue
            if (t - q).total_seconds() > window_s:
                break
            if session_id is not None and sid != session_id:
                continue
            hit = ((t - q).total_seconds(), sid)
            break
        out.append((q, hit[0] if hit else None, hit[1] if hit else None))
    return out


def wilson_closed_form(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(1 - (1 - conf) / 2)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    centre = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    half = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return float(centre - half), float(centre + half)


def main() -> int:
    try:
        rows = recoveries(LOG.read_text(errors="replace"))
    except NoRestarts as exc:
        print(f"nothing to measure: {exc}")
        return 2

    print(f"Forced restarts in the app's own log, and whether the remote session")
    print(f"came back unaided within {DEFAULT_WINDOW_S:.0f} s of the restart:\n")
    for q, lag, sid in rows:
        if lag is None:
            print(f"  {q}  ->  NO reconnect inside the window")
        else:
            print(f"  {q}  ->  recovered after {lag:.0f} s   (session {sid})")

    n = len(rows)
    k = sum(1 for _, lag, _ in rows if lag is not None)
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, alpha=0.05, method="beta")
    lo_m, hi_m = wilson_closed_form(k, n)
    print(f"\n  self-recovered: {k} of {n} = {k/n:.2%}")
    print(f"    Wilson 95%          [statsmodels] : [{lo_w:.2%}, {hi_w:.2%}]")
    print(f"    Wilson 95%          [mpmath     ] : [{lo_m:.2%}, {hi_m:.2%}]   agree={abs(lo_w-lo_m)<1e-12}")
    print(f"    Clopper-Pearson 95% [statsmodels] : [{lo_c:.2%}, {hi_c:.2%}]")

    good = [lag for _, lag, _ in rows if lag is not None]
    if good:
        print(f"\n  recovery lag: min {min(good):.0f} s, max {max(good):.0f} s, mean {sum(good)/len(good):.1f} s")
    print("\n  Sensitivity to the window, since 600 s was a choice and not a measurement:")
    text = LOG.read_text(errors="replace")
    for w in (60, 120, 300, 600, 1800):
        r = recoveries(text, window_s=w)
        print(f"    within {w:>4d} s : {sum(1 for _, l, _ in r if l is not None)} of {len(r)}")
    print("\n  THE INTERVAL IS WIDE BECAUSE n IS 2. This says the host side recovered")
    print("  unaided on BOTH occasions on record; it does not establish that it always will.")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    raise SystemExit(main())
