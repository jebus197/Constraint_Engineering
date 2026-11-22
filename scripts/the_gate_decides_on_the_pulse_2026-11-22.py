#!/usr/bin/env python3
"""The `cy` gate calls a LIVE watchdog absent for 5/6 of every heartbeat cycle.

READY TO DROP INTO `scripts/` AFTER THE BATCH 1 COMMIT. Written and verified
from a scratch directory while that board held the tree.

WHAT IS WRONG, AND IT IS MY OWN FIX OF 2026-11-21. `hooks/cy_monitor_gate.py`
chooses its remediation advice by asking whether a `cy_watchdog.log` was
modified within `_fresh` seconds, under a comment reading *"5x the watchdog's
own cadence"*. `_fresh` IS 5x the PULSE cadence. It is applied to the LOG, whose
cadence is the watchdog's `--heartbeat-minutes`, and a healthy watchdog with
nothing to report writes NOTHING to its log between heartbeats.

OBSERVED: on 2026-11-22 the gate printed, in ONE message, *"pulse 51 s old. The
watch is healthy"* and then *"no cy_watchdog.log exists, so there is no watchdog
to tail."* Measured at that moment: pulse age 11.5 s, log age 431.6 s.

THE FIX: decide on the sibling `cy_pulse.json`, which DEFAULTS to existing and
is rewritten every interval regardless of events — it exists precisely to be the
machine-readable liveness signal a Stop gate reads. Merely NAME the log.

AND IT REPLACED A DEFECT WITH ITS MIRROR, which is why both directions are
measured here. The code before my fix globbed historical logs with no freshness
test at all, so the branch ALWAYS fired and every dead run looked watched. Mine
makes a live healthy watchdog look absent. One wrong in each direction; a fix
that merely always names the log would be the first defect again.

EVERY ANCHOR IS DERIVED, NOT TYPED. `_fresh` is read out of the gate and the
heartbeat default out of the watchdog's own argument parser, because a harness
that hardcodes the numbers it measures can only ever agree with itself — and if
either value changes, this script must move with it rather than silently keep
asserting a stale ratio.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "hooks" / "cy_monitor_gate.py").is_file():
            return cand
    fb = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
    if (fb / "hooks" / "cy_monitor_gate.py").is_file():
        return fb
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()
GATE = REPO / "hooks" / "cy_monitor_gate.py"
WATCHDOG = REPO / "scripts" / "cy_watchdog_2026-10-02.py"


def derived_fresh() -> float:
    """The gate's advice window, read from the gate."""
    m = re.search(r"_fresh\s*=\s*([0-9.]+)", GATE.read_text())
    if not m:
        raise SystemExit("the gate no longer defines _fresh; re-read the advice branch")
    return float(m.group(1))


def derived_heartbeat_seconds() -> int:
    """The watchdog's log cadence, read from its own argument parser."""
    m = re.search(r'"--heartbeat-minutes".*?default=(\d+)',
                  WATCHDOG.read_text(), re.S)
    if not m:
        raise SystemExit("the watchdog no longer declares --heartbeat-minutes")
    return int(m.group(1)) * 60


def derived_pulse_seconds() -> int:
    m = re.search(r'"--interval".*?default=(\d+)', WATCHDOG.read_text(), re.S)
    return int(m.group(1)) if m else 60


#: ★ THE FRAME IS INVERTED, AND IT HAD TO BE. 2026-11-22.
#:
#: This producer was written BEFORE the repair, so it patched the live gate
#: FORWARD and compared current against fixed. The repair then landed, the
#: `old` anchor ceased to exist, and the producer exited 1 with "the advice
#: branch has moved" -- which `bench/tests/test_todays_producers_run_2026-11-22.py`
#: correctly reported as a RED producer, found by the 55 deciding guards derived
#: from the diff. **A before-and-after measurement whose BEFORE is the live code
#: dies the moment its own recommendation is adopted.**
#:
#: So it now anchors on the LIVE code and reverts BACKWARD to reconstruct the
#: defect, which is how a mutation harness is built and for the same reason: the
#: anchor must be something that exists. The comparison is unchanged in meaning
#: -- 1 arm has the fix, 1 does not -- and the arms have swapped roles.
#:
#: THE ANCHOR IS DERIVED FROM THE SUBJECT, NOT TYPED. It is located by its first
#: and last lines and lifted whole, so a change to the block's interior cannot
#: silently stop matching. A failure to locate it REFUSES rather than measuring
#: a gate it did not alter.
#:
#: AND THE LIVE FIX IS STRONGER THAN THE ONE THIS SCRIPT PROPOSED: the proposal
#: read the pulse's MTIME, while the applied fix reads its `written_at` field
#: with mtime only as a fallback -- because the gate's own status line judges
#: liveness by that field, and 2 surfaces judging the same thing by different
#: clocks is the defect this file exists to document.
_REVERT_FIRST = "            def _pulse_age(_p):"
_REVERT_LAST = '                         and (p.parent / "cy_watchdog.log").is_file())'
_PRE_FIX = """            _wd = sorted(p for p in _ld.glob("*/cy_watchdog.log")
                         if _now - p.stat().st_mtime <= _fresh)"""


