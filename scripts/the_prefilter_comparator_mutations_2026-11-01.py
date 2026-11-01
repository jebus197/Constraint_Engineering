#!/usr/bin/env python3
r"""Was pinning the prefilter LITERAL worse than comparing the 2 declarations?

THE CLAIM UNDER TEST, made in the docstring of
`bench/tests/test_the_prefilter_assumption_is_checked_2026-10-28.py`: the old
literal assertion was RED on a correct change and GREEN on the real defect, and
the comparator inverts both. That is a claim about evidence until a script
produces it, so this is the script.

THE 2x2. Two forms of the guard, two mutations of the harvester:

  CORRECT CHANGE   a new kind added to BOTH `MARKER` and `CANDIDATE_LINE`
                   -- exactly what happened when `stm` was admitted 2026-11-01.
  REAL DEFECT      a new kind added to `MARKER` ONLY, leaving the prefilter
                   short, so his annotations carrying it are dropped before the
                   marker ever sees them.

A guard is USEFUL iff it is green on the correct change and red on the defect.

RESTORE DISCIPLINE: every mutated file is restored from the bytes read BEFORE
mutation and the restore is asserted, because `git checkout --` once ate the
subject of the measurement (2026-11-01).
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
HARVESTER = REPO / "scripts" / "harvest_tickets_2026-10-17.py"
GUARD = REPO / "bench" / "tests" / "test_the_prefilter_assumption_is_checked_2026-10-28.py"
NODE = ("TestTheAssumptionIsCheckedNotTrusted::"
        "test_the_live_prefilter_is_the_form_the_measurement_chose")

#: The literal the guard carried until 2026-11-01, reconstructed verbatim.
LITERAL_FORM = '''        h = _harvester()
        assert h.CANDIDATE_LINE.pattern == r"(?:fr|pf|qs|wr)\\b", (
            f"the live prefilter is {h.CANDIDATE_LINE.pattern!r}. The measured "
            f"choice was fable's `(?:fr|pf|qs|wr)\\\\b`; if it has moved, say which "
            f"measurement moved it")
'''


def _green(path: pathlib.Path) -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", f"{path}::{NODE}",
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def _body_of_current_guard(text: str) -> str:
    """The live assertion body, so the literal form can be swapped in for it."""
    start = text.index("        h = _harvester()\n        marker_kinds")
    end = text.index("    def test_the_left_boundary_is_gone")
    return text[start:end]


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="the_prefilter_comparator_mutations_2026-11-01.py",
        description="Measure the literal form against the comparator form over "
                    "a correct change and a real defect. Writes nothing "
                    "permanently; restores every file it mutates.")
    ap.parse_args()

    harv_orig = HARVESTER.read_bytes()
    guard_orig = GUARD.read_bytes()
    harv_txt = harv_orig.decode()
    guard_txt = guard_orig.decode()
    live_body = _body_of_current_guard(guard_txt)

    # the harvester as it stands already carries `stm` in both declarations,
    # so "correct change" is the TREE AS IT IS, and the 2 mutations are:
    #   - defect: drop `stm` from CANDIDATE_LINE only (marker keeps it)
    mut_defect = harv_txt.replace(
        r'CANDIDATE_LINE = re.compile(r"(?:fr|pf|qs|wr|stm)\b", re.IGNORECASE)',
        r'CANDIDATE_LINE = re.compile(r"(?:fr|pf|qs|wr)\b", re.IGNORECASE)')
    assert mut_defect != harv_txt, "defect mutation did not apply"

    guard_literal = guard_txt.replace(live_body, LITERAL_FORM)
    assert guard_literal != guard_txt, "literal-form substitution did not apply"

    results: dict[tuple[str, str], bool] = {}
    try:
        for guard_name, guard_src in (("comparator", guard_txt),
                                      ("literal", guard_literal)):
            for mut_name, harv_src in (("correct change (stm in both)", harv_txt),
                                       ("real defect (stm in MARKER only)", mut_defect)):
                GUARD.write_text(guard_src)
                HARVESTER.write_text(harv_src)
                results[(guard_name, mut_name)] = _green(GUARD)
    finally:
        HARVESTER.write_bytes(harv_orig)
        GUARD.write_bytes(guard_orig)
        assert HARVESTER.read_bytes() == harv_orig, "HARVESTER NOT RESTORED"
        assert GUARD.read_bytes() == guard_orig, "GUARD NOT RESTORED"
        print("restored both files byte-for-byte")

    print()
    hdr = f"{'guard form':<12} | {'correct change':<16} | {'real defect':<16}"
    print(hdr)
    print("-" * len(hdr))
    verdicts = {}
    for g in ("literal", "comparator"):
        ok_correct = results[(g, "correct change (stm in both)")]
        ok_defect = results[(g, "real defect (stm in MARKER only)")]
        verdicts[g] = (ok_correct, ok_defect)
        print(f"{g:<12} | {'GREEN' if ok_correct else 'RED  ':<16} "
              f"| {'GREEN' if ok_defect else 'RED  ':<16}")
    print()
    print("A guard is USEFUL iff: GREEN on the correct change, RED on the defect.")
    bad = []
    lit_c, lit_d = verdicts["literal"]
    cmp_c, cmp_d = verdicts["comparator"]
    if lit_c:
        bad.append("the literal was GREEN on the correct change -- the docstring's "
                   "claim that it fired on correct code is NOT reproduced")
    if not lit_d:
        bad.append("the literal was RED on the real defect -- it catches the "
                   "defect after all, and the claimed advantage shrinks")
    if not cmp_c:
        bad.append("the comparator is RED on the correct change -- it is no better")
    if cmp_d:
        bad.append("the comparator is GREEN on the real defect -- IT DOES NOT "
                   "CATCH THE THING IT WAS WRITTEN FOR")
    if bad:
        print("CLAIM NOT SUPPORTED:")
        for b in bad:
            print("  -", b)
        return 1
    print("CLAIM REPRODUCED: literal RED/GREEN (wrong both ways); "
          "comparator GREEN/RED (right both ways).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
