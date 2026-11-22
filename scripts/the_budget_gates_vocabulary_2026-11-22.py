#!/usr/bin/env python3
"""Does the budget gate see the idioms this project ACTUALLY writes?

RAISED BY THE PANEL 2026-11-22 AND VERIFIED BEFORE ADOPTION. The B182 repair of
2026-11-21 closed a 150-cell grid -- 5 verbs by 10 nouns by 3 tails -- taking
the blind rate from 126 of 150 to 0 of 150. Seat cc2 attacked exactly the right
seam: the 10 nouns were chosen by the hand that wrote the pattern, so closing
the grid can only report that the LISTED phrasings are caught. That is a claim
about the grid, not about the vocabulary.

THE TWO SENTENCES THAT MATTER MOST ARE THE PROJECT'S OWN. This hook's refusal
message says *"run the board ONCE yourself, save the result"*, and the panel
brief dispatched on 2026-11-22 said *"Run the guards."* Both are instructions of
precisely the shape the gate exists to refuse, and both passed through it.

THE SEATS DISAGREED ON ONE FACT AND IT WAS SETTLED BY COUNTING, not by
preferring a seat. cc2 reported 398 occurrences of unhyphenated `rerun`; fable
reported 0 and concluded the risk was unexercised. Counted across the project's
own .md/.py/.txt: 444 unhyphenated against 7,162 hyphenated, an unhyphenated
share of 0.058375 with Wilson [0.053326, 0.063870] and Clopper-Pearson
[0.053210, 0.063881] agreeing on 2 routes. cc2 was substantially right that the
form occurs; fable was right that the hyphenated form dominates. Neither had it
whole, and `\\brun\\b` catches `re-run` because a hyphen is a word boundary while
catching nothing inside `rerun`, where it is not.

BOTH DIRECTIONS ARE MEASURED, because widening an ACCEPTING predicate is a
tightening: every instruction newly caught risks a prohibition newly refused.
A gate that refuses a brief forbidding heavy work is worse than one that misses
an instruction, since the refusal is the thing the author must then argue with.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

# `_cli_help` lives in scripts/. Located rather than assumed at a fixed depth,
# so the import works when this file is IMPORTED as well as when it is RUN.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402


REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_HOOK = pathlib.Path.home() / ".claude" / "hooks" / "local_resource_budget.py"

#: Instructions the gate SHOULD refuse. Every one is a real phrasing: the first
#: two are quoted from this project's own files.
SHOULD_REFUSE = [
    "run the board ONCE yourself, save the result",      # the hook's own message
    "Run the guards.",                                    # the 2026-11-22 brief
    "run the board and report what fails",
    "execute the board before answering",
    "please run bench/tests and paste the tail",
    "invoke pytest over bench/tests to confirm",
    "rerun the suite and tell me the count",
    "reran the board? do it again and report",
    "start the guards and wait for them",
    "kick off the board, then summarise",
]

#: Briefs that FORBID heavy work. None may be refused.
SHOULD_PASS = [
    "do not run the board; read the cached result instead",
    "never execute the guards yourself",
    "without running bench/tests, tell me what it would cover",
    "skip the suite entirely and work from the last report",
    "rather than rerun the board, consult the committed ledger",
    "you must not start the guards on this machine",
]

#: Ordinary prose naming the nouns with NO instruction in it. A gate that
#: refuses these is refusing description, which would make it unusable.
SHOULD_ALSO_PASS = [
    "the board refused on 2 faults and both are fixed",
    "a board costs about 27 minutes of his machine",
    "the guards in bench/tests are the project's regression record",
    "that rerun landed 55 severities on 2026-11-02",
]


def load(hook: pathlib.Path):
    spec = importlib.util.spec_from_file_location("lrb_vocab", hook)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lrb_vocab"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m._instructs_heavy_verification


def main() -> int:
    #: ★ ONE PARSER, NOT 2 — 2026-11-22. A first repair added an argparse
    #: parser in the `__main__` block to satisfy
    #: `test_operational_scripts.py`'s rule that an unrecognised flag be
    #: REJECTED, and left the hand-rolled `sys.argv` read in place below it.
    #: Both agreed, so nothing failed; 2 sources of truth for 1 flag is a
    #: latent defect regardless, and this project's record is full of
    #: producers and consumers that agreed until they did not.
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--subject", default=None,
                    help="a second copy of the budget-gate hook to measure "
                         "instead of the live one")
    args = ap.parse_args()
    hook = pathlib.Path(args.subject).resolve() if args.subject else DEFAULT_HOOK
    print(f"subject: {hook}\n")
    f = load(hook)

    missed = [s for s in SHOULD_REFUSE if not f(s)]
    wrongly = [s for s in SHOULD_PASS if f(s)]
    wrongly_prose = [s for s in SHOULD_ALSO_PASS if f(s)]

    print(f"INSTRUCTIONS that should be refused : "
          f"{len(SHOULD_REFUSE) - len(missed)} of {len(SHOULD_REFUSE)} caught")
    for s in missed:
        print(f"    MISSED   {s!r}")
    print(f"PROHIBITIONS that must not be refused: "
          f"{len(SHOULD_PASS) - len(wrongly)} of {len(SHOULD_PASS)} correct")
    for s in wrongly:
        print(f"    WRONGLY REFUSED   {s!r}")
    print(f"DESCRIPTIVE PROSE that must not be refused: "
          f"{len(SHOULD_ALSO_PASS) - len(wrongly_prose)} of "
          f"{len(SHOULD_ALSO_PASS)} correct")
    for s in wrongly_prose:
        print(f"    WRONGLY REFUSED   {s!r}")

    ok = not missed and not wrongly and not wrongly_prose
    print(f"\n{'ALL THREE DIRECTIONS HOLD' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
