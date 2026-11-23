#!/usr/bin/env python3
"""Which guards does THIS commit put at risk? Derived from the diff, not guessed.

DRAFTED 2026-11-22; destination `scripts/`.

WHY IT EXISTS, MEASURED RATHER THAN ARGUED. A commit board costs about 52 minutes
on the current ledger. Before board 2 of 2026-11-22 I assembled cheap checks by
GREPPING the gate's list for subject words -- `morning|decision|task_list|
done_marker|desktop|tracker|spoken` -- which gave 13 guards, ran in 2 minutes 59,
and reported 169 passed. **The board then refused with 5 failures, 4 of them in
`test_the_note_ratchet_preflight_2026-11-01.py`: the guard OF the file I had spent
the night rewriting, which contains none of those words.**

A grep over SUBJECTS selects guards about what you were thinking about. The
failures come from what you changed and stopped thinking about. The sets overlap
and are not the same, and the difference is invisible because the same mental
model chose the checks and wrote the change.

★ AND THE FIRST VERSION OF THIS DERIVATION WAS ITSELF TOO WIDE, WHICH IS B206's
LESSON ARRIVING ON THE INSTRUMENT BUILT TO APPLY IT. Taking every guard that
names any staged file gives **215** -- most of the board. Restricting to files
whose BEHAVIOUR changes gives **119**. But 42 of those are NOT on the gate's
`GUARDS` list, so their failures cannot refuse a commit: one of them,
`test_the_nested_suite_stays_bounded_2026-10-28.py`, is recorded in B203 as red
at HEAD, with B203 stating that the commit board does not run it. **A predictor
must share its subject's population.** So:

    DECIDING  = guards naming changed CODE, intersected with the gate's list
    ADVISORY  = the rest -- guards of changed code the gate does not run,
                which is B204's guard-gap in concrete form

Measured on the 2026-11-22 batch: 86 staged files, 42 behaviour-changing, 119
naming them, **76 deciding** and 42 advisory.

★ `test_precommit_gate_cost_2026-09-10.py` IS EXCLUDED BY NAME AND NOT BY A RULE.
It invokes `precommit_gate_cost_2026-09-10.py --repeats 1`, and `--repeats 1`
TIMES the board by running the whole `GUARDS` list. Measured 2026-11-22 by
killing it at 18 minutes. Including it would make these checks cost the board
they exist to avoid.

IT DECIDES NOTHING AND REFUSES NOTHING. It prints 2 sets and the command to run
the deciding one.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

#: Named, not pattern-matched: this is 1 known file, and a rule broad enough to
#: catch it would catch guards that merely mention the gate.
CONTAINS_THE_BOARD = {"bench/tests/test_precommit_gate_cost_2026-09-10.py"}


def _repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for c in [here.parent, *here.parents]:
        if (c / "bench" / "tests").is_dir() and (c / "hooks").is_dir():
            return c
    return pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


REPO = _repo()


def staged(repo: pathlib.Path) -> list[str]:
    r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                       cwd=repo, capture_output=True, text=True, check=True)
    return [p for p in (r.stdout or "").split() if p]


def behaviour_changing(paths: list[str]) -> list[str]:
    """Every staged file a guard might assert on -- CODE **AND** DOCUMENTS.

    ★ DOCUMENTS WERE EXCLUDED UNTIL 2026-11-22 AND THE EXCLUSION COST A BOARD.
    This function read `startswith(("scripts/", "hooks/", "bench/")) and
    endswith(".py")`, so `experimental_notes/RUNWAY_to_BR2_2026-08-18.md` failed
    BOTH conditions and no guard naming it could ever be selected. The batch-3
    board then refused after **48 min 50 s** on
    `test_r1_has_a_position_on_the_runway_2026-11-01.py::test_the_citation_prefix_is_byte_stable`,
    a guard that IS on the gate and names that document in a `git show`
    argument. The pre-board check passed 1619 tests and could not see it.

    ★ THE OLD DOCSTRING'S REASONING WAS SOUND WHEN WRITTEN AND IS NOW STALE.
    It said data and notes are "named by ~100 guards each" and that including
    them "turns 42 files into 215 guards, which is not a cheap check -- it is
    the board with extra steps". That counted the UNION OF ALL GUARDS NAMING
    THEM, before this script grew the DECIDING/ADVISORY split its own header
    now describes. **The gate intersection already bounds the cost**, so the
    premise no longer holds.

    ★ MEASURED ON THE BATCH-3 DIFF BEFORE THIS CHANGE WAS MADE. 6 non-.py
    staged files: 62 guards name at least one of them, and **34 of those 62 are
    on the gate** -- so including documents adds 34 deciding guards to the 34
    already found. The pre-board set roughly doubles, from 348 s to about 700 s
    against a board of 2930 s. **0.24 of a board to avoid a whole one**, and a
    landed batch costs 1.916667 boards in expectation, so the trade is not
    close.

    ★ A DISCRIMINATOR I PROPOSED AND MEASURED AS USELESS, recorded so it is not
    proposed again. The idea was to count a document's guards only where the
    path appears in a CODE string rather than in a comment or docstring, on the
    reasoning that prose mentions are incidental. Measured with an `ast` walk
    that strips docstrings: **62 guards either way.** Per-file it moves a
    little (the task list 40 -> 38, the runway 6 -> 5), but the UNION is
    identical, so the extra machinery buys nothing. Dropped.

    `bench/tickets/` stays excluded: it is an append-only store written by the
    harvester on nearly every commit, so it would select guards on every run
    while telling nothing about the batch.
    """
    out = []
    for p in paths:
        if p.startswith("bench/tickets/"):
            continue
        if p == "hooks/pre-commit" or (
                p.startswith(("scripts/", "hooks/", "bench/")) and p.endswith(".py")):
            out.append(p)
            continue
        # DOCUMENTS AND DATA. The gate intersection downstream is what keeps
        # this cheap; see the measurement above.
        if p.endswith((".md", ".json", ".txt", ".toml", ".jsonl", ".sh", ".cfg")):
            out.append(p)
    return out


def board_guards(repo: pathlib.Path) -> set[str]:
    """The gate's own list, read from the hook rather than copied."""
    m = re.search(r'GUARDS="(.*?)"', (repo / "hooks" / "pre-commit").read_text(), re.S)
    if not m:
        raise SystemExit("could not locate GUARDS in hooks/pre-commit")
    return {x.strip() for x in m.group(1).split() if x.strip()}


