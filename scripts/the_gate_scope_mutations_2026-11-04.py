#!/usr/bin/env python3
"""Reverse each half of the gate-scope repair and require the guard to go red.

A guard that has not been taken red is a hypothesis about what it detects. This
reverts the repair 7 ways across its 2 subjects -- `hooks/pre-commit` and
`scripts/the_gate_board_is_not_the_suite_2026-11-04.py` -- and requires
`bench/tests/test_the_gate_board_is_not_the_suite_2026-11-04.py` to fail on
each.

2 FAULTS IN THIS HARNESS'S PREDECESSOR, AVOIDED HERE BY CONSTRUCTION. Its
sibling of the same night hardcoded its anchors: one held a literal character
where the subject holds an escape, because the escape was decoded in transit on
the way to disk, so the anchor could never match; and a table was emptied with
an empty dict on the left of an `or`, which in Python evaluates to the SECOND
operand because an empty dict is falsy, so the mutation changed nothing and the
harness reported a pass as a pass. So every anchor here is READ FROM the file
it mutates, and any substitution that changes 0 bytes is refused outright
rather than counted.

RESTORATION RESTORES WHAT WAS FOUND, not what git holds: the working tree
carries uncommitted work, so `git checkout --` would discard it. The original
bytes are held in memory and written back in a `finally`, then verified by
sha256.

Usage: python3 scripts/the_gate_scope_mutations_2026-11-04.py
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
GATE = REPO / "hooks" / "pre-commit"
PROD = REPO / "scripts" / "the_gate_board_is_not_the_suite_2026-11-04.py"
GUARD = REPO / "bench" / "tests" / "test_the_gate_board_is_not_the_suite_2026-11-04.py"


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _guard_is_red() -> tuple:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO))
    tail = [l for l in r.stdout.splitlines() if l.strip()]
    return r.returncode != 0, (tail[-1] if tail else "(no output)")


#: (label, file, find, replace). `find` is matched against the live bytes, so a
#: mutation whose anchor has moved is reported as an anchor failure rather than
#: silently counted as a pass.
MUTATIONS = [
    ("the gate's scope echo is deleted", GATE,
     'echo "pre-commit: that board is the gate\'s ${_GUARD_FILES} guard files '
     'of ${_SUITE_FILES} in bench/tests/ -- NOT the suite."',
     ': # scope line removed'),
    ("the scope line is hardcoded instead of counted", GATE,
     '_GUARD_FILES=$(printf \'%s\\n\' "$GUARDS" | grep -c \'[^[:space:]]\')',
     '_GUARD_FILES=127'),
    ("the suite-file count is hardcoded", GATE,
     '_SUITE_FILES=$(ls bench/tests/test_*.py 2>/dev/null | wc -l | tr -d \' \')',
     '_SUITE_FILES=811'),
    ("the producer citation is removed from the gate", GATE,
     'For the test-count share: python3 scripts/the_gate_board_is_not_the_suite_2026-11-04.py',
     'For the test-count share: ask someone'),
    ("guard_list stops reading the gate and returns a constant", PROD,
     '    return [l.strip() for l in m.group(1).splitlines() if l.strip()]',
     '    return ["bench/tests/test_alpha.py"]'),
    ("collect returns a constant instead of collecting", PROD,
     '''    r = subprocess.run(
        [sys.executable, "-m", "pytest", *[str(t) for t in targets],
         "--collect-only", "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO))''',
     '''    return 2540
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *[str(t) for t in targets],
         "--collect-only", "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO))'''),
    ("a failed collection reports 0 rather than admitting it failed", PROD,
     '            return int(m.group(1))\n    return -1',
     '            return int(m.group(1))\n    return 0'),
]


def main() -> int:
    answer_help(__doc__, __file__)
    for p in (GATE, PROD, GUARD):
        if not p.is_file():
            print(f"missing subject: {p}")
            return 3

    red0, line0 = _guard_is_red()
    print(f"baseline: guard red = {red0}   [{line0}]")
    if red0:
        print("THE GUARD IS ALREADY RED. Every mutation below would 'pass' for")
        print("the wrong reason, so the measurement is void.")
        return 3

    originals = {p: p.read_bytes() for p in (GATE, PROD)}
    shas = {p: _sha(p) for p in (GATE, PROD)}
    results = []
    try:
        for label, path, find, repl in MUTATIONS:
            text = path.read_text(encoding="utf-8")
            n = text.count(find)
            if n != 1:
                results.append((label, None,
                                f"ANCHOR MATCHED {n} TIMES, not 1 -- not a test"))
                print(f"  [ANCHOR] {label}: matched {n} times")
                continue
            mutated = text.replace(find, repl)
            if mutated == text:
                results.append((label, None,
                                "the substitution changed 0 bytes -- not a test"))
                print(f"  [NO-OP]  {label}")
                continue
            path.write_text(mutated, encoding="utf-8")
            try:
                red, line = _guard_is_red()
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
    if len(bad) > 3:
        print(f"  ... and {len(bad) - 3} further non-red result(s) of "
              f"{len(bad)} total, all listed above")
    return 0 if red_n == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())
