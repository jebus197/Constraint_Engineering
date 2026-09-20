#!/usr/bin/env python3
"""Which of the 191 archived refusals were actually decided by the unmeasured constants?

WHY THIS EXISTS. CC1 reported to the founder, and put into the round-4 panel
brief, that "191 fixes were refused on the strength of a constant nobody
measured". The kimi seat marked that PARTIAL in round 4 and gave the reason:

    "In v3, `tristate = SK_ADMISSIBLE if sk > 0 else SK_REJECTED` (v3:10896) --
     a fix with no parsed/applied blocks is REJECTED at sk=0 regardless of any
     constant. Only the corrected-gate threshold path (`compute_rk(R,q,sk) > R`)
     refuses on the constants."

That citation is exact. There are therefore 2 different refusal paths and the
brief's sentence conflated them:

  STRUCTURAL. `sk == 0` -- the proposed fix parsed or applied no blocks at all.
  The verdict is REJECTED whatever q, R_old, nu_b and nu_f happen to be. No
  constant decides it, so it is NOT evidence for wiring measured parameters.

  THRESHOLD. `sk > 0` and the gate refused anyway, by comparing against a
  break-even computed FROM the constants. These are the refusals the claim is
  about.

This script splits the archive by that predicate and reports both counts with
Wilson intervals, cross-checked against statsmodels.

Run:  python3 scripts/split_the_191_refusals_2026-09-20.py
"""
from __future__ import annotations

import argparse
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


def collect():
    """Every archived sk_result, with the fields that decide which path refused it."""
    rows = []
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
            d = json.loads(raw)
        except Exception:
            continue
        run = os.path.basename(os.path.dirname(f))

        def walk(o):
            if isinstance(o, dict):
                sk = o.get("sk_result")
                if isinstance(sk, dict) and "tristate" in sk:
                    rows.append({
                        "run": run,
                        "tristate": sk.get("tristate"),
                        "sk": sk.get("sk"),
                        "passes_threshold": sk.get("passes_threshold"),
                        "s_star": sk.get("s_star"),
                        "blocks_parsed": sk.get("blocks_parsed"),
                        "blocks_applied": sk.get("blocks_applied"),
                    })
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(d)
    return rows


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)

    rows = collect()
    total = len(rows)
    rejected = [r for r in rows if r["tristate"] == "REJECTED"]
    n = len(rejected)

    # STRUCTURAL: sk == 0, so v3:10896 sets REJECTED before any constant is read.
    structural = [r for r in rejected if (r["sk"] or 0) == 0]
    # THRESHOLD: sk > 0 and the gate still refused.
    threshold = [r for r in rejected if (r["sk"] or 0) > 0]

    # AND THE REFUSALS THE CONSTANTS COULD DECIDE ARE NOT IN `rejected` AT ALL.
    # Found by P-passing the first version of this script, which looked only at
    # the REJECTED tristate and reported 0 of 191. Reading the flow explains why:
    # `_evaluate_sk_for_findings` reaches the threshold check ONLY under
    # `if sk_result.tristate == SK_ADMISSIBLE` (v3:11958), so a REJECTED verdict
    # can never have been a threshold refusal. A gate refusal is an ADMISSIBLE
    # tristate carrying `passes_threshold: false`. That is the population the
    # claim was really about, and it has to be counted separately.
    admissible = [r for r in rows if r["tristate"] == "ADMISSIBLE"]
    scored = [r for r in admissible if r["passes_threshold"] is not None]
    gate_refused = [r for r in scored if r["passes_threshold"] is False]

    print("THE 191 REFUSALS, SPLIT BY WHICH PATH REFUSED THEM")
    print("=" * 68)
    print(f"  archived sk_result decisions : {total}")
    print(f"  REJECTED                     : {n}")
    print()
    for label, subset, why in (
        ("STRUCTURAL (sk == 0)", structural,
         "no blocks parsed/applied; v3:10896 refuses regardless of any constant"),
        ("THRESHOLD  (sk >  0)", threshold,
         "the gate refused a scored fix, by a break-even computed FROM the constants"),
    ):
        k = len(subset)
        lo, hi = wilson(k, n) if n else (0.0, 0.0)
        print(f"  {label}: {k} of {n} = {k/n:.4%}  Wilson [{lo:.4%}, {hi:.4%}]" if n
              else f"  {label}: 0")
        print(f"      {why}")
    print()

    try:
        from statsmodels.stats.proportion import proportion_confint
        agree = True
        for subset in (structural, threshold):
            if not n:
                continue
            lo2, hi2 = proportion_confint(len(subset), n, alpha=0.05, method="wilson")
            lo1, hi1 = wilson(len(subset), n)
            if abs(lo1 - lo2) > 1e-12 or abs(hi1 - hi2) > 1e-12:
                agree = False
        print(f"  cross-check, statsmodels Wilson agrees: {agree}")
    except ImportError:
        print("  cross-check: statsmodels unavailable")

    print()
    print("  refusals per run, threshold path only:")
    by_run = Counter(r["run"] for r in threshold)
    for run, k in by_run.most_common(8):
        print(f"      {k:4d}  {run}")
    if not by_run:
        print("      (none)")

    print()
    print("  THE POPULATION THE CLAIM WAS REALLY ABOUT -- gate refusals:")
    print(f"      ADMISSIBLE verdicts               : {len(admissible)}")
    print(f"      ...carrying passes_threshold      : {len(scored)}")
    k_gate = len(gate_refused)
    if scored:
        lo, hi = wilson(k_gate, len(scored))
        print(f"      ...where the gate REFUSED         : {k_gate} = "
              f"{k_gate/len(scored):.4%}  Wilson [{lo:.4%}, {hi:.4%}]")
    print()
    print("-" * 68)
    k_thr = len(threshold)
    if k_thr == 0 and k_gate == 0:
        print("CC1'S CLAIM IS WITHDRAWN. It said, to the founder and in the round-4")
        print("panel brief: \"191 fixes were refused on the strength of a constant")
        print("nobody measured\". Measured on both paths, the constants decided")
        print("NOTHING on the archive:")
        print(f"   {len(structural)} of {n} refusals were STRUCTURAL -- the fix scored 0, so")
        print("      v3:10896 refused it before any constant was read;")
        print(f"   {k_gate} of {len(scored)} scored fixes were refused BY THE GATE.")
        print()
        print("AND THE REPOSITORY ALREADY SAID SO. bench/reference_runner_v3.py:11820,")
        print("in sk_threshold_shadow's docstring: \"passes_threshold reads false 0")
        print("times under every method and every corpus tried. The gate has never")
        print("rejected a fix\" -- pinned by")
        print("bench/tests/test_stated_gate_count_matches_measurement_2026-09-07.py.")
        print("The claim contradicted a committed, test-pinned measurement that was")
        print("never consulted.")
        print()
        print("WHAT SURVIVES. The machinery DID run:", total, "decisions across the")
        print("archive, so cc2's residual 2 is closed on its first half. But its")
        print("second half resolves cc2's OWN way: \"if none did, then CHANGE")
        print("NOTHING becomes the correct verdict for the archive (though not for")
        print("future runs)\". The case for wiring measured parameters rests on")
        print("what happens when a scored fix first meets the gate -- not on the")
        print("archive, which contains no such event.")
    else:
        lo, hi = wilson(k_thr, n)
        print(f"CC1's claim is CORRECTED, not withdrawn: {k_thr} of {n} refusals")
        print(f"({k_thr/n:.4%}, Wilson [{lo:.4%}, {hi:.4%}]) were decided by the gate")
        print("using constants no measurement supplied. The other "
              f"{len(structural)} were structural.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
