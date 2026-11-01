#!/usr/bin/env python3
"""Reversion test for `test_r1_has_a_position_on_the_runway_2026-11-01.py`.

A guard is only worth its runtime if breaking the thing it guards turns it RED.
Each mutation below damages the runway in a way the project has actually seen or
could plausibly see from a well-meaning edit, and the guard must fail on every
one. The file is restored from git after each.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNWAY = REPO / "experimental_notes" / "RUNWAY_to_BR2_2026-08-18.md"
GUARD = "bench/tests/test_r1_has_a_position_on_the_runway_2026-11-01.py"

#: (name, what it simulates, mutate(text) -> text)
MUTATIONS = [
    ("delete_the_whole_section",
     "someone removes STAGE 4C as redundant with the task list",
     lambda t: t[:t.index("## STAGE 4C")]),
    ("rename_the_heading",
     "the heading is reworded so it no longer reads as a stage",
     lambda t: t.replace("## STAGE 4C", "### A note on R1", 1)),
    ("drop_the_gate_instrument",
     "the gate is softened to a judgement instead of a measurement",
     lambda t: t.replace("`scripts/task_list_markers.py` `effective_state()`",
                         "when the list looks clear", 1)),
    ("drop_the_threshold",
     "'0 OPEN entries' is loosened to 'few remaining'",
     lambda t: t.replace("0 OPEN entries", "few remaining entries", 1)),
    ("paraphrase_his_words",
     "his verbatim instruction is tightened for rhythm -- his 2026-10-19 ruling "
     "forbids exactly this",
     lambda t: t.replace("It should probably be the next task on our runway",
                         "It should be the next runway task", 1)),
    ("claim_the_spend_is_authorised",
     "the section is read as releasing the money",
     lambda t: t.replace("His authorisation at launch", "Spend approved", 1)),
    ("move_the_section_up_shifting_the_prefix",
     "a tidy-up moves STAGE 4C beside STAGE 4B, shifting every citation",
     lambda t: (lambda sec: t[:t.index("## STAGE 4B")] + sec
                + t[t.index("## STAGE 4B"):t.index("## STAGE 4C")])(
         t[t.index("## STAGE 4C"):])),
    ("drop_the_not_a_decision_sentence",
     "the sentence that stops it being re-presented is cut",
     lambda t: t.replace(
         "**IT IS NOT A DECISION AWAITING HIM AND MUST NOT BE PUT TO HIM AGAIN.**",
         "**ON ITS STATUS.**", 1)),
]


#: ★ THE RESTORE MUST REPLAY THE BYTES THIS SCRIPT FOUND, NEVER GIT'S.
#: The first version of this harness restored with `git checkout --`, and on its
#: first run it DESTROYED the very section it was testing: STAGE 4C was written
#: minutes earlier and was therefore not in HEAD, so "restore" meant "delete".
#: The guard went from 8 passed to 5 failed and the runway went from 872 lines
#: back to 849. A mutation harness is ALWAYS pointed at work that was just
#: written -- that is when a guard is built -- so git's copy is by construction
#: the wrong baseline. The original bytes are captured once, in memory, and
#: replayed. This comment stays because the failure is not obvious until it has
#: happened to you.
def restore(original: str) -> None:
    RUNWAY.write_text(original, encoding="utf-8")


def guard_is_red() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q",
                        "-p", "no:randomly"],
                       capture_output=True, text=True, cwd=str(REPO))
    tail = [l for l in r.stdout.splitlines() if l.strip()]
    return r.returncode != 0, (tail[-1] if tail else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    original = RUNWAY.read_text(encoding="utf-8")
    baseline_red, baseline_line = guard_is_red()
    if "## STAGE 4C" not in original:
        print("REFUSING: the runway has no STAGE 4C section to mutate.")
        print("  A mutation run against an absent subject measures nothing, and")
        print("  this check exists because an earlier version of this script")
        print("  deleted that section and then reported 8 of 8 caught.")
        return 1
    results = []
    try:
        for name, why, fn in MUTATIONS:
            try:
                RUNWAY.write_text(fn(original), encoding="utf-8")
            except Exception as exc:          # a mutation that cannot apply
                results.append({"mutation": name, "why": why,
                                "red": None, "note": f"inapplicable: {exc}"})
                restore(original)
                continue
            red, line = guard_is_red()
            results.append({"mutation": name, "why": why,
                            "red": red, "pytest": line})
            restore(original)
    finally:
        restore(original)
        assert RUNWAY.read_text(encoding="utf-8") == original, (
            "the restore did not reproduce the bytes this script found")

    caught = sum(1 for r in results if r.get("red") is True)
    applicable = sum(1 for r in results if r.get("red") is not None)

    if args.json:
        print(json.dumps({"baseline_green": not baseline_red,
                          "caught": caught, "applicable": applicable,
                          "results": results}, indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"BASELINE (unmutated): {'GREEN' if not baseline_red else 'RED -- ' + baseline_line}")
    if baseline_red:
        print("  A guard that is red before any mutation measures nothing.")
        return 1
    print()
    for r in results:
        if r.get("red") is None:
            mark = "n/a "
        else:
            mark = "RED " if r["red"] else "GREEN"
        print(f"  [{mark}] {r['mutation']}")
        print(f"          simulates: {r['why']}")
        if r.get("red") is False:
            print("          ** NOT CAUGHT -- the guard does not pin this **")
        if r.get("note"):
            print(f"          {r['note']}")
    print()
    print(f"CAUGHT {caught} of {applicable} applicable mutations.")
    if caught == applicable and applicable == len(MUTATIONS):
        print("Every mutation turns the guard red, and the guard is green at rest.")
    else:
        print("At least one mutation passes unnoticed. Name it rather than")
        print("rounding the figure up: an unpinned property is not pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
