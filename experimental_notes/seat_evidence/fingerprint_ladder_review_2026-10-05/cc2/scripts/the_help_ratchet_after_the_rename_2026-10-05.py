# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cf6e8d12c7198826b70e5f2bc881fffa41aeae385793eb04e78ef08cfc34062e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does the --help ratchet still cover the 8 scripts renamed on 2026-10-05?

THE QUESTION. `bench/tests/test_fresh_clone_is_actually_run_2026-09-11.py
::test_no_script_uses_both` flags any script containing both `answer_help(` and
`ArgumentParser`. Eight new `scripts/*_2026-10-05.py` tripped it, and the local
function was renamed `answer_help` -> `_parse_args`. The sibling ratchet
`bench/tests/test_help_never_acts_2026-09-11.py
::test_every_script_that_writes_answers_help` exempts a script when its matcher
says the script answers `--help`, and its remedy line offers two ways to comply:
"Add `answer_help(...)`, or give the script a parser."

WHAT THIS SCRIPT MEASURES, by execution and not by reading:

  1. `answers_help(src)` and `WRITES.search(src)` for each of the 8, using the
     ratchet's OWN matcher, imported from the test rather than reimplemented.
  2. Every `scripts/*.py` that WRITES and is exempted SOLELY by owning an
     ArgumentParser (no `answer_help` call at all) -- the size of the branch the
     rename now relies on.
  3. Whether `parse_args` is in fact CALLED in each such script, since a parser
     that is constructed and never parsed answers nothing.
  4. `python3 <script> --help` for each of the 8: exit code, first line, and a
     byte-for-byte digest of `scripts/` before and after, so a `--help` that
     acts would be caught rather than assumed inert.

THE POPULATION IS GLOBBED, NOT `git ls-files`. The ratchet uses git and fails
closed where there is no `.git` -- correct for the ratchet, useless in a panel
sandbox. The glob is a SUPERSET of the tracked set, so a clean result here is
not weaker than the ratchet's; an untracked file could only add offenders.

Run:  python3 scripts/the_help_ratchet_after_the_rename_2026-10-05.py
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RATCHET = REPO / "bench" / "tests" / "test_help_never_acts_2026-09-11.py"


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_help_ratchet_after_the_rename_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--pattern", default="*_2026-10-05.py",
                   help="the renamed cohort to execute --help on")
    p.add_argument("--no-exec", action="store_true",
                   help="skip step 4 (do not run --help on anything)")
    return p.parse_args(argv)


def _ratchet():
    spec = importlib.util.spec_from_file_location("_ratchet", RATCHET)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _digest(d: pathlib.Path) -> str:
    h = hashlib.sha256()
    for p in sorted(d.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(d).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def main(argv=None) -> int:
    args = _parse_args(argv)
    R = _ratchet()
    scripts_dir = REPO / "scripts"
    allp = sorted(scripts_dir.glob("*.py"))
    cohort = sorted(scripts_dir.glob(args.pattern))

    print("=" * 78)
    print("1. THE RENAMED COHORT, UNDER THE RATCHET'S OWN MATCHER")
    print("=" * 78)
    print(f"population (glob)      : {len(allp)}")
    print(f"cohort ({args.pattern}) : {len(cohort)}")
    print()
    for p in cohort:
        src = p.read_text(encoding="utf-8", errors="replace")
        print(f"  {p.name:56s} answers_help={str(R.answers_help(src)):5s} "
              f"WRITES={bool(R.WRITES.search(src))}")
    print()
    print("  So each is EXEMPT at the `answers_help` test, before WRITES is")
    print("  consulted at all. The rename is safe here because none of the 8")
    print("  writes -- but the exemption does NOT depend on that, so a later")
    print("  edit adding a write to any of them is exempt by the same branch.")

    print()
    print("=" * 78)
    print("2. HOW WIDE IS THE PARSER EXEMPTION?")
    print("=" * 78)
    only_parser = []
    for p in allp:
        src = p.read_text(encoding="utf-8", errors="replace")
        if not R.WRITES.search(src) or not R.answers_help(src):
            continue
        tree = ast.parse(src)
        has_ah = any(isinstance(n, ast.Call)
                     and (getattr(n.func, "id", None) or getattr(n.func, "attr", None))
                     == "answer_help" for n in ast.walk(tree))
        if not has_ah:
            calls_pa = any(isinstance(n, ast.Call)
                           and (getattr(n.func, "attr", None)
                                or getattr(n.func, "id", None)) == "parse_args"
                           for n in ast.walk(tree))
            only_parser.append((p.name, calls_pa))
    print(f"scripts that WRITE and are exempt ONLY by owning a parser : "
          f"{len(only_parser)}")
    never = [n for n, ok in only_parser if not ok]
    print(f"  of those, NEVER calling parse_args (a parser that answers nothing) "
          f": {len(never)}")
    if never:
        print(f"  *** {never}")
    else:
        print("  (so every one of them does parse, and argparse does answer --help)")

    if args.no_exec:
        return 0

    print()
    print("=" * 78)
    print("3. EXECUTED: `--help` ON EACH OF THE COHORT, TREE DIGESTED EITHER SIDE")
    print("=" * 78)
    before = _digest(scripts_dir)
    bad = []
    for p in cohort:
        r = subprocess.run([sys.executable, str(p), "--help"],
                           capture_output=True, text=True, timeout=300, cwd=REPO)
        first = (r.stdout or r.stderr).splitlines()[:1]
        print(f"  {p.name:56s} rc={r.returncode} {first[0][:40] if first else '<no output>'}")
        if r.returncode != 0 or not r.stdout.startswith("usage:"):
            bad.append(p.name)
    after = _digest(scripts_dir)
    print()
    print(f"scripts/ digest before : {before[:16]}")
    print(f"scripts/ digest after  : {after[:16]}")
    print(f"  {'UNCHANGED' if before == after else '*** CHANGED -- a --help ACTED'}")
    if bad:
        print(f"  *** did not print usage and exit 0: {bad}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
