#!/usr/bin/env python3
"""Mutate the descriptor roster and require its guard to go RED each time.

ANCHORS ARE DERIVED FROM THE SUBJECT, never typed as an expectation: each
mutation names a substring, asserts it occurs EXACTLY ONCE in the live file, and
reports an ANCHOR MISS otherwise -- so a refactor that moves the code makes this
harness complain rather than silently mutate nothing and report green.

THE EXPECTATION IS NOT PER-TEST. The harness never says which test should fail;
it requires the guard to go red and REPORTS which tests did. Naming the test in
advance is how a harness ends up agreeing with itself, which this project has
now corrected in its own instruments more than once.

RESTORES WHAT IT FOUND, not what it assumes: the original bytes of BOTH subject
files are held in memory and written back in a `finally`, verified by sha256.
`hooks/task_list_pulse.py` shares an inode with the live hook in ~/.claude, so a
failed restore would leave the SESSION's own context injection broken -- which
is why the restore is verified rather than trusted.

Run: python3 scripts/the_descriptor_roster_mutations_2026-11-10.py
Exit 0 only when every mutation turns the guard red.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys


def _find_root() -> pathlib.Path:
    start = pathlib.Path(__file__).resolve().parent
    for cand in (start, *start.parents):
        if (cand / "bench" / "domain_immune.py").is_file():
            return cand
    raise SystemExit("cannot locate the repository")


ROOT = _find_root()
TLM = ROOT / "scripts" / "task_list_markers.py"
HOOK = ROOT / "hooks" / "task_list_pulse.py"
NVL = ROOT / "scripts" / "note_vagueness_lint.py"
GUARD = ROOT / "bench" / "tests" / (
    "test_an_entry_code_never_travels_alone_in_chat_2026-11-10.py")

#: (label, file, find, replace)
MUTATIONS = [
    ("M1  drop the descriptor, print the code alone", TLM,
     'rows = [f"{e.ident} {entry_descriptor(e.text, words)}"',
     'rows = [f"{e.ident} "'),
    ("M2  put CLOSED entries in the open roster", TLM,
     'for e in parse_entries(path) if e.state == "OPEN"]',
     'for e in parse_entries(path)]'),
    ("M3  descriptor becomes a constant, not the title", TLM,
     '    toks = t.split()[:words]',
     '    toks = ["an", "outstanding", "project", "entry"]; t = t'),
    ("M4  remove the dangling-word trim", TLM,
     "    while toks and toks[-1].lower().strip(\",;:.-\") in _DANGLING:\n"
     "        toks.pop()",
     "    pass"),
    ("M5  ignore the word budget", TLM,
     "    toks = t.split()[:words]",
     "    toks = t.split()"),
    # ★ M7 ADDED 2026-11-14. The dotted branch of `_ENTRY_IDENT` was narrowed
    # to exclude version numbers and 3-component section references, measured at
    # 159 of 29,864 matches dropped with 0 genuine entry references among them.
    # Reverting it must turn the guard red, or the 12 cases added beside it are
    # asserting nothing.
    ("M7  the detector reads version numbers as entry codes again", NVL,
     'r"|(?<![.\\d])(?<![vV])\\d{1,2}\\.\\d{1,2}[a-z]?(?!\\.?\\d)))\\b")',
     'r"|\\d{1,2}\\.\\d{1,2}[a-z]?))\\b")'),
    ("M6  the hook stops injecting the roster", HOOK,
     '    if roster:\n        ctx += ("\\n[entries] print a code only WITH its '
     'descriptor — "\n                + roster)',
     '    if False:\n        ctx += roster'),
]


def run_guard() -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    return r.returncode, r.stdout + r.stderr


def failing(out: str) -> list[str]:
    return sorted({m for m in re.findall(r"^(?:FAILED|ERROR) (\S+)", out, re.M)})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)

    #: ★ DERIVED FROM THE MUTATION TABLE, 2026-11-14, not a hand-written
    #: tuple. This read `(TLM, HOOK)`, so adding a mutation against a 3rd
    #: subject raised `KeyError` on the first mutation that named it -- and
    #: the closing line still said "both subjects restored", which would have
    #: been a false reassurance about a file the harness had never captured.
    #: A list of subjects beside a table that already names them is the
    #: duplicate-declaration shape this project keeps paying for.
    originals = {path: path.read_text()
                 for _label, path, _find, _repl in MUTATIONS}
    shas = {p: hashlib.sha256(t.encode()).hexdigest()
            for p, t in originals.items()}

    print("=" * 78)
    print("DESCRIPTOR ROSTER MUTATION BOARD")
    print(f"  repository: {ROOT}")
    print("=" * 78)
    rc, out = run_guard()
    print(f"  baseline (unmutated)                                 exit={rc}  "
          f"{'GREEN' if rc == 0 else 'RED'}")
    if rc != 0:
        print("  *** not green to begin with; nothing below means anything ***")
        print(out[-2500:])
        return 1

    red = 0
    try:
        for label, path, find, repl in MUTATIONS:
            n = originals[path].count(find)
            if n != 1:
                print(f"  {label:52s}  ANCHOR MISS ({n} occurrences)")
                continue
            path.write_text(originals[path].replace(find, repl, 1))
            rc, out = run_guard()
            if rc == 0:
                print(f"  {label:52s}  exit=0  *** STILL GREEN ***")
            else:
                red += 1
                names = ", ".join(t.split("::")[-1] for t in failing(out)) \
                    or "collection error"
                print(f"  {label:52s}  exit={rc}  RED")
                print(f"       detected by: {names}")
            path.write_text(originals[path])
    finally:
        for p, t in originals.items():
            p.write_text(t)
            back = hashlib.sha256(p.read_text().encode()).hexdigest()
            assert back == shas[p], f"RESTORE FAILED for {p}"
        print(f"\n  {len(originals)} subject(s) restored, sha256 verified")

    print(f"\n  {red} of {len(MUTATIONS)} mutations turn the guard RED")
    print("=" * 78)
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
