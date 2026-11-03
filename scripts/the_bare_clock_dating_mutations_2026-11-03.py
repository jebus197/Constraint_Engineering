#!/usr/bin/env python3
"""Undo the header-date preference 4 ways and require its guard to go red.

THE FIX UNDER TEST is the bare-clock branch of `future_stamp` in
`scripts/note_vagueness_lint.py`: a bare clock time in a note's header is dated
from a prose date in that same header, falling back to the file's mtime only
when no prose date is present.

4 MUTATIONS:
  M1  the prose date is ignored            -> back to mtime dating, 16 false hits
  M2  the prose date is used unconditionally, with no mtime fallback
                                           -> a dateless header stops being checked
  M3  the fallback base is a fixed epoch   -> nothing is ever accused
  M4  the prose-date pattern matches nothing -> silently back to M1

M2 AND M3 ARE THE INTERESTING ONES. M1 and M4 restore the defect the guard was
written against, and a guard can hold those while being blind to the opposite
failure. M2 asks whether the guard noticed that the mtime path was RETAINED
rather than replaced -- a note with a bare clock and no date has nothing else to
be dated from, and dropping that case would quietly stop checking it. M3 turns
the rule into one that accuses nobody, which from the outside is
indistinguishable from the rule being switched off, and that is precisely how a
report-only linter becomes ignored.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "note_vagueness_lint.py"
GUARD = (REPO / "bench" / "tests"
         / "test_a_bare_clock_is_dated_from_the_header_2026-11-03.py")

BLOCK = '''        _pd = _PROSE_DATE_IN_HEADER.search(header)
        _base = mtime
        if _pd:
            try:
                _base = _dt.datetime.strptime(
                    f"{int(_pd.group(1))} {_pd.group(2)} {_pd.group(3)}",
                    "%d %B %Y")
            except ValueError:
                _base = mtime'''

PATTERN = '''_PROSE_DATE_IN_HEADER = re.compile(
    r"\\b(\\d{1,2})\\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\\s+(\\d{4})\\b")'''

MUTATIONS = [
    ("M1 the prose date is ignored",
     "the header-date preference, which is the pre-fix behaviour",
     BLOCK,
     "        _base = mtime  # MUTANT"),
    ("M2 the prose date is required, with no mtime fallback",
     "the retained mtime path for a header with no date at all",
     BLOCK,
     '        _pd = _PROSE_DATE_IN_HEADER.search(header)\n'
     '        if not _pd:\n'
     '            return None  # MUTANT\n'
     '        try:\n'
     '            _base = _dt.datetime.strptime(\n'
     '                f"{int(_pd.group(1))} {_pd.group(2)} {_pd.group(3)}",\n'
     '                "%d %B %Y")\n'
     '        except ValueError:\n'
     '            return None'),
    ("M3 the base is a fixed epoch, so nothing is ever ahead of it",
     "the rule's ability to accuse anything at all",
     BLOCK,
     "        _base = _dt.datetime(2099, 1, 1)  # MUTANT"),
    ("M4 the prose-date pattern matches nothing",
     "the pattern itself, which is how an addition reaches nothing",
     PATTERN,
     '_PROSE_DATE_IN_HEADER = re.compile(r"(?!x)x(a)(b)(c)")  # MUTANT'),
]


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=900,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    return r.returncode == 0, (lines[-1] if lines else "")


def main() -> int:
    argparse.ArgumentParser(
        description=("Undo the header-date preference and require its guard to "
                     "go red.")).parse_args()
    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED linter passes the guard", green, tail))
        if not green:
            print(f"  The guard fails unmutated, so mutating proves nothing. {tail}")
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
    print("=" * 78)
    print("DOES THE GUARD NOTICE THE HEADER-DATE PREFERENCE BEING UNDONE?")
    print("=" * 78)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  linter restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    return 0 if (n_ok == len(results) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
