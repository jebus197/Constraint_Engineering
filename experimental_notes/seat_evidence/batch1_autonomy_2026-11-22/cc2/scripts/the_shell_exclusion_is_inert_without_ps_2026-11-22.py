# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'batch1_autonomy_2026-11-22', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: fe93c757fc861c1061ddbcac560870b2f9146d30a5651e4a94ac34de31d09b53
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The shell exclusion the B205 widening relies on is inert where `ps` is denied.

WHAT THE CODE CLAIMS. `scripts/blocker_triage.py` widened `_BOARD_PATTERNS` to
`pytest.*bench/tests` under B205 and justified the one false positive it admits:

    It also matches a waiter shell whose command line merely NAMES pytest --
    and `cy._is_shell` already returns True for that shell and False for the
    real pytest, so the shell exclusion documented above removes the only false
    positive this introduces.

THE CLAIM IS CONDITIONAL ON `ps` AND DOES NOT SAY SO. `cy._is_shell` is
documented "unreadable -> KEEP, fail toward refusing", which is the correct
direction for `hooks/cy_monitor_gate.py` and the WRONG one for the triage,
whose own docstring promises the opposite:

    FAIL-SAFE TOWARD WRITING: any failure of this predicate returns ''.

So where `ps` is unavailable or refused by sandbox policy, a SHELL that merely
names pytest is reported as a running commit board.

WHY THAT IS NOT CONFINED TO THE TRIAGE. `hooks/work_not_narrate.py` stands its
entire Stop gate down on this predicate:

    if _a_commit_board_is_running():
        return 0

A shell naming pytest therefore switches the Stop gate OFF. B205(c) set out to
make the gate stand down DURING a board; this makes it stand down for a string
on a command line.

HOW THIS IS MEASURED. A real shell is planted, and `pgrep` is stubbed to return
ONLY that shell, so the correct answer is unambiguously ''. `ps` is left real in
arm A and denied in arm B. On a machine where `ps` works, arm A returns '' and
arm B returns the pid -- that difference IS the defect. On a sandbox where `ps`
is already denied, both arms return the pid. It edits nothing.

NOTE ON WHAT THIS DOES NOT CLAIM. It does not claim the predicate is wrong
whenever it fires. Where a real board is also running the verdict is right and
only the pid attributed is wrong. The defect is the case where NO board runs.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    return mod


def _arm(bt, shell_pid: str, deny_ps: bool) -> str:
    """a_commit_board_is_running() with pgrep stubbed to the planted shell."""
    real = bt.subprocess.run

    class _R:
        def __init__(self, out):
            self.stdout, self.stderr, self.returncode = out, "", 0

    def fake(cmd, *a, **k):
        if cmd and str(cmd[0]) == "pgrep":
            return _R(shell_pid + "\n")
        if cmd and str(cmd[0]) == "ps" and deny_ps:
            raise PermissionError(1, "Operation not permitted: 'ps'")
        return real(cmd, *a, **k)

    bt.subprocess.run = fake
    # cy_monitor_gate is imported fresh inside the predicate, so `ps` denial has
    # to reach ITS module too; the predicate loads it by path each call.
    cy_path = REPO / "hooks" / "cy_monitor_gate.py"
    cy = _load("bt_cy_gate", cy_path)
    cy_real = cy.subprocess.run

    def cy_fake(cmd, *a, **k):
        if cmd and str(cmd[0]) == "ps" and deny_ps:
            raise PermissionError(1, "Operation not permitted: 'ps'")
        return cy_real(cmd, *a, **k)

    cy.subprocess.run = cy_fake
    try:
        return bt.a_commit_board_is_running()
    finally:
        bt.subprocess.run = real
        cy.subprocess.run = cy_real


def main() -> int:
    bt = _load("bt_shell_probe", REPO / "scripts" / "blocker_triage.py")

    proc = subprocess.Popen(["/bin/zsh", "-c", "sleep 20"])
    time.sleep(0.3)
    pid = str(proc.pid)
    try:
        print(f"  planted a real /bin/zsh at pid {pid}; pgrep is stubbed to return")
        print("  ONLY that pid, so a correct predicate MUST return '' (a shell is")
        print("  not a board). No pytest is involved in either arm.")
        print()
        a = _arm(bt, pid, deny_ps=False)
        b = _arm(bt, pid, deny_ps=True)
        print(f"    arm A, ps as the machine provides it : {a!r}")
        print(f"    arm B, ps denied by policy           : {b!r}")
        print()
        if b:
            print("  FALSIFIED: a shell was reported as a running commit board.")
            print("  scripts/blocker_triage.py then refuses every triage write, and")
            print("  hooks/work_not_narrate.py returns 0 -- the Stop gate is OFF.")
            if a:
                print("  (arm A agrees because `ps` is ALREADY denied on this machine,")
                print("   which is the condition under test, not a confound.)")
            return 1
        print("  not demonstrated: the shell exclusion held in both arms")
        return 0
    finally:
        proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
