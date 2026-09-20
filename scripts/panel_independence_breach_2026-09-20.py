#!/usr/bin/env python3
"""Did any panel seat read another seat's reply from the SAME round?

THE DEFECT. The 5 paid seats (cx, cgpt, ge, ds, kimi) are dispatched over HTTP
and have no working directory to confine, so `panel_sandbox` cannot place them
in a copy: the sandbox manifest for round 4 lists 2 sandboxes for 7 seats, both
belonging to the CLI seats. Their `run_python` is kernel-confined READ-ONLY
against the LIVE repository.

Read-only was thought sufficient. It is not, for a reason nobody stated: the
dispatcher writes each seat's reply into
`bench/logs/<round>/<seat>.json` AS THAT SEAT FINISHES, so the live tree
accumulates the current round's answers WHILE later seats are still working. A
seat that runs `grep -rn <term> bench` therefore sweeps its competitors'
in-progress answers into its own context.

MEASURED, round 4: seats finished at 117.4 s (cx), 223.3 s (cgpt), 279.2 s (ge),
378.7 s (ds) and 560.5 s (kimi). Any seat could read every seat that finished
before it.

WHY IT MATTERS. The founder's standing rule is that panel disagreement is
INFORMATION and must be preserved rather than smoothed. A seat that has read
another's answer is no longer an independent verdict, and convergence between
2 such seats is not corroboration. This project has already recorded the
sibling defect twice ("panel agents edit the repo mid-run").

Run:  python3 scripts/panel_independence_breach_2026-09-20.py [--round DIR]
"""
from __future__ import annotations

import argparse
import json
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEATS = ("cx", "cgpt", "ge", "ds", "kimi", "cc2", "fable")
WINDOW, STEP = 120, 40


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def coverage(needle: str, haystack: str) -> tuple[int, int]:
    """How much of `needle` appears verbatim in `haystack`, by sliding window."""
    wins = [needle[i:i + WINDOW] for i in range(0, max(0, len(needle) - WINDOW), STEP)]
    if not wins:
        return (0, 0)
    return (sum(1 for w in wins if w in haystack), len(wins))


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--round", default="bench/logs/maths_panel_2026-09-20_r4")
    a = ap.parse_args(argv)
    d = ROOT / a.round

    seats = {}
    for s in SEATS:
        f = d / f"{s}.json"
        if f.is_file():
            seats[s] = json.loads(f.read_text(errors="replace"))

    print(f"PANEL INDEPENDENCE, {a.round}")
    print("=" * 70)
    print("  finish order (a seat can only read those that finished BEFORE it):")
    for s, j in sorted(seats.items(), key=lambda kv: kv[1].get("elapsed_s") or 0):
        print(f"      {s:6s} {j.get('elapsed_s', 0):7.1f}s  route={j.get('route')}")
    print()

    breaches = []
    for reader, rj in seats.items():
        blob = json.dumps(rj.get("tool_calls") or [])
        if not blob or blob == "[]":
            continue
        for other, oj in seats.items():
            if other == reader:
                continue
            resp = oj.get("response") or ""
            if len(resp) < 400:
                continue
            k, n = coverage(resp, blob)
            # TWO FILTERS, BOTH FOUND BY P-PASSING THIS SCRIPT AGAINST ITSELF.
            #
            # (1) CAUSALITY. A seat cannot read a reply written after it
            #     finished. The first version reported "cx read cgpt" when cx
            #     finished at 117.4 s and cgpt at 223.3 s -- impossible, and the
            #     proof that single-window hits are coincidence.
            # (2) A SINGLE WINDOW IS NOT EVIDENCE. 120 characters of shared
            #     phrasing between 2 seats answering the SAME brief is expected;
            #     every impossible pair above matched exactly 1 window. Real
            #     contamination shows as a run of windows.
            if (oj.get("elapsed_s") or 0) >= (rj.get("elapsed_s") or 0):
                continue
            if k < 2:
                continue
            if k:
                lo, hi = wilson(k, n)
                breaches.append((reader, other, k, n, lo, hi))

    if not breaches:
        print("  No seat's tool output contains another seat's reply. CLEAN.")
    else:
        print("  *** BREACHES FOUND ***")
        for reader, other, k, n, lo, hi in breaches:
            print(f"      {reader} read {other}: {k} of {n} windows = {k/n:.4%}"
                  f"  Wilson [{lo:.4%}, {hi:.4%}]")
        print()
        print("  The vector, from the recorded tool calls:")
        for reader, other, *_ in breaches:
            for i, c in enumerate(seats[reader].get("tool_calls") or []):
                args = str(c.get("arguments") or "")
                if "bench" in args and ("grep" in args or "rglob" in args or "walk" in args):
                    print(f"      {reader} call {i}: {args[:150]}")
                    break
    print()
    print("-" * 70)
    print("THE FIX IS NOT MORE CONFINEMENT. Read-only is already enforced by the")
    print("kernel. The problem is WHAT IS READABLE: the current round's own")
    print("directory. Either write seat replies outside the tree the seats can")
    print("read until the round closes, or exclude the live round directory from")
    print("the paid seats' filesystem view. Both are changes to the harness, and")
    print("neither is in scope while the founder has said discuss-before-acting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
