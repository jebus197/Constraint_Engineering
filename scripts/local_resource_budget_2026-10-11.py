#!/usr/bin/env python3
"""How much of the founder's machine may a fan-out use? Derived, not guessed.

THE FOUNDER'S RULING, 2026-10-11: *"You have to be aware of the resources you are working
with. As you said sq (when in force) tells you not to overload Anthropic's servers. But clearly
I also have limits, and unlike Anthropic, my resources don't change. So you will need to
implement a permanent fix for this."*

WHAT WENT WRONG, MEASURED. A single audit fan-out spawned 48 agents which issued 2,310 local
Bash calls on his machine -- 876 grep, 464 other, 416 git, 291 python3 and **263 pytest**. The
machine is a Macmini9,1: 8 logical cores, 8 physical, 8 GiB of RAM. Observed load averages
immediately after the stop were 1.36 (1 min), 2.33 (5 min) and 3.37 (15 min); the 15-minute
figure sitting 2.5x above the 1-minute one is the run draining off the machine.

THE BINDING CONSTRAINT IS MEMORY, NOT CORES, AND THE OLD CAP EXCEEDED IT. Measured 2026-10-11
by sampling the resident set size of a real pytest process tree on this repository every 0.4 s
over 42 samples: ONE pytest tree peaks at 364.7 MiB. Live headroom at the time (free plus
inactive plus speculative pages) was 1.91 GiB. So the machine holds 1.91*1024/364.7 = 5.36
concurrent heavy processes, while the harness default cap is min(16, ncpu-2) = 6. **The default
was already above capacity**, which is why the run pinned the machine rather than merely
loading it.

AND THE WORK DID NOT NEED DOING AT ALL. 263 pytest invocations were issued where ONE full board
answers the test question for every item. A full board is 3998.65 s. At the cheapest pytest run
measured that day (17.33 s) the fan-out spent 4557.8 s against 3998.65 s needed, 1.14x; at the
3-file rate measured the same day (64.81 s) it spent 17045.0 s, 4.26x.

WHY THIS IS A SEPARATE RULE FROM `sq`. `sq` exists to avoid stressing ANTHROPIC's servers and is
invoked per session. It says nothing about the founder's own hardware, and his point is that his
resources are FIXED where Anthropic's are elastic. So this budget binds whether or not `sq` is
in force, and it is derived from the live machine rather than from a remembered number.

Run:  python3 scripts/local_resource_budget_2026-10-11.py
      python3 scripts/local_resource_budget_2026-10-11.py --json
      python3 scripts/local_resource_budget_2026-10-11.py --check-fanout 48 --work-class heavy
          exit 0 if the requested fan-out fits, exit 3 if it does not.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys

#: Peak resident set size of ONE process doing each class of work, in MiB.
#: HEAVY is MEASURED on this repository (42 samples, 2026-10-11). LIGHT is the floor a Python
#: interpreter plus the agent's own tooling occupies before it does anything expensive; it is
#: deliberately an over-estimate, because under-estimating it is what pins the machine.
WORK_CLASS_MIB = {
    "heavy": 364.7,   # runs pytest, or imports reference_runner_v3
    "light": 80.0,    # grep / git / read / small python
}

#: Fraction of LIVE headroom a fan-out may claim. The rest is left for the operating system,
#: the desktop application, the founder's own terminals and his editor. 0.5 is a judgement,
#: not a measurement, and it is named here rather than buried so it can be argued with.
HEADROOM_SHARE = 0.5

#: Cores left for the founder's own interactive work. The harness reserves 2; on an 8-core
#: machine that still allowed 6 heavy processes, which exceeds what 8 GiB holds.
RESERVED_CORES = 2


def logical_cores() -> int:
    try:
        return int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True,
                                  text=True, timeout=20).stdout.strip())
    except Exception:
        return os.cpu_count() or 1


def total_ram_mib() -> float:
    try:
        b = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True,
                               text=True, timeout=20).stdout.strip())
        return b / (1024 * 1024)
    except Exception:
        return 0.0


def headroom_mib() -> float:
    """Free plus inactive plus speculative pages, which is what a new process can actually take."""
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return 0.0
    m = re.search(r"page size of (\d+) bytes", out)
    page = int(m.group(1)) if m else 4096
    total = 0
    for label in ("Pages free", "Pages inactive", "Pages speculative"):
        mm = re.search(rf"{label}:\s+(\d+)", out)
        if mm:
            total += int(mm.group(1))
    return total * page / (1024 * 1024)


def load_averages() -> tuple:
    try:
        return tuple(round(x, 2) for x in os.getloadavg())
    except Exception:
        return (0.0, 0.0, 0.0)


def budget(work_class: str = "heavy") -> dict:
    """The number of concurrent agents this machine can hold RIGHT NOW, for this work class.

    Two independent ceilings, and the budget is the smaller:
      cores  -- logical cores minus the founder's reserve
      memory -- the share of live headroom divided by one process's measured peak
    """
    per = WORK_CLASS_MIB.get(work_class)
    if per is None:
        raise SystemExit(f"unknown work class {work_class!r}; "
                         f"choose from {sorted(WORK_CLASS_MIB)}")
    cores = logical_cores()
    head = headroom_mib()
    core_ceiling = max(1, cores - RESERVED_CORES)
    mem_ceiling = max(1, math.floor(head * HEADROOM_SHARE / per))
    chosen = min(core_ceiling, mem_ceiling)
    la = load_averages()
    # A machine already under load gets a further halving.
    #
    # THE THRESHOLD WAS 0.7 PER CORE AND IT MISSED BY 0.18. Measured 2026-10-11 while this
    # very module was being tested: 2 concurrent pytest trees drove the 1-minute load average
    # to 5.42 on 8 cores and headroom down to 1224.2 MiB. The memory arm correctly cut the
    # budget from 2 to 1, but `machine_already_loaded` still read False because 5.42 < 5.6.
    # A near-miss on a safety threshold is a defect, not a success, so the trigger is now
    # 0.6 per core AND an independent memory-pressure arm: if headroom has fallen below twice
    # one process's cost there is no room for a second whatever the load average says.
    loaded = (la[0] > 0.6 * cores) or (head < 2 * per)
    if loaded:
        chosen = max(1, chosen // 2)
    return {
        "work_class": work_class,
        "per_process_peak_mib": per,
        "logical_cores": cores,
        "total_ram_mib": round(total_ram_mib(), 1),
        "live_headroom_mib": round(head, 1),
        "headroom_share": HEADROOM_SHARE,
        "reserved_cores": RESERVED_CORES,
        "core_ceiling": core_ceiling,
        "memory_ceiling": mem_ceiling,
        "binding_constraint": "memory" if mem_ceiling < core_ceiling else "cores",
        "load_averages": la,
        "machine_already_loaded": loaded,
        "max_concurrent_agents": chosen,
        "harness_default_cap": min(16, max(1, cores - 2)),
    }


def claim_the_harness_default_exceeds_this_machine() -> dict:
    """The finding that prompted the rule, recomputed every run rather than quoted."""
    b = budget("heavy")
    return {
        "harness_default_cap": b["harness_default_cap"],
        "measured_safe_cap": b["max_concurrent_agents"],
        "default_exceeds_capacity": b["harness_default_cap"] > b["max_concurrent_agents"],
        "by_how_many": b["harness_default_cap"] - b["max_concurrent_agents"],
        "note": ("the harness cap is derived from CORES ALONE; on 8 GiB the binding constraint "
                 "is memory, so a core-derived cap over-commits the machine"),
    }


def claim_one_board_beats_many_targeted_runs(n_invocations: int = 263) -> dict:
    """263 pytest runs were issued where 1 full board answers every test question."""
    CHEAPEST = 17.33   # measured 2026-10-11: test_dormant_switches..., 5 passed
    THREE_FILE = 64.81  # measured 2026-10-11: 3 config guards, 113 passed
    BOARD = 3998.65     # full board, recorded 2026-10-07
    return {
        "pytest_invocations_issued": n_invocations,
        "one_full_board_seconds": BOARD,
        "floor_cost_seconds": round(n_invocations * CHEAPEST, 1),
        "floor_ratio_vs_one_board": round(n_invocations * CHEAPEST / BOARD, 2),
        "measured_rate_cost_seconds": round(n_invocations * THREE_FILE, 1),
        "measured_rate_ratio_vs_one_board": round(n_invocations * THREE_FILE / BOARD, 2),
        "verdict": ("run the board ONCE and let every item consult the cached result; a "
                    "per-item pytest invocation is strictly wasteful above 1 item"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--work-class", default="heavy", choices=sorted(WORK_CLASS_MIB))
    ap.add_argument("--check-fanout", type=int, metavar="N",
                    help="exit 3 if N concurrent agents exceeds this machine's budget")
    args = ap.parse_args()

    b = budget(args.work_class)
    if args.json:
        print(json.dumps({"budget": b,
                          "harness": claim_the_harness_default_exceeds_this_machine(),
                          "board": claim_one_board_beats_many_targeted_runs()},
                         indent=1))
    else:
        print(f"== local resource budget, work class {b['work_class']} ==")
        for k, v in b.items():
            print(f"   {k}: {v}")
        print("\n== is the harness default safe here? ==")
        for k, v in claim_the_harness_default_exceeds_this_machine().items():
            print(f"   {k}: {v}")
        print("\n== one board versus many targeted runs ==")
        for k, v in claim_one_board_beats_many_targeted_runs().items():
            print(f"   {k}: {v}")

    if args.check_fanout is not None:
        ok = args.check_fanout <= b["max_concurrent_agents"]
        print(f"\n   requested fan-out {args.check_fanout}, budget "
              f"{b['max_concurrent_agents']} ({b['binding_constraint']}-bound) -> "
              f"{'WITHIN BUDGET' if ok else 'REFUSED: OVER BUDGET'}", file=sys.stderr)
        return 0 if ok else 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
