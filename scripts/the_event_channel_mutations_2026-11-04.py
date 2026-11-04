#!/usr/bin/env python3
"""Reverse the event channel 5 ways and require its guard to go red.

`bench/tests/test_the_event_channel_reaches_the_actuator_2026-11-04.py` asserts
that the watchdog's event channel reaches the actuator's evidence and does NOT
reach its decision. A guard that has not been taken red is a hypothesis about
what it detects, so each half of the channel is reversed here and the guard must
fail on every one.

THE CHANNEL HAS 2 ENDS AND BOTH ARE MUTATED. Dropping the field in the WRITER
and dropping the read in the CONSUMER are different defects that a single-ended
harness would miss: a test that only planted a pulse by hand would never notice
the writer, and one that only called write_pulse would never notice the reader.

AND THE 5TH MUTATION IS THE INTERESTING ONE: it makes an event kind DRIVE the
decision, which is the widening the actuator's own docstring says must not
happen. The guard has a test for that design decision precisely because an
absence cannot be asserted by noticing nothing.

RESTORATION RESTORES WHAT WAS FOUND, not what git holds, because the working
tree carries uncommitted work; the bytes are held in memory and verified by
sha256 in a `finally`.

Usage: python3 scripts/the_event_channel_mutations_2026-11-04.py
Exit 0 iff every mutation takes the guard red.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
WATCHDOG = REPO / "scripts" / "cy_watchdog_2026-10-02.py"
ACTUATOR = REPO / "bench" / "tools" / "cy_actuator_2026-11-03.py"
GUARD = (REPO / "bench" / "tests"
         / "test_the_event_channel_reaches_the_actuator_2026-11-04.py")

MUTATIONS = [
    ("the WRITER stops recording the events", WATCHDOG,
     '            "events": [{"kind": k, "message": str(m)[:300]}\n'
     '                       for k, m in (events or [])][-8:],',
     '            "events": [],'),
    ("the writer keeps only the KIND and drops the message", WATCHDOG,
     '            "events": [{"kind": k, "message": str(m)[:300]}\n'
     '                       for k, m in (events or [])][-8:],',
     '            "events": [{"kind": k} for k, _m in (events or [])][-8:],'),
    ("the cap moves from 8 to 3", WATCHDOG,
     '                       for k, m in (events or [])][-8:],',
     '                       for k, m in (events or [])][-3:],'),
    ("the cap keeps the FIRST events rather than the most recent", WATCHDOG,
     '                       for k, m in (events or [])][-8:],',
     '                       for k, m in (events or [])][:8],'),
    ("the CONSUMER stops reading the channel", ACTUATOR,
     '          "events": pulse.get("events") or []}',
     '          "events": []}'),
    ("an event kind DRIVES the decision, widening the narrow table", ACTUATOR,
     '    if exit_code == PAUSED:',
     '    if any(e.get("kind") == "TROUBLE"\n'
     '           for e in (pulse.get("events") or [])):\n'
     '        return {"decision": "RESUME", "reason": "trouble seen",\n'
     '                "evidence": ev}\n'
     '    if exit_code == PAUSED:'),
]


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _red():
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO))
    tail = [l for l in r.stdout.splitlines() if l.strip()]
    return r.returncode != 0, (tail[-1] if tail else "(no output)")


def main() -> int:
    answer_help(__doc__, __file__)
    for p in (WATCHDOG, ACTUATOR, GUARD):
        if not p.is_file():
            print(f"missing subject: {p}")
            return 3

    red0, line0 = _red()
    print(f"baseline: guard red = {red0}   [{line0}]")
    if red0:
        print("THE GUARD IS ALREADY RED, so every mutation below would 'pass'")
        print("for the wrong reason and the measurement is void.")
        return 3

    originals = {p: p.read_bytes() for p in (WATCHDOG, ACTUATOR)}
    shas = {p: _sha(p) for p in originals}
    results = []
    try:
        for label, path, find, repl in MUTATIONS:
            text = path.read_text(encoding="utf-8")
            n = text.count(find)
            if n != 1:
                results.append((label, None, f"ANCHOR MATCHED {n} TIMES, not 1"))
                print(f"  [ANCHOR] {label}: matched {n} times")
                continue
            mutated = text.replace(find, repl)
            if mutated == text:
                results.append((label, None, "changed 0 bytes -- not a test"))
                print(f"  [NO-OP]  {label}")
                continue
            path.write_text(mutated, encoding="utf-8")
            try:
                red, line = _red()
            finally:
                path.write_bytes(originals[path])
            results.append((label, red, line))
            print(f"  [{'RED ' if red else 'GREEN'}] {label}\n           {line}")
    finally:
        for p, b in originals.items():
            p.write_bytes(b)
            if _sha(p) != shas[p]:
                print(f"RESTORE FAILED for {p}; the tree is NOT as it was found")
                return 3
        print("\nboth subjects restored byte-identically (sha256 verified)")

    red_n = sum(1 for _, r, _ in results if r is True)
    bad = [(l, m) for l, r, m in results if r is not True]
    print(f"\nmutations taken RED: {red_n} of {len(MUTATIONS)}")
    for label, msg in bad:
        print(f"  NOT RED: {label} -- {msg}")
    return 0 if red_n == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())
