#!/usr/bin/env python3
"""Characterise WHEN the reviewed file was rewritten during the 2026-09-08 Exp 45 run.

Input: bench/logs/target_mutation_watch_2026-09-08/target_state_transitions.log,
written by the 15-second poll loop that ran as background task bx051kc0l from
07:14 to 16:40 BST on 2026-09-08. Each line records a blob hash for
bench/dm/_memory.py that the poller had not seen before.

The question this answers: were the rewrites spread evenly across the run (many
seats each editing as they went), or concentrated in a burst (one seat editing
repeatedly)? Even spread and burst have different causes and different remedies,
so the distinction is not cosmetic.

CORRECTION 2026-09-08 18:15 BST, from the P-pass on the first version of this
script. Three defects, all found by attacking it rather than reading it:

  1. THE BINOMIAL WAS ANTI-CONSERVATIVE BY 3.9x. It asked "what is the chance
     that 7 of 12 arrivals land in a 600 s slice, if arrivals were uniform over
     the window" and got 6.541e-06. But the window IS [first arrival, last
     arrival]: those two are the minimum and maximum, not free draws, and the
     first is inside the slice BY CONSTRUCTION because it defines the slice's
     start. Conditioning on the endpoints, only the 10 interior points are free,
     and the event is 6 of those 10. Correct value 2.538e-05. The conclusion
     survives; the number did not, and a number that flatters its own conclusion
     is the direction this project keeps getting caught in.
  2. A RUN CROSSING MIDNIGHT PRODUCED NEGATIVE GAPS. The log stores HH:MM:SS
     with no date, so 23:58:00 -> 00:03:00 parsed as a gap of -86,100 s and
     every statistic downstream was garbage. Now unwrapped.
  3. AN EMPTY OR SINGLE-ENTRY LOG CRASHED with IndexError, or returned a silent
     nan, instead of saying there was not enough data.

The KS test and the gap-dispersion Monte Carlo were already conditioned on the
endpoints correctly and are unchanged; both are also free of the 600 s window,
which was chosen by eye, so the clustering conclusion does not rest on it.

Two tools per claim, per the 21 Apr 2026 cross-verification rule.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint

# THE TRACKED COPY IS CANONICAL, corrected 2026-09-09. The original path is under
# bench/logs/, which .gitignore:41 excludes with `bench/logs/**`, so this script
# read a file no clone has and the measurement could not be reproduced by anyone
# else -- the exact failure `measured-rate-travels-with-its-script` names, in the
# script written to satisfy it. The untracked path is kept as a fallback so the
# script still works on the machine that produced it.
DEFAULT_LOG = Path("experimental_notes/evidence/target_mutation_watch_2026-09-08/target_state_transitions.log")
_LEGACY_LOG = Path("bench/logs/target_mutation_watch_2026-09-08/target_state_transitions.log")
if not DEFAULT_LOG.is_file() and _LEGACY_LOG.is_file():
    DEFAULT_LOG = _LEGACY_LOG
LINE = re.compile(r"NEW target state (\d+) at (\d\d):(\d\d):(\d\d): blob (\w+), (\d+) bytes")
DAY = 86_400


class InsufficientData(ValueError):
    """Fewer than 3 arrivals: no interior point exists, so nothing is testable."""


def parse_log(text: str) -> tuple[np.ndarray, list[int], list[str]]:
    """Return (seconds, sizes, blobs). Seconds are UNWRAPPED across midnight.

    The log carries a wall-clock time of day and no date. A watch that spans
    midnight therefore emits a smaller number after a larger one. Any backward
    step is treated as one day forward, which is correct for a poll loop whose
    interval (15 s) is far shorter than a day.
    """
    secs: list[float] = []
    sizes: list[int] = []
    blobs: list[str] = []
    day_offset = 0
    prev_raw: float | None = None
    for line in text.splitlines():
        m = LINE.match(line.strip())
        if not m:
            continue
        raw = int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
        if prev_raw is not None and raw < prev_raw:
            day_offset += DAY
        prev_raw = raw
        secs.append(raw + day_offset)
        blobs.append(m.group(5))
        sizes.append(int(m.group(6)))
    return np.asarray(secs, dtype=float), sizes, blobs


def arrival_stats(t: np.ndarray, burst_window: float = 600.0, *, seed: int = 20260908,
                  draws: int = 200_000) -> dict:
    """Test whether arrivals cluster, conditioning on the observed endpoints.

    Raises InsufficientData for fewer than 3 arrivals.
    """
    n = len(t)
    if n < 3:
        raise InsufficientData(f"need at least 3 arrivals to have an interior point, got {n}")
    span = float(t[-1] - t[0])
    if span <= 0:
        raise InsufficientData("all arrivals share one timestamp; span is zero")
    gaps = np.diff(t)

    # --- Test 1: KS of the interior arrival positions against Uniform(0,1).
    # Endpoints are excluded because they are fixed by construction.
    u = (t[1:-1] - t[0]) / span
    ks = sps.kstest(u, "uniform")

    # --- Test 2: dispersion of the gaps, null band by Monte Carlo.
    # Independent of test 1: a different statistic on the same conditioning.
    cv = float(gaps.std(ddof=1) / gaps.mean())
    rng = np.random.default_rng(seed)
    sim = rng.random((draws, n - 2))
    sim.sort(axis=1)
    edges = np.concatenate([np.zeros((draws, 1)), sim, np.ones((draws, 1))], axis=1)
    g = np.diff(edges, axis=1) * span
    cv_null = g.std(axis=1, ddof=1) / g.mean(axis=1)
    p_cv = float((cv_null >= cv).mean())

    # --- The burst, conditioned on the endpoints.
    # The FIRST arrival is inside the window by construction: it starts it.
    # Only the interior points are free draws, so the test is over those.
    interior = t[1:-1]
    n_int = len(interior)
    k_int = int(((interior - t[0]) <= burst_window).sum())
    k_all = int(((t - t[0]) <= burst_window).sum())
    q = min(burst_window / span, 1.0)
    p_burst_scipy = float(sps.binom.sf(k_int - 1, n_int, q)) if k_int > 0 else 1.0
    mp.mp.dps = 30
    p_burst_mp = float(mp.nsum(
        lambda i: mp.binomial(n_int, i) * mp.mpf(q) ** i * (1 - mp.mpf(q)) ** (n_int - i),
        [k_int, n_int])) if k_int > 0 else 1.0

    lo_w, hi_w = proportion_confint(k_all, n, alpha=0.05, method="wilson")
    lo_c, hi_c = proportion_confint(k_all, n, alpha=0.05, method="beta")
    z = mp.mpf(str(sps.norm.ppf(0.975)))
    p_hat, N = mp.mpf(k_all) / n, mp.mpf(n)
    centre = (p_hat + z ** 2 / (2 * N)) / (1 + z ** 2 / N)
    half = (z / (1 + z ** 2 / N)) * mp.sqrt(p_hat * (1 - p_hat) / N + z ** 2 / (4 * N ** 2))

    return {
        "n": n, "span_s": span, "gaps_s": gaps.tolist(),
        "ks_D": float(ks.statistic), "ks_p": float(ks.pvalue), "n_interior": n_int,
        "cv": cv, "cv_null_mean": float(cv_null.mean()), "cv_p": p_cv,
        "burst_window_s": burst_window, "k_in_window": k_all, "k_interior_in_window": k_int,
        "burst_p_scipy": p_burst_scipy, "burst_p_mpmath": p_burst_mp,
        "share": k_all / n, "wilson": (lo_w, hi_w), "clopper_pearson": (lo_c, hi_c),
        "wilson_mpmath": (float(centre - half), float(centre + half)),
    }




def _print_usage_and_exit() -> "None":
    """Answer `--help` instead of consuming it as data.

    FOUND 2026-09-11 BY TASK A16'S SURVEY, which is exactly what that survey was
    for. All 5 measurement scripts that failed `--help` failed the SAME way: the
    flag was not recognised, so it was taken as a positional argument -- a report
    path, a note to lint, a log to read. One crashed with FileNotFoundError on
    the literal string `--help`; the others silently ran a full measurement when
    the caller asked for usage.

    This project already carries the rule in its strong form -- "a `--help` must
    never cost money", written after 15 of 17 runners billed a live dispatch on
    an unrecognised argument. These are measurements and cost nothing but time.
    The principle is the same: a flag the program does not understand must not be
    read as data.
    """
    import sys as _sys
    print((__doc__ or "").strip())
    print()
    print(f"usage: {_sys.argv[0].split('/')[-1]} [paths...]")
    raise SystemExit(0)


def _help_requested() -> bool:
    import sys as _sys
    return any(a in ("-h", "--help") for a in _sys.argv[1:])


def main(path: Path = DEFAULT_LOG) -> int:
    if _help_requested():
        _print_usage_and_exit()
    t, sizes, _ = parse_log(path.read_text())
    try:
        s = arrival_stats(t)
    except InsufficientData as exc:
        print(f"insufficient data: {exc}")
        return 2
    print(f"distinct target states logged     : {s['n']}")
    print(f"window                            : {s['span_s']:.0f} s ({s['span_s']/60:.1f} min)")
    print(f"gaps (s)                          : {', '.join(str(int(g)) for g in s['gaps_s'])}")
    print(f"\n[scipy]  KS vs uniform arrivals   : D={s['ks_D']:.4f}, p={s['ks_p']:.4g}  (n={s['n_interior']} interior)")
    print(f"[numpy]  gap CV                   : {s['cv']:.4f}  (uniform-null mean {s['cv_null_mean']:.4f}), MC p={s['cv_p']:.4g}")
    print(f"\nstates within {s['burst_window_s']:.0f}s of the first  : {s['k_in_window']} of {s['n']}"
          f"  ({s['k_interior_in_window']} of {s['n_interior']} interior, which is what is testable)")
    print(f"[statsmodels] Wilson 95%          : {s['share']:.4f}  [{s['wilson'][0]:.4f}, {s['wilson'][1]:.4f}]")
    print(f"[statsmodels] Clopper-Pearson 95% : {s['share']:.4f}  [{s['clopper_pearson'][0]:.4f}, {s['clopper_pearson'][1]:.4f}]")
    print(f"[mpmath]      Wilson 95% (closed) : [{s['wilson_mpmath'][0]:.4f}, {s['wilson_mpmath'][1]:.4f}]")
    print(f"[scipy ]      P(burst | uniform)  : {s['burst_p_scipy']:.4g}   <- conditioned on the endpoints")
    print(f"[mpmath]      same                : {s['burst_p_mpmath']:.4g}")
    print(f"\nbytes vs HEAD, min/max            : {min(sizes)} / {max(sizes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LOG))
