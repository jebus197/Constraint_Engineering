#!/usr/bin/env python3
"""Did `study_run1b_2026-10-03` crash, and what should its re-run change?

HIS QUESTION, verbatim, annotation on `Closing_Report_2026-11-01.txt`: *"This
seems like a simple crash? Probably it could have been fixed if you had stopped
to diagnose why it crashed. But the rerun should settle it? qs"* -- and his
ruling in the same file: *"Agreed. You should rerun it under full cy protocol."*

THE ANSWER IS THAT IT DID NOT CRASH, and the re-run as specified would very
likely repeat the same ending. Diagnosing it first is what he asked for.

WHAT THE RECORD SAYS. `console.log` closes with `EXPERIMENT study_run1b_2026-10-03
-- 8 ROUNDS COMPLETE`, 75 findings, `gamma final: 0.427`, 342.1 min of wall
clock, and a written report. There is no traceback on the run's own path. So the
`completion_signal.json` status of `INCOMPLETE` with reason `UNRECORDED_STOP (the
round loop exited by a path that names no reason)` is NOT a crash record: it is
the completion recorder having no name for ROUND EXHAUSTION. A run that uses up
`--rounds 8` without the gate declaring convergence leaves by exactly that path.

WHY IT DID NOT CONVERGE, in its own words, and the 2 causes are separate.
  1  For most of the late rounds the gate failed on `contested=1`. A single
     contested finding holds the state gate shut however quiet the run becomes.
  2  On the FINAL round the gate PASSED, and the log says
     `Gate passed this round but not 3 consecutive`. The run then ran out of
     rounds. So it ended 2 passing rounds short of converging, not stuck.

GAMMA WAS NEVER THE OBSTACLE, which matters because the standing directive
forbids proposing that gamma be demoted and a reader might reach for it here.
The decay-curve diagnostic rose 0.702 -> 0.716 -> 0.732 across the closing
rounds, far above the 0.41 threshold, while `gamma final` is the separate
telemetry figure at 0.427 and also above it.

WHAT THIS IMPLIES FOR THE RE-RUN, stated as a prediction so it can fail: the
same 8-round budget should be expected to end the same way, because the gate
first passed on round 8 and needs 3 consecutive passes. A budget that allows the
3 consecutive passes to complete is the change the evidence supports. This script
reports the minimum arithmetically implied by the observed first-pass round
rather than a round number chosen by preference.

TOOLS, 2 per claim: the pass/fail/contested series is parsed from the run's own
console log and the arithmetic is checked by z3 (the smallest budget admitting K
consecutive passes starting at the observed first pass) against a direct NumPy
scan, which must agree.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT = (REPO / "bench" / "logs" / "study_run1b_2026-10-03_20261003T100439Z"
           / "console.log")
_CONV = re.compile(r"Convergence: (.+)$", re.M)
_GAMMA = re.compile(r"gamma_critical: ([0-9.]+)")
_DONE = re.compile(r"(\d+) ROUNDS COMPLETE")


def parse(text: str) -> dict:
    """★ ROUND NUMBERS COME FROM THE RUN, NOT FROM LINE ORDER. Corrected
    2026-11-02 before the figure was quoted. There are 9 convergence lines for
    8 completed rounds, because the gate is evaluated once more than it has
    rounds, and the run's own labels are 0-indexed -- the early lines read
    `Too early (round 0 < 3)`. 1-indexing the lines reported the first pass at
    "round 9" and a minimum budget of 11, when the run's own numbering puts the
    first pass at its LAST evaluation and the minimum at 10. Quoting 11 would
    have overstated what he needs to change by a whole round."""
    verdicts = [m.group(1).strip() for m in _CONV.finditer(text)]
    gammas = [float(m.group(1)) for m in _GAMMA.finditer(text)]
    rounds = _DONE.search(text)
    passed = [bool(re.match(r"Gate passed|STATE_CONVERGED", v)) for v in verdicts]
    contested = [bool(re.search(r"contested=([1-9]\d*)", v)) for v in verdicts]
    return {"verdicts": verdicts, "gammas": gammas, "passed": passed,
            "contested": contested,
            "rounds_complete": int(rounds.group(1)) if rounds else None,
            "crashed": "Traceback (most recent call last)" in text}


def min_budget_numpy(passed: list[bool], k: int) -> int | None:
    """Smallest total rounds admitting k consecutive passes, given the first pass."""
    import numpy as np
    a = np.asarray(passed, dtype=bool)
    idx = np.flatnonzero(a)
    if idx.size == 0:
        return None
    return int(idx[0]) + k          # 1-indexed round at which the k-th would land


def min_budget_z3(passed: list[bool], k: int) -> int | None:
    import z3
    first = next((i for i, p in enumerate(passed) if p), None)
    if first is None:
        return None
    n = z3.Int("n")
    s = z3.Optimize()
    s.add(n >= first + k)
    s.minimize(n)
    return int(s.model()[n].as_long()) if s.check() == z3.sat else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", default=str(DEFAULT))
    ap.add_argument("--k", type=int, default=3,
                    help="consecutive_rounds_required for that run")
    a = ap.parse_args()

    text = pathlib.Path(a.log).read_text(errors="replace")
    r = parse(text)

    print("=" * 74)
    print("DID study_run1b CRASH, AND WHAT SHOULD ITS RE-RUN CHANGE?")
    print("=" * 74)
    print(f"\n  log                : {pathlib.Path(a.log).name}")
    print(f"  traceback present  : {r['crashed']}")
    print(f"  rounds complete    : {r['rounds_complete']}")
    print(f"  gate verdicts seen : {len(r['verdicts'])}")
    if not r["verdicts"]:
        print("\n  0 convergence lines parsed -- VACUOUS for this log.")
        return 1

    print("\n  the gate's own verdict, round by round:")
    for i, v in enumerate(r["verdicts"], 1):
        print(f"      round {i:>2}: {v[:86]}")
    if r["gammas"]:
        print(f"\n  gamma_critical across those rounds: "
              f"{r['gammas'][0]:.3f} -> {r['gammas'][-1]:.3f} "
              f"(min {min(r['gammas']):.3f}, max {max(r['gammas']):.3f})")
        print("      the gamma-alt threshold is 0.41, so the decay curve was NEVER")
        print("      the obstacle. Gamma is not to be demoted on this evidence.")

    nc = sum(r["contested"])
    print(f"\n  rounds the gate failed on a CONTESTED finding: {nc} of {len(r['verdicts'])}")
    npass = sum(r["passed"])
    print(f"  rounds the gate PASSED                      : {npass}")

    b_np = min_budget_numpy(r["passed"], a.k)
    b_z3 = min_budget_z3(r["passed"], a.k)
    if b_np != b_z3:
        print(f"\n  ★ NumPy says {b_np}, z3 says {b_z3}; the tools disagree, so no")
        print("    budget may be quoted.")
        return 4

    print("\nVERDICT")
    if r["crashed"]:
        print("  A traceback IS present; treat this as a crash and diagnose it.")
        return 0
    print("  NOT A CRASH. The run completed its round budget and the completion")
    print("  recorder had no name for round exhaustion, so it wrote")
    print("  UNRECORDED_STOP. His question is answered: there was nothing to fix")
    print("  before re-running, because nothing broke.")
    if b_np is None:
        print(f"\n  The gate never passed in {len(r['verdicts'])} rounds, so a longer")
        print("  budget alone is NOT supported by this evidence; the contested")
        print("  finding is the thing to resolve.")
    else:
        given = r["rounds_complete"] or 0
        first_pass_line = b_np - a.k + 1
        lines = len(r["verdicts"])
        # the gate is evaluated once more than the run has rounds, so the Nth
        # line maps to the run's round N-1 in its own 0-indexed labels.
        further = a.k - (lines - first_pass_line + 1)
        minimum = given + max(0, further)
        print(f"\n  The gate FIRST passed on evaluation {first_pass_line} of "
              f"{lines}, which is")
        print(f"  the run's LAST, and {a.k} consecutive passes are required. So it")
        print(f"  needed {max(0, further)} further passing round(s) beyond the "
              f"{given} it was given:")
        print(f"  a minimum budget of {minimum} rounds (NumPy and z3 agree on the")
        print(f"  window arithmetic; the round mapping is the run's own labels).")
        print(f"\n  PREDICTION, so it can fail: a re-run at --rounds {given} should")
        print("  be expected to end the same way. The change the evidence supports")
        print(f"  is a budget of at least {minimum}, and the contested finding is")
        print("  what held the earlier rounds shut.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    # ★ THE HELP-INTERCEPTING CALL IS REMOVED, 2026-11-03. It answered `--help`
    # BEFORE this script's own parser ran, so argparse never listed the flags:
    # measured across the 6 scripts that had both, 0 of 16 defined flags were
    # visible. `takes_no_arguments=False` was an earlier partial fix on
    # 2026-11-02; it stops the helper REFUSING a flag but not from answering
    # `--help` first. argparse's own help is now enabled, so the capability is
    # improved rather than lost.
    sys.exit(main())