def guards_naming(repo: pathlib.Path, code: list[str]) -> set[str]:
    hit = set()
    for g in sorted((repo / "bench" / "tests").glob("test_*.py")):
        rel = f"bench/tests/{g.name}"
        if rel in code:
            hit.add(rel)                      # a changed guard guards itself
            continue
        t = g.read_text(errors="ignore")
        if any(c in t or pathlib.Path(c).name in t for c in code):
            hit.add(rel)
    for c in code:                            # a newly added guard, same rule
        if c.startswith("bench/tests/"):
            hit.add(c)
    return hit


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths-only", action="store_true",
                    help="print the deciding guards 1 per line and nothing "
                         "else, for a caller that must not scrape prose")
    _args = ap.parse_args(argv)
    files = staged(REPO)
    code = behaviour_changing(files)
    if not code:
        print("no staged file changes behaviour; the gate's guards are not at risk "
              "from code, though notes may still move the ratchet.")
        return 0

    naming = guards_naming(REPO, code)
    board = board_guards(REPO)
    deciding = sorted((naming & board) - CONTAINS_THE_BOARD)
    advisory = sorted(naming - board - CONTAINS_THE_BOARD)
    skipped = sorted(naming & CONTAINS_THE_BOARD)

    #: ★ MACHINE-READABLE MODE, SHARING THE NARRATIVE'S OWN `deciding`
    #: EXPRESSION -- including the `CONTAINS_THE_BOARD` exclusion. A caller that
    #: derives the set by hand misses that exclusion and may run guards which
    #: make a real commit inside themselves, nesting a board inside a
    #: pre-flight. Measured on this commit the exclusion changed nothing, 35
    #: against 35, so the hazard is latent here rather than realised -- which is
    #: exactly when it is cheap to close.
    #:
    #: IT EXISTS BECAUSE SCRAPING THE PROSE WENT WRONG ON 2026-11-23: the
    #: printed command was truncated at 4 paths with an ellipsis, a regex over
    #: the output returned 8 of 44 guards, and the pre-board reported itself
    #: complete having run 18 per cent of the set.
    if _args.paths_only:
        for g in deciding:
            print(g)
        return 0

    print("=" * 74)
    print("WHICH GUARDS DOES THIS COMMIT RISK?")
    print("=" * 74)
    print(f"  staged files                  : {len(files)}")
    print(f"  of those, behaviour-changing  : {len(code)}")
    print(f"  guards naming one of them     : {len(naming)}")
    print(f"  DECIDING (also on the gate)   : {len(deciding)}")
    print(f"  advisory (NOT on the gate)    : {len(advisory)}")
    if skipped:
        print(f"  excluded, contains the board  : {len(skipped)}")
        for s in skipped:
            print(f"      {s}")

    print("\n  DECIDING -- a failure here WILL refuse the commit:")
    for g in deciding:
        print(f"    {g}")
    print("\n  ADVISORY -- guards of changed code the gate does NOT run.")
    print("  A failure here is information, not a blocker. This is B204's")
    print("  guard-gap in concrete form; B203 records one that is red at HEAD.")
    for g in advisory:
        print(f"    {g}")

    #: ★ THE WHOLE COMMAND, NOT ITS FIRST 4 PATHS. Until 2026-11-23 this
    #: printed `deciding[:4]` followed by a literal `...`, so the command it
    #: told the operator to run was UNRUNNABLE whenever the deciding set
    #: exceeded 4 -- which it always does. Worse, it invited exactly the error
    #: it caused on 2026-11-23: the printed text was scraped with a regex, the
    #: ellipsis swallowed the rest, and a pre-board ran **8 of 44** guards while
    #: reporting itself complete. An 82 per cent miss, presented as a pass.
    print("\n  run the deciding set with:")
    print("    python3 -m pytest -q -p no:cacheprovider \\\n      "
          + " \\\n      ".join(deciding))
    print(f"\n  ({len(deciding)} guard(s) above -- the FULL command, not a "
          f"sample. Use --paths-only to")
    print("   get them 1 per line for a script, which is safer than scraping "
          "this text.)")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        #: `takes_no_arguments=False` because this script now has
        #: `--paths-only`. B214: the default refuses a caller's own flags with
        #: exit 2 before argparse is reached, making the flag unreachable.
        answer_help(__doc__, __file__, takes_no_arguments=False)
    except ImportError:
        pass
    sys.exit(main())
