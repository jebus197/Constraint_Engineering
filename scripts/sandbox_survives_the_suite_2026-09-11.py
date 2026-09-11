#!/usr/bin/env python3
"""Task A13: does running the suite inside a panel sandbox destroy that sandbox?

THE REPORT. In panel round 4 the cc2 seat recorded that the sandbox's `bench/`
tree emptied WHILE it was working: at 03:32 a script ran to completion there, at
03:33 pytest over 3 files returned `95 passed in 1.30s`, and by 03:36 the same
command died at `reference_runner_v3.py:169` with `ModuleNotFoundError: No module
named 'dynamic_management'`, with `bench/*.py` holding 8 files against the
canonical tree's 167. The seat restored its own 2 writes, verified them
byte-identical with `diff -q`, and DECLINED TO ATTRIBUTE the removals. That is
the right way to report something you cannot pin down.

TWO CANDIDATE CAUSES, and they have different remedies.

  THE OTHER SEAT. Until 2026-09-11 every seat shared ONE writable sandbox and
  they ran concurrently, so a destructive action by the seat finishing first
  landed under the seat still working -- and fable returned at 03:36:19, the
  minute the tree emptied. That cause is now CLOSED: each seat gets its own
  sandbox (task A20).

  A TEST. This project has already had `rmtree(x.parent)` take 179 entries out
  of TMPDIR on 2026-09-07, so a test that cleans up too broadly is not a
  hypothesis, it is a recurrence. THAT CAUSE IS STILL OPEN, and it is the one
  this script settles, by the falsifier the entry itself names: build a sandbox,
  count, run the suite inside it, count again.

WHY THE COUNT IS TAKEN 3 TIMES. Before, after collection, and after the run. A
sandbox that empties during COLLECTION implicates an import-time side effect; one
that empties during the RUN implicates a test body. The entry's report cannot
distinguish them and neither could a 2-point measurement.

DO NOT RUN THIS CONCURRENTLY WITH A REAL PANEL. It builds a sandbox of its own
and it runs the whole suite inside it.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))


def census(root: pathlib.Path) -> dict:
    return {
        "bench/*.py": len(list((root / "bench").glob("*.py"))),
        "bench/**/*.py": len(list((root / "bench").rglob("*.py"))),
        "tracked-shaped files": sum(1 for p in root.rglob("*") if p.is_file()),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tests", default="bench/tests",
                    help="what to run inside the sandbox")
    ap.add_argument("--keep", action="store_true", help="do not tear down")
    a = ap.parse_args()

    import panel_sandbox

    canonical = census(REPO)
    print(f"canonical tree: {canonical}")
    sandbox = panel_sandbox.build(REPO)
    print(f"sandbox       : {sandbox}")
    before = census(sandbox)
    print(f"BEFORE        : {before}")
    assert before["bench/*.py"] > 100, (
        f"the sandbox was born short: {before}. Nothing downstream is "
        f"interpretable if the copy is already incomplete.")

    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "--collect-only", a.tests],
            cwd=sandbox, capture_output=True, text=True, timeout=1800)
        after_collect = census(sandbox)
        print(f"AFTER COLLECT : {after_collect}  (pytest exit {r.returncode})")

        r2 = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "--tb=no", a.tests],
            cwd=sandbox, capture_output=True, text=True, timeout=7200)
        after_run = census(sandbox)
        tail = [ln for ln in r2.stdout.splitlines()
                if "passed" in ln or "failed" in ln]
        print(f"AFTER RUN     : {after_run}  (pytest exit {r2.returncode})")
        print(f"  suite line  : {tail[-1] if tail else '(none)'}")

        lost_collect = before["bench/*.py"] - after_collect["bench/*.py"]
        lost_run = after_collect["bench/*.py"] - after_run["bench/*.py"]
        print(f"\nbench/*.py lost during COLLECTION: {lost_collect}")
        print(f"bench/*.py lost during the RUN   : {lost_run}")
        if lost_collect == 0 and lost_run == 0:
            print("\nTHE SANDBOX SURVIVES. The round-4 emptying is NOT reproduced "
                  "by running the\nsuite inside a sandbox, so a test cleaning up "
                  "too broadly is not supported as\nthe cause. The other "
                  "candidate -- the seat sharing the directory -- was closed on\n"
                  "2026-09-11 by giving every seat its own sandbox (task A20).")
        else:
            print("\n*** REPRODUCED. A test removes files from the sandbox it "
                  "runs in. ***")
        return 0
    finally:
        if not a.keep:
            panel_sandbox.teardown(sandbox)
            print(f"\ntorn down: {sandbox}")


if __name__ == "__main__":
    raise SystemExit(main())
