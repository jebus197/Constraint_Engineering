#!/usr/bin/env python3
"""Re-adjudicate the 133 similarity pairs with both 2026-08-30 defects repaired.

The archived adjudication in `experimental_notes/data/adjudication_by_repair.json`
was computed with two defects now known and fixed:

  1. `_direction`'s SAME was the FALL-THROUGH, so an ERRORed falsifier leg did not
     merely contaminate a verdict -- it PRODUCED one. 40 of 178 leg-bearing
     directions across 34 of 133 pairs rested on legs that cannot carry them.

  2. `_apply_fix_to_source` matched SEARCH text as a raw substring, so a block
     whose first line lost its indentation spliced INSIDE an indented line and
     left the file unparseable. 12 of 313 archived fixes were corrupted, and the
     wreckage was then judged as the model's proposal.

This re-run uses `bench.fix_efficacy.probe_pair`, which carries the corrected
verdict rule AND works through the discrimination-control overlay, so no reviewed
target is written to at any point -- unlike the original tool, which writes the
patched text to the live file and restores it in a `finally`.

Writes JSON. Changes no finding's status.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

from bench.fix_efficacy import probe_pair  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--out", default="experimental_notes/data/readjudication_2026-08-30.json")
    args = ap.parse_args()

    old = json.loads((REPO / "experimental_notes" / "data" /
                      "adjudication_by_repair.json").read_text(encoding="utf-8"))["rows"]

    arch = json.loads((REPO / "experimental_notes" / "data" /
                       "discrimination_control_archive.json").read_text(encoding="utf-8"))
    arows = arch if isinstance(arch, list) else (arch.get("rows") or next(iter(arch.values())))
    tmap = {(str(r.get("exp")), r.get("cid")): r.get("target")
            for r in arows if r.get("target")}

    ents: dict = {}
    for d in sorted((REPO / "bench" / "logs").glob("exp4*")):
        if not d.is_dir():
            continue
        reps = [p for p in d.glob("*_report.json") if ".errata" not in str(p)]
        if not reps:
            continue
        try:
            ents[d.name.split("_")[0]] = json.loads(
                reps[0].read_text(encoding="utf-8"))["registry"]["entries"]
        except Exception:                                     # noqa: BLE001
            continue

    rows = old[:args.limit] if args.limit else old
    print(f"  {len(rows)} archived pairs to re-adjudicate", flush=True)

    out, moved, tally = [], collections.Counter(), collections.Counter()
    t0 = time.monotonic()
    for i, r in enumerate(rows, 1):
        run = r["run"]
        A = ents.get(run, {}).get(r["a"])
        B = ents.get(run, {}).get(r["b"])
        tgt = tmap.get((run, r["a"])) or tmap.get((run, r["b"]))
        if not (A and B and tgt and (REPO / tgt).is_file()):
            tally["UNRESOLVABLE"] += 1
            out.append({**{k: r[k] for k in ("run", "a", "b")},
                        "was": r["verdict"], "now": "UNRESOLVABLE"})
            continue
        try:
            res = probe_pair(A, B, tgt, repo_root=REPO, timeout=args.timeout)
            now, detail = res.outcome, res.detail
        except Exception as exc:                              # noqa: BLE001
            now, detail = "PROBE_ERROR", f"{type(exc).__name__}: {exc}"
        tally[now] += 1
        moved[(r["verdict"], now)] += 1
        out.append({**{k: r[k] for k in ("run", "a", "b")},
                    "was": r["verdict"], "now": now, "detail": detail[:300]})
        if i % 25 == 0:
            print(f"    {i}/{len(rows)}  {int(time.monotonic()-t0)}s", flush=True)

    dest = REPO / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"tally": dict(tally),
                                "transitions": {f"{k[0]} -> {k[1]}": v for k, v in moved.items()},
                                "rows": out}, indent=2), encoding="utf-8")
    print(f"\n  new verdicts: {dict(tally)}")
    print("\n  transitions (was -> now):")
    for k, v in sorted(moved.items(), key=lambda x: -x[1]):
        flag = "" if k[0] == k[1] else "   <-- CHANGED"
        print(f"    {k[0]:22s} -> {k[1]:24s} {v:4d}{flag}")
    print(f"\n  written: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
