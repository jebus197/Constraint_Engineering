#!/usr/bin/env python3
"""Can the guard on `what_the_backtick_changed_2026-11-04.py` go red?

6 mutations, each required to redden a NAMED test. Anything that leaves the
board green is reported as a blind spot rather than excused.

ANCHORS ARE DERIVED by regular expression over the subject and their uniqueness
is asserted before anything is written, so a mutation cannot silently become a
no-op when the file is edited above the anchor.

THE RESTORE IS FROM BYTES THIS SCRIPT READ, never from git, and is verified by
sha256 before the result is reported.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROD = REPO / "scripts" / "what_the_backtick_changed_2026-11-04.py"
T = "bench/tests/test_what_the_backtick_changed_2026-11-04.py"

MUTATIONS = [
    ("the derivation changes 2 characters, not 1",
     r'(    before = pattern\.replace\("\[\*`\]", )"\[\*\]"(, 1\))',
     lambda m: m.group(1) + '""' + m.group(2),
     "TestThePreFixPatternIsDerivedNotRetyped::"
     "test_the_derivation_changes_exactly_one_character"),

    ("the derivation is a no-op in disguise, so it cannot reproduce the defect",
     r'(    before = pattern\.replace\(")\[\*`\]("\, "\[\*\]", 1\))',
     lambda m: m.group(1) + "ZZNOTPRESENTZZ" + m.group(2),
     # TARGET CORRECTED 2026-11-04. This was first pointed at
     # `test_it_refuses_when_the_class_is_gone`, which passes a string with no
     # markup class and only asserts that SystemExit is raised -- and under this
     # mutation it still is, for the wrong reason, so the harness reported a
     # blind spot that was its own. The test this mutation actually reaches is
     # the one that calls the derivation on the LIVE pattern.
     "TestThePreFixPatternIsDerivedNotRetyped::test_the_derivation_reproduces_the_defect"),

    ("gained and lost are transposed",
     r'(        elif after and not prior:\n            )gained(\.append\(label\))',
     lambda m: m.group(1) + "lost" + m.group(2),
     "TestThePairedTableIsAPartition::test_no_verdict_is_lost"),

    ("a cell is dropped so the table no longer partitions",
     r'(        elif not prior and not after:\n            neither \+= )1',
     lambda m: m.group(1) + "0",
     "TestThePairedTableIsAPartition::test_the_four_cells_close_on_the_population"),

    ("the second McNemar route is corrupted",
     r'(    p_mp = float\(min\(mp\.mpf\(1\), )2 \* tail(\)\))',
     lambda m: m.group(1) + "3 * tail" + m.group(2),
     "TestEveryProbabilityRestsOnTwoRoutes::"
     "test_mcnemar_agrees_across_two_implementations"),

    ("the help guard is removed so the flag measures",
     r"(    from _cli_help import answer_help\n)(    answer_help\(__doc__, __file__\)\n)",
     lambda m: m.group(1),
     "TestItRunsAndItsHelpDoesNot::test_help_answers_without_measuring"),
]


def main() -> int:
    found = PROD.read_bytes()
    digest = hashlib.sha256(found).hexdigest()
    blind, red = [], 0
    try:
        for name, pattern, build, target in MUTATIONS:
            text = found.decode()
            hits = list(re.finditer(pattern, text))
            if len(hits) != 1:
                blind.append(f"{name}: anchor matched {len(hits)} times, not 1 "
                             f"-- NOT applied, so it proves nothing")
                print(f"  {name}\n      ANCHOR AMBIGUOUS ({len(hits)}) -- not counted")
                continue
            m = hits[0]
            PROD.write_text(text[:m.start()] + build(m) + text[m.end():])
            p = subprocess.run(
                [sys.executable, "-m", "pytest", f"{T}::{target}", "-q", "--no-header"],
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
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file in
    # place and restoring it from bytes it read.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
