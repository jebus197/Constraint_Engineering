#!/usr/bin/env python3
"""Verify the 3 load-bearing empirical claims from the 2026-09-06 reach panel.

The panel (cc2 + fable, both Max-plan, free) proposed solutions rather than only
faults. 3 of its claims decide the priority order of the whole programme, so each
is re-measured here rather than accepted. Under measured-rate-travels-with-its-script
the numbers may not be quoted without this file.

CLAIM 1 (cc2). R_k is telemetry: R_new is WRITTEN and never READ, so wiring reach
into sigma changes a reported number and not a decision. cc2 offered this as its
own refutation test #1 -- "if any line reads it, my claim is dead".

CLAIM 2 (cc2). The breadth channel has no variance to explain: essentially every
archived fix touches exactly 1 SEARCH/REPLACE block, so nu's reach channel is
empirically inert while sigma's coverage channel carries all the signal. This is
what makes cc2 answer "sigma only" where fable answers "both homes".

CLAIM 3 (cc2 + the 2026-09-05 record). s_star reads 0.0 in every archived record.

Run: python3 scripts/measure_rk_and_gate_are_disconnected.py
"""
from __future__ import annotations

import ast
import json
import sys
from collections import Counter
from pathlib import Path

from scipy.stats import beta as beta_dist
from statsmodels.stats.proportion import proportion_confint

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
LOGS = REPO / "bench" / "logs"


def _ci(k: int, n: int) -> str:
    if n == 0:
        return "no denominator"
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_cp = beta_dist.ppf(0.025, k, n - k + 1) if k else 0.0
    hi_cp = beta_dist.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return (f"{k} of {n} = {100*k/n:.2f}%  Wilson [{100*lo_w:.2f}%, {100*hi_w:.2f}%]  "
            f"Clopper-Pearson [{100*lo_cp:.2f}%, {100*hi_cp:.2f}%]")


def claim_1_rk_is_write_only() -> bool:
    """AST, not grep: count genuine reads of R_new separately from writes."""
    print("CLAIM 1 -- is R_new written and never read?")
    tree = ast.parse(RUNNER.read_text())
    writes, reads = [], []
    for node in ast.walk(tree):
        # dict-subscript form: entry["R_new"] / d['R_new']
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                and node.slice.value == "R_new":
            (writes if isinstance(node.ctx, ast.Store) else reads).append(node.lineno)
        # bare name form
        elif isinstance(node, ast.Name) and node.id == "R_new":
            (writes if isinstance(node.ctx, ast.Store) else reads).append(node.lineno)
    print(f"  writes: {len(writes)} at lines {sorted(set(writes))}")
    print(f"  reads : {len(reads)} at lines {sorted(set(reads))}")
    # A read that only feeds a write of the same value (return / dict store) is not
    # a decision. Report both, and let the caller judge -- do not silently filter.
    return True


def _iter_reports():
    for path in LOGS.rglob("*.json"):
        try:
            doc = json.loads(path.read_text())
        except Exception:
            continue
        yield path, doc


def _walk_for_key(obj, key):
    """Find every occurrence of `key` at ANY depth. The 2026-09-05 audit defect was
    a top-level-only scan that missed blocks nested inside each round."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            yield from _walk_for_key(v, key)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_for_key(item, key)


def claims_2_and_3_from_archive() -> bool:
    print("\nCLAIMS 2 and 3 -- measured from the archive")
    blocks, s_stars, n_files = Counter(), Counter(), 0
    for _path, doc in _iter_reports():
        n_files += 1
        for v in _walk_for_key(doc, "blocks_applied"):
            if isinstance(v, int):
                blocks[v] += 1
        for v in _walk_for_key(doc, "s_star"):
            if isinstance(v, (int, float)):
                s_stars[round(float(v), 12)] += 1

    print(f"  report files scanned: {n_files}")
    nb = sum(blocks.values())
    if nb:
        print(f"  blocks_applied records: {nb}; distribution {dict(sorted(blocks.items()))}")
        print(f"  exactly 1 block: {_ci(blocks.get(1, 0), nb)}")
        print(f"  mean {sum(k*v for k, v in blocks.items())/nb:.4f}  max {max(blocks)}")
    else:
        print("  blocks_applied: NOT FOUND in the archive -- claim 2 unverifiable here")

    ns = sum(s_stars.values())
    if ns:
        print(f"  s_star records: {ns}; distinct values {dict(sorted(s_stars.items()))}")
        print(f"  s_star == 0.0: {_ci(s_stars.get(0.0, 0), ns)}")
    else:
        print("  s_star: NOT FOUND in the archive -- claim 3 unverifiable here")
    return True


def main() -> int:
    claim_1_rk_is_write_only()
    claims_2_and_3_from_archive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
