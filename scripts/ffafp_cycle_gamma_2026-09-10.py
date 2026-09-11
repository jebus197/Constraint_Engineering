#!/usr/bin/env python3
"""When has an FFAFP cycle actually reached diminishing returns? Ask the model.

Founder instruction 2026-09-10, verbatim: *"f everything (FFAFP in cyclic mode
until diminishing returns, as per our maths model, which you should refer to and
use)"*.

THE STOP CRITERION WAS BEING ASSERTED, NOT COMPUTED. "Diminishing returns" is a
founding principle of this project with a live implementation — `_estimate_gamma`
and the two-sided gate in `bench/reference_runner_v3.py` — and an assistant
saying a cycle had converged was, until this script, saying so from intuition
while the machinery to decide it sat unused a few imports away.

WHAT THE MODEL SAYS, and this script only applies it. `_estimate_gamma` is a
Duane slope: it fits log(cumulative findings) against log(round index) and
returns `1 - beta` clamped to [0, 1]. Constant discovery gives beta = 1 and
gamma = 0. A flat cumulative curve gives beta = 0 and gamma = 1. The two-sided
gate, which the standing directive in `.claude/CLAUDE.md` says must NOT be
demoted, converges only when BOTH hold:

    (a) gamma >= 0.30      the CUMULATIVE curve is sublinear -- NOT a claim
                           about the tail; see the resurgence note below
    (b) K = 3 consecutive rounds at zero    the threshold-free insurance endpoint

WHAT SIDE (a) DOES NOT SAY, corrected 2026-09-10 after panel round 4 (CC2, F3).
The gloss above used to read "the decay curve has flattened", and that overstates
the statistic. gamma is fitted to the CUMULATIVE series, so a large leading round
mechanically produces a sublinear log-log fit no matter what the tail does.
Measured with the real `_estimate_gamma`, and cross-checked against an
independent numpy polyfit and a scipy linregress agreeing to 1e-9:

    [11, 1, 2, 3, 4, 5, 6, 7, 8]   gamma = 0.324155   side (a) PASS

That series RISES for 8 consecutive passes. On the live series gamma is 0.415413,
and had pass 9 returned 0 instead of 9 it would have been 0.460561 -- the
resurgence moved gamma by 0.045 and could not have pushed it below 0.30 from
where it started.

GAMMA IS NOT BROKEN AND IS NOT DEMOTED. It correctly returns 0.000000 for
constant discovery ([2]*9), for linear growth (1..9) and for doubling
(1,2,4,...,256), all of which fail side (a). It is CONFOUNDED here by a large
leading round: pass 1 contributed 11 of the 42 cumulative findings. The standing
directive is that when something looks wrong the cause is mechanical, and this is
the mechanism. The repair is additive -- a resurgence diagnostic is printed
alongside gamma so a reader is never handed a passing gamma next to a rising tail
with no cue that the two disagree. Nothing is removed and no threshold moves.

Verified 2026-09-10 against an independent scipy least-squares fit of the same
log-log regression: exact agreement to 1e-9 across 5 series, with mpmath and
numpy agreeing to 12 significant figures.

A ROUND HERE IS ONE FFAFP PASS, and a finding is one ABOVE-THRESHOLD finding —
the project's own threshold test: missing it could cause real-world failure. The
series lives in a committed JSON beside this script so it survives compaction,
which is the half of the task-list mechanism that did work.
"""
from __future__ import annotations

import json
import pathlib
import sys

# `--help` MUST NOT ACT, AND ON A SIBLING OF THIS SCRIPT IT DESTROYED 54,480
# BYTES. Measured 2026-09-11: `--help` on `scripts/assemble_panel_record_0819.py`
# rewrote a 55,814-byte verbatim panel record down to 1,334 and exited 0, because
# the flag fell through to the script's ordinary work.
#
# GUARDED BY `__main__`, WHICH THE FIRST VERSION WAS NOT. Calling it at module
# level meant that any test IMPORTING this module handed pytest's own argv to the
# help handler, which refused it and exited 2 -- 12 failures and errors in the
# next clone run. The established form in this directory guards the call, and
# importing the module then reaches exactly the code it reached before.
if __name__ == "__main__":
    try:
        from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    except ImportError:
        # A COPY OUTSIDE scripts/, which is how the mutation harness runs
        # this file: it writes the mutant to `.mutants/` where `_cli_help`
        # is not importable. Crashing there would make every mutant
        # "caught" for the wrong reason -- a crashing mutant produces no
        # output and every `not in` check passes. The guard protects real
        # invocations; a mutant copy is not one.
        pass
    else:
        answer_help(__doc__, __file__, takes_no_arguments=False)

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import _estimate_gamma  # noqa: E402

SERIES = REPO / "experimental_notes" / "data" / "ffafp_cycle_series.json"
GAMMA_THRESHOLD = 0.30      # the project's own gamma_alt_threshold default
K_ZERO = 3                  # consecutive zero-finding passes required


