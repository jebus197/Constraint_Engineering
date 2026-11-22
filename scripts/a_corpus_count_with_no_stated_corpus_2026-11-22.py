#!/usr/bin/env python3
"""6 answers to 1 question: how often does the project write unhyphenated `rerun`?

WRITTEN 2026-11-22, out of the joint panel round on batch 1.

★ THE SEATS DISAGREED BY A FACTOR OF MORE THAN 100 AND BOTH WERE MEASURING.
Reviewing the budget gate's vocabulary blind, the `fable` seat reported that
unhyphenated `rerun` appears **0** times in the project's prose and used that to
dismiss the widening as below threshold. The `cc2` seat reported **398** and used
it to justify the widening. In the joint round `fable` re-measured, got **474**,
and withdrew its own figure with the sentence this script is named after:

    a corpus count with no stated corpus is not a measurement

★ RE-MEASURED IN THE LIVE TREE, THE SPREAD IS WIDER THAN EITHER SEAT SAW, AND
THE DOMINANT TERM IS NOT WHAT `fable` NAMED. It is not case sensitivity. It is
whether HARVESTED SEAT TREES are counted: `experimental_notes/seat_evidence/` and
`bench/logs/*/sandbox_harvest/` hold COPIES of project files, so counting them
counts the same prose several times over. That is the double-counting class entry
B121 records, where a symlink walked twice inflated 3,311 severities to a figure
that had to be withdrawn.

★ WHICH NUMBER GOVERNS, AND WHY IT IS THE SMALL ONE. The question the gate
actually asks is whether unhyphenated `rerun` is an idiom THE PROJECT USES, so
the corpus is the project's own prose and code. A harvested seat tree is a record
of what a seat wrote, not something the project wrote, and it is excluded for the
same reason `bench/tests/test_a_cited_path_must_exist_2026-10-30.py` excludes
verbatim panel transcripts from its own scope.

★ NEITHER SEAT'S FIGURE IS REPRODUCIBLE HERE, and that is reported rather than
smoothed. `fable` ran in a sandbox copy taken before this session's later edits,
so its tree genuinely differed from this one; its 474 is not an error so much as
a measurement of a different tree. The lesson survives its own number, which is
the point worth keeping.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
EXTS = ("*.md", "*.py", "*.txt")

#: Copies of project files, not project prose. Counting these counts the same
#: sentence once per harvest.
HARVEST = ("experimental_notes/seat_evidence/", "bench/logs/", "/sandbox_harvest/")

#: What the 2 seats reported, pinned so the spread stays legible.
SEAT_FIGURES = {"fable blind": 0, "cc2 blind": 398, "fable joint": 474}


#: ★ THIS FILE EXCLUDES ITSELF, AND IT DID NOT AT FIRST. The first run returned
#: 444 where a hand count minutes earlier returned 440, because this script's own
#: docstring says the term it is counting. A measuring instrument inside its own
#: population measures itself -- `feedback_a_watcher_is_part_of_what_it_watches`,
#: recorded 3 times in 1 night on 2026-11-22, once on a monitor that matched its
#: own output. The exclusion is asserted to BITE below, so it cannot quietly stop
#: working.
SELF = pathlib.Path(__file__).resolve()


def count(term: str, *, case_insensitive: bool, exclude_harvest: bool,
          exclude_self: bool = True) -> "tuple[int, int]":
    pat = re.compile(rf"\b{re.escape(term)}\b", re.I if case_insensitive else 0)
    n = files = 0
    for ext in EXTS:
        for f in REPO.rglob(ext):
            s = str(f)
            if "/.git/" in s:
                continue
            if exclude_self and f.resolve() == SELF:
                continue
            if exclude_harvest and any(h in s for h in HARVEST):
                continue
            try:
                k = len(pat.findall(f.read_text(errors="ignore")))
            except OSError:
                continue
            if k:
                files += 1
                n += k
    return n, files


def main() -> int:
    term = sys.argv[1] if len(sys.argv) > 1 else "rerun"
    print("=" * 74)
    print(f"A CORPUS COUNT WITH NO STATED CORPUS IS NOT A MEASUREMENT  --  '{term}'")
    print("=" * 74)

    rows = []
    for ci in (True, False):
        for ex in (False, True):
            n, fl = count(term, case_insensitive=ci, exclude_harvest=ex)
            label = (f"{'case-insensitive' if ci else 'case-SENSITIVE  '}, "
                     f"{'EXCLUDING harvests' if ex else 'all files        '}")
            rows.append((label, n, fl))
            print(f"  {label} : {n:6d}  across {fl} file(s)")

    counts = [n for _l, n, _f in rows]
    lo, hi = min(counts), max(counts)
    print(f"\n  SPREAD FROM CORPUS CHOICE ALONE : {lo} to {hi}", end="")
    if lo:
        print(f"  = {hi / lo:.4f}x")
    else:
        print()
    print("  The dominant term is the HARVEST exclusion, not case sensitivity:")
    ci_all = next(n for l, n, _ in rows if "insensitive" in l and "all" in l)
    ci_ex = next(n for l, n, _ in rows if "insensitive" in l and "EXCLUDING" in l)
    cs_all = next(n for l, n, _ in rows if "SENSITIVE" in l and "all" in l)
    print(f"    harvest exclusion moves it by {ci_all - ci_ex}")
    print(f"    case sensitivity moves it by   {ci_all - cs_all}")

    print("\n  WHAT THE 2 SEATS REPORTED, for the same question:")
    for k, v in SEAT_FIGURES.items():
        print(f"    {k:14s}: {v}")
    # ANTI-VACUITY ON THE SELF-EXCLUSION: it must actually change the answer,
    # or a future edit could drop it with nothing noticing.
    with_self, _ = count(term, case_insensitive=True, exclude_harvest=False,
                         exclude_self=False)
    without_self = ci_all
    print(f"\n  SELF-EXCLUSION: counting this script too gives {with_self}, "
          f"excluding it gives {without_self}")
    if term == "rerun":
        assert with_self > without_self, (
            "this script's self-exclusion no longer bites, which means either the "
            "docstring stopped naming the term or the exclusion broke. Both make "
            "the figures above measurements of this instrument.")
        print(f"    the exclusion BITES by {with_self - without_self}, so this "
              f"instrument is outside its own population")

    print(f"\n  So {len(set(counts)) + len(set(SEAT_FIGURES.values()) - set(counts))} "
          f"distinct answers exist to 1 question.")
    print("  THE GOVERNING FIGURE IS THE HARVEST-EXCLUDED ONE, because the gate asks")
    print("  whether the PROJECT uses the idiom, and a harvested seat tree is a record")
    print("  of what a seat wrote rather than something the project wrote.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    sys.exit(main())
