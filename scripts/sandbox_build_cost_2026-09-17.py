#!/usr/bin/env python3
"""What 1 panel sandbox costs to build: wall time and size on disk.

PANEL ROUND 16, 2026-09-17. `bench/confer_maths_panel_2026-09-05.py` justifies 1
sandbox per seat with "6.53 s and 606 MB per copy on this machine", and the same
figure sits in `bench/tests/test_panel_seats_are_independent_2026-09-11.py`. No
script produced it. This times `panel_sandbox.build(repo)`, measures the copy,
tears it down, and checks that the teardown removed it.

WHAT THE FIGURE DEPENDS ON, so 2 runs are not compared blindly. `build` copies
the WHOLE working directory, ignored and untracked files included (only `.git` is
excluded), so the size tracks whatever the checkout holds on the day: run logs
under bench/logs/, caches, and any worktrees nested inside it. On APFS `cp -Rc`
clones, so the wall time is mostly metadata and `du` reports the blocks the copy
would own if its source were deleted, not new blocks written.

It builds real copies under the system temp directory and removes them. It sends
nothing anywhere.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _apparent_bytes(root: Path) -> int:
    total = 0
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            try:
                total += os.lstat(os.path.join(dirpath, f)).st_size
            except OSError:
                pass
    return total


def _du_kib(root: Path) -> int | None:
    r = subprocess.run(["du", "-sk", str(root)], capture_output=True, text=True)
    try:
        return int(r.stdout.split()[0])
    except (IndexError, ValueError):
        return None


def measure(repo: Path, runs: int = 1) -> list[dict]:
    sys.path.insert(0, str(REPO / "bench"))
    import panel_sandbox

    rows = []
    for _ in range(runs):
        t0 = time.monotonic()
        sandbox = panel_sandbox.build(repo)
        elapsed = time.monotonic() - t0
        try:
            du = _du_kib(sandbox)
            apparent = _apparent_bytes(sandbox)
        finally:
            panel_sandbox.teardown(sandbox)
        rows.append({"seconds": elapsed, "du_kib": du, "apparent_bytes": apparent,
                     "sandbox": str(sandbox), "removed": not sandbox.parent.exists()})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", type=Path, default=REPO,
                    help="tree to copy (default: this repository's working directory)")
    ap.add_argument("--runs", type=int, default=1, help="builds to time (default 1)")
    a = ap.parse_args()
    if not a.repo.is_dir():
        print(f"REFUSING: {a.repo} is not a directory", file=sys.stderr)
        return 2
    if a.runs < 1:
        print("REFUSING: --runs must be at least 1", file=sys.stderr)
        return 2
    rows = measure(a.repo.resolve(), a.runs)
    print(f"repo copied : {a.repo.resolve()}")
    for i, r in enumerate(rows, 1):
        du = f"{r['du_kib'] / 1024:.1f} MiB" if r["du_kib"] is not None else "unknown"
        print(f"build {i}     : {r['seconds']:.2f} s, du {du}, apparent "
              f"{r['apparent_bytes'] / 1_000_000:.1f} MB, torn down: {r['removed']}")
    if not all(r["removed"] for r in rows):
        print("*** A SANDBOX WAS NOT REMOVED; inspect the system temp directory. ***",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
