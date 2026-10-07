#!/usr/bin/env python3
"""Does exhausting the ladder really lower gamma, or only resolve findings LATE?

THE FOUNDER'S CHALLENGE, 2026-10-06, to the panel's finding: *"making the capability
ladder run until the problem has been resolved causing Gamma to become more difficult is
anti-intuitive. If a weaker model cannot resolve a problem adequately and the problem
gets passed to progressively stronger and stronger/more capable models, one might
justifiably expect that the problem would be resolved relatively quickly? That indeed
has been our experience so far."*

THE FINDING HE IS CHALLENGING. Flipping every unresolved critical to CONFIRMED moves
`gamma_critical` down in 9 of 14 archived runs and across the 0.30 arm in 2. The stated
mechanism is that unresolved criticals skew LATE, and late mass steepens a cumulative
curve, raising beta and lowering gamma = 1 - beta.

THE LIMIT IN THAT MEASUREMENT, WHICH IS WHAT THIS SCRIPT EXISTS TO TEST. It flips those
findings to CONFIRMED **at their existing `open_since_round`**. It holds their TIMING
FIXED. So it answers "what if these had been resolved" and NOT "what if the ladder had
resolved them PROMPTLY" -- and prompt resolution is exactly what removing the rung cap
is for. Measured here: of 210 archived routed resolutions, 174 landed in a LATER round
than the one that filed them and only 36 in the same round, median gap 1 round. Routing
TODAY mostly defers; exhaustion is the change that could stop it deferring.

SO THIS SCRIPT COMPARES 3 WORLDS over the same runs:
  A  as recorded                      -- the unresolved criticals stay unresolved
  B  resolved LATE   (the panel's)    -- flipped at their existing round
  C  resolved PROMPTLY (his)          -- flipped, and their round pulled EARLIER by the
                                         measured median routing gap

If gamma falls in B and rises in C, then the panel measured the cost of resolving
findings late and not the cost of exhausting the ladder, and his intuition is right.

Run: python3 scripts/gamma_and_when_the_ladder_resolves_2026-10-07.py
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

CRIT = 0.7
ARM = 0.30


def _wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    p = k / n
    c = 1.0 / (1.0 + z * z / n)
    centre = c * (p + z * z / (2 * n))
    half = c * z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - half, centre + half)


def _agree(k, n):
    from statsmodels.stats.proportion import proportion_confint
    a = proportion_confint(k, n, alpha=0.05, method="wilson")
    b = _wilson(k, n)
    assert abs(a[0] - b[0]) < 1e-12 and abs(a[1] - b[1]) < 1e-12, "tools disagree"
    return b


def _median_gap(all_entries):
    gaps = []
    for e in all_entries:
        if not e.get("resolved_by_routing"):
            continue
        o, r = e.get("open_since_round"), e.get("last_status_change_round")
        if o is None or r is None:
            continue
        if r > o:
            gaps.append(r - o)
    if not gaps:
        return 0, 0
    gaps.sort()
    n = len(gaps)
    med = gaps[n // 2] if n % 2 else (gaps[n // 2 - 1] + gaps[n // 2]) / 2
    return med, n


def _gamma(rounds):
    """The runner's own gamma estimate over a per-round novel-critical series."""
    from bench.reference_runner_v3 import _estimate_gamma
    return _estimate_gamma(rounds)


def _series(entries, flip: bool, pull: float):
    """Novel criticals per round. `flip` resolves the unresolved; `pull` moves a
    flipped finding EARLIER by that many rounds, floored at round 1."""
    counts: dict = {}
    for e in entries:
        try:
            sev = float(e.get("severity") or 0.0)
        except (TypeError, ValueError):
            sev = 0.0
        if sev < CRIT:
            continue
        rnd = e.get("open_since_round")
        if rnd is None:
            continue
        unresolved = e.get("status") in ("UNCONFIRMED", None) and not e.get("verified")
        if unresolved and not flip:
            continue
        if unresolved and flip and pull:
            rnd = max(1, int(round(rnd - pull)))
        counts[rnd] = counts.get(rnd, 0) + 1
    if not counts:
        return []
    return [counts.get(r, 0) for r in range(1, max(counts) + 1)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="gamma_and_when_the_ladder_resolves_2026-10-07.py",
        description=__doc__.split("\n\n")[0])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    all_entries = []
    runs = []
    for f in sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json"))):
        try:
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ents = list(((d.get("registry") or {}).get("entries") or {}).values())
        all_entries.extend(ents)
        if len(d.get("gamma_history") or []) >= 3:
            runs.append((pathlib.Path(f).parent.name, ents))

    pull, n_gaps = _median_gap(all_entries)
    print("=" * 92)
    print(f"ROUTED RESOLUTIONS THAT LANDED LATE: {n_gaps}; median gap {pull} round(s)")
    print(f"RUNS WITH AT LEAST 3 ROUNDS: {len(runs)}")
    print("=" * 92)
    print(f"{'run':46s} {'A recorded':>11s} {'B late':>9s} {'C prompt':>9s}")

    down_b = up_c = cross_b = cross_c = 0
    measured = 0
    for name, ents in runs:
        a = _series(ents, flip=False, pull=0)
        b = _series(ents, flip=True, pull=0)
        c = _series(ents, flip=True, pull=pull)
        if len(a) < 3 or len(b) < 3 or len(c) < 3:
            continue
        ga, gb, gc = _gamma(a), _gamma(b), _gamma(c)
        if None in (ga, gb, gc):
            continue
        measured += 1
        down_b += gb < ga
        up_c += gc > gb
        cross_b += (ga >= ARM) and (gb < ARM)
        cross_c += (gb < ARM) and (gc >= ARM)
        if not args.quiet:
            print(f"  {name[:44]:44s} {ga:>11.4f} {gb:>9.4f} {gc:>9.4f}")

    print()
    if measured:
        lo, hi = _agree(down_b, measured)
        print(f"B lower than A (the panel's finding): {down_b} of {measured} = "
              f"{100*down_b/measured:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
        lo, hi = _agree(up_c, measured)
        print(f"C higher than B (prompt beats late) : {up_c} of {measured} = "
              f"{100*up_c/measured:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
        print(f"runs crossing the {ARM} arm DOWN from A to B : {cross_b}")
        print(f"runs crossing the {ARM} arm BACK UP from B to C: {cross_c}")
    print()
    print("If gamma falls when findings resolve LATE and recovers when they resolve")
    print("PROMPTLY, the panel measured the cost of lateness, not the cost of")
    print("exhausting the ladder -- and exhaustion is the change that stops the")
    print("deferral. That is the founder's hypothesis, stated as a test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
