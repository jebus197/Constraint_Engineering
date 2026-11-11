#!/usr/bin/env python3
"""Mutations against the both-texts admission rule and the dimensional repair route.

Each mutation reinstates a specific defect the founder's 2026-11-11 rulings
closed. Every one must turn its guard RED.

★ ANCHORS ARE DERIVED FROM THE SUBJECT, not typed from memory: a mutation whose
anchor is absent is reported SKIPPED, never counted as caught, because a harness
that cannot find its target is not evidence that the target is guarded.

★ IT RESTORES WHAT IT FOUND, never `git checkout --`. This project lost a live
subject to that once.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DI = ROOT / "bench" / "domain_immune.py"
RR = ROOT / "bench" / "reference_runner_v3.py"

GUARDS = [
    "bench/tests/test_the_dimensional_repair_route_2026-11-11.py",
    "bench/tests/test_the_launcher_substitutes_no_suite_2026-11-11.py",
    "bench/tests/test_a_confirming_tool_must_discriminate_to_admit_2026-11-10.py",
    #: ★ ADDED AFTER THE FIRST RUN REPORTED A MISS THAT WAS MINE, NOT THE
    #: GUARDS'. Blanking `_FindingView.proposed_fix` makes every gate admission
    #: fail closed -- the route goes INERT, which is `additive-standard`'s
    #: removal clause broken by a repair. The first guard set did not catch it,
    #: and the honest reading was NOT that a guard was missing: this file drives
    #: `_apply_back_gate` end to end with a real registry entry dict and would
    #: have caught it all along. The harness was simply not running it. A
    #: mutation harness is only as wide as the guard set it names.
    "bench/tests/test_the_verification_set_comes_from_the_topic_2026-11-10.py",
]

MUTATIONS = [
    (DI, "drop the fix-side conjunct, reopening the unexamined-fix hole",
     '''    out["admits"] = (bool(computing_for) and bool(fix_computing)
                     and not definitive_against)''',
     '''    out["admits"] = bool(computing_for) and not definitive_against'''),

    (DI, "admit when there is NO proposed fix at all (fail open)",
     '''        fix_for, fix_against, fix_computing = [], [], []''',
     '''        fix_for, fix_against, fix_computing = [], [], list(computing_for)'''),

    (DI, "escalate on the FIRST failure rather than a repeated one",
     "MAX_REPAIR_ATTEMPTS = 2",
     "MAX_REPAIR_ATTEMPTS = 1"),

    (DI, "let a model's candidate through without the tool re-verifying it",
     '''        if verify(candidate):
            return {"action": "REPAIRED", "attempts": attempts,''',
     '''        if True:
            return {"action": "REPAIRED", "attempts": attempts,'''),

    (DI, "ask a model to choose among equally minimal repairs",
     '''    if not repair_is_unique(claim):''',
     '''    if False and not repair_is_unique(claim):'''),

    (RR, "stop exposing the proposed fix on the finding view",
     '''        self.proposed_fix = str(
            e.get("proposed_fix") or e.get("fix") or e.get("fix_text") or "")''',
     '''        self.proposed_fix = ""'''),
]


def run_guards() -> bool:
    """True == GREEN."""
    d = subprocess.run([sys.executable, "-m", "pytest", *GUARDS, "-q",
                        "--no-header", "-x"],
                       capture_output=True, text=True, cwd=str(ROOT), timeout=1800)
    return d.returncode == 0


def main() -> int:
    originals = {p: p.read_text(encoding="utf-8") for p, *_ in MUTATIONS}
    if not run_guards():
        print("BASELINE IS RED -- fix the guards before mutating", file=sys.stderr)
        return 2
    print("baseline GREEN\n")
    red = skipped = 0
    try:
        for path, name, anchor, replacement in MUTATIONS:
            src = originals[path]
            if anchor not in src:
                print(f"  SKIPPED  {name}\n           anchor absent from {path.name}")
                skipped += 1
                continue
            path.write_text(src.replace(anchor, replacement, 1), encoding="utf-8")
            green = run_guards()
            print(f"  {'GREEN -- NOT CAUGHT' if green else 'RED   -- caught'}  {name}")
            red += (not green)
            path.write_text(src, encoding="utf-8")
    finally:
        for p, s in originals.items():
            p.write_text(s, encoding="utf-8")
    total = len(MUTATIONS) - skipped
    print(f"\n{red} of {total} applicable mutation(s) RED "
          f"({skipped} skipped for an absent anchor)")
    for p, s in originals.items():
        assert p.read_text(encoding="utf-8") == s, f"{p} was not restored"
    print("every subject restored byte-for-byte")
    return 0 if total and red == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
