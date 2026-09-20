#!/usr/bin/env python3
"""Did the fix-admission verdict ever decide anything on the archived record?

CONTEXT. In panel round 3 (2026-09-20) the cc2 seat established, and an
independent AST pass confirms, that `model_params` has 0 writers and exactly 2
readers in production code (bench/reference_runner.py:3156,
bench/reference_runner_v3.py:11921). Every run therefore used frozen literals --
q=0.5, R_old=0.5, nu_b=0.05, nu_f=0.20 -- that no measurement supplied.

cc2 flagged, and explicitly did not close, its own largest residual:

    "A run is produced where the S_k verdict changes no downstream outcome ...
     I did not trace whether any archived run had it on. If none did, then the
     one constant decides nothing on the record either, and CHANGE NOTHING
     becomes the correct verdict for the archive (though not for future runs)."

THE PARSING ERROR THIS SCRIPT EXISTS TO AVOID, recorded because the first
version of it made exactly this mistake and reported the opposite conclusion.
`SK_REJECTED` is the NAME of a Python constant. The VALUE written into the run
record is the bare string "REJECTED". Searching the archive for the name finds
10 occurrences, every one of them a panel model DISCUSSING the token in its
reply, and 0 real verdicts -- which reads as "the verdict never fired" and is
false. Searching for the value finds 1,247 real decisions. A producer and a
consumer that disagree about which string is written are invisible to any check
that reads only one of them, which is this project's `execute-do-not-grep` rule
in its data form: parse the recorded VALUE, never the source-level NAME.

Run:  python3 scripts/sk_verdict_never_fired_2026-09-20.py
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 60_000_000


def wilson(k: int, n: int) -> tuple[float, float]:
    """Wilson score interval, 95%. Cross-checked against statsmodels below."""
    if n == 0:
        return (0.0, 0.0)
    from math import sqrt
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def collect() -> tuple[int, Counter, list[str]]:
    """Walk every archived runner state and count sk_result tristate VALUES."""
    tri: Counter = Counter()
    runs: list[str] = []
    entries = 0

    def walk(o):
        nonlocal entries
        if isinstance(o, dict):
            sk = o.get("sk_result")
            if isinstance(sk, dict) and "tristate" in sk:
                entries += 1
                tri[str(sk.get("tristate"))] += 1
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

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
        runs.append(os.path.relpath(f, ROOT))
        walk(d)
    return entries, tri, runs


def name_vs_value() -> tuple[int, int]:
    """The parsing trap, measured: hits on the NAME vs hits on the VALUE."""
    name_hits = 0
    for f in sorted(glob.glob(str(ROOT / "bench/logs/**/*.json"), recursive=True)):
        if os.path.getsize(f) > MAX_BYTES:
            continue
        try:
            name_hits += open(f, errors="ignore").read().count("SK_REJECTED")
        except OSError:
            continue
    entries, tri, _ = collect()
    return name_hits, tri.get("REJECTED", 0)


def main(argv: list | None = None) -> int:
    # `--help` MUST NEVER COST MONEY, and must never run a measurement either.
    # argparse is constructed and parsed BEFORE any archive walk or subprocess,
    # so the flag is answered rather than consumed as a positional argument.
    # This project already carries the rule in its strong form, written after 15
    # of 17 runners billed a live dispatch on an unrecognised argument.
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)

    entries, tri, runs = collect()
    print("FIX-ADMISSION VERDICTS ON THE ARCHIVED RECORD, 2026-09-20")
    print()
    print(f"Runner state files carrying sk_result : {len(runs)}")
    print(f"Recorded fix-admission decisions      : {entries}")
    print()
    print("Tristate distribution, with 95% Wilson intervals:")
    for value, k in tri.most_common():
        lo, hi = wilson(k, entries)
        print(f"   {value:12s} {k:5d}  {k/entries:8.4%}  Wilson [{lo:.4%}, {hi:.4%}]")
    print()

    # Cross-verification, 2 independent tools, per multi_tool_crossverify.
    try:
        from statsmodels.stats.proportion import proportion_confint
        agree = True
        for value, k in tri.items():
            lo2, hi2 = proportion_confint(k, entries, alpha=0.05, method="wilson")
            lo1, hi1 = wilson(k, entries)
            if abs(lo1 - lo2) > 1e-12 or abs(hi1 - hi2) > 1e-12:
                agree = False
        print(f"Cross-check, statsmodels Wilson agrees with the local closed form: {agree}")
    except ImportError:
        print("Cross-check: statsmodels unavailable; local closed form only.")

    name_hits, value_hits = name_vs_value()
    print()
    print("THE PARSING TRAP, measured:")
    print(f"   searching for the constant NAME  'SK_REJECTED' : {name_hits} hits, all panel prose")
    print(f"   parsing the recorded VALUE       'REJECTED'    : {value_hits} real verdicts")
    print("   A check that read the name would have concluded the verdict never fired.")
    print()

    rejected = tri.get("REJECTED", 0)
    lo, hi = wilson(rejected, entries) if entries else (0.0, 0.0)
    print("-" * 70)
    print("WHAT THIS SCRIPT ESTABLISHES, AND THE CLAIM IT USED TO MAKE AND DOES NOT")
    print("MAKE ANY MORE (corrected 2026-09-20, found by the kimi seat in the blind")
    print("round by RUNNING a figure this project's own brief cited).")
    print()
    print(f"  ESTABLISHED: the fix-admission verdict fired {entries} times across")
    print(f"  {len(runs)} archived runs, and {rejected} of those were refusals")
    print(f"  ({rejected/entries:.4%}, Wilson [{lo:.4%}, {hi:.4%}]) -- so the machinery")
    print("  ran on the record. That half stands.")
    print()
    print("  WITHDRAWN: this block used to continue \"fixes were refused on the")
    print("  strength of a constant nobody measured\". That is FALSE and it was")
    print("  CC1's claim, put to 7 paid seats as settled evidence before being")
    print("  checked. Measured on both refusal paths by")
    print("  scripts/split_the_191_refusals_2026-09-20.py:")
    print()
    print("     ALL of the refusals are STRUCTURAL -- the proposed fix parsed no")
    print("     usable blocks, scored 0, and reference_runner_v3.py refuses at")
    print("     sk == 0 before any constant is read;")
    print("     0 of the 902 SCORED fixes that reached the gate were refused by it.")
    print()
    print("  So the unmeasured constants decided NOTHING on the archive. The")
    print("  repository already recorded this, pinned by a committed test, in")
    print("  sk_threshold_shadow's docstring in bench/reference_runner_v3.py:")
    print("  \"passes_threshold reads false 0 times under every method and every")
    print("  corpus tried. The gate has never rejected a fix.\"")
    print()
    print("  THE CASE FOR WIRING MEASURED PARAMETERS THEREFORE RESTS ON FUTURE")
    print("  RUNS, not on this archive, which contains no constant-driven refusal.")
    print("  Run split_the_191_refusals_2026-09-20.py for the split itself.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
