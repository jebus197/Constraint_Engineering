#!/usr/bin/env python3
"""Reproduce the maths-routing divergence figure, which previously lived only in prose.

WHY THIS EXISTS. On 2026-09-06 CC1 unified 2 divergent copies of `_MATH_PATTERN`
and justified it with "40 of 8709 archived descriptions, 0.46%, Wilson [0.34%,
0.62%]". The guard test's docstring then claimed agreement was enforced "by
EXECUTING both over the archived corpus". The shipped corpus is 14 hand-written
strings. fable caught it: the figure was real when it was run and NOTHING COMMITTED
REPRODUCED IT -- the exact `measured-rate-travels-with-its-script` violation CC1 had
cited at others 4 times that same day, committed in a test written to enforce rigour.

This script is that missing artefact. It replays BOTH historical pattern forms over
every distinct finding description in the archive and reports the disagreement with
its interval, so the number in the docstring can be checked rather than believed.

Run: python3 scripts/measure_math_pattern_divergence.py
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scipy.stats import beta as beta_dist
from statsmodels.stats.proportion import proportion_confint

REPO = Path(__file__).resolve().parents[1]

# The 2 forms as they stood BEFORE unification, preserved here because the point of
# the measurement is the gap between them. immune_agents carried 7 alternatives that
# verification_utils lacked: log, exp, bound, threshold, inequality, formula, equation.
BROAD = re.compile(
    r"(?:[=<>!]=?|[+\-*/^]|\bsqrt\b|\blog\b|\bexp\b|\b\d+\s*[*/+\-]"
    r"|\bEq\(|\bGt\(|\bLt\(|\bbound\b|\bthreshold\b|\binequality\b"
    r"|\bformula\b|\bequation\b)")
NARROW = re.compile(
    r"(?:[=<>!]=?|[+\-*/^]|\bsqrt\b|\b\d+\s*[*/+\-]|\bEq\(|\bGt\(|\bLt\()")


def _descriptions() -> list[str]:
    seen = set()
    for path in (REPO / "bench" / "logs").rglob("*.json"):
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue
        stack = [doc]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                v = o.get("description")
                if isinstance(v, str) and len(v) > 20:
                    seen.add(v)
                stack.extend(o.values())
            elif isinstance(o, list):
                stack.extend(o)
    return sorted(seen)


def main() -> int:
    argparse.ArgumentParser(description=__doc__.split("\n")[0]).parse_args()
    descs = _descriptions()
    n = len(descs)
    if not n:
        print("no archived descriptions found")
        return 1
    disagree = [d for d in descs if bool(BROAD.search(d)) != bool(NARROW.search(d))]
    k = len(disagree)
    broad_only = sum(1 for d in disagree if BROAD.search(d))
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_cp = beta_dist.ppf(0.025, k, n - k + 1) if k else 0.0
    hi_cp = beta_dist.ppf(0.975, k + 1, n - k) if k < n else 1.0
    print("Maths-routing pattern divergence, replayed over the real archive")
    print("=" * 68)
    print(f"  distinct archived finding descriptions : {n}")
    print(f"  the 2 historical forms disagree on     : {k} = {100*k/n:.2f}%")
    print(f"     Wilson [{100*lo_w:.2f}%, {100*hi_w:.2f}%]  "
          f"Clopper-Pearson [{100*lo_cp:.2f}%, {100*hi_cp:.2f}%]")
    if k:
        blo, bhi = proportion_confint(broad_only, k, alpha=0.05, method="wilson")
        print(f"  of those, the BROAD form routed as maths and the narrow did not: "
              f"{broad_only} of {k} = {100*broad_only/k:.1f}%  "
              f"Wilson [{100*blo:.1f}%, {100*bhi:.1f}%]")
        print(f"  example: {disagree[0][:100]!r}")
    print()
    print("  Unification took the BROAD form: a false positive costs a wasted check,")
    print("  a false negative costs an unchecked mathematical claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
