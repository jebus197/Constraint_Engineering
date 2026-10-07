#!/usr/bin/env python3
"""The filing model's failed attempt was missing from its own denominator.

THE FOUNDER'S VERDICT, 2026-10-06, on the cc2 seat's finding: *"Verdict. Fix it."*

THE DEFECT. `competence_provenance.analyse` credited ONE author per entry. On a routed
entry that author is the model that WROTE the resolving falsifier -- correct, and the
subject of the 2026-10-06 repair. But the FILER then received nothing: not a
confirmation, and not the failed attempt either. A model that files criticals it never
resolves therefore accumulates no denominator at all, and an EMPTY record reads as a
PERFECT one.

WHY IT IS NOT A PENALTY. Routing fires only on a critical whose source did not resolve
it, so a routed entry IS a recorded failed attempt by the filer. Counting it records
the attempt that actually happened.

WHY IT MATTERS NOW. The founder has ruled that routing must rank on MEASURED capability
rather than on model names. A measure that omits a model's failures is not a measure of
capability; it is a measure of how often that model got lucky enough to be routed away
from. This script reports how many models' ranks move once the failures are counted.

Run: python3 scripts/the_filers_failure_was_missing_2026-10-07.py
     --quiet   totals only
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


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
    lo_s, hi_s = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_c, hi_c = _wilson(k, n)
    assert abs(lo_s - lo_c) < 1e-12 and abs(hi_s - hi_c) < 1e-12, (
        f"statsmodels and the closed form disagree on {k}/{n}")
    return lo_c, hi_c


def _tally(entries, count_filer_failure: bool):
    """Per-model (attempts, confirmations). `count_filer_failure` is the fix."""
    per = collections.defaultdict(lambda: collections.Counter())
    for e in entries:
        src = e.get("source_model") or "?"
        author = (e.get("resolved_by_routing") or e.get("resolved_in_round")
                  or e.get("resolved_by_sweep") or src)
        per[author]["n"] += 1
        if e.get("falsifier_verdict") == "CONFIRMED":
            per[author]["confirmed"] += 1
        if count_filer_failure and author != src:
            per[src]["n"] += 1
    return per


def _rank(per, min_n=1):
    rates = {m: c["confirmed"] / c["n"] for m, c in per.items() if c["n"] >= min_n}
    return [m for m, _ in sorted(rates.items(), key=lambda kv: (-kv[1], kv[0]))], rates


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="the_filers_failure_was_missing_2026-10-07.py",
        description=__doc__.split("\n\n")[0])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    entries = []
    for f in sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json"))):
        try:
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        entries.extend(((d.get("registry") or {}).get("entries") or {}).values())

    routed = [e for e in entries if e.get("resolved_by_routing")]
    print("=" * 80)
    print(f"ARCHIVE: {len(entries):,} entries, {len(routed):,} routed")
    if entries:
        lo, hi = _agree(len(routed), len(entries))
        print(f"  routed share: {100*len(routed)/len(entries):.4f}%  "
              f"Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")

    before, after = _tally(entries, False), _tally(entries, True)
    order_b, rates_b = _rank(before)
    order_a, rates_a = _rank(after)

    print()
    print(f"{'model':16s} {'n before':>9s} {'n after':>8s} {'rate before':>12s} "
          f"{'rate after':>11s} {'rank':>10s}")
    for m in sorted(set(order_b) | set(order_a)):
        rb = order_b.index(m) + 1 if m in order_b else 0
        ra = order_a.index(m) + 1 if m in order_a else 0
        moved = "" if rb == ra else f"  {rb} -> {ra}"
        print(f"  {m:14s} {before[m]['n']:>9d} {after[m]['n']:>8d} "
              f"{rates_b.get(m, float('nan')):>12.4f} {rates_a.get(m, float('nan')):>11.4f}"
              f"{moved}")

    moved = sum(1 for m in order_b
                if m in order_a and order_b.index(m) != order_a.index(m))
    n = len(order_b)
    print()
    if n:
        lo, hi = _agree(moved, n)
        print(f"MODELS WHOSE RANK MOVES once the filer's failure is counted: "
              f"{moved} of {n} = {100*moved/n:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
    print()
    print("A measure that omits a model's failures is not a measure of capability.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
