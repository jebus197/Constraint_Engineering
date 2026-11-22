#!/usr/bin/env python3
"""MUTATIONS FOR THE MEMORY-INDEX PRESSURE RELIEF.

Each mutation reverses exactly ONE property the guard claims to hold. A mutation
that leaves the guard green marks a property the guard only describes.

ANCHORS ARE DERIVED FROM THE SUBJECT, NEVER TYPED AS LINE NUMBERS. Every
mutation is a unique string replacement located by searching the live file, so a
later edit that shifts the function cannot silently turn a mutation into a no-op
-- the recorded failure being a harness whose 2 of 5 misses were the probe and
not the subject.

THE ORIGINAL BYTES ARE CAPTURED AND RESTORED, not recovered with `git checkout`:
on 2026-11-01 a restore by checkout ate uncommitted work in the same file.

Usage:  python3 scripts/the_index_relief_mutations_2026-11-21.py
Exit 0 only when EVERY mutation turns the guard red.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "scripts" / "cdsfl_sv.py"
GUARD = "bench/tests/test_the_index_can_never_stop_filling_2026-11-21.py"

#: (name, find, replace, the property it reverses)
MUTATIONS: list[tuple[str, str, str, str]] = [
    (
        "salience is ignored in the eviction order",
        "    candidates.sort(key=lambda c: (c[0], c[1], c[2], c[3]))",
        "    candidates.sort(key=lambda c: (c[1], c[2], c[3]))",
        "lowest salience is evicted first",
    ),
    (
        "age is ignored inside a salience tier",
        "    candidates.sort(key=lambda c: (c[0], c[1], c[2], c[3]))",
        "    candidates.sort(key=lambda c: (c[0], -c[2], -c[3]))",
        "oldest goes first within a tier",
    ),
    (
        "a dry run writes anyway",
        '    if dry_run:\n        report["ok"] = True\n        report["reason"] = "dry run — nothing written"\n        return report\n\n    stamp = datetime.now().astimezone().isoformat(timespec="seconds")',
        '    if False:\n        report["ok"] = True\n        report["reason"] = "dry run — nothing written"\n        return report\n\n    stamp = datetime.now().astimezone().isoformat(timespec="seconds")',
        "a dry run writes absolutely nothing",
    ),
    (
        "no backup is written before the change",
        '        backup.write_text(text, encoding="utf-8")\n        report["backup"] = backup.name',
        '        report["backup"] = backup.name',
        "a backup holds the original bytes",
    ),
    (
        "the moved pointers never reach the companion",
        "        if old_overflow:\n            overflow.write_text(old_overflow + header + body, encoding=\"utf-8\")",
        "        if old_overflow:\n            overflow.write_text(old_overflow + header, encoding=\"utf-8\")",
        "no lesson pointer is lost",
    ),
    (
        "the companion is not counted by the orphan scan",
        "_MEMORY_POINTER_SIBLINGS = (_MEMORY_ARCHIVE_NAME, _MEMORY_OVERFLOW_NAME)",
        "_MEMORY_POINTER_SIBLINGS = (_MEMORY_ARCHIVE_NAME,)",
        "the orphan scan counts the companion's pointers",
    ),
    (
        "the relief is unwired from the automatic save path",
        "    _rel = relieve_memory_index_pressure(_mem_dir, dry_run=not apply)",
        '    _rel = {"ok": True, "moved": 0, "reason": "disabled"}',
        "the relief is wired into the automatic path",
    ),
    (
        "an emptied heading is left standing over nothing",
        "                if not has_child:\n                    continue",
        "                if not has_child:\n                    pass",
        "a heading is not left standing over nothing",
    ),
    (
        "the companion no longer says the lessons still bind",
        'f"stays inside the loader\'s limits. **Nothing here is retired.** "',
        'f"stays inside the loader\'s limits. "',
        "the companion says the lessons still bind",
    ),
    (
        "prose with no link is treated as an evictable lesson",
        "    links = list(_MEMORY_LINK_RE.finditer(unit))\n    if not links:\n        return -1",
        "    links = list(_MEMORY_LINK_RE.finditer(unit))\n    if not links:\n        return 0",
        "prose on a shared line is never evicted",
    ),
    (
        "the relief refuses to act once the index is over its target",
        '    if len(text) <= target:',
        '    if True:',
        "it brings an over-full index under the target",
    ),
]


def run_guard() -> tuple[int, str]:
    pr = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", GUARD],
        capture_output=True, text=True, cwd=ROOT)
    tail = (pr.stdout.strip().splitlines() or ["<no output>"])[-1]
    return pr.returncode, tail


def main(argv=None) -> int:
    #: `--help` answers with a usage line and runs NOTHING, per
    #: `bench/tests/test_help_is_answered_2026-09-11.py`. This harness mutates a
    #: live source file and runs pytest once per mutation, so a `--help` that
    #: did the work would edit the tree to answer a question about itself.
    argparse.ArgumentParser(
        description=__doc__.splitlines()[0]).parse_args(argv)
    original = SUBJECT.read_text(encoding="utf-8")
    try:
        rc, tail = run_guard()
        print(f"BASELINE: rc={rc}  {tail}")
        if rc != 0:
            print("!! the guard is red before any mutation; fix that first")
            return 1

        red = 0
        for name, find, repl, prop in MUTATIONS:
            n = original.count(find)
            if n != 1:
                print(f"  [ANCHOR  ] {name}: anchor found {n} times, expected 1 "
                      f"-- the probe is broken, not the subject")
                continue
            SUBJECT.write_text(original.replace(find, repl, 1), encoding="utf-8")
            rc, tail = run_guard()
            SUBJECT.write_text(original, encoding="utf-8")
            ok = rc != 0
            red += ok
            print(f"  [{'RED  ' if ok else 'GREEN'}] {name}")
            print(f"            reverses: {prop}")
            if not ok:
                print(f"            !! the guard stayed green: {tail}")
        print(f"\n{red} of {len(MUTATIONS)} mutations turned the guard red")
        rc, tail = run_guard()
        print(f"RESTORED: rc={rc}  {tail}")
        if rc != 0:
            print("!! the subject was not restored cleanly")
            return 1
        return 0 if red == len(MUTATIONS) else 1
    finally:
        if SUBJECT.read_text(encoding="utf-8") != original:
            SUBJECT.write_text(original, encoding="utf-8")
            print("(subject restored in the finally block)")


if __name__ == "__main__":
    raise SystemExit(main())
