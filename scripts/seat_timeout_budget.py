#!/usr/bin/env python3
"""Choose the seat wall-clock cap from the archive, not from a sibling's setting.

WHY THIS EXISTS. `run_simulated_experiment.py` capped each seat at 900s because
that "matches the live CC2 timeout in the real panel". That is a per-seat
justification for a parameter whose failures compound per RUN: a 6-seat, 16-round
experiment makes 96 dispatches, and losing any one of them damages a round.

On 2026-09-08 run `sim45_memory_20260908T011846Z` lost 3 of 6 seats in round 0 --
the blind baseline -- each killed at exactly 900s with 0 characters returned,
while the three that survived took 624s, 768s and 845s. The largest success was
94% of the cap.

This script recomputes the trade-off from every archived dispatch that carries a
duration, so the number in the runner can be cited rather than asserted. Run it
after any change to seat count, target size or round count.

    python3 scripts/seat_timeout_budget.py [--seats 6] [--rounds 16]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

DURATION_KEYS = ("elapsed_s", "duration_s", "wall_s", "elapsed", "seconds")
CANDIDATE_CAPS = (600, 900, 1200, 1800, 2400, 3000, 3600, 5400)


def collect(root: pathlib.Path) -> list[float]:
    """Every seat record in the archive that reports how long it took.

    Seat records use two naming conventions (`r5_gemini_<ts>.json` and
    `round5_gemini_<ts>.json`) and some runs write BOTH for the same dispatch, so
    duplicates are dropped on (parent, seat, round, duration) rather than on
    filename -- counting filenames would double every such run.
    """
    seen, out = set(), []
    for p in sorted(root.rglob("*.json")):
        if "ABORTED.txt" in [q.name for q in p.parent.iterdir() if q.is_file()]:
            continue  # an abandoned run is not evidence about normal dispatch
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        for k in DURATION_KEYS:
            v = d.get(k)
            if isinstance(v, (int, float)) and v > 0:
                key = (p.parent.name, str(d.get("model")), str(d.get("round")), float(v))
                if key not in seen:
                    seen.add(key)
                    out.append(float(v))
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", default="bench/logs")
    ap.add_argument("--seats", type=int, default=6)
    ap.add_argument("--rounds", type=int, default=16)
    args = ap.parse_args()

    root = pathlib.Path(args.logs)
    if not root.is_dir():
        print(f"FATAL: no log archive at {root}", file=sys.stderr)
        return 2

    durs = sorted(collect(root))
    n = len(durs)
    if n < 30:
        print(f"FATAL: only {n} dispatches carry a duration; too few to budget from.",
              file=sys.stderr)
        return 2

    def q(f: float) -> float:
        return durs[min(n - 1, int(f * n))]

    dispatches = args.seats * args.rounds
    print(f"archived dispatches with a duration: {n}")
    print(f"  median {statistics.median(durs):.0f}s   p90 {q(.90):.0f}s   "
          f"p95 {q(.95):.0f}s   p99 {q(.99):.0f}s   max {durs[-1]:.0f}s")
    print(f"\na run of {args.seats} seats x {args.rounds} rounds = {dispatches} dispatches\n")
    print("   cap    per-seat loss    P(run loses NO seat)    expected seats lost")
    for cap in CANDIDATE_CAPS:
        over = sum(1 for x in durs if x > cap)
        p = over / n
        clean = (1.0 - p) ** dispatches
        print(f"  {cap:5d}s      {100 * p:6.2f}%             {100 * clean:6.1f}%"
              f"                {dispatches * p:6.2f}")
    print("\nA cap is not a guarantee: these rates come from the archive's mixture of")
    print("seat counts and target sizes. A configuration slower than that mixture will")
    print("lose more. Cross-check against the run's own observed durations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
