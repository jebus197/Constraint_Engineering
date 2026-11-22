#!/usr/bin/env python3
"""Would the guard NOTICE if the pre-flight stopped matching the gate?

A suite says whether the code passes. A harness says whether the suite would
notice if it stopped -- and this project has already been caught once by the
difference: on 2026-11-21 three assertions were made conditional, the suite
stayed green, and `the_status_flag_mutations_2026-11-21.py` reported 5 of 8 red
with 2 properties silently unguarded.

SUBJECT: `scripts/note_ratchet_preflight_2026-11-01.py`.
GUARD:   `bench/tests/test_the_preflight_population_is_the_gates_2026-11-22.py`.

EACH MUTATION REVERTS ONE HALF OF THE 2026-11-22 REPAIR, so a mutation that
stays GREEN names a property the guard does not actually hold:

  1. the gate population widened back to `changed_notes()`
  2. the index read reverted to the double-colon form
  3. a NEW note skipped instead of held to a baseline of 0
  4. the `.md` suffix requirement dropped
  5. the `seat_evidence` exclusion dropped
  6. the `experimental_notes/` prefix requirement dropped
  7. the tree scored in place of the index
  8. the tree/index divergence no longer recorded

ANCHORS ARE DERIVED FROM THE SUBJECT, NEVER TYPED FROM MEMORY. Every `old`
string below is asserted to appear EXACTLY ONCE in the live file before the
edit is made, so a mutation that no longer matches is reported as a HARNESS
failure rather than silently skipped -- which is how 2 of 5 misses were
mis-attributed on 2026-11-04.

IT RESTORES WHAT IT FOUND. The subject is backed up byte-exactly, restored
after every mutation, and the restoration is verified by sha256 before the next
one is applied. If a restore ever fails to reproduce the original bytes the run
ABORTS rather than continuing against a corrupted subject.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "note_ratchet_preflight_2026-11-01.py"
GUARD = "bench/tests/test_the_preflight_population_is_the_gates_2026-11-22.py"

MUTATIONS: list[tuple[str, str, str]] = [
    (
        "gate population widened back to changed_notes()",
        #: ANCHORED ON THE 2 LINES TOGETHER. `return sorted(set(out))` ALONE
        #: appears twice -- `changed_notes` ends the same way -- and the
        #: harness reported that as a HARNESS FAILURE rather than mutating the
        #: wrong function silently, which is the whole point of asserting the
        #: anchor count before the edit.
        "            out.append(path)\n    return sorted(set(out))",
        "            out.append(path)\n    return changed_notes()",
    ),
    (
        "index read reverted to the double-colon form",
        '        staged = _score_rev("", f)',
        '        staged = _score_rev(":", f)',
    ),
    (
        "a NEW note skipped instead of held to a baseline of 0",
        "        base = 0 if head is None else head",
        "        base = head if head is not None else 10**9",
    ),
    (
        "the .md suffix requirement dropped",
        '        if (path.startswith(GATE_DIR) and path.endswith(".md")',
        '        if (path.startswith(GATE_DIR) and path.endswith((".md", ".txt"))',
    ),
    (
        "the seat_evidence exclusion dropped",
        "                and not path.startswith(GATE_EXCLUDE)):",
        "                and True):",
    ),
    (
        "the experimental_notes prefix requirement dropped",
        '        if (path.startswith(GATE_DIR) and path.endswith(".md")\n'
        "                and not path.startswith(GATE_EXCLUDE)):",
        '        if (path.endswith(".md")\n'
        "                and not path.startswith(GATE_EXCLUDE)):",
    ),
    (
        "the tree scored in place of the index",
        '        staged = _score_rev("", f)\n'
        "        if staged is None:",
        "        staged = _findings(REPO / f, logical=f) if (REPO / f).is_file() else None\n"
        "        if staged is None:",
    ),
    (
        "the tree/index divergence no longer recorded",
        "        if tree is not None and tree != staged:\n"
        "            divergent.append((f, staged, tree))",
        "        if False:\n"
        "            divergent.append((f, staged, tree))",
    ),
]


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _run_guard() -> bool:
    """True when the guard PASSES (so a mutation here means it did NOT notice)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", GUARD],
        cwd=REPO, capture_output=True, text=True, timeout=900)
    return r.returncode == 0


def main() -> int:
    original = SUBJECT.read_text()
    original_sha = _sha(SUBJECT)
    print(f"subject sha256 {original_sha[:16]}  ({len(original)} bytes)")

    print("\nbaseline: the guard must PASS against the unmutated subject")
    if not _run_guard():
        print("  BASELINE RED — the harness cannot measure anything. Stop.")
        return 2
    print("  baseline green")

    red = 0
    harness_failures: list[str] = []
    print()
    for i, (name, old, new) in enumerate(MUTATIONS, start=1):
        n = original.count(old)
        if n != 1:
            harness_failures.append(f"{i}. {name}: anchor appears {n} times, not 1")
            print(f"  {i}. {name}\n     HARNESS FAILURE: anchor appears {n} times")
            continue
        try:
            SUBJECT.write_text(original.replace(old, new, 1))
            noticed = not _run_guard()
        finally:
            SUBJECT.write_text(original)
            if _sha(SUBJECT) != original_sha:
                print("  RESTORE FAILED — subject bytes differ. ABORTING.")
                return 3
        red += 1 if noticed else 0
        print(f"  {i}. {name}\n     {'RED — the guard noticed' if noticed else 'GREEN — THE GUARD DID NOT NOTICE'}")

    total = len(MUTATIONS) - len(harness_failures)
    print(f"\n{red} of {total} mutations red.")
    if harness_failures:
        print("HARNESS FAILURES (anchors that no longer match the subject):")
        for h in harness_failures:
            print(f"  {h}")
    if red == total and not harness_failures:
        print("Every reverted half of the repair is held by the guard.")
        return 0
    print("A GREEN mutation names a property the guard does not hold.")
    return 1


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
