#!/usr/bin/env python3
"""Would the guard NOTICE if the producer stopped separating its 2 questions?

SUBJECT: `scripts/is_the_hash_chain_majority_real_2026-11-22.py`.
GUARD:   `bench/tests/test_the_majority_and_the_rise_are_2_questions_2026-11-22.py`.

A suite says whether the code passes. A harness says whether the suite would
notice if it stopped. This project has been caught by the difference: 3
assertions were made conditional, the suite stayed green, and only a harness
reported that 2 properties had gone silently unguarded.

THE 5 MUTATIONS, each a plausible way this producer could be written wrong:

  1. the rise verdict hard-wired TRUE -- a bigger denominator reported as a gain
     in coverage, which is the exact failure the producer exists to prevent
  2. the rise verdict hard-wired FALSE -- the opposite error, which would make
     the withholding paragraph unfalsifiable and therefore worthless
  3. the 2 Clopper-Pearson routes collapsed into 1 function called twice -- the
     defect measured in this project's own falsifier pairing, where statsmodels
     and scipy resolved to a single verifier
  4. the refusal on an unparseable producer replaced by a DEFAULT pair, so an
     absent measurement becomes an invented one
  5. the prior pin re-pointed at the live reading, which makes the comparison
     compare today with today and therefore always return "no change"

ANCHORS ARE DERIVED FROM THE SUBJECT. Each `old` is asserted to appear EXACTLY
ONCE before the edit; one that no longer matches is reported as a HARNESS
FAILURE rather than silently skipped, because a mutation that did not apply is
not a mutation that was survived.

IT RESTORES WHAT IT FOUND, verified by sha256 after every mutation, and ABORTS
rather than continuing against a corrupted subject.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "is_the_hash_chain_majority_real_2026-11-22.py"
GUARD = "bench/tests/test_the_majority_and_the_rise_are_2_questions_2026-11-22.py"

MUTATIONS: "list[tuple[str, str, str]]" = [
    ("the rise verdict hard-wired TRUE (a bigger denominator read as a gain)",
     "    rose = bool(pf < 0.05)",
     "    rose = True  # mutation"),
    ("the rise verdict hard-wired FALSE (the withholding made unfalsifiable)",
     "    rose = bool(pf < 0.05)",
     "    rose = False  # mutation"),
    ("the 2 Clopper-Pearson routes collapsed into 1",
     "    lo2 = float(bisect(tail_ge, mp.mpf(\"0.025\"), mp.mpf(\"0.0\"), mp.mpf(\"1.0\")))\n"
     "    hi2 = float(bisect(lambda x: -tail_le(x), -mp.mpf(\"0.025\"), mp.mpf(\"0.0\"), mp.mpf(\"1.0\")))",
     "    lo2, hi2 = float(lo1), float(hi1)  # mutation: the same route twice"),
    ("an unparseable producer DEFAULTS instead of refusing",
     "        raise SystemExit(\n"
     "            \"REFUSED: the assessment producer printed no 'hashed and valid: V of T' \"\n"
     "            \"line, so there is no live count to measure. Nothing is assumed.\")",
     "        return 160, 266  # mutation: an invented measurement"),
    ("the prior pin re-pointed at the live reading",
     "    tbl = [[v, t - v], [PRIOR_VALID, PRIOR_TOTAL - PRIOR_VALID]]",
     "    tbl = [[v, t - v], [v, t - v]]  # mutation: today against today"),
]


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _guard_passes() -> bool:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", GUARD],
        cwd=REPO, capture_output=True, text=True, timeout=900)
    return r.returncode == 0


def main() -> int:
    if not SUBJECT.is_file():
        print(f"REFUSED: no subject at {SUBJECT}.")
        return 2

    original = SUBJECT.read_text()
    sha0 = _sha(SUBJECT)
    print(f"subject sha256 {sha0[:16]}  ({len(original)} bytes)")

    print("\nbaseline: the guard must PASS against the unmutated producer")
    if not _guard_passes():
        print("  BASELINE RED -- nothing here is measurable. Stop.")
        return 2
    print("  baseline green")

    red = 0
    harness_failures: "list[str]" = []
    print()
    for i, (name, old, new) in enumerate(MUTATIONS, start=1):
        n = original.count(old)
        if n != 1:
            harness_failures.append(f"{i}. {name}: anchor appears {n} times, not 1")
            print(f"  {i}. {name}\n     HARNESS FAILURE: anchor appears {n} times")
            continue
        try:
            SUBJECT.write_text(original.replace(old, new, 1))
            noticed = not _guard_passes()
        finally:
            SUBJECT.write_text(original)
            if _sha(SUBJECT) != sha0:
                print("  RESTORE FAILED -- subject bytes differ. ABORTING.")
                return 3
        red += 1 if noticed else 0
        print(f"  {i}. {name}")
        print("     " + ("RED -- the guard noticed" if noticed
                         else "GREEN -- THE GUARD DID NOT NOTICE"))

    total = len(MUTATIONS) - len(harness_failures)
    print(f"\n{red} of {total} mutations red.")
    if harness_failures:
        print("HARNESS FAILURES (anchors that no longer match the subject):")
        for h in harness_failures:
            print(f"  {h}")
    if red == total and not harness_failures:
        print("Every way this producer could stop separating its 2 questions is held.")
        print("Subject restored byte-for-byte (sha256 unchanged).")
        return 0
    print("A GREEN mutation names a property the guard does not hold.")
    return 1


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    sys.exit(main())
