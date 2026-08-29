#!/usr/bin/env python3
"""Run the fix-efficacy probe across every archived finding that carries both a
falsifier and a proposed fix.

Answers the founder's question with a number rather than an argument: of the
findings whose fixes nobody has ever checked, how many actually cure the defect
they claim to?

Writes JSON. Changes nothing. The reviewed targets are never modified -- the
probe works through the discrimination control's overlay.
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

from bench.fix_efficacy import probe  # noqa: E402


def _target_map() -> dict:
    """(run, cid) -> repo-relative target, from the discrimination archive.

    The run reports do NOT record which file was under review: `context_files` is
    empty, and no entry carries `target_file` or `location`. The discrimination
    control archive does record it, per finding, for 372 findings across six
    targets, and all six still exist on disk. Using it is not a convenience --
    without it this sweep resolves zero targets, which is exactly what the first
    version of this script did.
    """
    a = json.loads((REPO / "experimental_notes" / "data" /
                    "discrimination_control_archive.json").read_text(encoding="utf-8"))
    rows = a if isinstance(a, list) else (a.get("rows") or next(iter(a.values())))
    out = {}
    for r in rows:
        t = r.get("target")
        if t and (REPO / str(t)).is_file():
            out[(r.get("run"), r.get("cid"))] = str(t)
    return out


def _target_for(run_dir: str, cid: str, tmap: dict) -> str | None:
    run = run_dir.split("_")[0]
    return tmap.get((run, cid)) or tmap.get((run_dir, cid))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--out", default="experimental_notes/data/fix_efficacy_2026-08-30.json")
    args = ap.parse_args()

    tmap = _target_map()
    print(f"  target map: {len(tmap)} findings", flush=True)
    work = []
    for d in sorted((REPO / "bench" / "logs").glob("exp4*")) + \
             sorted((REPO / "bench" / "logs").glob("exp5*")):
        if not d.is_dir():
            continue
        reps = [p for p in d.glob("*_report.json") if ".errata" not in str(p)]
        if not reps:
            continue
        try:
            rep = json.loads(reps[0].read_text(encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            continue
        for cid, e in (rep.get("registry", {}).get("entries", {}) or {}).items():
            if not (e.get("falsifier_code") or "").strip():
                continue
            if not (e.get("proposed_fix") or "").strip():
                continue
            tgt = _target_for(d.name, cid, tmap)
            if tgt:
                work.append((d.name, cid, tgt, e))

    if args.limit:
        work = work[:args.limit]
    print(f"  {len(work)} findings carry a falsifier, a fix and a resolvable target", flush=True)

    rows, tally = [], collections.Counter()
    t0 = time.monotonic()
    for i, (run, cid, tgt, e) in enumerate(work, 1):
        try:
            r = probe({"falsifier_code": e["falsifier_code"], "proposed_fix": e["proposed_fix"]},
                      tgt, repo_root=REPO, timeout=args.timeout)
            out, detail = r.outcome, r.detail
        except Exception as exc:                              # noqa: BLE001
            out, detail = "PROBE_ERROR", f"{type(exc).__name__}: {exc}"
        tally[out] += 1
        rows.append({"run": run, "cid": cid, "target": tgt, "outcome": out, "detail": detail[:300]})
        if i % 20 == 0:
            print(f"    {i}/{len(work)}  {int(time.monotonic()-t0)}s  {dict(tally)}", flush=True)

    dest = REPO / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"tally": dict(tally), "rows": rows}, indent=2), encoding="utf-8")
    print(f"\n  {dict(tally)}")
    print(f"  written: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
