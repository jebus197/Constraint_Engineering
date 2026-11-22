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


#: THE GATE'S OWN POPULATION, AND IT IS NOT THE ONE `changed_notes` RETURNS.
#: Measured 2026-11-22 against hooks/pre-commit, which selects:
#:     git diff --cached --name-only --diff-filter=ACM
#:       | grep -E '^experimental_notes/.*\.md$'
#:       | grep -v '^experimental_notes/seat_evidence/'
#: `changed_notes` is wider on 4 axes and so disagreed with the gate in BOTH
#: directions. FALSE POSITIVE: it refused on `resources/RECOVERY.md` 81 -> 83,
#: a file the gate never lints, and the hook's own comment names that risk --
#: a guard that fires on the ordinary case teaches people to reach for
#: --no-verify by reflex. FALSE NEGATIVE, which is the expensive one: it scores
#: the WORKING TREE while the gate scores the INDEX, and it reports a NEW file
#: without ever refusing on it, while the gate holds a new note to a baseline
#: of 0. Both halves fired on 2026-11-22 -- the batch-1 full record read 0 in
#: the tree and 3 in the index, and `BRIEF.md.txt` printed 33 findings beside
#: an exit code of 0.
#:
#: THE WIDE SCAN IS KEPT AND DEMOTED, NOT REMOVED. It is the only thing
#: watching `.txt` companions and `resources/`, which the gate does not judge
#: but the note standard does. It now reports; it no longer decides.
GATE_DIR = "experimental_notes/"
GATE_EXCLUDE = "experimental_notes/seat_evidence/"


def gate_population() -> list[str]:
    """The files the commit gate's note ratchet will actually judge."""
    r = subprocess.run(["git", "diff", "--cached", "--name-only",
                        "--diff-filter=ACM"],
                       capture_output=True, text=True, cwd=REPO, check=True)
    out = []
    for line in (r.stdout or "").splitlines():
        path = line.strip()
        if (path.startswith(GATE_DIR) and path.endswith(".md")
                and not path.startswith(GATE_EXCLUDE)):
            out.append(path)
    return sorted(set(out))


def _score_rev(rev: str, f: str) -> int | None:
    """Score the blob at `rev` for path `f`, as the gate does. None if absent."""
    r = subprocess.run(["git", "show", f"{rev}:{f}"],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        return None
    with tempfile.NamedTemporaryFile("w", suffix=pathlib.Path(f).suffix,
                                     delete=False) as tmp:
        tmp.write(r.stdout)
        tmp_path = pathlib.Path(tmp.name)
    try:
        return _findings(tmp_path, logical=f)
    finally:
        tmp_path.unlink(missing_ok=True)


def gate_verdict() -> tuple[list, list, list, list]:
    """(rows, worse, divergent, unreadable) over the gate's own population.

    THE EMPTY `rev` IS THE INDEX. `git show :path` reads the staged blob, and
    the f-string below supplies that colon -- passing ":" as `rev` builds
    `git show ::path`, which fails and scores every file as unreadable.
    """
    rows, worse, divergent, unreadable = [], [], [], []
    for f in gate_population():
        staged = _score_rev("", f)
        if staged is None:
            unreadable.append(f)
            continue
        head = _score_rev("HEAD", f)
        base = 0 if head is None else head   # a NEW note is held to the standard
        tree = _findings(REPO / f, logical=f) if (REPO / f).is_file() else None
        bad = staged > base
        rows.append((f, head, staged, bad))
        if tree is not None and tree != staged:
            divergent.append((f, staged, tree))
        if bad:
            worse.append((f, base, staged, head is None))
    return rows, worse, divergent, unreadable


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
    print("=" * 74)
    print("NOTE RATCHET PRE-FLIGHT — the stage that runs after the suite")
    print("=" * 74)

    # ---- the half that DECIDES: exactly what the gate will judge ----
    gate = gate_population()
    rows, worse, divergent, gate_unreadable = gate_verdict()
    _st = subprocess.run(["git", "diff", "--cached", "--name-only"],
                         capture_output=True, text=True, cwd=REPO, check=True)
    staged_paths = {ln.strip() for ln in (_st.stdout or "").splitlines() if ln.strip()}
    print()
    print("THE GATE'S OWN POPULATION — staged, under experimental_notes, .md,")
    print("excluding seat_evidence. This half alone sets the exit code.")
    if not gate:
        print("  (nothing staged that the gate's note ratchet judges)")
    for f, head, staged, bad in rows:
        base = "new" if head is None else head
        flag = "   <-- WORSE, the gate WILL refuse this" if bad else ""
        print(f"  {f:<58} HEAD={base} staged={staged}{flag}")

    # A DIVERGENCE IS A FINDING IN ITS OWN RIGHT. A note fixed in the working
    # tree but not staged reads clean to every tree-based check and is refused
    # by the gate, which reads the index. That is what happened on 2026-11-22.
    # ---- the half that REPORTS: everything else the note standard governs ----
    advisory = [f for f in changed_notes() if f not in set(gate)]
    if advisory:
        print()
        print("ADVISORY — changed notes the gate does NOT judge (.txt companions,")
        print("resources/, docs/). These never refuse a commit here.")
        for f in advisory:
            cur = _findings(REPO / f, logical=f) if (REPO / f).is_file() else None
            if cur is None:
                print(f"  {f:<58} UNREADABLE")
                continue
            head = _score_rev("HEAD", f)
            # THE SAME TREE-OR-INDEX QUESTION, ASKED OF EVERY STAGED FILE.
            # A file outside the gate's population is still RECORDED by the
            # commit from the index, so an unstaged fix is lost there too --
            # it simply is not refused. Reported wherever it is staged.
            if f in staged_paths:
                st = _score_rev("", f)
                if st is not None and st != cur:
                    divergent.append((f, st, cur))
            if head is None:
                print(f"  {f:<58} new file, {cur} finding(s)")
            else:
                mark = "   <-- worse than HEAD" if cur > head else ""
                print(f"  {f:<58} HEAD={head} tree={cur}{mark}")

    if divergent:
        print()
        print("TREE AND INDEX DISAGREE — the gate reads the INDEX:")
        for f, staged, tree in divergent:
            hint = "fixed but NOT STAGED; run: git add " + f
            if tree > staged:
                hint = "the tree is worse than what is staged"
            print(f"  {f}: staged={staged} tree={tree}  ({hint})")

    print()
    if gate_unreadable:
        print(f"{len(gate_unreadable)} staged note(s) the linter could not score;")
        print("    a count read off a failed run is not a count. Treat as REFUSE.")
        return 1
    for f, base, staged, was_new in worse:
        shown = "new file, no baseline" if was_new else f"{base}"
        print(f"REFUSED IN PRE-FLIGHT: {f} {shown} -> {staged}")
        print(f"    see the findings with: python3 scripts/note_vagueness_lint.py {f}")
    if worse:
        print()
        print("judged per file, exactly as the gate judges it: a commit that")
        print("cleans one note may not smuggle a new violation into another.")
        print("A NEW note carries no baseline and is held to the whole standard.")
        return 1
    print("OK — no STAGED note under experimental_notes is worse than its")
    print("     committed version, and no new one carries a finding.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
