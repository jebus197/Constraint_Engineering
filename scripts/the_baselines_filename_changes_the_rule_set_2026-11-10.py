#!/usr/bin/env python3
"""A lint baseline whose FILENAME loses its date is held to a different rule set.

WHY THIS MATTERS AND WHY IT IS DANGEROUS IN ONE DIRECTION ONLY. The pre-commit
note ratchet refuses a commit when a file's finding count RISES. To pre-check it
by hand you need both sides measured the same way. `--as` was added for exactly
that and `feedback_compare_lint_counts_like_with_like_2026-10-15` already named
it the correct idiom -- but that memory also states that "the FILENAME is
irrelevant and only in-repo-versus-not matters", and that is FALSE.

MEASURED 2026-11-10 ON BYTE-IDENTICAL CONTENT, varying ONLY the logical path
passed to `--as`:

    experimental_notes/RUNWAY_to_BR2_2026-08-18.md  -> 22 findings
    experimental_notes/RUNWAY_2026-08-18.md         -> 22
    experimental_notes/RUNWAY_2026-10-28.md         -> 22
    experimental_notes/RUNWAY_2026-10-29.md         -> 88
    experimental_notes/RUNWAY_to_BR2.md             -> 88   (no date)
    experimental_notes/r.md                         -> 88   (no date)

So a date BEFORE 2026-10-29 is grandfathered; a date from 2026-10-29 onward, OR
NO DATE AT ALL, is held to the full standard. The entire gap is `SPELLED
NUMBER`. The module's own comment at line 231 states the principle: "THE CUTOFF
IS THE DATE ENFORCEMENT BEGINS, NOT THE DATE HE RULED."

THE ABSOLUTE COUNTS ABOVE ARE FROM THE HEAD VERSION OF THAT FILE AND WILL
DRIFT, which is why this script asserts the RELATIONSHIP and never the values:
on-cutoff must exceed pre-cutoff, and undated must equal on-cutoff. Reading the
live file on 2026-11-10 after STAGE 8 was appended gives 21 and 89 rather than
22 and 88, and the relationship is unchanged. A pin on the absolute number would
be the stale-pin failure this project has recorded 3 times in 2 days.

THE DANGEROUS DIRECTION. A baseline copied to a name without a date reads 88
where the truth is 22. The staged side, read at its real dated name, reads 23.
88 > 23, so a hand check says OK -- while the gate, comparing 22 against 23,
correctly says WORSENED. **The wrong filename HIDES a real worsening rather
than inventing a false one.** That happened on 2026-11-10: a hand check cleared
2 files the gate then refused, and the gate was right both times.

THE IDIOM, and it is not optional. Pass the REAL logical path, date and all:

    python3 scripts/note_vagueness_lint.py --as "<real/path/with_DATE.md>" <bytes>

Run: python3 scripts/the_baselines_filename_changes_the_rule_set_2026-11-10.py
Exit 0 when the measurement above reproduces, 1 if the linter's scoping moved.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

def _find_repo() -> pathlib.Path:
    """Locate the repository by its contents, not by this file's position.

    A producer that only runs from one directory is fragile, and resolving
    `parents[1]` of `__file__` made the FIRST run of this script report its
    subject as missing while the subject was present -- the probe's location
    manufacturing the failure. Search upward from this file and then from the
    working directory for the linter it drives.
    """
    for start in (pathlib.Path(__file__).resolve().parent,
                  pathlib.Path.cwd().resolve()):
        for cand in (start, *start.parents):
            if (cand / "scripts" / "note_vagueness_lint.py").is_file():
                return cand
    raise SystemExit("cannot locate the repository: no scripts/"
                     "note_vagueness_lint.py above this file or the cwd")


REPO = _find_repo()
LINT = REPO / "scripts" / "note_vagueness_lint.py"
SUBJECT = REPO / "experimental_notes" / "RUNWAY_to_BR2_2026-08-18.md"
CUTOFF = "2026-10-29"


def count(logical: str, path: pathlib.Path) -> int | None:
    r = subprocess.run([sys.executable, str(LINT), "--as", logical, str(path)],
                       capture_output=True, text=True)
    hits = re.findall(r"^[ \t]*(\d+) finding", r.stdout + r.stderr, re.M)
    return int(hits[-1]) if hits else None


def main(argv=None) -> int:
    #: A `--help` MUST NEVER COST MINUTES -- his standing rule, and the
    #: project enforces it. This producer had no argparse at all, so `--help`
    #: was ignored and the whole measurement ran. The description is taken
    #: from the module docstring so the usage text cannot drift from the file.
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0] if __doc__ else "")
    _ap.parse_args(argv)
    if not SUBJECT.is_file():
        print(f"subject missing: {SUBJECT}")
        return 1
    cases = [
        ("experimental_notes/RUNWAY_to_BR2_2026-08-18.md", "dated, pre-cutoff"),
        ("experimental_notes/X_2026-10-28.md", "dated, day before cutoff"),
        ("experimental_notes/X_2026-10-29.md", "dated, ON the cutoff"),
        ("experimental_notes/RUNWAY_to_BR2.md", "UNDATED"),
        ("experimental_notes/r.md", "UNDATED, short"),
    ]
    print("=" * 74)
    print("IDENTICAL BYTES, VARYING ONLY THE DECLARED LOGICAL PATH")
    print("=" * 74)
    got = {}
    for logical, label in cases:
        n = count(logical, SUBJECT)
        got[logical] = n
        print(f"  {logical:48s} {str(n):>4s}  ({label})")

    pre = got["experimental_notes/X_2026-10-28.md"]
    on = got["experimental_notes/X_2026-10-29.md"]
    undated = got["experimental_notes/r.md"]
    print()
    print(f"  pre-cutoff   {pre}")
    print(f"  on cutoff    {on}")
    print(f"  undated      {undated}")

    ok = (pre is not None and on is not None and undated is not None
          and on > pre and undated > pre and undated == on)
    print("\n" + "=" * 74)
    if ok:
        print(f"  PASS — the scoping cutoff is {CUTOFF}; an UNDATED baseline is")
        print("         held to the SAME full standard as a post-cutoff note,")
        print("         so it reads HIGHER than the truth and HIDES a worsening.")
    else:
        print("  FAIL — the linter's date scoping has moved. Re-derive the")
        print("         cutoff before quoting any figure that depends on it.")
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
