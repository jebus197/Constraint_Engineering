#!/usr/bin/env python3
"""PreToolUse gate: refuse a fan-out that would over-commit the founder's own machine.

HIS RULING, 2026-10-11: *"You have to be aware of the resources you are working with. As you
said sq (when in force) tells you not to overload Anthropic's servers. But clearly I also have
limits, and unlike Anthropic, my resources don't change. So you will need to implement a
permanent fix for this."*

WHAT THIS PREVENTS, measured on 2026-10-11. One audit fan-out spawned 48 agents issuing 2,310
local Bash calls, of which 263 were pytest. The machine is a Macmini9,1 with 8 logical cores and
8 GiB of RAM. A pytest process tree on this repository peaks at 364.7 MiB (42 samples), and live
headroom was 1.91 GiB, so the machine holds about 5 concurrent heavy processes. The harness cap
is min(16, ncpu-2) = 6, i.e. ALREADY ABOVE CAPACITY, and it is derived from cores alone while
the binding constraint on 8 GiB is memory.

WHY A HOOK RATHER THAN A NOTE. The project's own standard is that a guard must be structurally
enforced rather than hoped for (`feedback_falsification_gate`). A directive in CLAUDE.md is read
once per session and can be forgotten mid-task; this runs on every call.

WHAT IT REFUSES, deliberately narrow to avoid false positives:
  * an Agent/Task call whose prompt instructs pytest or the full suite -- subagents must consult
    a cached board instead, because 263 invocations answered what 1 board answers;
  * a Workflow whose script both fans out AND instructs pytest.
Everything else is ADVISED, not blocked: the budget is injected so it cannot be unseen.

Exit codes: 0 allow (with context on stdout), 2 block with the reason on stderr.
"""
import json
import math
import os
import re
import subprocess
import sys

HEAVY_MIB = 364.7          # measured: one pytest tree on Constraint_Engineering
LIGHT_MIB = 80.0
HEADROOM_SHARE = 0.5
RESERVED_CORES = 2
GATED_TOOLS = {"Agent", "Task", "Workflow"}


def _sysctl(name, default=0):
    try:
        return int(subprocess.run(["sysctl", "-n", name], capture_output=True,
                                  text=True, timeout=10).stdout.strip())
    except Exception:
        return default


def _headroom_mib():
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return 0.0
    m = re.search(r"page size of (\d+) bytes", out)
    page = int(m.group(1)) if m else 4096
    tot = 0
    for label in ("Pages free", "Pages inactive", "Pages speculative"):
        mm = re.search(rf"{label}:\s+(\d+)", out)
        if mm:
            tot += int(mm.group(1))
    return tot * page / (1024 * 1024)


def budget(per_mib):
    cores = _sysctl("hw.ncpu", os.cpu_count() or 1)
    head = _headroom_mib()
    core_c = max(1, cores - RESERVED_CORES)
    mem_c = max(1, math.floor(head * HEADROOM_SHARE / per_mib))
    chosen = min(core_c, mem_c)
    try:
        la1 = os.getloadavg()[0]
    except Exception:
        la1 = 0.0
    # 0.6 rather than 0.7 per core, plus an independent memory-pressure arm. Measured
    # 2026-10-11: at load 5.42 on 8 cores the 0.7 threshold (5.6) did not fire, while
    # headroom had already fallen to 1224.2 MiB. A near-miss on a safety threshold is a defect.
    if la1 > 0.6 * cores or head < 2 * per_mib:
        chosen = max(1, chosen // 2)
    return chosen, core_c, mem_c, round(head, 1), cores, round(la1, 2)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tool = payload.get("tool_name") or ""
    if tool not in GATED_TOOLS:
        return 0
    ti = payload.get("tool_input") or {}
    blob = " ".join(str(ti.get(k, "")) for k in ("prompt", "script", "description", "args"))
    low = blob.lower()

    heavy_b, core_c, mem_c, head, cores, la1 = budget(HEAVY_MIB)
    light_b, *_ = budget(LIGHT_MIB)

    wants_pytest = bool(re.search(r"\bpytest\b|python3? -m pytest|full board|the suite\b", low))
    fans_out = bool(re.search(r"\bparallel\s*\(|\bpipeline\s*\(|batch|fan.?out", low))

    if wants_pytest and (tool in ("Agent", "Task") or fans_out):
        sys.stderr.write(
            "REFUSED by local_resource_budget: this call instructs pytest inside delegated "
            f"work.\n  The founder's machine has {cores} cores and {head} MiB live headroom; "
            f"one pytest tree peaks at {HEAVY_MIB} MiB, so it holds {mem_c} concurrent heavy "
            f"process(es) (budget {heavy_b}).\n  Measured 2026-10-11: 263 delegated pytest "
            "invocations cost 4557.8 s at the cheapest observed rate against 3998.65 s for ONE "
            "full board.\n  DO THIS INSTEAD: run the board ONCE yourself, save the result, and "
            "have the delegated work consult that cached file.\n  His ruling of 2026-10-11: "
            '"you will need to implement a permanent fix for this."\n')
        return 2

    print(f"[local-budget] founder's machine: {cores} cores, {head} MiB headroom, load {la1}. "
          f"Concurrent agent budget: {heavy_b} heavy (pytest/import-grade), {light_b} light "
          f"(grep/read-grade). Memory-bound at {mem_c}; harness default is "
          f"{min(16, max(1, cores - 2))} and is CORE-derived, so it over-commits 8 GiB. "
          f"Scale the fan-out to the budget, not to the token allowance.\n"
          f"[token-arm] HIS SECOND RESOURCE, raised 2026-10-04: \"a big spike in my Anthropic "
          f"Max plan usage quota, and right now I am nearly out of my weekly allowance ... I "
          f"usually only barely scratch the surface.\" Agents spend that allowance; reasoning "
          f"effort spends it too but costs 0 local CPU. BEFORE this fan-out, call "
          f"mcp__ccd_session_mgmt__get_usage and read the WEEKLY window. Prefer DEPTH "
          f"(more reasoning, more falsification passes on one claim) over BREADTH (more "
          f"agents): of 12 errors measured on 2026-10-11, 10 were catchable by reasoning "
          f"before running and only 2 needed execution.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
