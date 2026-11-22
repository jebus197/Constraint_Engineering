#!/usr/bin/env python3
"""The cy gate's anti-trap budget binds for WATCHED runs and not for unwatched ones.

DRAFTED 2026-11-22; destination `scripts/`. Held in the scratchpad until the
batch-2 board finishes, because the board reads the tree and a tree that moves
under a running board is this project's recorded 2-of-8 failure of 2026-11-02.

SUBJECT: `hooks/cy_monitor_gate.py`, its `spend()` and the key `main()` builds.

★ WHAT THE BUDGET IS FOR, IN THE GATE'S OWN WORDS. `MAX_REFUSALS = 60` is an
ANTI-TRAP SAFEGUARD: on exhaustion `main()` prints *"Allowing the stop so a
session cannot be trapped. THE RUN MAY STILL BE LIVE -- check it."* So the
budget's whole job is to stop the gate refusing for ever.

★ THE DEFECT. `main()` builds the key as

    session_id + "|" + str(sorted(r["dir"] for r in live + unwatched) or pids)

and `spend()` zeroes the count whenever the key changes. With NO watched run the
key falls back to `pids`, the live runner process ids. A commit board spawns a
fresh pytest child per guard file, so that list churns, so the key changes, so
the counter resets and 60 is never reached.

★ SO THE SAFEGUARD IS INERT FOR EXACTLY THE RUNS THE GATE CANNOT READ, which is
the only case in which a session could be trapped: a watched run has a stable
directory key and binds correctly. A mechanism that does not reach the case it
exists for is the shape `additive-standard` names, and this project's record
holds 11 confirmed defects of it against 0 removals of something needed.

★ IT IS DRIVEN, NOT READ. `execute-do-not-grep`: a test asserting on this hook's
source would establish only that the file describes itself consistently. Both
arms call the real `spend()` against a temporary state file, so the reset is
OBSERVED. The state path is overridable through `CDSFL_CY_STATE`, the seam the
hook already carries for exactly this reason.

★ IT TOUCHES NOTHING LIVE. The hook is imported, never executed as a hook; the
state file is a temporary directory; the real
`~/.claude/hooks/.cy_monitor_gate_state.json` is not read or written. Verified
by asserting the override is in force before any call.

OBSERVED IN THE WILD, not only constructed: during the batch-2 board of
2026-11-22 the counter was seen reading "1 of 60", then 2, then 3, then back to
"1 of 60", each reset coinciding with a changed child pid.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys
import tempfile

#: ★ THE ROOT IS FOUND BY WALKING, NOT BY `parents[1]`, AND THE FIRST DRAFT USED
#: `parents[1]`. Run from a scratch directory to test it before promotion, that
#: resolved to `/private` and the import died on
#: `/private/hooks/cy_monitor_gate.py`. `parents[1]` is correct ONLY from the
#: script's destination, so it makes a producer that cannot be exercised
#: anywhere else -- and a producer first run on the day it is needed is a
#: producer whose first use is its first trial. Walking upward for the markers
#: works from any location, which is the pattern this project's own guards use.
#: `CDSFL_CY_GATE_PATH` additionally lets a guard point at a CONSTRUCTED hook.
def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "hooks").is_dir() and (cand / "bench" / "tests").is_dir():
            return cand
    fb = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
    if (fb / "hooks").is_dir():
        return fb
    raise SystemExit(
        "cannot locate the repository from " + str(here) + "; pass "
        "CDSFL_CY_GATE_PATH to name the hook directly rather than guessing.")


REPO = _find_repo()
GATE = pathlib.Path(os.environ.get("CDSFL_CY_GATE_PATH")
                    or REPO / "hooks" / "cy_monitor_gate.py")

#: The pid lists are the SHAPE a board produces: one long-lived process and a
#: child that is replaced per guard file. Taken from the live board of
#: 2026-11-22 rather than invented, so the arm reproduces a real sequence.
CHURNING_PIDS = [
    ["70507"],
    ["70507", "76042"],
    ["70507", "77353"],
    ["70507", "78785"],
    ["70507", "79475"],
]
STABLE_DIR_KEY = "sess|['bench/logs/run1']"


def load_gate():
    spec = importlib.util.spec_from_file_location("cy_gate_under_test", GATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cy_gate_under_test"] = m
    spec.loader.exec_module(m)
    return m


def arm_stable(m, polls: int) -> "list[int]":
    """A WATCHED run: the key is the run directory and does not move."""
    return [m.spend(STABLE_DIR_KEY) for _ in range(polls)]


def arm_churning(m) -> "list[int]":
    """An UNWATCHED run: the key falls back to a pid list that churns."""
    return [m.spend("sess|" + str(p)) for p in CHURNING_PIDS]


def main() -> int:
    td = tempfile.mkdtemp(prefix="cy_budget_probe_")
    os.environ["CDSFL_CY_STATE"] = str(pathlib.Path(td) / "state.json")
    m = load_gate()

    #: ANTI-FOOTGUN: if the override were ignored this probe would spend the
    #: REAL session's budget. Asserted before any call rather than trusted.
    assert str(m.state_path()).startswith(td), (
        f"the state override is not in force: {m.state_path()}. Refusing to run, "
        f"because this probe would otherwise consume the live session's budget.")

    print("=" * 74)
    print("DOES THE cy GATE'S ANTI-TRAP BUDGET ACTUALLY BIND?")
    print("=" * 74)
    print(f"  MAX_REFUSALS declared in the hook : {m.MAX_REFUSALS}")
    print(f"  state file for this probe          : {m.state_path()}")

    stable = arm_stable(m, len(CHURNING_PIDS))
    print(f"\n  ARM 1  WATCHED run, key = run directory (stable)")
    print(f"         {len(stable)} polls -> {stable}")
    print(f"         climbs: the budget BINDS and 60 is reachable")

    churning = arm_churning(m)
    print(f"\n  ARM 2  UNWATCHED run, key = pid list (churns per guard file)")
    print(f"         {len(churning)} polls -> {churning}")
    print(f"         resets: the budget NEVER binds and 60 is unreachable")

    binds = stable == list(range(1, len(stable) + 1))
    inert = set(churning) == {1}

    print("\n  VERDICT")
    print(f"    watched arm binds        : {binds}")
    print(f"    unwatched arm is inert   : {inert}")
    if binds and inert:
        print("\n  THE SAFEGUARD IS INERT FOR PRECISELY THE RUNS THE GATE CANNOT READ,")
        print("  which is the only case in which a session could be trapped. A watched")
        print("  run has a stable key and does not need the protection.")
        print("\n  SEVERITY IS REAL BUT CONDITIONAL: the condition is an IDLE session")
        print("  during a long unwatched run. A session with work to do answers each")
        print("  refusal and never notices.")
        return 1          # a live defect: non-zero so a guard can gate on it
    if binds and not inert:
        print("\n  THE DEFECT IS REPAIRED: the unwatched arm now climbs too.")
        return 0
    print("\n  UNEXPECTED: the WATCHED arm does not bind either. The budget is")
    print("  broken more widely than this script was written to measure -- read")
    print("  `spend()` and the key construction before trusting any figure here.")
    return 2


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    sys.exit(main())
