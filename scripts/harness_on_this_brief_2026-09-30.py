#!/usr/bin/env python3
"""Q5: what the CDSFL harness actually does when the target is THIS BRIEF.

Run from the repository root:

    python3 scripts/harness_on_this_brief_2026-09-30.py

The brief asks what the harness does on a prose-heavy problem carrying
unstated computable elements, and names itself as one such problem. The real
dispatched brief is on disk at
`bench/logs/intelligence_first_2026-09-30/BRIEF.md`, so this drives the live
instruments over the actual bytes rather than a paraphrase.

Nothing is dispatched and nothing is written.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

TARGETS = [
    ("this brief", "bench/logs/intelligence_first_2026-09-30/BRIEF.md"),
    ("the A19 calculator brief", "bench/logs/a19_calculator_design_2026-09-30/BRIEF.md"),
    ("a corpus fixture (STEM, fenced)", "bench/tests/fixtures/stem/docs/NUM-05-REF-01.md"),
]


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Drives the live target-classification, reducibility and "
                    "S_k instruments over real briefs. Writes nothing.")
    ap.parse_args(argv)

    from reference_runner_v3 import (
        _gateable_source, _gateable_hunks, compute_sk, resolve_target_kind)
    from input_complexity import compute_gamma_input

    for label, rel in TARGETS:
        p = REPO / rel
        print(f"\n=== {label}")
        print(f"    {rel}")
        if not p.is_file():
            print("    ABSENT in this sandbox — skipped")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        kind, why = resolve_target_kind(str(p), text)
        red, red_why = _gateable_source(text, str(p))
        hunks = _gateable_hunks(text, str(p))
        r_off = compute_sk(fix_text="", source=text, source_path=str(p),
                           score_prose_listings=False)
        r_on = compute_sk(fix_text="", source=text, source_path=str(p),
                          score_prose_listings=True)
        # THE RUNNER'S RETRY, reference_runner_v3.py:15185-15196, NOT the
        # naive call. An earlier draft of this script omitted it and reported
        # gamma_input = 0.500000 for every target -- the ASSUMED_DEFAULT
        # returned when n_windows < MIN_WINDOWS, not a measurement. That figure
        # was wrong and is recorded here as wrong. See
        # scripts/target_complexity_is_a_constant_2026-09-30.py.
        from input_complexity import (
            WINDOW_SIZE_CHARS as _W, MIN_WINDOWS as _MW, tokenize as _tok)
        cx = compute_gamma_input(text)
        _nt = len(_tok(text))
        if cx.n_windows < _MW and _nt >= _MW * 4:
            cx = compute_gamma_input(text, window_size=max(4, (4 * _nt) // (_MW * 2)))
        print(f"    chars                 {len(text)}")
        print(f"    resolve_target_kind   {kind}  ({why})")
        print(f"    reducible             {red is not None}  ({red_why})")
        print(f"    fenced listings       {len(hunks)}")
        print(f"    S_k  flag OFF         {r_off.tristate}")
        print(f"    S_k  flag ON          {r_on.tristate}")
        print(f"    gamma_input           {cx.gamma:.6f}  beta={cx.beta:.6f} "
              f"r2={cx.r_squared:.6f} n_windows={cx.n_windows}")

    print("\n--- what this shows -------------------------------------------")
    print("The harness classifies a panel brief as `prose`, and S_k returns")
    print("NO_SCORE on it whichever way the A19 flag is set. That is the")
    print("CORRECT answer and not a defect: S_k scores a proposed FIX against")
    print("a target, and no fix was offered. What the harness has no")
    print("instrument for at all is the question the brief is really asking --")
    print("'which sentences in here are decidable?' -- because no live")
    print("component takes a CLAIM as its unit. The reducibility check above")
    print("answers 'does this file contain Python', which is a different")
    print("question that happens to correlate on the fixture corpus and not")
    print("at all on a brief.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
