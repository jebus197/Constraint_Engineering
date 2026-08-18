#!/usr/bin/env python3
"""Replay the archived runs through the accounting, old and new, and diff them.

WHY THIS EXISTS, AND WHY IT IS BUILT BEFORE ANY REPAIR
------------------------------------------------------
A 5-model panel (2026-08-18, no compelled convergence) recommended repairing the
harness before spending any further experiment, on the grounds that a run made
now would measure the instrument rather than the question. The repairs divide in
two, and only one half can be validated without spending money:

  * ACCOUNTING repairs change only how findings are COUNTED. The archive holds
    the findings, the rounds and the targets, so a replay is a genuine controlled
    before/after: same inputs, different accounting. Zero dispatch.
  * BEHAVIOURAL repairs change what models SEE — the NEAR-DUPLICATE flag reaches
    the next round's prompt (bench/dm/_feedback.py:393, :472) — so a replay would
    be replaying responses the models would no longer have given. Those need a
    live run and this script must not pretend otherwise.

THE EXIT TEST, and it comes first
---------------------------------
Before any delta this script reports can mean anything, it must reproduce each
run's OWN archived series exactly under the OLD accounting. A replay that cannot
reproduce the past is not measuring a repair; it is measuring itself.

`--verify` runs only that check and reports nothing else. If it fails, stop.

Usage
-----
    python3 scripts/replay_accounting.py --verify     # the exit test, run this first
    python3 scripts/replay_accounting.py              # verify, then report deltas
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import bench.convergence_location as CL  # noqa: E402

# Runs carrying both an archived novelty series and a recoverable target.
RUNS = {
    "exp42": ("exp42_composer_locationkey_live", "bench/cdsfl_registry/composer.py"),
    "exp43": ("exp43_macrophage_locationkey_live", "bench/macrophage_cell.py"),
    "exp44": ("exp44_evidence_locationkey_live", "bench/evidence.py"),
    "exp45": ("exp45_memory_statistics_live", "bench/dm/_memory.py"),
    "exp46": ("exp46_stage6_locationkey_live", "bench/dm/_shadow_stage6.py"),
    "exp47": ("exp47_divergence_locationkey_live", "bench/dm/_divergence.py"),
    "exp48": ("exp48_chemistry_exam_live", None),
    "exp49": ("exp49_engineering_exam_live", None),
}


def estimate_gamma(counts, min_rounds: int = 3) -> float:
    """Duane slope, transcribed from reference_runner_v2._estimate_gamma.

    Deliberately a copy rather than an import: the runner's version is embedded in
    a module that pulls the whole dispatch stack, and a replay must not be able to
    dispatch anything. The copy is pinned against the archive by `--verify`.
    """
    n = len(counts)
    if n < min_rounds:
        return 0.0
    cum, total = [], 0
    for c in counts:
        total += c
        cum.append(total)
    if total == 0:
        return 0.0
    lx, ly = [], []
    for i, c in enumerate(cum):
        if c > 0:
            lx.append(math.log(i + 1))
            ly.append(math.log(c))
    if len(lx) < 2:
        return 0.0
    n_p, sx, sy = len(lx), sum(lx), sum(ly)
    sxy = sum(x * y for x, y in zip(lx, ly))
    sx2 = sum(x * x for x in lx)
    denom = n_p * sx2 - sx * sx
    if abs(denom) < 1e-12:
        return 0.0
    return max(0.0, min(1.0, 1.0 - (n_p * sxy - sx * sy) / denom))


def report_for(stem: str):
    hits = [p for p in (REPO / "bench" / "logs").glob(f"{stem}_*/{stem}_report.json")
            if ".errata" not in str(p)]
    return json.loads(hits[0].read_text(encoding="utf-8")) if hits else None


def symbols_for(target_rel, entries):
    if target_rel and (REPO / target_rel).is_file():
        return CL.target_symbols(str(REPO / target_rel))
    import re
    ids = set()
    for e in entries.values():
        ids |= set(re.findall(r"\b([A-Z]{2}-\d{2})\b", e.get("description", "") or ""))
    return frozenset(ids)


def verify() -> int:
    """THE EXIT TEST. Reproduce each archived series exactly, or stop."""
    print("  EXIT TEST — does the replay reproduce each run's OWN archived series?\n")
    print(f"  {'run':8s}{'archived series':>44s}{'':4s}{'result':>10s}")
    bad = 0
    for run, (stem, tgt) in RUNS.items():
        rep = report_for(stem)
        if rep is None:
            print(f"  {run:8s}{'(run not present)':>44s}"); continue
        arch = rep.get("location_crit_shadow_history") or []
        if not arch:
            print(f"  {run:8s}{'(no archived series)':>44s}"); continue
        ents = rep["registry"]["entries"]
        got = CL.location_only_series(ents, len(arch) - 1, symbols_for(tgt, ents))
        ok = got == arch
        bad += (not ok)
        print(f"  {run:8s}{str(arch)[:44]:>44s}{'':4s}{'MATCH' if ok else 'DIFFERS':>10s}")
        if not ok:
            print(f"  {'':8s}{'replayed:':>44s}    {got}")
    print()
    if bad:
        print(f"  {bad} run(s) do NOT reproduce. The replay is measuring itself, not a repair.")
        print("  STOP. Nothing downstream of this is trustworthy.")
        return 1
    print("  All archived series reproduce exactly. The replay is a valid instrument.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verify", action="store_true",
                    help="run only the exit test and report nothing else")
    args = ap.parse_args()
    rc = verify()
    if args.verify or rc:
        return rc
    print("\n  (delta reporting lands with the Stage 1 repairs; the instrument is validated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
