#!/usr/bin/env python3
"""Revert the 2-hash heading rule and require its guard to go red.

A FIX I HAVE NOT TRIED TO BREAK IS A HYPOTHESIS. The rule under test is 3 lines
in `scripts/read_founder_responses_2026-10-11.py`: a line opening with 2 or more
hashes is a markdown heading and never one of his annotations. It was added
2026-11-02 after the commit gate refused a commit because 2 markdown headings in
an externally written note had been read as his annotations and so had no
verdict row.

4 MUTATIONS, EACH UNDOING A DIFFERENT PROPERTY:
  M1  the rule is deleted outright       -> the leaking headings return
  M2  it fires at 3+ hashes instead of 2 -> a `##` heading leaks
  M3  it returns False instead of True   -> every multi-hash heading leaks
  M4  it fires at 1+ hashes              -> it swallows HIS OWN annotations

M4 IS THE ONE THAT MATTERS MOST. A rule this shape could have been written to
treat ANY hash as a heading, which would delete every annotation he has ever
written while leaving the first 3 mutations' tests green. If the guard does not
go red on M4 then it is not holding the anti-vacuity property and the rule is
one typo away from silencing him.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE, per
`feedback_a_harness_must_restore_what_it_found_2026-11-01`: the original bytes
are held in memory, written back in a `finally`, and the sha256 compared before
the exit code is decided.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
GUARD = (REPO / "bench" / "tests"
         / "test_a_markdown_heading_is_not_his_annotation_2026-11-02.py")

RULE = """    if len(stripped) - len(stripped.lstrip("#")) >= 2:
        return True"""

MUTATIONS = [
    ("M1 the rule is deleted outright",
     "the 2-hash discriminator entirely, which is the pre-fix behaviour",
     RULE,
     '    pass  # MUTANT: the 2-hash rule is gone'),
    ("M2 it fires at 3+ hashes instead of 2",
     "coverage of `##` headings, leaving only `###` and deeper caught",
     RULE,
     '    if len(stripped) - len(stripped.lstrip("#")) >= 3:  # MUTANT\n'
     '        return True'),
    ("M3 it returns False instead of True",
     "the verdict itself: a multi-hash line is declared NOT a heading",
     RULE,
     '    if len(stripped) - len(stripped.lstrip("#")) >= 2:\n'
     '        return False  # MUTANT'),
    ("M4 it fires at 1+ hashes and swallows HIS annotations",
     "the boundary that separates his single hash from a heading's 2",
     RULE,
     '    if len(stripped) - len(stripped.lstrip("#")) >= 1:  # MUTANT\n'
     '        return True'),
]


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=600,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    return r.returncode == 0, (lines[-1] if lines else "")


def main() -> int:
    argparse.ArgumentParser(
        description=("Revert the 2-hash markdown-heading rule and require its "
                     "guard to go red.")).parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED reader passes the guard", green, tail))
        if not green:
            print("  The guard fails on the unmutated reader; mutating it would")
            print(f"  prove nothing. {tail}")
            return 1
        text = original.decode()
        for name, reverts, find, repl in MUTATIONS:
            n = text.count(find)
            if n != 1:
                results.append((f"{name} [NOT APPLIED]", False,
                                f"its anchor occurs {n} times, not 1"))
                continue
            SUBJECT.write_text(text.replace(find, repl, 1), encoding="utf-8")
            red, tail = _run_guard()
            SUBJECT.write_bytes(original)
            results.append((name, not red,
                            tail if not red else
                            f"GAP: the guard stayed GREEN, so it does not hold "
                            f"{reverts}."))
    finally:
        SUBJECT.write_bytes(original)

    h1 = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    restored = h0 == h1
    print("=" * 76)
    print("DOES THE GUARD NOTICE THE 2-HASH RULE BEING UNDONE?")
    print("=" * 76)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  reader restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    if not restored:
        print("  THE READER WAS NOT RESTORED. Fix that before anything else.")
    return 0 if (n_ok == len(results) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
