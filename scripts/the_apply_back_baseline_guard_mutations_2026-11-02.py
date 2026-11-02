#!/usr/bin/env python3
"""Revert each half of the apply-back baseline repair and require the guard to go red.

A GUARD THAT HAS NOT BEEN SHOWN TO FAIL IS NOT KNOWN TO GUARD ANYTHING. Each
mutation below undoes one property of the 2026-11-02 repair in
`bench/reference_runner_v3.py` and runs
`bench/tests/test_the_apply_back_gate_has_a_baseline_2026-11-02.py` against it.
A mutation that leaves the guard green is reported as a GAP, because it names a
property the guard does not actually hold.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE. `feedback_a_harness_must_restore_what_it_found_2026-11-01`
records a harness that destroyed the work it was measuring; the original bytes
are held in memory, written back in a `finally`, and the sha256 is compared
before the exit code is decided. If the digest does not match, this script says
so loudly and fails, rather than leaving a mutated runner behind.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "bench" / "reference_runner_v3.py"
GUARD = REPO / "bench" / "tests" / "test_the_apply_back_gate_has_a_baseline_2026-11-02.py"

#: (name, what it reverts, find, replace). Each `find` must occur exactly once.
MUTATIONS = [
    (
        "M1 the baseline is assumed green instead of measured",
        "the comparison that stops a pre-existing failure being blamed",
        "        new = failing_nodeids(r.stdout + r.stderr) - base_ids",
        "        new = failing_nodeids(r.stdout + r.stderr)  # MUTANT: no baseline",
    ),
    (
        "M2 the prose refusal is re-nested behind the command check",
        "the hoisted refusal, so prose with a command falls through to pytest",
        '    if not is_python_target(rel_target):\n'
        '        return False, ("no suite can gate a non-Python target "\n'
        '                       f"({rel_target}); a prose fix needs its falsifier, "\n'
        '                       "not pytest")\n'
        '    if not test_cmd:\n'
        '        return False, "no test_cmd configured (cannot gate)"',
        '    if not test_cmd:  # MUTANT: the prose refusal is unreachable again\n'
        '        if not is_python_target(rel_target):\n'
        '            return False, ("no suite can gate a non-Python target "\n'
        '                           f"({rel_target}); a prose fix needs its "\n'
        '                           "falsifier, not pytest")\n'
        '        return False, "no test_cmd configured (cannot gate)"',
    ),
    (
        "M3 an abnormal exit is refused without consulting the baseline's",
        "the exit-code half of the baseline, which is what stops a sandbox that "
        "already aborts from refusing every candidate",
        "        if r.returncode not in (0, 1) and r.returncode != base_rc:",
        "        if r.returncode not in (0, 1):  # MUTANT: baseline rc ignored",
    ),
    (
        "M4 the runner parses failures with its own FAILED-only matcher",
        "the shared parser, which counts collection ERRORs too",
        "from bench.build_acceptance import failing_nodeids",
        "import re as _mre  # MUTANT: a second, FAILED-only parser\n"
        "def failing_nodeids(out):\n"
        "    return frozenset(_mre.findall(r'^FAILED\\s+(\\S+)', out or '', _mre.M))",
    ),
    (
        "M5 the acceptance no longer says the sandbox was not green",
        "the disclosure that stops `ok` being read as a passing suite",
        '            return True, (f"ok (no new failures; {len(base_ids)} pre-existing"\n'
        '                          f", baseline rc{base_rc})")',
        '            return True, "ok"  # MUTANT: silent about the baseline',
    ),
]


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=600,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    tail = lines[-1] if lines else ""
    return r.returncode == 0, tail


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Revert each half of the apply-back baseline repair and "
                     "require its guard to go red."))
    ap.parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []

    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED subject passes the guard", green, tail))
        if not green:
            print("  The guard does not pass on the unmutated subject; "
                  "mutating it would prove nothing.")
            print(f"  {tail}")
            return 1

        text = original.decode()
        for name, reverts, find, repl in MUTATIONS:
            n = text.count(find)
            if n != 1:
                results.append((f"{name} [NOT APPLIED]", False,
                                f"its anchor occurs {n} times, not 1"))
                continue
            SUBJECT.write_text(text.replace(find, repl), encoding="utf-8")
            red, tail = _run_guard()
            SUBJECT.write_bytes(original)
            results.append((name, not red,
                            tail if not red else
                            f"GAP: the guard stayed GREEN. It does not hold "
                            f"{reverts}."))
    finally:
        SUBJECT.write_bytes(original)

    h1 = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    restored = h0 == h1

    print("=" * 76)
    print("DOES THE GUARD NOTICE EACH HALF OF THE REPAIR BEING UNDONE?")
    print("=" * 76)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  subject restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    if not restored:
        print("  THE SUBJECT WAS NOT RESTORED. Fix that before anything else.")
    return 0 if (n_ok == len(results) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
