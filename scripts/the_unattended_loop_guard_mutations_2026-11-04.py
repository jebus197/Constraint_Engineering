#!/usr/bin/env python3
"""Can the new guard on the unattended-loop producer go red?

6 mutations, each required to redden a NAMED test. The first restores the exact
swallowed exception that was repaired, so the guard is shown able to catch a
regression to the state it was written for, and not merely to pass today.

ANCHORS ARE DERIVED by regular expression and their uniqueness asserted before
anything is written. THE RESTORE IS FROM BYTES THIS SCRIPT READ, verified by
sha256 before the result is reported.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROD = REPO / "scripts" / "the_unattended_loop_has_never_been_reachable_2026-11-04.py"
T = "bench/tests/test_the_unattended_loop_producer_2026-11-04.py"

MUTATIONS = [
    ("the swallowed exception is RESTORED, exactly as it was repaired",
     r"(?s)                except \(json\.JSONDecodeError.*?unreadable\.append\(\(where, type\(err\)\.__name__\)\)",
     lambda m: "                except Exception:\n                    pass",
     "TestTheUnevaluableCounterActuallyCounts::"
     "test_a_malformed_file_is_counted_not_swallowed"),

    ("the record is computed and then discarded",
     r"(                    )unreadable\.append\(\(where, type\(err\)\.__name__\)\)",
     lambda m: m.group(1) + "pass",
     "TestTheUnevaluableCounterActuallyCounts::"
     "test_a_malformed_file_is_counted_not_swallowed"),

    ("the P1 predicate is made dead",
     r"(                if k == \"hil_review\" and v is )True(:)",
     lambda m: m.group(1) + "None" + m.group(2),
     "TestTheUnevaluableCounterActuallyCounts::"
     "test_a_well_formed_true_file_is_detected"),

    ("the completeness key is dropped from the return",
     r'(    return \{"cfg_true": len\(cfg_true\), "n": n, "iv": iv),\n            "unreadable": unreadable(\})',
     lambda m: m.group(1) + m.group(2),
     "TestTheRealArchive::test_the_zero_states_its_own_completeness"),

    ("the completeness line is no longer printed",
     r'(    print\(f"  )files P1 could NOT evaluate(        : \{len\(unreadable\)\}")',
     lambda m: m.group(1) + "quietly ignored" + m.group(2),
     "TestItRunsAndItsHelpDoesNot::"
     "test_it_exits_zero_and_prints_all_three_predicates"),

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
                cwd=REPO, capture_output=True, text=True, timeout=1800)
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
