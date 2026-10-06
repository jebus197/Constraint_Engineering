#!/usr/bin/env python3
"""The provenance gate credited every routed confirmation to the wrong model.

`scripts/competence_provenance.py` decides whether a model's record is SAFE TO RANK
ON. Until 2026-10-06 it keyed its per-model tally on `source_model` — the model that
REPORTED a finding. When the routing ladder resolves a critical, the falsifier is
written by a RUNG further up the ladder and recorded in `resolved_by_routing`; the
filing model is precisely the one that failed to produce a working test.

Found by the cc2 seat in the joint round of 2026-10-05. This script measures it.

WHY THE DIRECTION MATTERS. The founder has ruled the capability ladder must become a
measured statistic rather than a frozen list of vendor names. Crediting a strong rung's
work to the weak filer flatters exactly the models the ladder exists to demote, and the
error compounds: a flattered model is routed MORE work, which it then fails, which is
credited to whoever filed next.

Run:  python3 scripts/the_provenance_gate_credits_the_filer_2026-10-06.py
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


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_provenance_gate_credits_the_filer_2026-10-06.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--logs", default=str(REPO / "bench" / "logs"))
    return p.parse_args(argv)


def _ci(k, n):
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import norm
    a = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = float(norm.ppf(0.975)); p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return a[0] * 100, a[1] * 100, abs(a[0] - (c - h)) < 1e-9


def main(argv=None) -> int:
    args = _parse_args(argv)
    total = routed = mis = 0
    pairs = collections.Counter()
    for f in sorted(glob.glob(str(pathlib.Path(args.logs) / "*" / "runner_state.json"))):
        try:
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for e in ((d.get("registry") or {}).get("entries") or {}).values():
            total += 1
            rb = (e.get("resolved_by_routing") or "").strip()
            if not rb:
                continue
            routed += 1
            sm = (e.get("source_model") or "").strip()
            if sm and rb != sm:
                mis += 1
                pairs[(sm, rb)] += 1

    print("=" * 78)
    print("WHO GETS CREDIT FOR A FALSIFIER THE ROUTING LADDER WROTE?")
    print("=" * 78)
    print(f"archived registry entries         : {total}")
    print(f"carrying resolved_by_routing      : {routed}")
    if routed:
        lo, hi, ok = _ci(mis, routed)
        print(f"  of those, credited to the FILER : {mis} "
              f"= {100 * mis / routed:.4f}% of routed, Wilson [{lo:.4f}%, {hi:.4f}%]"
              f"{'' if ok else '  *** TOOLS DISAGREE ***'}")
    if total:
        lo, hi, ok = _ci(mis, total)
        print(f"  as a share of ALL entries       : {mis} "
              f"= {100 * mis / total:.4f}%, Wilson [{lo:.4f}%, {hi:.4f}%]")
    print()
    print("commonest filed/resolved pairs (the filer failed, the rung succeeded):")
    for (sm, rb), n in pairs.most_common(6):
        print(f"    filed by {sm:<16} resolved by {rb:<16} n={n}")
    if not routed:
        print()
        print("0 routed entries — the defect affects nothing in this archive.")
        return 0
    print()
    print("REPAIRED 2026-10-06: `competence_provenance.falsifier_author` takes the")
    print("recorded resolver in precedence over the filer, mirroring the runner's own")
    print("`_corrected_copy_owner`. Guard:")
    print("bench/tests/test_provenance_credits_the_falsifier_author_2026-10-06.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
