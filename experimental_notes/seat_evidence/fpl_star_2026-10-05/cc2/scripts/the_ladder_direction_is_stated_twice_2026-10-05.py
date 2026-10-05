# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fpl_star_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: eafb5aed92ba0b930ca248a9df531fb30678e62e71552ccad16f83154f106684
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""`bench/routing.py` states the ladder's direction twice, incompatibly.

WHY THIS EXISTS (panel review 2026-10-05, claude seat). Two seats and CC1 reached
OPPOSITE verdicts on which simulated seat map is faithful, and the disagreement is
not about evidence -- it is about which of two contradictory sentences in the SAME
docstring is the specification.

STATEMENT A, module docstring, first paragraph:
    "route the falsification to progressively STRONGER models (ordered by
     capability fingerprint)"
Read literally, rung 1 is the WEAKEST tried and capability ASCENDS with rung index.

STATEMENT B, `rank_falsifier_writers` docstring and `DEFAULT_FALSIFIER_STRENGTH`:
    "Return the available model labels ordered strongest-first"
Rung 1 is the STRONGEST tried and capability DESCENDS with rung index.

The module's own Exp-42 account sides with A, explicitly:
    rung 1 = gpt-5.5 (Codex) -> 6/7
    "the remaining one ... is resolved by the next, STRONGER rung (opus-class)"
so in the only validated ladder this project has, rung 2 is described as stronger
than rung 1 -- while `DEFAULT_FALSIFIER_STRENGTH` places Codex at index 0 and CC2
at index 1, i.e. Codex "strongest". Codex is therefore simultaneously the strongest
model and weaker than the model at the next rung.

WHAT RESOLVES IT, and it is not a contradiction in the CODE. The tuple is ordered by
Exp-42 EMPIRICAL falsifier-confirm rate (Codex 90%, CC2 75%, ...), which the comment
says outright, and confirm rate is not generic capability. The code is coherent. The
DOCSTRING's word "STRONGER" is the unbacked term, and it sits in the same sentence
as the unbacked phrase "ordered by capability fingerprint" that the 2026-10-05
proposal is about. The proposal caught one false claim in that sentence and left the
other.

WHY IT IS ABOVE THRESHOLD. CC1's guard
`bench/tests/test_the_exercised_ladder_prefix_is_mixed_2026-10-05.py` asserts
"no weaker model appears before a stronger one", i.e. it PINS statement B as the
specification, and falsifies the fable seat's seat map on that basis. Under
statement A -- and under the Exp-42 rung order the docstring narrates -- the fable
seat's map is the correctly directed one and CC1's is inverted. A test has now
frozen one reading of an ambiguous specification without the ambiguity being
recorded anywhere. Whichever reading the founder rules for, the other sentence has
to go.

Read-only. Exits 1 while both statements are present.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _help_requested() -> bool:
    return any(a in ("-h", "--help") for a in sys.argv[1:])


def main() -> int:
    if _help_requested():
        print((__doc__ or "").strip())
        print()
        print(f"usage: {sys.argv[0].split('/')[-1]}")
        return 0

    import bench.routing as RT

    print("=" * 78)
    print("WHAT THE CODE DOES")
    print("=" * 78)
    order = list(RT.DEFAULT_FALSIFIER_STRENGTH)
    print(f"  DEFAULT_FALSIFIER_STRENGTH               : {order}")
    rungs = RT.rank_falsifier_writers(
        ["DeepSeek", "Gemini", "ChatGPT", "CC2", "Codex"])
    print(f"  rank_falsifier_writers(shuffled)         : {rungs}")
    print(f"  rung 1 (tried FIRST)                     : {rungs[0]}")
    print(f"  rung 2 (tried second)                    : {rungs[1]}")
    assert rungs[0] == "Codex" and rungs[1] == "CC2", rungs

    print()
    print("=" * 78)
    print("WHAT THE DOCSTRING SAYS, BOTH TIMES")
    print("=" * 78)
    # whitespace-normalised: the phrase is split across a source line.
    doc = " ".join((RT.__doc__ or "").split())
    a = "progressively STRONGER models" in doc
    b = "strongest-first" in (RT.rank_falsifier_writers.__doc__ or "")
    narrative = "the next, stronger rung (opus-class)" in doc
    print(f"  module docstring says 'progressively STRONGER models'      : {a}")
    print(f"  rank_falsifier_writers says 'ordered strongest-first'      : {b}")
    print(f"  module docstring calls rung 2 'the next, stronger rung'    : {narrative}")
    print()
    print("  So the module asserts BOTH that rung 1 is the strongest model AND that")
    print("  the model at rung 2 is stronger than the model at rung 1. The code is")
    print("  coherent -- the tuple is ordered by Exp-42 CONFIRM RATE, which the")
    print("  comment states -- but the docstring's word 'STRONGER' is unbacked, and")
    print("  it is the word CC1's new guard pins as the specification.")

    print()
    print("=" * 78)
    print("WHAT TURNS ON IT -- the two seat maps, both correct, under one reading each")
    print("=" * 78)
    from bench.tools.sim_dispatch_shim import DEFAULT_LADDER
    seats = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM",
             "Gemini-SIM", "Fable-SIM"]
    fable_map = dict(DEFAULT_LADDER, **{"Codex-SIM": "fable"})
    for name, smap, budget in (("CC1 (shipped), budget 4", DEFAULT_LADDER, 4),
                               ("fable seat, budget 2", fable_map, 2)):
        rows = []
        for s in seats:
            ms = [smap.get(r, "opus")
                  for r in RT.rank_falsifier_writers(seats, exclude=(s,))[:budget]]
            rows.append(ms)
        mixed = sum(1 for m in rows if len(set(m)) > 1)
        desc = sum(1 for m in rows if len(set(m)) > 1 and all(
            not (m[i] == "fable" and "opus" in m[i + 1:]) for i in range(len(m))))
        asc = sum(1 for m in rows if len(set(m)) > 1 and all(
            not (m[i] == "opus" and "fable" in m[i + 1:]) for i in range(len(m))))
        print(f"  {name:<26} mixed {mixed}/6   "
              f"descending(statement B) {desc}/6   ascending(statement A) {asc}/6")
    print()
    print("  Neither map is 'the' faithful one until the founder rules which")
    print("  statement is the specification. CC1's test currently freezes B.")

    present = a and narrative
    print()
    print(f"  BOTH CONTRADICTORY STATEMENTS STILL PRESENT: {present}")
    return 1 if present else 0


if __name__ == "__main__":
    raise SystemExit(main())
