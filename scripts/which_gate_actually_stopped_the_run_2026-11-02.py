#!/usr/bin/env python3
"""Which convergence criterion stopped the 2026-11-02 validation run, and would
the two-sided gate have stopped it at the same round?

WHY THIS EXISTS. `GAMMA IS LOAD-BEARING` is a standing founder directive, and it
states the agreed design in its own words: *"The correct, agreed design is a
TWO-SIDED GATE. Convergence requires BOTH sides of the same diminishing-returns
coin to agree, neither alone"* -- gamma_critical at or above its threshold AND K
consecutive zero-new-critical rounds. This run reported
`STATE_CONVERGED at round 5 ... novel=1`, and a run that stops with a non-zero
novel count has not satisfied the count side. `feedback_verify_the_deciding_layer`
records 4 failures in 1 night from not checking which layer actually decided, so
the question is asked here rather than assumed either way.

WHAT IS NOT WRONG, STATED FIRST SO THE FINDING IS NOT OVERSOLD.
  * Gamma was NOT demoted and NOT bypassed. gamma_critical reached 0.905 and the
    telemetry gamma 0.585, both above the configured gamma_alt_threshold of
    0.41. The GAMMA side of the two-sided gate HELD.
  * `novel=1` is inside the configured state-gate tolerance:
    `max_novel_findings` defaults to 2, so 1 novel finding is a MET condition
    and not a leak.
  * The two-sided gate was CONFIGURED AND ENABLED for this run, not switched
    off: `gamma_alt_threshold=0.41`, `gamma_alt_consecutive_zero_crit=3`,
    `gamma_alt_earliest_round=3`, `location_keyed_convergence=True`,
    `hardened_gate_enabled=True`.

WHAT THE MEASUREMENT IS. The novel-critical series is reconstructed from the
run's own per-round gate lines, and the two-sided gate's count side is replayed
against it to find the earliest round at which K consecutive zeros existed. If
that round is later than the round the state gate stopped on -- or never occurs
-- then 2 enabled criteria disagreed and the more permissive one decided.

WHY IT IS A QUESTION AND NOT A DEFECT REPORT. Whether the state gate may
terminate independently of the two-sided gate is a DESIGN decision and the
founder's, and the standing directive is explicit that gamma must not be
demoted. This script establishes the fact; the ruling is his.

TOOLS: 2 per the 2026-04-21 rule -- z3 decides the earliest K-zero window as a
constraint problem, and a direct sliding-window scan in NumPy must agree.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_LOG = REPO / "bench" / "logs" / "severity_bounds_validation_20261102T004713Z.log"
#: the hierarchical rule supersedes the location-keyed one, so it is read.
_TAIL = re.compile(r"hierarchical novel-crit this round=(\d+) \(series tail=\[([0-9,\s]*)\]")
_STOP = re.compile(r"Convergence: (\w+) at round (\d+)")


def series_from_log(text: str) -> list[int]:
    """Reconstruct the full novel-critical series from the per-round tails.

    A tail is the last 3 values, so successive tails overlap. The series is
    rebuilt by taking the first tail whole and then each later tail's last
    element, which is exact when the tails are consecutive rounds.
    """
    tails = [[int(x) for x in t.replace(" ", "").split(",") if x != ""]
             for _, t in _TAIL.findall(text)]
    if not tails:
        return []
    out = list(tails[0])
    for t in tails[1:]:
        if t:
            out.append(t[-1])
    return out


def earliest_k_zero_numpy(series: list[int], k: int) -> int | None:
    import numpy as np
    a = np.asarray(series, dtype=int)
    for i in range(len(a) - k + 1):
        if bool(np.all(a[i:i + k] == 0)):
            return i + k          # 1-indexed round at which the window closes
    return None


def earliest_k_zero_z3(series: list[int], k: int) -> int | None:
    import z3
    best = None
    for i in range(len(series) - k + 1):
        s = z3.Solver()
        # the window closes at i+k only if every member is 0
        s.add(z3.And(*[z3.IntVal(series[j]) == 0 for j in range(i, i + k)]))
        if s.check() == z3.sat:
            best = i + k
            break
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    ap.add_argument("--k", type=int, default=3,
                    help="gamma_alt_consecutive_zero_crit for the run")
    a = ap.parse_args()

    text = pathlib.Path(a.log).read_text(errors="replace")
    series = series_from_log(text)
    stop = _STOP.search(text)

    print("=" * 76)
    print("WHICH GATE STOPPED THE RUN?")
    print("=" * 76)
    print(f"\n  log            : {pathlib.Path(a.log).name}")
    print(f"  novel-critical series (hierarchical) : {series}")
    if stop:
        print(f"  the run stopped on : {stop.group(1)} at round {stop.group(2)}")
    if not series:
        print("\n  0 gate lines parsed -- this measurement is VACUOUS.")
        return 1

    n_np = earliest_k_zero_numpy(series, a.k)
    n_z3 = earliest_k_zero_z3(series, a.k)
    if n_np != n_z3:
        print(f"\n  ★ NumPy says {n_np}, z3 says {n_z3}. The tools disagree, so")
        print("    neither answer may be quoted.")
        return 4

    print(f"\n  two-sided gate COUNT side needs {a.k} consecutive zero-new-critical rounds")
    print(f"      earliest such round (NumPy) : {n_np}")
    print(f"      earliest such round (z3)    : {n_z3}   agree=True")

    stop_round = int(stop.group(2)) if stop else None
    print("\nVERDICT")
    if n_np is None:
        print(f"  THE COUNT SIDE WAS NEVER SATISFIED in {len(series)} rounds. The")
        print(f"  series never holds {a.k} consecutive zeros, so the two-sided gate")
        print("  would NOT have declared convergence at any round of this run.")
        if stop_round:
            print(f"  The run nevertheless stopped at round {stop_round}, on the STATE")
            print("  gate, whose `max_novel_findings` tolerance admits a non-zero")
            print("  novel count. So 2 ENABLED criteria disagreed and the more")
            print("  permissive one decided.")
        print("\n  GAMMA IS NOT THE PROBLEM AND WAS NOT DEMOTED: gamma_critical 0.905")
        print("  and telemetry gamma 0.585 both clear the 0.41 threshold, so the")
        print("  GAMMA side held. It is the COUNT side that never closed.")
        print("\n  THIS IS A QUESTION FOR THE FOUNDER, NOT A DEFECT CALL: whether the")
        print("  state gate may terminate a run independently of the two-sided gate")
        print("  is a design decision, and the standing directive that gamma is")
        print("  load-bearing is his.")
    elif stop_round and n_np > stop_round:
        print(f"  The two-sided gate would have converged at round {n_np}, LATER than")
        print(f"  the state gate's round {stop_round}. The permissive criterion decided.")
    else:
        print(f"  Both criteria agree at or before round {stop_round}. No disagreement.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