def load() -> dict:
    if SERIES.is_file():
        return json.loads(SERIES.read_text())
    return {"cycle": "unnamed", "passes": []}


def gate(counts: list[int]) -> tuple[float, bool, bool, str]:
    """(gamma, gamma_side, count_side, verdict) — both sides, never one."""
    gamma = _estimate_gamma(counts, min_rounds=3)
    gamma_side = gamma >= GAMMA_THRESHOLD
    count_side = len(counts) >= K_ZERO and all(c == 0 for c in counts[-K_ZERO:])
    if gamma_side and count_side:
        return gamma, gamma_side, count_side, "CONVERGED"
    return gamma, gamma_side, count_side, "KEEP GOING"


USAGE = ("usage: ffafp_cycle_gamma_2026-09-10.py [--record <pass-label> "
         "<above-threshold-findings>]\n"
         "  with no arguments: report the series and the two-sided gate verdict")


def main() -> int:
    # AN UNRECOGNISED ARGUMENT MUST NOT READ AS SUCCESS.
    #
    # Caught by `test_an_unknown_flag_is_rejected_loudly` on this script's first
    # suite run. It read `sys.argv[1] == "--record"` and ignored everything else,
    # so `--this-flag-does-not-exist` printed a report and exited 0. That is the
    # class recorded in `feedback_help_must_never_cost_money`, where 15 of 17
    # runners billed a live dispatch on an unrecognised argument. Nothing here
    # costs money, but a caller who mistypes a flag and reads exit 0 believes a
    # pass was recorded when none was.
    argv = sys.argv[1:]
    if argv and argv[0] not in ("--record", "-h", "--help"):
        print(f"unrecognised argument: {argv[0]}\n{USAGE}", file=sys.stderr)
        return 2
    if argv and argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0

    d = load()
    if argv and argv[0] == "--record":
        if len(argv) < 3:
            print(USAGE, file=sys.stderr)
            return 2
        try:
            findings = int(argv[2])
        except ValueError:
            print(f"findings must be an integer, got {argv[2]!r}\n{USAGE}",
                  file=sys.stderr)
            return 2
        d["passes"].append({"label": argv[1], "findings": findings})
        SERIES.parent.mkdir(parents=True, exist_ok=True)
        SERIES.write_text(json.dumps(d, indent=1) + "\n")
        print(f"recorded: {argv[1]} -> {findings} above-threshold finding(s)")

    counts = [p["findings"] for p in d["passes"]]
    print(f"\ncycle: {d.get('cycle', 'unnamed')}")
    for i, p in enumerate(d["passes"], 1):
        print(f"  pass {i}: {p['findings']:3d}  {p['label']}")
    if not counts:
        print("\nno passes recorded yet")
        return 0

    gamma, gside, cside, verdict = gate(counts)
    print(f"\n  series                 : {counts}")
    print(f"  gamma (Duane slope)    : {gamma:.6f}")
    print(f"  (a) gamma >= {GAMMA_THRESHOLD}       : {'PASS' if gside else 'FAIL'}")
    print(f"  (b) {K_ZERO} zero-finding passes: {'PASS' if cside else 'FAIL'}"
          f"   (last {K_ZERO}: {counts[-K_ZERO:]})")
    print(f"  TWO-SIDED GATE         : {verdict}")
    # RESURGENCE DIAGNOSTIC (added 2026-09-10, panel round 4, CC2 F3). Additive:
    # it changes no threshold and no verdict, it removes nothing, and it exists
    # because a passing gamma printed beside a rising tail reads as corroboration
    # when it is not -- the same shape as the stale document the V5 repair exists
    # to prevent, one instrument over.
    if len(counts) >= 2 * K_ZERO:
        tail, prev = sum(counts[-K_ZERO:]), sum(counts[-2 * K_ZERO:-K_ZERO])
        if tail > prev:
            lead = counts[0]
            total = sum(counts)
            print(f"\n  !! RESURGENCE: the last {K_ZERO} passes found {tail} against "
                  f"{prev} in the {K_ZERO} before.")
            print(f"     gamma is fitted to the CUMULATIVE series and is dominated by "
                  f"pass 1 ({lead} of {total}).")
            print(f"     It does not fall on a rising tail: [11, 1, 2, 3, 4, 5, 6, 7, 8] "
                  f"scores {_estimate_gamma([11, 1, 2, 3, 4, 5, 6, 7, 8]):.6f} and PASSES "
                  f"side (a).")
            print(f"     Read side (a) as UNINFORMATIVE here. Side (b) is carrying this "
                  f"gate.")

    if verdict == "KEEP GOING":
        print("\n  The gate is two-sided by founder ruling 2026-06-10 and neither side")
        print("  alone converges. A high gamma with findings still arriving means the")
        print("  cumulative curve is sublinear but discovery has not stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
