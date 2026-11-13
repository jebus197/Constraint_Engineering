#!/usr/bin/env python3
"""Revert each part of the B169 residue rule and confirm a test goes red.

A guard that passes with the defect restored is not a guard. This drives 6
reversions of `hooks/work_not_narrate.py` and of the producer's labels, and
requires each to fail at least 1 named test.

★ IT RESTORES WHAT IT FOUND, NOT WHAT GIT HOLDS. The subject is UNCOMMITTED
while this runs, so `git checkout --` would discard the repair rather than the
mutation -- the exact destruction recorded in this project's memory as "a
harness must restore what it FOUND". The original bytes are read first, written
back in a `finally`, and the SHA-256 is compared at the end.

★ AND THE SUBJECT IS THE LIVE STOP HOOK. `hooks/work_not_narrate.py` shares an
inode with `~/.claude/hooks/work_not_narrate.py`, so a mutation here IS a
mutation of the running gate. The window is kept to one pytest invocation and
the restore is verified by digest, not by assumption.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
HOOK = REPO / "hooks" / "work_not_narrate.py"
PROD = REPO / "scripts" / "which_residue_rule_discriminates_2026-11-13.py"
TEST = (REPO / "bench" / "tests"
        / "test_a_movable_entry_is_not_one_that_merely_asks_nothing_2026-11-12.py")

#: (name, file, find, replace, why it must be caught)
MUTATIONS = [
    ("M1 drop the narrowing (back to this morning's rule)", HOOK,
     "and not _THIS_ITEM.search(sent):", "and not False:",
     "the object rule alone under-reports a residue tied to this entry"),
    ("M2 drop B169's subject rule", HOOK,
     "if _only_he and _ATTRIBUTIVE.search(sent):",
     "if False and _ATTRIBUTIVE.search(sent):",
     "an attributive frame with a definite object reads as a claim"),
    ("M3 widen the narrowing so it always fires", HOOK,
     '_THIS_ITEM = re.compile(\n    r"\\bthis\\s+(?:entry|item|change|one)\\b',
     '_THIS_ITEM = re.compile(\n    r"(?:)|\\bthis\\s+(?:entry|item|change|one)\\b',
     "the class-statement rule is disabled entirely"),
    ("M4 make the object rule never match", HOOK,
     '_CLASS_OBJECT = re.compile(\n    r"\\bonly\\s+he\\s+(?:may|can)',
     '_CLASS_OBJECT = re.compile(\n    r"(?!x)x\\bonly\\s+he\\s+(?:may|can)',
     "every class statement becomes a residue again"),
    ("M5 flip B169's class-statement label in the producer", PROD,
     '("only he may reject a feature request", False,',
     '("only he may reject a feature request", True,',
     "a label was changed to make a rule look better"),
    # ★ M6 FIRST READ "this change" -> "this CHANGED", WHICH WAS NOT A
    # MUTATION AT ALL: the renamed sentence still carries its attributive
    # frame, so the predicate still answers False and the label still matches.
    # A mutation has to remove the DISCRIMINATING PROPERTY, not a word.
    ("M6 flip the minimal pair's label in the producer", PROD,
     '("his rule is that only he may approve this change", False,',
     '("his rule is that only he may approve this change", True,',
     "a label was flipped on the one case separating the candidates"),
    ("M7 shorten the corpus below its own boundary", PROD,
     "\n]\n\n\ndef load():", "\n]\nCASES = CASES[:8]\n\n\ndef load():",
     "the corpus loses a case and the measurement no longer covers its "
     "own boundary"),
]


def _red(paths_text: dict) -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(TEST), "-x", "-q",
         "--no-header", "-p", "no:cacheprovider"],
        cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode != 0, (r.stdout or "")[-400:]


def main() -> int:
    originals = {p: p.read_bytes() for p in (HOOK, PROD)}
    digests = {p: hashlib.sha256(b).hexdigest() for p, b in originals.items()}
    results = []
    try:
        ok, _ = _red({})
        if ok:
            print("  ABORT: the suite is RED before any mutation.")
            return 2
        print(f"  baseline GREEN; driving {len(MUTATIONS)} reversions\n")
        for name, path, find, repl, why in MUTATIONS:
            text = originals[path].decode()
            if text.count(find) != 1:
                results.append((name, None, f"anchor matched {text.count(find)}x"))
                print(f"  {name:52s} ANCHOR MISS ({text.count(find)})")
                continue
            path.write_text(text.replace(find, repl, 1))
            try:
                red, tail = _red({})
            finally:
                path.write_bytes(originals[path])
            results.append((name, red, why))
            print(f"  {name:52s} {'RED' if red else 'STILL GREEN'}")
            if not red:
                print(f"      NOT CAUGHT -- {why}")
    finally:
        for p, b in originals.items():
            p.write_bytes(b)
        bad = [p for p, d in digests.items()
               if hashlib.sha256(p.read_bytes()).hexdigest() != d]
        if bad:
            print(f"\n  ★ RESTORE FAILED for {bad}")
            return 3
        print("\n  restore verified byte-identical by SHA-256 on "
              f"{len(originals)} files")
    caught = sum(1 for _, r, _ in results if r is True)
    print(f"  {caught} of {len(MUTATIONS)} reversions caught")
    return 0 if caught == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
