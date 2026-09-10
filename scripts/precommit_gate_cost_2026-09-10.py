#!/usr/bin/env python3
"""Task 1.1: what does the pre-commit documentation gate actually cost?

MEASURED, and committed alongside the figure (`measured-rate-travels-with-its-script`).

WHY A SCRIPT AND NOT A SENTENCE. Entry 1.1 quoted "28 tests in 1.26 s", which was
then corrected to "56 tests in 1.88 s", which was then corrected again -- and the
second correction was applied INSIDE the first, so the entry ended up reading
"56 tests in 1.88 s (CORRECTED: '56 tests in 1.88 s (CORRECTED: '28 tests in
1.26 s' never reproduced)' never reproduced)". A sentence that quotes itself as
the thing it is refuting is no longer a claim about anything. Three prose
corrections to one figure, and no instrument at any point.

A TIMING FIGURE IS NOT LIKE A COUNT, and this script treats it differently.
A count either reproduces or it does not. A wall-clock time depends on the
machine, on what else is running, and on filesystem cache state, so a single
number quoted to 2 decimal places implies a precision the measurement does not
have. This runs the gate REPEATEDLY and reports the median with the full range,
and it names the conditions. The test COUNT is exact and is reported as such.

The comparison figure -- the full suite -- is deliberately NOT re-measured here.
It takes over 11 minutes and re-running it on every invocation would make this
script something nobody runs, which is how the 6.2 instrument died.
"""
from __future__ import annotations

import argparse
import pathlib
import platform
import statistics
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "pre-commit"

#: The 4 files the gate runs. READ FROM THE HOOK, not typed here -- an instrument
#: that hardcodes the list cannot notice the hook's list changing, which is the
#: defect panel round 4 found in the watchdog script.
def gate_files() -> list[str]:
    """Parse the hook's `GUARDS=` assignment.

    NOT A TOKEN SCAN, and the first version was one. It split every line on
    whitespace and stripped quotes, which missed
    `test_documentation_drift_guards_2026-08-25.py` because that file sits on the
    assignment line itself as `GUARDS="bench/tests/...` -- the token carries the
    variable name. It reported 5 files where the hook names 6, and it would have
    produced a cost figure over the wrong set. Caught before the figure was
    believed, which is the only reason to run an instrument against a known case
    first.
    """
    src = HOOK.read_text(encoding="utf-8")
    start = src.index("GUARDS=")
    body = src[start + len("GUARDS="):]
    quote = body[0]
    if quote not in "\"'":
        raise SystemExit("the GUARDS assignment in hooks/pre-commit is not quoted; "
                         "this parser cannot find its end")
    body = body[1:body.index(quote, 1)]
    files = [ln.strip() for ln in body.splitlines() if ln.strip()]
    for f in files:
        if not f.startswith("bench/tests/test_") or not f.endswith(".py"):
            raise SystemExit(f"unexpected entry in the hook's GUARDS list: {f!r}")
    return files


def collected(files: list[str]) -> int:
    r = subprocess.run([sys.executable, "-m", "pytest", *files, "--co", "-q",
                        "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    for line in reversed(r.stdout.strip().splitlines()):
        if "test" in line and "collected" in line:
            return int(line.split()[0])
        if line.strip().endswith("tests collected") or "/" in line:
            continue
    # `-q --co` ends with "N tests collected in ...s"
    for line in reversed(r.stdout.strip().splitlines()):
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].startswith("test"):
            return int(parts[0])
    raise SystemExit(f"could not read a collection count from pytest:\n{r.stdout[-800:]}")


def time_once(files: list[str]) -> tuple[float, int]:
    t0 = time.perf_counter()
    r = subprocess.run([sys.executable, "-m", "pytest", *files, "-q",
                        "-p", "no:cacheprovider", "--netguard-strict"],
                       cwd=REPO, capture_output=True, text=True, timeout=1800)
    return time.perf_counter() - t0, r.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repeats", type=int, default=5,
                    help="how many timed runs (default 5; 1 gives no range)")
    a = ap.parse_args()

    files = gate_files()
    if not files:
        raise SystemExit("no test files found in hooks/pre-commit — the gate's "
                         "file list has moved and this script cannot see it")
    print(f"gate files, read from hooks/pre-commit ({len(files)}):")
    for f in files:
        exists = (REPO / f).is_file()
        print(f"    {f}{'' if exists else '   <-- MISSING'}")
        if not exists:
            raise SystemExit(f"the hook names {f} and it does not exist")

    n = collected(files)
    print(f"\ntests collected: {n}   (exact — a count, not a timing)")

    times, codes = [], []
    for i in range(max(1, a.repeats)):
        el, rc = time_once(files)
        times.append(el)
        codes.append(rc)
        print(f"  run {i + 1}: {el:.2f} s   exit {rc}")

    if any(c != 0 for c in codes):
        print(f"\n  *** THE GATE IS RED: exit codes {codes}. The cost figure below "
              f"is the cost of a FAILING gate. ***")

    med = statistics.median(times)
    print(f"\nwall clock over {len(times)} run(s), including interpreter start:")
    print(f"    median : {med:.2f} s")
    print(f"    range  : {min(times):.2f} s to {max(times):.2f} s")
    if len(times) > 1:
        print(f"    spread : {max(times) - min(times):.2f} s "
              f"({(max(times) - min(times)) / med:.0%} of the median)")
    print(f"\nconditions: {platform.platform()}, Python "
          f"{sys.version.split()[0]}, cwd {REPO}")
    print("A wall-clock figure is a property of this machine under this load, not "
          "of the gate.\nQuote it with the conditions or not at all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
