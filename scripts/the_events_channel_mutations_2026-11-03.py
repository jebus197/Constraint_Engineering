#!/usr/bin/env python3
"""Revert the watchdog's events channel and require its guard to go red.

A FIX I HAVE NOT TRIED TO BREAK IS A HYPOTHESIS. The subject is B20's
precondition, built 2026-11-03: `probe()` in `scripts/cy_watchdog_2026-10-02.py`
now returns the events it emitted as a 7th element, and the mid-run
`write_pulse` carries them under their own key, so an actuator can learn WHICH
event fired without parsing prose.

7 MUTATIONS, EACH UNDOING A DIFFERENT PROPERTY:
  M1  the final return drops the events        -> the channel does not exist
  M2  the recorder records nothing             -> the channel is always empty
  M3  the PROCESS GONE return drops them       -> 1 of 2 exits is silent
  M4  an emission bypasses the recorder        -> stdout and the return DISAGREE
  M5  the pulse drops the events key           -> nothing crosses the file
  M6  the events are written into `verdict`    -> a mid-run event reads as an outcome
  M7  the bound is removed                     -> a gate-read file grows unboundedly

M4 IS THE ONE THAT MATTERS MOST and it is why the guard compares stdout against
the return value rather than asserting the list is non-empty. A `say()` added
inside `probe()` without recording leaves an event on stdout and absent from the
return, and only a comparison of the 2 forms can see it. If M4 does not go red,
the guard is checking that something was recorded rather than that EVERYTHING
emitted was recorded, and the next emission added to probe will go unnoticed.

M6 GUARDS A SEMANTIC BOUNDARY RATHER THAN A MECHANISM. `verdict` means the final
outcome. Folding the latest mid-run event into it would make every live pulse
look like it carried a result, which is the failure shape this project records
as a verdict reader treating "NOT FALSIFIED" as "FALSIFIED": a field whose
meaning quietly widens is read under its old meaning.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE, per
`feedback_a_harness_must_restore_what_it_found_2026-11-01`: the original bytes
are held in memory, written back in a `finally`, and the sha256 compared before
the exit code is decided. This matters more than usual here, because the subject
is the live watchdog that monitors every experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "cy_watchdog_2026-10-02.py"
GUARD = (REPO / "bench" / "tests"
         / "test_the_watchdog_events_reach_the_pulse_2026-11-03.py")

MUTATIONS = [
    ("M1 the final return drops the events",
     "the events channel's existence on the ordinary exit",
     "    return offset, last_size, last_change, rounds, False, _cpu_seconds(pid), events",
     "    return offset, last_size, last_change, rounds, False, _cpu_seconds(pid)  # MUTANT"),

    ("M2 the recorder records nothing",
     "the recording itself, leaving the channel permanently empty",
     "        events.append((kind, msg))\n        say(kind, msg)",
     "        say(kind, msg)  # MUTANT: records nothing"),

    ("M3 the PROCESS GONE return drops the events",
     "the second of probe's 2 exits, which is the one an actuator most needs",
     "        return offset, last_size, last_change, rounds, True, last_cpu, events",
     "        return offset, last_size, last_change, rounds, True, last_cpu, []  # MUTANT"),

    ("M4 an emission bypasses the recorder",
     "the agreement between stdout and the return, which is the only property "
     "that catches a future unrecorded emission",
     '            for mt in matches:\n                ev("TROUBLE", mt)',
     '            for mt in matches:\n                say("TROUBLE", mt)  # MUTANT'),

    ("M5 the pulse drops the events key",
     "the crossing from process memory to a file a reader can open",
     '            "events": [{"kind": k, "message": str(m)[:300]}\n'
     '                       for k, m in (events or [])][-8:],',
     '            # MUTANT: the events never reach the file'),

    ("M6 the events are written into `verdict`",
     "the boundary between a mid-run event and a final outcome",
     '            "verdict": verdict,',
     '            "verdict": verdict or (events[-1][0] if events else None),  # MUTANT'),

    ("M7 the bound is removed",
     "the bound on a file a Stop gate reads on every stop",
     '                       for k, m in (events or [])][-8:],',
     '                       for k, m in (events or [])],  # MUTANT: unbounded'),
]


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=900,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    return r.returncode == 0, (lines[-1] if lines else "")


def main() -> int:
    argparse.ArgumentParser(
        description=("Revert the watchdog's events channel and require its "
                     "guard to go red.")).parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED watchdog passes the guard", green, tail))
        if not green:
            print("  The guard fails on the unmutated watchdog; mutating it")
            print(f"  would prove nothing. {tail}")
            return 1
        text = original.decode()
        for name, reverts, find, repl in MUTATIONS:
            n = text.count(find)
            if n != 1:
                results.append((f"{name} [NOT APPLIED]", False,
                                f"its anchor occurs {n} times, not 1"))
                continue
            SUBJECT.write_text(text.replace(find, repl, 1), encoding="utf-8")
            red, tail = _run_guard()
            SUBJECT.write_bytes(original)
            results.append((name, not red,
                            tail if not red else
                            f"GAP: the guard stayed GREEN, so it does not hold "
                            f"{reverts}."))
    finally:
        SUBJECT.write_bytes(original)

    h1 = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    restored = h0 == h1
    print("=" * 76)
    print("DOES THE GUARD NOTICE THE EVENTS CHANNEL BEING UNDONE?")
    print("=" * 76)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  watchdog restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    if not restored:
        print("  THE WATCHDOG WAS NOT RESTORED. It monitors every experiment;")
        print("  fix that before anything else.")
    return 0 if (n_ok == len(results) == len(MUTATIONS) + 1 and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
