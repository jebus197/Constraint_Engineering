# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'batch1_autonomy_2026-11-22', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 35fb94a3c55f14ac36909af003cec8888cbc1f44c62f5b29a94dccc52a3ed0c4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""B182 closed the grid. The grid is not the vocabulary.

PANEL FINDING 2026-11-22, answering the attack the 2026-11-21 brief invited:
"`kick off` may not be the only idiom missing. Name another the project
actually writes, and the claim that the grid is closed is a claim about the
grid rather than about the vocabulary."

THE DECLARED FIGURES REPRODUCE EXACTLY and are not in dispute: 0 of 150,
Wilson upper 0.024970, Clopper-Pearson upper 0.024293. The objection is to what
they cover. The 10 nouns were chosen by the same hand that wrote the pattern,
so the measurement can only report that the listed phrasings are caught.

THE 3 IDIOMS BELOW WERE NOT CHOSEN BY READING THE PATTERN EITHER. They were
counted in this repository's own .md/.py/.txt:

    bare "the board", not full/commit/verification/guard/test   1816
    "bench/tests" with NO trailing slash                        1048
    "the guards"                                                 525
    "rerun"/"reruns"/"rerunning", unhyphenated                   398

2 of them are sentences this project writes AT ITSELF. The hook's own refusal
message says "run the board ONCE yourself, save the result". The 2026-11-21
panel brief says, in its section 2, "Run the guards." Both passed straight
through the gate that exists to refuse them.

BOTH DIRECTIONS ARE MEASURED, because widening an accepting predicate is
exactly how a gate starts refusing prohibitions -- the failure B182's own note
calls the one that matters. The negation arm must stay at 0.
"""
from __future__ import annotations

import importlib.util
import itertools
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
REPAIRED = REPO / "hooks" / "local_resource_budget.py"
LIVE = pathlib.Path.home() / ".claude" / "hooks" / "local_resource_budget.py"

VERBS = ["run", "execute", "please run", "kick off", "start", "rerun"]
#: The 10 of B182's grid, plus the 3 counted above.
NOUNS = ["the suite", "the test suite", "the full test suite",
         "the entire test suite", "the whole test suite",
         "the full suite", "bench/tests/", "the full board",
         "the commit board", "the verification board",
         "the board", "bench/tests", "the guards"]
TAILS = ["", " and report the result", " and tell me what fails"]

#: Prohibitions over the SAME extended grid. Every one MUST pass through.
NEGATIONS = ["do not {}", "never {}", "you must not {}", "without instruction to {}",
             "rather than {}", "instead of asking you to {}"]

#: Sentences this project actually writes at itself.
NATIVE = [
    "run the board ONCE yourself, save the result",
    "Run the guards.",
    "run the board's own 317 guards",
    "rerun the full test suite and report the result",
    "python3 -m pytest -q -p no:cacheprovider bench/tests",
]


def predicate(path):
    spec = importlib.util.spec_from_file_location("lrb_" + path.parent.name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lrb_" + path.parent.name] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m._instructs_heavy_verification


def grid():
    return [f"{v} {n}{t}" for v, n, t in itertools.product(VERBS, NOUNS, TAILS)]


def report(label, fn):
    cases = grid()
    through = [c for c in cases if not fn(c.lower())]
    print(f"  {label}")
    print(f"    extended grid {len(VERBS)}x{len(NOUNS)}x{len(TAILS)} = {len(cases)} cells,"
          f" every one a genuine instruction")
    print(f"    LET THROUGH: {len(through)} of {len(cases)} = {len(through)/len(cases):.6f}")
    blind = {}
    for noun in NOUNS:
        sub = [f"{v} {noun}{t}" for v, t in itertools.product(VERBS, TAILS)]
        n = sum(1 for c in sub if not fn(c.lower()))
        if n:
            blind[noun] = (n, len(sub))
    for noun, (n, d) in blind.items():
        print(f"      {n}/{d} through  {noun!r}")
    neg = [t.format(c) for t, c in itertools.product(NEGATIONS, grid()[:40])]
    wrongly = [c for c in neg if fn(c.lower())]
    print(f"    NEGATION ARM: {len(wrongly)} of {len(neg)} prohibitions wrongly refused")
    nat = [c for c in NATIVE if not fn(c.lower())]
    print(f"    THIS PROJECT'S OWN SENTENCES: {len(nat)} of {len(NATIVE)} through")
    for c in nat:
        print(f"      through: {c!r}")
    print()
    return len(through), len(wrongly)


def main() -> int:
    print()
    if LIVE.is_file() and LIVE.read_bytes() != REPAIRED.read_bytes():
        before, nb = report("BEFORE  (~/.claude/hooks, as dispatched)", predicate(LIVE))
    else:
        before = nb = None
        print("  BEFORE: the live hook is identical to the repaired one; no contrast\n")
    after, na = report("AFTER   (hooks/local_resource_budget.py, repaired)",
                       predicate(REPAIRED))
    if before is not None:
        print(f"  blind cells {before} -> {after};"
              f" prohibitions wrongly refused {nb} -> {na}")
    if na:
        print("  REGRESSION: the widening broke the negation half. Not acceptable.")
        return 1
    print("  the negation half is unchanged and still correct, which is the")
    print("  falsification that matters for a widened accepting predicate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
