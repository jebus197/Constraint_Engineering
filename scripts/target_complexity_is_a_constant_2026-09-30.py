#!/usr/bin/env python3
"""FALSIFIER for Q6(c): is `target_complexity.gamma_input` a MEASUREMENT on a
real target, or a hard-coded default?

Run from the repository root:

    python3 scripts/target_complexity_is_a_constant_2026-09-30.py

WHY IT MATTERS. The founder's alternative to the unreproducible `n*` is to
compute the round count from TARGET COMPLEXITY before a run, and the brief
notes that `target_complexity` is already recorded in every report carrying
`gamma_input`, `beta`, `r_squared`, `n_windows`, `target_chars`. A quantity can
only carry a round count if it VARIES with the target.

`input_complexity.compute_gamma_input` returns `beta=0.5, gamma=1-beta=0.5`
whenever `n_windows < MIN_WINDOWS` (input_complexity.py:232), and the runner
records that as `fit="ASSUMED_DEFAULT"`. The runner ALSO retries with a
shrunken window (reference_runner_v3.py:15185-15196) because this repository
runs ~14:1 chars-per-token while `input_complexity` assumes 4:1. This script
reproduces BOTH the naive call and the runner's retry, so the number reported
is the one the runner would actually record.

THE CLAIM UNDER TEST: `gamma_input` as recorded discriminates between targets.
FALSIFIED (AssertionError) iff it is constant across targets of very different
character, i.e. it is a default and not a measurement.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

CANDIDATES = [
    ("this brief", "bench/logs/intelligence_first_2026-09-30/BRIEF.md"),
    ("A19 calculator brief", "bench/logs/a19_calculator_design_2026-09-30/BRIEF.md"),
    ("corpus fixture NUM-05", "bench/tests/fixtures/stem/docs/NUM-05-REF-01.md"),
    ("corpus fixture ALG-02", "bench/tests/fixtures/stem/docs/ALG-02-REF-01.md"),
    ("GLOSSARY", "docs/GLOSSARY.md"),
    ("EXTENDED_RATIONALE", "docs/EXTENDED_RATIONALE.md"),
    ("PAPER", "PAPER.md"),
    ("the runner itself (.py)", "bench/reference_runner_v3.py"),
    ("bugzilla_loop (.py)", "bench/bugzilla_loop.py"),
]


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Measures whether gamma_input varies across targets. "
                    "Writes nothing.")
    ap.parse_args(argv)

    from input_complexity import (
        compute_gamma_input, WINDOW_SIZE_CHARS, MIN_WINDOWS, tokenize as _tok)

    print(f"input_complexity: WINDOW_SIZE_CHARS={WINDOW_SIZE_CHARS} "
          f"MIN_WINDOWS={MIN_WINDOWS}\n")
    print(f"{'target':24s} {'chars':>8s} {'tok':>7s} "
          f"{'naive g':>9s} {'nw':>3s} | {'retry g':>9s} {'nw':>3s} {'fit':>16s}")
    print("-" * 92)

    as_recorded = []
    for label, rel in CANDIDATES:
        p = REPO / rel
        if not p.is_file():
            print(f"{label:24s}  ABSENT")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        cx = compute_gamma_input(text)
        n_tokens = len(_tok(text))
        # The runner's retry, reference_runner_v3.py:15185-15196.
        win = WINDOW_SIZE_CHARS
        cx2 = cx
        if cx.n_windows < MIN_WINDOWS and n_tokens >= MIN_WINDOWS * 4:
            win = max(4, (4 * n_tokens) // (MIN_WINDOWS * 2))
            cx2 = compute_gamma_input(text, window_size=win)
        fit = ("measured" if cx2.n_windows >= MIN_WINDOWS
               else "NO_TOKENS" if cx2.n_windows == 0 else "ASSUMED_DEFAULT")
        as_recorded.append((label, round(cx2.gamma, 6), fit))
        print(f"{label:24s} {len(text):8d} {n_tokens:7d} "
              f"{cx.gamma:9.6f} {cx.n_windows:3d} | "
              f"{cx2.gamma:9.6f} {cx2.n_windows:3d} {fit:>16s}")

    print("-" * 92)
    naive_default = sum(1 for _, g, f in as_recorded if f == "ASSUMED_DEFAULT")
    distinct = sorted({g for _, g, _ in as_recorded})
    print(f"targets measured            {len(as_recorded)}")
    print(f"recorded as ASSUMED_DEFAULT {naive_default}")
    print(f"distinct gamma values       {len(distinct)}  {distinct[:8]}")

    # Second, independent tool on the same numbers: variance and range.
    import statistics as st
    import numpy as np
    vals = [g for _, g, _ in as_recorded]
    print(f"stdlib  variance {st.pvariance(vals):.8f}  range "
          f"{max(vals)-min(vals):.6f}")
    print(f"numpy   variance {float(np.var(vals)):.8f}  range "
          f"{float(np.ptp(vals)):.6f}")

    if len(distinct) <= 1:
        print("\nFALSIFIED")
        raise AssertionError(
            f"gamma_input took {len(distinct)} distinct value(s) across "
            f"{len(as_recorded)} targets spanning "
            f"{min(len(open(REPO/r).read()) for _, r in CANDIDATES if (REPO/r).is_file())}"
            f"..{max(len(open(REPO/r).read()) for _, r in CANDIDATES if (REPO/r).is_file())}"
            f" chars. A constant cannot carry a round count.")

    print("\nNOT FALSIFIED: gamma_input varies across targets, so it is a "
          "measurement and could in principle carry a round count. Whether it "
          "SHOULD is a separate question this script does not answer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
