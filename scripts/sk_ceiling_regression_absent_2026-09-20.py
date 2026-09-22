#!/usr/bin/env python3
"""Does the fix score discriminate? The ceiling pile-up, decomposed.

Blind panel round 2026-09-20, Section 6.1. Measured on the archived record:

  * 902 ADMISSIBLE fixes; 672 score exactly 1.0 -- the gate's ceiling.
  * E is a renormalised weighted mean over AVAILABLE gates
    (bench/reference_runner_v3.py, compute_sk): a gate returning None is
    silently DROPPED from the mean rather than counted against the fix.
  * e2_regression -- the only gate that observes behaviour -- is the dropped
    gate in every such case here, mostly via the 120s pytest timeout.

So a subset of the 1.0 scores are 'ruff + bandit alone passed, the regression
suite never executed', printed indistinguishably from 'everything passed'.
This script counts that subset, with Wilson intervals, and counts which gate
drives every below-ceiling deduction. It changes nothing; it measures.

Run: python3 scripts/sk_ceiling_regression_absent_2026-09-20.py
"""
from __future__ import annotations

import glob
import json
import os
from collections import Counter
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 60_000_000


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def collect() -> list[dict]:
    recs: list[dict] = []

    def walk(o):
        if isinstance(o, dict):
            sk = o.get("sk_result")
            if isinstance(sk, dict) and sk.get("tristate") == "ADMISSIBLE":
                recs.append(sk)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for f in sorted(glob.glob(str(ROOT / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > MAX_BYTES:
            continue
        try:
            raw = open(f, errors="ignore").read()
        except OSError:
            continue
        if "sk_result" not in raw:
            continue
        try:
            walk(json.loads(raw))
        except Exception:
            continue
    return recs


def main() -> int:
    adm = collect()
    n = len(adm)
    ones = [r for r in adm if float(r.get("sk", 0)) == 1.0]
    lo, hi = wilson(len(ones), n)
    print("THE FIX-SCORE CEILING, DECOMPOSED (archived ADMISSIBLE records)")
    print()
    print(f"ADMISSIBLE fixes                 : {n}")
    print(f"score exactly 1.0                : {len(ones)}  "
          f"({len(ones)/n:.4%}, Wilson [{lo:.4%}, {hi:.4%}])")

    def e2_absent(r):
        gd = r.get("gate_details") or {}
        e2 = gd.get("e2_regression") or {}
        return e2.get("score", 0) is None

    abs_ceiling = [r for r in ones if e2_absent(r)]
    lo2, hi2 = wilson(len(abs_ceiling), len(ones))
    print(f"of those, e2_regression ABSENT   : {len(abs_ceiling)}  "
          f"({len(abs_ceiling)/len(ones):.4%} of ceiling scores, "
          f"Wilson [{lo2:.4%}, {hi2:.4%}])")
    tos = Counter()
    for r in abs_ceiling:
        d = str((r["gate_details"]["e2_regression"] or {}).get("detail", ""))
        tos["timeout" if "timed out" in d else d[:50]] += 1
    for cause, k in tos.most_common(5):
        print(f"    absence cause: {cause:30s} {k:4d}")

    below = [r for r in adm if float(r.get("sk", 0)) < 1.0]
    drivers = Counter()
    for r in below:
        gd = r.get("gate_details") or {}
        low = tuple(k for k in ("e2_regression", "e3_ruff", "e4_bandit")
                    if isinstance(gd.get(k), dict)
                    and gd[k].get("score") is not None and gd[k]["score"] < 1.0)
        drivers[low] += 1
    print()
    print(f"below-ceiling ADMISSIBLE         : {len(below)}")
    for gates, k in drivers.most_common():
        print(f"    deduction driven by {','.join(gates) or '(none)'}: {k}")
    e2_driven = sum(k for g, k in drivers.items() if "e2_regression" in g)
    lo3, hi3 = wilson(e2_driven, len(below))
    print(f"  e2_regression appears in the driver set: {e2_driven}/{len(below)} "
          f"({e2_driven/len(below):.4%}, Wilson [{lo3:.4%}, {hi3:.4%}])")
    print()
    print("READING: within ADMISSIBLE, e2_regression is effectively the only")
    print("discriminating gate -- and it is also the only gate permitted to go")
    print("silently absent at the ceiling. The pile-up at 1.0 is therefore part")
    print("measurement ('nothing objected') and part non-measurement ('the one")
    print("behavioural gate never ran'), and the score does not distinguish them.")
    return 0


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    raise SystemExit(main())
