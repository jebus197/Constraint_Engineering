# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ac99235035821e90e61d0d9e64d2c89bc12baa39553cd1d12c4106f5aad18eb7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does a TRANSIENT interpreter-probe failure permanently refuse correct falsifiers?

THE NAMED PROPERTY THIS MEASURES. `bench.falsifier_verify._secondary_interpreter_roots`
probes every `python3` on this machine for its own installation roots and adds
them to the integrity gate's allow set, so that a falsifier legitimately
spawning a second interpreter is not refused on its ordinary import bootstrap.
Each probe is a `subprocess.run` with a 10s timeout, and the result is memoised
in a module-level cache populated once per process.

THE JOINT ROUND OF 2026-10-12 ASKED WHETHER THE PROBE'S FAIL-CLOSED DIRECTION
CAN REGRESS THE GATE TO REFUSING CORRECT FALSIFIERS, and whether a declared
fallback list should therefore be kept beside it. This script answers the first
half by execution. It simulates the cheapest realistic machine state -- ONE
interpreter slow to start under load, raising `TimeoutExpired` on a single probe
-- and then measures what happens after the machine has recovered.

WHAT IT FINDS. The fail-closed DIRECTION is right; the CACHE is the defect.
Before the repair, one transient timeout cached a partial root list for the LIFE
of the process, so every later falsifier spawning that interpreter was refused
with INTEGRITY_VIOLATION long after the transient had passed. The regression is
end-to-end and not merely a count: a CORRECT falsifier goes from CONFIRMED to
INTEGRITY_VIOLATION on 13 bootstrap reads, which is exactly the false-refusal
class the probe exists to remove.

WHY THE ANSWER IS NOT A DECLARED FALLBACK LIST. A declared list of roots was
measured at 3 of 4 interpreters against the probe's 4 of 4
(scripts/interpreter_allowlist_coverage_2026-10-12.py), so it cannot improve
the covered set, and in the common path nothing would reach it. The repair is
to stop caching an INCOMPLETE discovery, which makes a transient failure
transient; the bounded retry and the named report of unprobeable interpreters
are the other two halves.

Usage: python3 scripts/secondary_root_discovery_failure_is_not_permanent_2026-10-12.py

The spawned interpreter under test is /usr/bin/python3, which is the macOS
system interpreter the original defect class names. On a machine without it,
this script says so and exits 0 rather than reporting a result it did not
measure.
"""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, _ROOT)

from _cli_help import answer_help  # noqa: E402

#: The interpreter whose probe is made to fail, and which the falsifier spawns.
TARGET = "/usr/bin/python3"

#: A CORRECT falsifier: it demonstrates its defect by spawning a second
#: interpreter, which is the shape of the real C0050 class. It prints the
#: literal FALSIFIED token on success, so a healthy gate returns CONFIRMED.
FALSIFIER = (
    "import subprocess\n"
    f"p = subprocess.run(['{TARGET}', '-c', 'import json, ssl, sysconfig'],\n"
    "                   capture_output=True, text=True)\n"
    "assert p.returncode == 0, p.stderr[-300:]\n"
    "print('FALSIFIED')\n"
)


def _probe_fails_once_for(target):
    """Install a `subprocess.run` that raises TimeoutExpired for `target`.

    This is the transient: the interpreter is present on disk and healthy, it
    simply did not answer within the probe's 10s budget on one attempt.
    """
    real = subprocess.run

    def flaky(*a, **k):
        cmd = a[0] if a else k.get("args")
        if isinstance(cmd, (list, tuple)) and cmd and str(cmd[0]) == target:
            raise subprocess.TimeoutExpired(cmd=target, timeout=10)
        return real(*a, **k)
    return real, flaky


def main() -> int:
    answer_help(__doc__, __file__)
    os.chdir(_ROOT)
    import bench.falsifier_verify as fv

    if not os.path.isfile(TARGET):
        print(f"{TARGET} is not present on this machine; the defect class this "
              "measures does not arise here. Nothing measured, nothing claimed.")
        return 0

    print(f"repaired module state: "
          f"SECONDARY_ROOTS_DISCOVERY_ATTEMPTS = "
          f"{getattr(fv, 'SECONDARY_ROOTS_DISCOVERY_ATTEMPTS', 'ABSENT')}")

    # ── healthy baseline ────────────────────────────────────────────────────
    fv._SECONDARY_ROOTS_CACHE = None
    fv._SECONDARY_ROOTS_ATTEMPTS = 0
    healthy = fv._secondary_interpreter_roots()
    print(f"\nHEALTHY  roots = {len(healthy):3d}")
    healthy_verdict = fv.reverify_falsifier(FALSIFIER, repo_root=os.getcwd(),
                                            timeout=120)
    print(f"HEALTHY  verdict on a CORRECT falsifier = {healthy_verdict}")

    # ── one transient timeout, then the machine is healthy again ───────────
    fv._SECONDARY_ROOTS_CACHE = None
    fv._SECONDARY_ROOTS_ATTEMPTS = 0
    real, flaky = _probe_fails_once_for(TARGET)
    subprocess.run = flaky
    try:
        during = fv._secondary_interpreter_roots()
    finally:
        subprocess.run = real
    print(f"\nTRANSIENT roots = {len(during):3d}   "
          f"lost = {len(set(healthy) - set(during))}")
    cached = fv._SECONDARY_ROOTS_CACHE is not None
    print(f"TRANSIENT pass was CACHED = {cached}   "
          + ("<-- PERMANENT: the next falsifier cannot recover"
             if cached else "<-- not cached: the next falsifier retries"))

    # The machine has recovered. Does the gate recover with it?
    after = fv._secondary_interpreter_roots()
    recovered = sorted(after) == sorted(healthy)
    print(f"AFTER     roots = {len(after):3d}   recovered = {recovered}")
    after_verdict = fv.reverify_falsifier(FALSIFIER, repo_root=os.getcwd(),
                                          timeout=120)
    print(f"AFTER     verdict on the SAME correct falsifier = {after_verdict}")

    print("\nnamed report of interpreters that never answered: "
          f"{fv.secondary_interpreter_discovery_incomplete()}"
          if hasattr(fv, "secondary_interpreter_discovery_incomplete")
          else "\nnamed report: ABSENT (pre-repair module)")

    print()
    if healthy_verdict != "CONFIRMED":
        print("INCONCLUSIVE: the healthy baseline did not reach CONFIRMED, so "
              "this run measures nothing about the transient.")
        return 0
    if after_verdict == "CONFIRMED" and recovered:
        print("REPAIRED: a transient probe failure no longer refuses a correct "
              "falsifier. The gate recovered with the machine.")
    else:
        print(f"REGRESSION PRESENT: a correct falsifier went "
              f"{healthy_verdict} -> {after_verdict} because one probe timed "
              f"out once. The false-refusal class is reinstated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
