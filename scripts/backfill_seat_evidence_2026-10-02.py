#!/usr/bin/env python3
"""Rescue the seat evidence that predates the preservation repair.

THE FOUNDER'S INSTRUCTION, 2026-10-02: *"Do this work while the suite runs and
you aren't busy doing anything else and decide what is and what is not worth
keeping."*

THE BACKLOG. `panel_sandbox.preserve_seat_evidence` has preserved a seat's work
since 2026-10-01, but rounds BEFORE it cannot be helped by it retroactively:
measured by `scripts/seat_evidence_is_gitignored_2026-09-30.py`, 46 of 281
harvested seat files are reachable from no clone at all.

THE DECISION, AND IT IS NOT TASTE. Every one of the 35 substantive files among
those 46 is CITED BY PATH in a committed document -- 0 uncited, checked with
`git grep` on the full path and falling back to the basename. A document citing
a path no clone can reach is the unrecoverable-citation defect this project
already ratchets on, so citation decides it rather than judgement. The remaining
11 are scratch and temp: 9 under `.scratch/`, which
`panel_sandbox._NO_PRESERVE_PARTS` already excludes, plus 1 duplicate listing
and 1 `mktemp` artefact. The founder's instruction was that scratch stays
unpreserved, and the mechanism already implements exactly that, so this script
adds no filter of its own.

PRESERVATION IS NOT ADOPTION, and the distinction is deliberate. 15 of the 35
are `bench/tests/test_*.py` that seats wrote and nobody adopted. This script
makes them REACHABLE. It does not put them on the collected root, where they
would run and might fail; that is a separate decision with a separate cost.

Run:  python3 scripts/backfill_seat_evidence_2026-10-02.py [--apply]
      (default is a dry run; nothing is written without --apply)
"""
from __future__ import annotations

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)


def harvest_dirs() -> list:
    """Every historical harvest attempt directory, oldest round first."""
    root = REPO / "bench" / "logs"
    if not root.is_dir():
        return []
    return sorted(root.glob("*/sandbox_harvest/*/attempt-*"))


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None)
    ap.add_argument("--apply", action="store_true",
                    help="write the rescued copies; default is a dry run")
    args = ap.parse_args()

    from panel_sandbox import preserve_seat_evidence

    dirs = harvest_dirs()
    print(f"harvest attempt directories: {len(dirs)}")
    if not args.apply:
        print("DRY RUN. Nothing is written. Re-run with --apply.")

    tot_pre = tot_skip = tot_known = tot_fail = 0
    touched = []
    for d in dirs:
        if not args.apply:
            # Count what WOULD be preserved without writing, using the
            # module's own filter so the dry run cannot disagree with the act.
            from panel_sandbox import _should_preserve
            fd = d / "files"
            if not fd.is_dir():
                continue
            would = [p.relative_to(fd).as_posix()
                     for p in sorted(fd.rglob("*")) if p.is_file()]
            pre = [r for r in would
                   if _should_preserve(r) and not (REPO / r).is_file()]
            tot_pre += len(pre)
            tot_skip += len(would) - len(pre)
            if pre:
                touched.append((d.parent.parent.parent.name, d.parent.name, len(pre)))
            continue
        man = preserve_seat_evidence(d, REPO)
        tot_pre += len(man["preserved"])
        tot_skip += len(man["skipped"])
        tot_known += len(man["already_tracked"])
        tot_fail += len(man["failed"])
        if man["preserved"]:
            touched.append((man["round"], man["seat"], len(man["preserved"])))
        for bad in man["failed"]:
            print(f"  FAILED {bad}")

    print(f"\n  would preserve / preserved : {tot_pre}")
    print(f"  skipped by the filter      : {tot_skip}  (.scratch, __pycache__, non .py/.md)")
    if args.apply:
        print(f"  already reachable          : {tot_known}")
        print(f"  failures                   : {tot_fail}")
    print("\n  by round and seat:")
    for rnd, seat, n in touched:
        print(f"    {rnd:<44} {seat:<8} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
