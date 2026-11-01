#!/usr/bin/env python3
"""Pre-flight the per-file NOTE RATCHET before paying for the 8-minute suite.

WHY THIS EXISTS. The pre-commit gate runs the note ratchet AFTER the test suite,
so a commit whose tests are entirely green is still refused minutes later by a
single word of prose. Measured 2026-11-01: a log reading `2333 passed, 9
skipped` ended `COMMIT_EXIT=1`, refused because
`experimental_notes/CDSFL_MASTER_TASK_LIST.md went from 24 to 26 note
finding(s)` -- a bare `count` and an undefined `live probe`, neither visible to
any of those 2,333 tests. That cost about 8 minutes, and the same shape had cost
another 8 minutes an hour earlier.

WHAT IT CHECKS, AND THE ONE SUBTLETY THAT MAKES IT CORRECT. For each changed
note it lints the working copy, then lints `git show HEAD:<path>` and passes
`--as <path>` so the linter sees the LOGICAL path. The linter is PATH-SENSITIVE
-- `experimental_notes/` is held to rules a scratch file is not -- so comparing a
temp copy without `--as` compares 2 different questions. That exact mistake was
measured on 2026-10-15 at 4 of 6 files.

IT IS A PRE-FLIGHT, NOT A GATE. It never writes, never commits, and has no
authority over the real ratchet in `hooks/pre-commit`: it exists so a refusal is
met in seconds rather than after the suite. A file absent from HEAD has no
baseline and is reported as new rather than counted as a rise.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
LINT = REPO / "scripts" / "note_vagueness_lint.py"
_COUNT = re.compile(r"^\s*(\d+) finding\(s\)\.", re.M)
NOTE_SUFFIXES = (".md", ".txt")


def _findings(path: pathlib.Path, logical: str | None = None) -> int | None:
    cmd = [sys.executable, str(LINT)]
    if logical:
        cmd += ["--as", logical]
    cmd.append(str(path))
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    m = _COUNT.search(r.stdout or "")
    return int(m.group(1)) if m else None


def changed_notes() -> list[str]:
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                       text=True, cwd=REPO, check=True)
    out = []
    for line in (r.stdout or "").splitlines():
        p = line[3:].strip().strip('"')
        if " -> " in p:                       # a rename: judge the destination
            p = p.split(" -> ", 1)[1]
        if p.endswith(NOTE_SUFFIXES):
            out.append(p)
    return sorted(set(out))


def main() -> int:
    notes = changed_notes()
    print("=" * 74)
    print("NOTE RATCHET PRE-FLIGHT — the stage that runs after the suite")
    print("=" * 74)
    if not notes:
        print("\nno changed notes; the ratchet cannot refuse this commit.")
        return 0
    worse, new, unreadable = [], [], []
    print()
    for f in notes:
        cur = _findings(REPO / f)
        if cur is None:
            unreadable.append(f)
            print(f"  {f:<58} UNREADABLE")
            continue
        head_ok = subprocess.run(["git", "cat-file", "-e", f"HEAD:{f}"],
                                 capture_output=True, cwd=REPO).returncode == 0
        if not head_ok:
            new.append((f, cur))
            print(f"  {f:<58} new file, {cur} finding(s)")
            continue
        with tempfile.NamedTemporaryFile("w", suffix=pathlib.Path(f).suffix,
                                         delete=False) as tmp:
            blob = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True,
                                  text=True, cwd=REPO, check=True).stdout
            tmp.write(blob)
            tmp_path = pathlib.Path(tmp.name)
        try:
            base = _findings(tmp_path, logical=f)
        finally:
            tmp_path.unlink(missing_ok=True)
        flag = ""
        if base is not None and cur > base:
            worse.append((f, base, cur))
            flag = "   <-- WORSE, the gate will refuse this"
        print(f"  {f:<58} HEAD={base} now={cur}{flag}")

    print()
    if unreadable:
        print(f"{len(unreadable)} note(s) the linter could not score; treat as unknown.")
    for f, base, cur in worse:
        print(f"REFUSED IN PRE-FLIGHT: {f} {base} -> {cur}")
        print(f"    see the findings with: python3 scripts/note_vagueness_lint.py {f}")
    if worse:
        print("\njudged per file, exactly as the gate judges it: a commit that")
        print("cleans one note may not smuggle a new violation into another.")
        return 1
    print("OK — no changed note is worse than its committed version.")
    if new:
        print(f"     {len(new)} new note(s) carry no baseline; their counts are above.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
