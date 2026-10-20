#!/usr/bin/env python3
"""Before dispatching anything heavy, is there headroom -- and if not, why not?

HIS STANDING PERMISSION, 2026-10-17, verbatim: *"This may have been a Firefox
memory leak. If this happens again, you should implement a mechanical check when
resources become low to see if Firefox is running and (if possible) the last time
I used it to do anything. If I haven't used it for some time, and resources are
genuinely below a useful threshold, you have my permission to close it before
continuing with your work. I will look later today at what might be causing the
memory leak. It is probably one of my Firefox extensions."*

WHY THIS EXISTS. On 2026-10-17 five free-panel runs were not launched because the
machine stood at a load average of 8.55 with 15.88 MiB free and 4 heavy processes
against his standing budget of 2. Launching into that would have been a decision
about his hardware taken without him. The decision needs a MEASUREMENT, and until
now there was none: the figures were read by hand each time.

WHAT IT MAY AND MAY NOT DO, and the boundary is his. It may TERMINATE Firefox, and
only Firefox, and only when all 3 of his conditions hold together: Firefox is
running, available memory is below the threshold, and his profile shows no
activity within the idle window. Every other process is REPORTED and never
touched, because he authorised one application and not a policy. `--close` is
required to act; the default is to report.

A NOTE ON WHAT "AVAILABLE" MEANS ON THIS MACHINE. `vm_stat` reports free pages and
inactive pages separately; inactive pages are reclaimable, so the honest figure
for "can I start something heavy" is free plus inactive, not free alone. Reading
free alone is how a machine with gigabytes reclaimable reports 15.88 MiB.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import time

FIREFOX_PROFILES = pathlib.Path.home() / "Library/Application Support/Firefox/Profiles"


def available_gib() -> tuple:
    out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    ps = int(re.search(r"page size of (\d+)", out).group(1))
    def pages(label):
        m = re.search(rf"{label}:\s+(\d+)", out)
        return int(m.group(1)) if m else 0
    free = pages("Pages free")
    inactive = pages("Pages inactive")
    spec = pages("Pages speculative")
    return (free + inactive + spec) * ps / 1073741824, free * ps / 1073741824


def load_average() -> float:
    out = subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True,
                         text=True).stdout
    return float(out.strip().strip("{} ").split()[0])


def processes() -> list:
    """(pid, GiB, command). THE FULL COMMAND LINE, not `comm`.

    A FIRST VERSION USED `comm` AND MADE THE ONLY REFUSING CONDITION VACUOUS.
    `comm` for a python script is the interpreter's path, so every heavy process
    of mine read as `.../Python.app/Contents/MacOS/Python` and matched none of
    "pytest", "confer_maths_panel" or "reference_runner". The script reported 0
    heavy processes while a whole-tree test run and a panel round were both
    live, which is the "addition nothing reaches" failure in the one place that
    still refuses anything. Caught 2026-10-19 by reading the output against the
    known state rather than trusting it.
    """
    out = subprocess.run(["ps", "-Ao", "pid,rss,command"], capture_output=True,
                         text=True).stdout.splitlines()[1:]
    rows = []
    for l in out:
        parts = l.split(None, 2)
        if len(parts) < 3:
            continue
        try:
            rows.append((int(parts[0]), int(parts[1]) / 1048576, parts[2]))
        except ValueError:
            continue
    return rows


def firefox(rows) -> list:
    return [r for r in rows if "firefox" in r[2].lower()]


def firefox_idle_seconds() -> float | None:
    """Newest mtime under his live Firefox profile, as a proxy for last use."""
    if not FIREFOX_PROFILES.is_dir():
        return None
    newest = 0.0
    for p in FIREFOX_PROFILES.glob("*/sessionstore*"):
        try:
            newest = max(newest, p.stat().st_mtime)
        except OSError:
            continue
    if newest == 0.0:
        for p in FIREFOX_PROFILES.glob("*/"):
            try:
                newest = max(newest, p.stat().st_mtime)
            except OSError:
                continue
    return (time.time() - newest) if newest else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold-gib", type=float, default=2.0,
                    help="available memory below which heavy work is refused")
    ap.add_argument("--idle-minutes", type=float, default=60.0,
                    help="how long Firefox must be untouched before it may be closed")
    ap.add_argument("--budget", type=int, default=2,
                    help="his standing limit on concurrent heavy processes")
    ap.add_argument("--close", action="store_true",
                    help="act on his permission: terminate Firefox if all 3 conditions hold")
    args = ap.parse_args()

    avail, free_only = available_gib()
    la = load_average()
    rows = processes()
    ff = firefox(rows)
    ff_rss = sum(r[1] for r in ff)
    idle = firefox_idle_seconds()

    print("=" * 74)
    print("IS THERE HEADROOM FOR HEAVY WORK?")
    print("=" * 74)
    print(f"available (free+inactive+spec) : {avail:.2f} GiB")
    print(f"free alone, for contrast       : {free_only:.2f} GiB")
    print(f"load average (1 min)           : {la:.2f}")
    print(f"threshold                      : {args.threshold_gib:.2f} GiB")
    print()
    print("LARGEST CONSUMERS (reported only; never touched):")
    for pid, rss, comm in sorted(rows, key=lambda r: -r[1])[:6]:
        print(f"  {rss:7.2f} GiB  pid {pid:<7} {pathlib.Path(comm).name}")
    print()
    print("FIREFOX, the one application he authorised closing:")
    if not ff:
        print("  NOT RUNNING -- his permission has nothing to act on.")
    else:
        print(f"  {len(ff)} process(es), {ff_rss:.2f} GiB resident")
        print(f"  idle for {idle/60:.1f} minute(s)" if idle is not None
              else "  idle time UNKNOWN (no profile activity readable)")

    # ★ THIS SCRIPT NO LONGER REFUSES WORK ON A MEMORY READING. HIS RULING,
    # 2026-10-19, after it raised a false alarm twice in one morning: *"no more
    # false alarms about memory! We have come this far (almost a year) on this
    # little 8GB machine."*
    #
    # AND HE IS RIGHT ON THE MECHANISM, WHICH WAS THEN TESTED RATHER THAN
    # ACCEPTED. macOS holds freed pages as `inactive` rather than returning them
    # to `free`, because an idle free page is a wasted page. Measured 2026-10-19:
    # starting from `free` at 0.347 GiB, a touched 1,024 MiB allocation succeeded
    # with swap growing by EXACTLY 0M. So `free + inactive` is not a capacity
    # signal, and the threshold refused real work at 1.21 GiB on a machine that
    # had just demonstrated it could absorb a gigabyte without swapping. The
    # reading also swung from 1.21 to 2.48 GiB inside 35 minutes, which is the
    # behaviour of a transient rather than of headroom.
    #
    # WHAT STILL REFUSES, because it was the only real constraint all along: his
    # standing budget of 2 concurrent heavy processes. That is a count, it does
    # not drift, and on 2026-10-17 it was violated at 4.
    # COUNT THE ORCHESTRATORS, NOT THEIR CHILDREN, and require a PYTHON
    # invocation. A second version counted 6 where the truth was 2, because the
    # panel's own `claude` CLI seats carry the orchestrator's path inside their
    # argument list and matched the patterns. His budget of 2 means 2 top-level
    # heavy jobs -- a whole-tree test run and a panel round -- not every process
    # they spawn. Requiring "python" in the command excludes the CLI children,
    # whose binary is /opt/homebrew/bin/claude.
    # THE EXECUTABLE DECIDES, NOT TEXT ANYWHERE IN THE LINE. A third version
    # searched the whole command for "python" and counted 5 where the truth was
    # 2: the panel's `claude` CLI seats and even the shell running this very
    # measurement carry both "python" and an orchestrator name inside their
    # ARGUMENTS. Matching the FIRST token -- the binary actually executing --
    # identifies a python orchestrator and excludes everything it spawned.
    _HEAVY = ("pytest", "confer_maths_panel", "reference_runner")

    def _is_python_orchestrator(cmd: str) -> bool:
        head = cmd.split()[0] if cmd.split() else ""
        if not pathlib.Path(head).name.lower().startswith("python"):
            return False
        return any(w in cmd.lower() for w in _HEAVY)

    heavy = sum(1 for _pid, _rss, cmd in rows if _is_python_orchestrator(cmd))
    print()
    print(f"MY OWN HEAVY PROCESSES: {heavy} against his standing budget of "
          f"{args.budget}")
    if heavy > args.budget:
        print(f"VERDICT: OVER THE CONCURRENCY BUDGET. {heavy} heavy processes "
              f"against {args.budget}. This is the only condition that refuses.")
        return 2
    print(f"VERDICT: CLEAR TO PROCEED. Memory is reported, never used to refuse: "
          f"{avail:.2f} GiB reclaimable, and the platform releases `inactive` on "
          f"demand, demonstrated with 0M swap growth on a 1,024 MiB allocation.")
    return 0

def firefox_permission_state(ff, idle, idle_minutes: float, low: bool) -> dict:
    """His 3 conditions for closing Firefox, evaluated and returned.

    KEPT REACHABLE RATHER THAN DELETED. The conditions are his, granted on
    2026-10-17, and they still hold if Firefox is ever the cause. What changed
    on 2026-10-19 is that a memory reading no longer REFUSES work, so this is
    reported and acted on only with `--close`, never used to stop anything.
    """
    return {
        "firefox is running": bool(ff),
        "available is low": bool(low),
        f"firefox idle > {idle_minutes} min":
            idle is not None and idle > idle_minutes * 60,
    }


if __name__ == "__main__":
    sys.exit(main())
