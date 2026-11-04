#!/usr/bin/env python3
"""Can the guard on the severity-frame producer actually go red?

A guard that cannot fail is a description. This applies 5 mutations to the
producer and requires each to turn a NAMED test red, and it reports any that
leaves the board green as a blind spot rather than excusing it.

ANCHORS ARE DERIVED FROM THE SUBJECT, never spelled out here, so a mutation
cannot quietly become a no-op when the producer is edited above the anchor. Each
anchor is located by a regular expression over the file and its uniqueness is
asserted before anything is written.

THE RESTORE IS FROM BYTES THIS SCRIPT READ, never from git, because
`git checkout --` discards uncommitted work and on 2026-11-01 destroyed the very
edit under test. Each file is written back and verified by sha256.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROD = REPO / "scripts" / "the_severity_frame_counts_one_run_twice_2026-11-04.py"
TESTS = "bench/tests/test_the_severity_frame_counts_one_run_twice_2026-11-04.py"

#: (name, regex locating the anchor, replacement built from the match, test it should redden)
MUTATIONS = [
    ("floors hardcoded instead of read from the guard",
     r"(    for name in FLOORED:\n)",
     lambda m: m.group(1) + "        out[name] = 9999\n        continue\n",
     "TestTheFloorsAreReadFromTheGuardNotCopied::"
     "test_a_moved_floor_moves_the_producers_answer"),

    ("the symlink exclusion made inert",
     r"real = \[p for p in files if (not p\.parent\.is_symlink\(\))\]",
     lambda m: "real = [p for p in files if True]",
     "TestTheDefectIsStillThere::test_the_arithmetic_closes"),

    ("exactness claimed without comparing multisets",
     r'"duplicate_is_exact": (sorted\(from_link\) == sorted\(target_sev\))',
     lambda m: '"duplicate_is_exact": (len(from_link) != len(target_sev))',
     "TestTheDefectIsStillThere::test_the_duplicate_is_exact_not_merely_similar"),

    ("the second Wilson route corrupted",
     r'(    z = mp\.mpf\("1\.9)(59963984540054235524594430520551527955"\))',
     lambda m: m.group(1) + '0"' + ")"[1:],
     "TestEveryQuantityRestsOnTwoRoutes::test_wilson_agrees_across_two_implementations"),

    ("the help guard removed so the flag measures",
     r"(    from _cli_help import answer_help\n)(    answer_help\(__doc__, __file__\)\n)",
     lambda m: m.group(1),
     "TestItRunsAndItsHelpDoesNot::test_help_answers_without_measuring"),
]


def main() -> int:
    found = PROD.read_bytes()
    digest = hashlib.sha256(found).hexdigest()
    blind: list[str] = []
    red = 0
    try:
        for name, pattern, build, target in MUTATIONS:
            text = found.decode()
            hits = list(re.finditer(pattern, text))
            if len(hits) != 1:
                blind.append(f"{name}: anchor matched {len(hits)} times, not 1 "
                             f"-- the mutation was NOT applied and proves nothing")
                print(f"  {name}\n      ANCHOR AMBIGUOUS ({len(hits)} matches) -- not counted")
                continue
            m = hits[0]
            PROD.write_text(text[:m.start()] + build(m) + text[m.end():])
            p = subprocess.run(
                [sys.executable, "-m", "pytest", f"{TESTS}::{target}", "-q", "--no-header"],
                cwd=REPO, capture_output=True, text=True, timeout=900)
            PROD.write_bytes(found)
            if p.returncode != 0:
                red += 1
                print(f"  {name}\n      RED, as required, on {target.split('::')[-1]}")
            else:
                blind.append(f"{name}: {target} stayed GREEN")
                print(f"  {name}\n      STILL GREEN -- blind spot on {target.split('::')[-1]}")
    finally:
        PROD.write_bytes(found)
        ok = hashlib.sha256(PROD.read_bytes()).hexdigest() == digest
        print(f"\n  {PROD.name} restored, sha256 verified: {ok}")
        if not ok:
            print("  THE RESTORE FAILED. Do not commit; compare against git HEAD.")
            return 2
    print(f"  {red} of {len(MUTATIONS)} mutations went red")
    if blind:
        print("\n  BLIND SPOTS, reported rather than excused:")
        for b in blind:
            print(f"    - {b}")
        return 1
    print("  no blind spots")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NOT run the measurement: this script WRITES, mutating a
    # tracked file in place and restoring it. Answering the flag by working
    # would edit the repository to print usage.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