def reverted_gate(dest: pathlib.Path) -> pathlib.Path:
    """A copy of the gate with the pulse repair REMOVED, so the defect returns."""
    s = GATE.read_text()
    i = s.find(_REVERT_FIRST)
    j = s.find(_REVERT_LAST)
    if i == -1 or j == -1 or j < i:
        raise SystemExit(
            "could not locate the pulse-deciding block in the live gate; the "
            "advice branch has moved. Re-read it rather than measuring a gate "
            "this script did not alter.")
    block = s[i:j + len(_REVERT_LAST)]
    if s.count(block) != 1:
        raise SystemExit("the pulse-deciding block is not unique in the gate")
    dest.write_text(s.replace(block, _PRE_FIX, 1))
    return dest


def advice(gate: pathlib.Path, logs: pathlib.Path) -> str:
    env = dict(os.environ)
    env["CDSFL_CY_LOGS"] = str(logs)
    env["CDSFL_CY_NO_PGREP"] = "1"
    out = subprocess.run(
        [sys.executable, str(gate)],
        input=json.dumps({"cwd": str(REPO)}),
        capture_output=True, text=True, timeout=120, env=env)
    for ln in (out.stdout + out.stderr).splitlines():
        if "Monitor on" in ln:
            return ln.strip()
    return "(no advice line emitted)"


def plant(logs: pathlib.Path, pid: int, pulse_age: float, log_age: float):
    d = logs / "run1"
    d.mkdir(parents=True, exist_ok=True)
    now = time.time()
    (d / "cy_pulse.json").write_text(json.dumps(
        {"schema": 1, "written_at": now - pulse_age, "pid": pid,
         "rounds_landed": 0, "log": "x"}))
    (d / "cy_watchdog.log").write_text("[cy] ARMED\n")
    os.utime(d / "cy_pulse.json", (now - pulse_age, now - pulse_age))
    os.utime(d / "cy_watchdog.log", (now - log_age, now - log_age))


def main() -> int:
    fresh = derived_fresh()
    hb = derived_heartbeat_seconds()
    pulse = derived_pulse_seconds()

    print("DERIVED, not typed:")
    print(f"  gate advice window `_fresh`        : {fresh:.0f} s")
    print(f"  watchdog pulse cadence `--interval`: {pulse} s")
    print(f"  watchdog log cadence (heartbeat)   : {hb} s")
    print(f"  window as a multiple of the PULSE  : {fresh/pulse:.1f}x   <- what the comment claims")
    print(f"  window as a multiple of the LOG    : {fresh/hb:.4f}x <- what it actually tests")

    import sympy as sp
    from fractions import Fraction
    share = sp.Rational(int(hb - fresh), int(hb))
    frac = Fraction(int(hb - fresh), int(hb))
    assert sp.simplify(share - sp.Rational(frac.numerator, frac.denominator)) == 0
    print(f"\n  share of a heartbeat cycle a HEALTHY watchdog reads as ABSENT:")
    print(f"    sympy     {share} = {float(share):.6f}")
    print(f"    fractions {frac} = {float(frac):.6f}   (2 routes agree)")

    # A REAL live pid: a pulse naming a dead process is correctly ignored, and
    # the first version of this probe planted 999999 and measured nothing.
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(90)"])
    time.sleep(0.5)
    rc = 0
    try:
        with tempfile.TemporaryDirectory() as td:
            logs = pathlib.Path(td) / "logs"
            reverted = reverted_gate(pathlib.Path(td) / "gate_pre_fix.py")

            print("\nHEALTHY watchdog: fresh pulse, log quiet within a heartbeat")
            plant(logs, sleeper.pid, pulse_age=0, log_age=min(hb - 1, fresh * 2))
            a_live, a_old = advice(GATE, logs), advice(reverted, logs)
            print(f"  live (repaired): {a_live[:104]}")
            print(f"  reverted       : {a_old[:104]}")
            healthy_ok = ("cy_watchdog.log, matching" in a_live
                          and "no cy_watchdog.log exists" in a_old)

            print("\nDEAD watchdog: stale pulse — ANTI-VACUITY, must still read absent")
            plant(logs, sleeper.pid, pulse_age=fresh * 3, log_age=min(hb - 1, fresh * 2))
            d_live = advice(GATE, logs)
            print(f"  live (repaired): {d_live[:104]}")
            dead_ok = "no cy_watchdog.log exists" in d_live

            print(f"\n  healthy case repaired   : {healthy_ok}")
            print(f"  dead case still correct : {dead_ok}")
            rc = 0 if (healthy_ok and dead_ok) else 1
    finally:
        sleeper.terminate()
        try:
            sleeper.wait(timeout=5)
        except Exception:                                    # noqa: BLE001
            sleeper.kill()

    print("\n" + ("THE FIX HOLDS IN BOTH DIRECTIONS." if rc == 0
                  else "FAILED: the fix does not hold in both directions."))
    return rc


if __name__ == "__main__":
    #: ANSWER `--help` WITHOUT DOING THE WORK. The guard EXECUTES any
    #: script whose behaviour it cannot establish structurally, so a
    #: producer without this runs its whole body merely by being asked
    #: what it does. That fault caused 3 of the 15 board failures on
    #: 2026-11-22.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
