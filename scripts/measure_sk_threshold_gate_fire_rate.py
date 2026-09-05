#!/usr/bin/env python3
"""Measure how often the S_k admissibility threshold has ever REJECTED a fix.

WHY THIS SCRIPT EXISTS, AND WHY ITS ABSENCE WAS ITSELF A DEFECT
---------------------------------------------------------------
The figure "0 of 3816, Wilson 95% CI [0.0000, 0.0010]" was reported to the
founder on 2026-09-04 and again on 2026-09-05, and used as the justification for
a proposed change to the gate. Measured 2026-09-05: NO COMMITTED SCRIPT
REPRODUCED IT. The number lived only as prose in resources/RECOVERY.md line 155
and in experimental_notes/Morning_Roundup_2026-09-04b.md.

That breaches the founder ruling `measured-rate-travels-with-its-script`, issued
2026-09-04 -- one day before the figure was quoted. The ruling's own text records
that the project had already learned this lesson once, on 2026-09-01, and
repeated it on 2026-09-02. This was the third repeat. A number that exists only
as prose is a claim ABOUT evidence, not evidence, and a fix justified by an
unreproducible number is a fix justified by nothing.

WHAT THE GATE IS
----------------
`check_sk_threshold` decides whether a proposed fix is good enough to accept.
A fix scoring below S* is refused as being in the "Valley of Bad Fixes" -- good
enough to look like progress, bad enough to make things worse. The question this
script answers is simply: has that ever actually happened?

TWO INDEPENDENT ROUTES, because one route can be wrong in a way that looks right.

  ROUTE 1, structured records. `passes_threshold` is written at
  reference_runner_v3.py:9922, and ONLY inside the `tristate == SK_ADMISSIBLE`
  branch. A fix rejected for any other reason (error path, no score) arrives
  already marked and never reaches that line. So `passes_threshold == False` is
  the unambiguous signature of a genuine THRESHOLD rejection, and it cannot be
  confused with the other rejection kinds.

  ROUTE 2, run logs. The threshold branch is the only place that emits
  "(Valley of Bad Fixes)". The error path emits "REJECTED A=" instead. Counting
  both separates a gate that never fires from a gate that is never reached.

If the routes disagree, the disagreement is the finding and this script says so
rather than picking a favourite.

Usage:
    python3 scripts/measure_sk_threshold_gate_fire_rate.py [--logs-dir DIR] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOGS = REPO_ROOT / "bench" / "logs"

# THESE MUST MATCH THE RUNNER'S EMITTED LINE FORMAT, NOT THE PHRASE.
#
# The first version of this script counted the bare substring
# "(Valley of Bad Fixes)" and found 11 hits, contradicting route 1. Every one of
# them was a MODEL DISCUSSING THE CONCEPT in a confer transcript or a panel
# patch -- files like confer_exp38_fix_review/*.json and
# panel_placement_20260904T030259Z/cc2.patch -- not a runner emission.
#
# That is phrase-mentions counted as events, and this project has made that exact
# error before: 1,577 phrase-mentions were once read as gate firings. A concept
# discussed in prose is not the concept occurring.
#
# So both patterns are anchored on the exact format the runner emits:
#   f"  S_k [{cid}]: REJECTED sk={sk:.3f} < S*={s_star:.3f} (Valley of Bad Fixes)"
#   f"  S_k [{cid}]: REJECTED A={A} ..."
THRESHOLD_REJECT_RE = re.compile(
    r"S_k \[[^\]]+\]:\s*REJECTED\s+sk=\d+\.\d+\s*<\s*S\*=\d+\.\d+\s*\(Valley of Bad Fixes\)"
)
ERROR_PATH_RE = re.compile(r"S_k \[[^\]]+\]:\s*REJECTED\s+A=")


def wilson_interval(k: int, n: int, z: float = 1.959963984540054):
    """Wilson score interval. Correct at k=0, where the normal approximation is not.

    Chosen deliberately: at k=0 a Wald interval gives the degenerate [0, 0],
    which would assert certainty the data cannot support.
    """
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _walk_sk_results(obj):
    """Yield every sk_result dict found anywhere in a nested report structure.

    Reports have changed shape across runner versions, so this searches rather
    than assuming a path -- a hard-coded path that silently matched nothing is
    exactly how a 0 could be manufactured.
    """
    if isinstance(obj, dict):
        if "passes_threshold" in obj:
            yield obj
        for v in obj.values():
            yield from _walk_sk_results(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_sk_results(v)


def route_1_structured(logs_dir: Path):
    """Count passes_threshold True/False across every archived JSON report."""
    true_n = false_n = 0
    files_with_field = 0
    files_scanned = 0
    per_run = Counter()

    for path in sorted(logs_dir.rglob("*.json")):
        files_scanned += 1
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        found_here = 0
        for res in _walk_sk_results(data):
            v = res.get("passes_threshold")
            if v is True:
                true_n += 1
                found_here += 1
            elif v is False:
                false_n += 1
                found_here += 1
                per_run[path.parent.name] += 1
        if found_here:
            files_with_field += 1

    return {
        "files_scanned": files_scanned,
        "files_with_field": files_with_field,
        "passes_true": true_n,
        "passes_false": false_n,
        "total": true_n + false_n,
        "runs_with_a_rejection": dict(per_run),
    }


def route_2_logs(logs_dir: Path):
    """Count the log line only the threshold branch can emit."""
    threshold_rejects = 0
    error_path_rejects = 0
    files_scanned = 0

    patterns = ("*.log", "*.txt", "*.jsonl")
    for pattern in patterns:
        for path in sorted(logs_dir.rglob(pattern)):
            files_scanned += 1
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue
            threshold_rejects += len(THRESHOLD_REJECT_RE.findall(text))
            error_path_rejects += len(ERROR_PATH_RE.findall(text))

    return {
        "files_scanned": files_scanned,
        "threshold_rejections": threshold_rejects,
        "error_path_rejections": error_path_rejects,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs-dir", type=Path, default=DEFAULT_LOGS)
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args(argv)

    if not args.logs_dir.is_dir():
        print(f"no such logs dir: {args.logs_dir}", file=sys.stderr)
        return 2

    r1 = route_1_structured(args.logs_dir)
    r2 = route_2_logs(args.logs_dir)

    k = r1["passes_false"]
    n = r1["total"]
    lo, hi = wilson_interval(k, n)

    result = {
        "route_1_structured_records": r1,
        "route_2_run_logs": r2,
        "fire_rate": {
            "rejections": k,
            "checks": n,
            "proportion": (k / n) if n else None,
            "wilson_95_ci": [lo, hi],
        },
        "routes_agree": (k == 0) == (r2["threshold_rejections"] == 0),
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print("S_k threshold gate — has it ever rejected a fix?")
    print("=" * 66)
    print("ROUTE 1, structured records (passes_threshold field)")
    print(f"  JSON files scanned          : {r1['files_scanned']}")
    print(f"  files carrying the field    : {r1['files_with_field']}")
    print(f"  passes_threshold == True    : {r1['passes_true']}")
    print(f"  passes_threshold == False   : {r1['passes_false']}   <-- threshold rejections")
    print()
    print("ROUTE 2, run logs (the line only the threshold branch emits)")
    print(f"  text files scanned          : {r2['files_scanned']}")
    print(f"  runner threshold-rejection lines : {r2['threshold_rejections']}")
    print(f"  runner error-path lines          : {r2['error_path_rejections']}")
    print()
    if n:
        print(f"FIRE RATE: {k} of {n}  = {100.0 * k / n:.4f}%")
        print(f"  Wilson 95% CI: [{lo:.4f}, {hi:.4f}]")
    else:
        print("FIRE RATE: no threshold checks found at all — the gate was never REACHED,")
        print("  which is a different claim from 'never fired'. Do not report a rate.")
    print()
    if result["routes_agree"]:
        print("The 2 routes AGREE.")
    else:
        print("*** THE 2 ROUTES DISAGREE. That disagreement is the finding. ***")
        print(f"    structured says {k} rejections; logs say {r2['threshold_rejections']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
