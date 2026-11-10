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

    originals = {p: p.read_text() for p in (TLM, HOOK)}
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
        print("\n  both subjects restored, sha256 verified")

    print(f"\n  {red} of {len(MUTATIONS)} mutations turn the guard RED")
    print("=" * 78)
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
