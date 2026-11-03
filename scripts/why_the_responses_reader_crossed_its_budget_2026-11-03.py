#!/usr/bin/env python3
"""Why did the responses reader cross a 300 s budget on 2026-11-03?

THE FAILURE. 2 guards in the commit gate's cheap-guard list shell out to
`scripts/read_founder_responses_2026-10-11.py` with `--since <date> --json`.
Both passed at 11:20 and 11:38 and both TIMED OUT at 11:51 and 11:59, refusing a
commit whose own 5 files neither test references.

★ 4 SINGLE-CAUSE EXPLANATIONS WERE GIVEN TO THE FOUNDER AND ALL 4 WERE REFUTED
BY MEASUREMENT. They are recorded because the pattern matters more than any of
them: each was reported at the moment it was formed rather than after it was
tested.

  1. CPU CONTENTION, from running other work during the board. REFUTED: the
     test times out with nothing else running, on an idle machine verified with
     a pattern that can see the reader process.
  2. AN OUTGROWN GUARD AT 97% OF BUDGET, from "291.48 s against 300 s".
     REFUTED: that figure was the CPU of a process KILLED AT 300 s, so it could
     not exceed the budget by construction. A truncated measurement was read as
     a cost. The true cost is 684.25 s, which is 2.280833 budgets.
  3. AN 11 MB FILE, BY DECODE COST. REFUTED: `read_any` on it takes 0.92 s.
  4. THE SAME FILE, BY ANNOTATION EXTRACTION. REFUTED: `_annotations_in` on it
     takes 0.93 s, and all 114 response files project to about 6 s.

THE ACTUAL CAUSE NEEDS 2 CONDITIONS AND NEITHER SUFFICES, WHICH IS WHY EVERY
SINGLE-CAUSE STORY FAILED.

  A. `context_for` RE-READS THE WHOLE FILE ONCE PER ANNOTATION. `main()` runs
     that loop whenever `--context > 0`, and the default is 6. The cost is
     therefore O(annotations in a file x size of that file), and it has always
     been there.
  B. A FILE OF 11,076,291 BYTES ENTERED `Responses/` AT 11:45:13, carrying 780
     annotations. Before it, the largest response file was about 83 KB, so the
     quadratic term was invisible.

So the loop re-reads about 8.6 GB for that 1 file. `annotations()` ALONE, which
does not call `context_for`, completes in 3.674 s -- so the library path is fast
and only the CLI path is slow, which is what the 2 guards invoke.

HOW THIS SCRIPT STAYS CHEAP AND STILL FALSIFIABLE. Re-running the CLI costs
about 684 s, so that 1 figure is PINNED from a completed run (exit 0, measured
to completion, not killed) and everything else is measured live in a few
seconds. The script REFUSES if the live projection fails to account for the
pinned wall time, so a future change that fixes the quadratic read makes it go
red rather than silently agreeing.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import time

REPO = pathlib.Path(__file__).resolve()
while REPO.name != "Constraint_Engineering" and REPO.parent != REPO:
    REPO = REPO.parent
if REPO.name != "Constraint_Engineering":
    REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"

#: Measured to COMPLETION on an idle machine, exit 0, 2026-11-03 12:32 GMT:
#: `--since 2026-11-01 --json` = 684.25 s and `--since 2026-10-01 --json` =
#: 687.04 s. The ratio 1.0041 is why the `--since` window is NOT the driver.
PINNED_CLI_WALL = 684.25
PINNED_BUDGET = 300.0

#: Samples per group. Small deliberately: the point is the ORDER of magnitude
#: between the 2 groups, and a bigger sample would cost minutes to sharpen a
#: figure whose conclusion does not turn on its third digit.
N_BIG, N_OTHER = 5, 20


def main() -> int:
    argparse.ArgumentParser(
        description=("Measure why the responses reader crossed its 300 s "
                     "budget: a per-annotation whole-file re-read meeting an "
                     "11 MB response file.")).parse_args()

    spec = importlib.util.spec_from_file_location(
        "rd", REPO / "scripts" / "read_founder_responses_2026-10-11.py")
    rd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rd)

    print("=" * 78)
    print("WHY THE RESPONSES READER CROSSED A 300 SECOND BUDGET")
    print("=" * 78)

    t0 = time.perf_counter()
    anns = rd.annotations()
    dt_ann = time.perf_counter() - t0
    print(f"\n  annotations() alone        : {dt_ann:7.3f} s for {len(anns)} rows")
    print(f"  the CLI with --json        : {PINNED_CLI_WALL:7.2f} s  [PINNED]")
    print(f"  so the CLI-only work is    : {PINNED_CLI_WALL - dt_ann:7.2f} s")

    sizes = {p.name: p.stat().st_size
             for p in (REPO.parent / "Responses").iterdir() if p.is_file()}
    if not sizes:
        print("  REFUSED: the Responses folder is unreadable here.")
        return 1
    biggest = max(sizes, key=sizes.get)
    tot = sum(sizes.values())
    print(f"\n  largest response file      : {sizes[biggest] / 1e6:.2f} MB, "
          f"{sizes[biggest] / tot:.6f} of {tot / 1e6:.2f} MB across {len(sizes)}")
    print(f"    {biggest[:66]}")

    from_big = [a for a in anns if a["file"] == biggest]
    others = [a for a in anns if a["file"] != biggest]
    if not from_big or not others:
        print("  REFUSED: cannot split annotations by file, so no comparison.")
        return 1
    print(f"  annotations in it          : {len(from_big)} of {len(anns)}")

    def per_call(rows, n):
        s = time.perf_counter()
        for a in rows[:n]:
            rd.context_for(a, before=6)
        return (time.perf_counter() - s) / max(1, len(rows[:n]))

    pc_big = per_call(from_big, N_BIG)
    pc_oth = per_call(others, N_OTHER)
    print(f"\n  context_for per call, that file : {pc_big:.4f} s")
    print(f"  context_for per call, the others: {pc_oth:.4f} s")
    print(f"  ratio                           : {pc_big / pc_oth:.1f}x")

    proj = pc_big * len(from_big) + pc_oth * len(others)
    share = proj / PINNED_CLI_WALL
    print(f"\n  projected context loop     : {proj:7.1f} s")
    print(f"    the big file's part       : {pc_big * len(from_big):7.1f} s")
    print(f"  accounts for               : {share:.1%} of the pinned wall")
    print(f"  budget it must fit inside  : {PINNED_BUDGET:7.1f} s "
          f"({PINNED_CLI_WALL / PINNED_BUDGET:.6f} budgets needed)")

    #: THE REFUSAL. If the loop no longer accounts for the pinned wall, either
    #: the quadratic read was fixed or the corpus changed, and in both cases this
    #: script's central claim is stale rather than confirmed.
    if not (0.6 <= share <= 1.6):
        print(f"\n  REFUSED: the context loop accounts for {share:.1%} of the "
              f"pinned {PINNED_CLI_WALL} s, outside [60%, 160%]. Either the "
              f"per-annotation re-read is gone or the corpus changed; re-pin "
              f"the wall time before trusting anything above.")
        return 1

    print("\n  SO: the loop accounts for the whole gap, and it needs BOTH the")
    print("  per-annotation whole-file re-read AND a response file large enough")
    print("  to make it visible. Neither alone produces the failure, which is")
    print("  why 4 single-cause explanations were each refuted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
