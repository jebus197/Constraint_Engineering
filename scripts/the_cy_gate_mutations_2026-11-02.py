#!/usr/bin/env python3
"""Reverse each property the cy gate claims and confirm its guard goes RED.

A test suite that cannot fail proves nothing. Each mutation below inverts ONE
property; the suite must go red for each. Any mutation that leaves it green
names a property the suite does not actually check.
"""
from __future__ import annotations
import pathlib, shutil, subprocess, sys, tempfile

HOOK = pathlib.Path.home() / ".claude" / "hooks" / "cy_monitor_gate.py"
TEST = (pathlib.Path(__file__).resolve().parents[1] / "bench" / "tests" /
        "test_the_cy_gate_refuses_while_a_run_is_live_2026-11-02.py")

MUTATIONS = [
    ("the refusal itself: exit 2 -> exit 0",
     "          f\"(cy refusal {used} of {MAX_REFUSALS} for this run)\", file=sys.stderr)\n    return 2",
     "          f\"(cy refusal {used} of {MAX_REFUSALS} for this run)\", file=sys.stderr)\n    return 0"),
    ("an ENDED run is no longer skipped",
     '        if d.get("ended"):\n            continue',
     '        if False:\n            continue'),
    ("a dead run process is no longer skipped",
     '        if not pid_alive(d.get("pid")):\n            continue',
     '        if False:\n            continue'),
    ("an unknown pid reads as DEAD instead of alive",
     "    if not pid:\n        return True",
     "    if not pid:\n        return False"),
    ("the staleness threshold swallows every stale pulse",
     "PULSE_STALE_SECONDS = 180",
     "PULSE_STALE_SECONDS = 10 ** 9"),
    ("an abandoned pulse never ages out",
     "MAX_PULSE_AGE_HOURS = 36",
     "MAX_PULSE_AGE_HOURS = 10 ** 9"),
    ("parking stops working",
     "    if parked():\n        return 0",
     "    if False:\n        return 0"),
    ("the budget becomes unbounded, so a session CAN be trapped",
     "MAX_REFUSALS = 60",
     "MAX_REFUSALS = 10 ** 9"),
    # THESE 2 WERE REWRITTEN 2026-11-02. The first pair was INEFFECTIVE: one
    # mutation merely PREPENDED text (removing nothing), the other removed the
    # first of TWO occurrences of `tail -f`. Both left the suite green, and
    # that green said nothing about the guard -- a mutation that does not
    # invert the property tests nothing, exactly like a SKIP. Reporting such a
    # green as "unguarded" would have been a false finding about my own guard.
    ("the refusal no longer names Monitor, the channel that works",
     '"Monitor on the run\'s cy_watchdog.log, matching "',
     '"something, somehow "'),
    ("the refusal no longer names tail -f, the channel that FAILED",
     '"`tail -f | grep` under a background shell delivers NOTHING, because "\n        "Bash background notifies on exit and `tail -f` never exits — that is "',
     '"a background shell delivers NOTHING, because "\n        "it notifies on exit — that is "'),
    ("a corrupt pulse crashes instead of being skipped",
     '        except Exception:                                    # noqa: BLE001\n            continue\n        age = now',
     '        except Exception:                                    # noqa: BLE001\n            raise\n        age = now'),
]


def run_suite() -> bool:
    p = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                        "--no-header", "-x"],
                       capture_output=True, text=True, timeout=300)
    return p.returncode == 0


def main() -> int:
    original = HOOK.read_text()
    print("=" * 78)
    print("CY GATE MUTATION TEST")
    print("=" * 78)
    if not run_suite():
        print("  THE SUITE IS ALREADY RED. Nothing can be concluded about the")
        print("  mutations until it is green. Stopping.")
        return 2
    print("  baseline: GREEN\n")
    red = 0
    try:
        for label, old, new in MUTATIONS:
            if original.count(old) != 1:
                print(f"  [SKIP  ] {label}")
                print(f"           anchor appears {original.count(old)} times, not 1 "
                      f"-- the mutation cannot be applied, so nothing is tested")
                continue
            HOOK.write_text(original.replace(old, new, 1))
            green = run_suite()
            if green:
                print(f"  [GREEN ] {label}")
                print(f"           *** THE SUITE DID NOT NOTICE. This property is "
                      f"NOT guarded. ***")
            else:
                red += 1
                print(f"  [RED   ] {label}")
    finally:
        HOOK.write_text(original)
    applied = sum(1 for _l, o, _n in MUTATIONS if original.count(o) == 1)
    print(f"\n  {red} of {applied} applied mutation(s) turned the suite RED")
    print(f"  hook restored to its original text: "
          f"{HOOK.read_text() == original}")
    return 0 if red == applied and applied else 1


if __name__ == "__main__":
    sys.exit(main())
