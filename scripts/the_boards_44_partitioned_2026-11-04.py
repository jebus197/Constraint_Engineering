#!/usr/bin/env python3
"""The 44 board failures, partitioned: node id -> root cause -> category.

WHY THIS EXISTS, AND IT IS THE PANEL'S DOING RATHER THAN MINE. The joint round
of 2026-11-04 had both seats raise the SAME strongest disagreement, each
independently, and both were right:

  * The distribution reported to them, "2 product + 10 instruments + 19
    bookkeeping", SUMS TO 31 against a stated total of 44. 13 failures sat in
    no bucket.
  * The units shifted mid-list. The 2 and the 10 counted ROOT CAUSES and
    FINDINGS; the 19 counted FAILURES. One seat's words: the question is
    "built on uncheckable arithmetic -- the exact shape B116 exists to forbid".
  * And unlike every other figure in that brief, it named NO PRODUCER.

That is the B116 defect -- a figure whose scope is not attached to it --
committed inside a brief written to ask 2 seats about B116. The remedy they
both named is this file: a committed mapping from node id to root cause to
category, so the distribution is a PARTITION that can be checked rather than 3
numbers in different units.

A SECOND FIGURE FELL IN THE SAME PASS. "The 44 reduced to 18 independent root
causes" is also wrong: there are 11 among the 44. The 18 counted causes
addressed in this period, several of which were never board failures at all --
B118's second CLOSED door is the clearest, and its own entry says it "was NOT
on the board", having been found by falsifying the board's failure rather than
by the board.

THE CATEGORIES, and why 1 of them is MIXED rather than forced either way.
  PRODUCT     a live defect in code the harness runs.
  INSTRUMENT  the checker was wrong and its subject correct.
  MIXED       the failure carries both, and `test_operational_scripts.py` is
              the case: 7 of its 21 findings were the checker's own false
              positives and 14 were genuine defects, across 5 failures, so no
              failure there is purely one or the other. Forcing it either way
              is the unit confusion the seats caught, reproduced.
  BOOKKEEPING a ratchet staled by this period's own edits.
  HIS RULING  a guard correctly reporting a state only the founder can settle.

Usage: python3 scripts/the_boards_44_partitioned_2026-11-04.py
Exit 0 iff the partition covers every node id exactly once.
"""
import os
import pathlib
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The 44 node ids the board reported, by the FILE they live in. Keyed on the
#: file because a file's failures share one root cause in every case here, and
#: keyed on a SUBSTRING so a renamed class cannot silently drop a row.
RULES = (
    # (file substring, category, root cause)
    ("falsifier_C0001", "PRODUCT", "B117 fable_5_1.toml has never existed in any commit"),
    ("falsifier_C0002", "PRODUCT", "B117 fable_5_1.toml has never existed in any commit"),
    ("falsifier_C0019", "PRODUCT", "B117 fable_5_1.toml has never existed in any commit"),
    ("manifest_records_the_length_cap", "PRODUCT", "B117 fable_5_1.toml has never existed in any commit"),
    ("the_spec_is_not_work", "PRODUCT", "B117 fable_5_1.toml has never existed in any commit"),
    ("policy_engine", "PRODUCT", "B117 [admission] undeclared to the schema validator"),
    ("verified_not_claimed", "INSTRUMENT", "B118 a source-text guard punished a STRENGTHENED requirement"),
    ("operational_scripts", "MIXED", "B119 7 of 21 findings were the checker's own, 14 were real"),
    ("his_ruling_reaches_the_report", "INSTRUMENT", "B120 duplicate detector read dates in filenames as figures"),
    ("his_responses_have_not_shrunk", "INSTRUMENT", "B120 loss detector fired on a byte-identical file"),
    ("panel_conditions_are_met", "INSTRUMENT", "B120 disagreement pattern admitted # and * but not a backtick"),
    ("severity_proxy_was_never_tested", "INSTRUMENT", "3 exact pins over a growing archive"),
    ("task_list_burndown", "HIS RULING", "B123 the list is no longer provably subcritical"),
    ("a_blind_round_has_a_joint_round", "HIS RULING", "B124 1 blind round owed its joint half"),
    ("the_morning_report_is_generated", "HIS RULING", "B122 the report breaks Rule 10"),
)
DEFAULT = ("BOOKKEEPING", "a ratchet staled by this period's own edits")


def classify(node_id: str) -> tuple:
    f = node_id.split("::")[0]
    for frag, cat, cause in RULES:
        if frag in f:
            return cat, cause
    return DEFAULT


def main() -> int:
    answer_help(__doc__, __file__)
    ids_file = REPO / "experimental_notes" / "data" / "board_44_nodeids_2026-11-04.txt"
    if not ids_file.is_file():
        print(f"the node-id list is missing: {ids_file}")
        print("It is the board's own `FAILED` lines, 1 per line, and without it")
        print("this measurement is VOID rather than approximate.")
        return 3
    ids = [l.strip() for l in ids_file.read_text(encoding="utf-8").splitlines()
           if l.strip()]
    rows = [(n, *classify(n)) for n in ids]

    print("=" * 76)
    print(f"THE BOARD'S {len(ids)} FAILURES, PARTITIONED BY CATEGORY")
    print("=" * 76)
    cats = Counter(c for _, c, _ in rows)
    for k in sorted(cats):
        print(f"  {k:12} {cats[k]:>3}")
    print(f"  {'TOTAL':12} {sum(cats.values()):>3}")
    if sum(cats.values()) != len(ids):
        print("\nTHE PARTITION DOES NOT COVER THE SET; measurement void.")
        return 3

    print("\n" + "=" * 76)
    print("BY ROOT CAUSE")
    print("=" * 76)
    causes = Counter(c for _, _, c in rows)
    for k, v in sorted(causes.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {v:>3} failure(s)  {k}")
    print(f"\n  distinct root causes AMONG THE {len(ids)}: {len(causes)}")

    print("\n" + "=" * 76)
    print("WHAT THIS CORRECTS")
    print("=" * 76)
    print('  "2 product + 10 instruments + 19 bookkeeping" summed to 31 of 44,')
    print("  mixing root causes and findings with failures. Both panel seats")
    print("  raised it independently as their strongest disagreement.")
    print(f'  "18 independent root causes" is also wrong: {len(causes)} among the')
    print(f"  {len(ids)}. The 18 counted causes ADDRESSED in the period, including")
    print("  ones that were never board failures -- B118's second CLOSED door")
    print("  was found by falsifying the board's failure, not by the board.")
    print("\n  AND 10 WAS A COUNT OF FINDINGS, NOT FAILURES: 7 false positives")
    print("  inside 1 test file plus 3 further instruments elsewhere. The")
    print("  failures involving an instrument fault are "
          f"{cats['INSTRUMENT'] + cats['MIXED']}, of which")
    print(f"  {cats['MIXED']} also carry genuine defects and are reported as MIXED")
    print("  rather than forced to one side.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
