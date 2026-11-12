#!/usr/bin/env python3
"""Revert each clause of the permission predicate and prove the guard goes RED.

★ WHY THIS EXISTS. `hooks/work_not_narrate.py` gained `_residue_is_his` on
2026-11-12, on his ruling that the refusal budget of 8 *"isn't sensible if it
causes you to stop on things you can do"*. The predicate separates an entry that
asks him nothing from an entry whose residue is his PERMISSION. A claim that its
guard "goes red when reverted" is a claim about evidence, so the producer is
committed beside the number -- `measured-rate-travels-with-its-script`.

★ IT ALREADY CAUGHT ONE REAL FAULT IN ITS OWN SUBJECT. The first version of the
predicate caught B56, B104 and B140 and MISSED B144, whose body says the design
consequence is his and is held under his `d`. 2 clauses were added for that
miss, and reverting them left the guard FULLY GREEN -- the repair for a measured
miss was itself tested by nothing. The tests that close it exist because this
harness said so.

★ ANCHORS ARE DERIVED, NEVER TYPED. Each mutation locates its target by reading
the live file, so a rename cannot leave a mutation silently matching nothing and
reporting a pass as a kill. A mutation whose anchor is absent is reported as
NOT APPLIED rather than counted.

★ RESTORE IS BYTE-EXACT AND FROM WHAT WAS FOUND, not from git: the file is
hard-linked to the live Stop hook at `~/.claude/hooks/`, so a careless restore
would be a careless edit of the hook that governs this session's stopping. The
original bytes are held in memory, the sha256 is compared after writing back,
and the write is in-place so the inode -- and therefore the hard link -- survives.

Costs nothing but local CPU: reads 2 local files, runs 1 pytest file per mutation.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "work_not_narrate.py"
GUARD = REPO / "bench" / "tests" / \
    "test_a_movable_entry_is_not_one_that_merely_asks_nothing_2026-11-12.py"


def _residue_block(src: str) -> tuple[int, int]:
    """(start, end) byte offsets of the `_HIS_RESIDUE` pattern's own source.

    ★ DERIVED, AND THE FIRST VERSION OF THIS FUNCTION WAS WRONG. It selected a
    clause by guessing at a line prefix -- `|`, `_HIS_RESIDUE` or `(` -- and the
    very first clause of the pattern begins with none of them, so the B56
    authorisation clause reported ANCHOR ABSENT when it was plainly present. A
    harness that cannot find its own target reports a pass as a kill. Bounding
    the pattern's text and searching inside it removes the guess.
    """
    i = src.index("_HIS_RESIDUE = re.compile(r\"\"\"(")
    j = src.index("\"\"\", re.I | re.X)", i)
    return i, j


def mutations(src: str) -> list[tuple[str, str, str]]:
    """(name, find, replace) with every `find` derived from the live source."""
    out: list[tuple[str, str, str]] = []

    guarded = "if not d.get(\"live_asks\") and not _residue_is_his(body):"
    out.append(("budget half stops consulting the predicate", guarded,
                "if not d.get(\"live_asks\"):"))

    naming = "if kind != \"OWED\" and not _residue_is_his(body):"
    out.append(("naming half stops consulting the predicate", naming,
                "if kind != \"OWED\":"))

    body_true = "        return bool(_HIS_RESIDUE.search(body or \"\"))"
    out.append(("predicate always says NO residue is his", body_true,
                "        return False"))
    out.append(("predicate always says EVERY residue is his", body_true,
                "        return True"))

    failsafe = "        return False           # fail-safe: costs the preference, never the gate"
    out.append(("fail-safe removed so rubbish raises", failsafe,
                "        raise"))

    for needle, label in (
            ("is\\s+still\\s+his\\s+authoris", "the B56 authorisation clause"),
            ("widen\\s+his\\s+own\\s+scope", "the B104 scope clause"),
            ("this\\s+is\\s+his\\s+and\\s+not\\s+mine", "the B140 his-not-mine clause"),
            ("held\\s+under\\s+his", "the B144 held-under-his-d clause"),
            ("(consequence|decision|choice|call)\\s+is\\s+his", "the B144 consequence clause"),
    ):
        i, j = _residue_block(src)
        block = src[i:j]
        if needle not in block:
            out.append((f"{label} (ANCHOR ABSENT)", needle, needle))
            continue
        #: ★ EVERY OCCURRENCE IN THE BLOCK, NOT THE FIRST LINE THAT MATCHES.
        #: The pattern carries overlapping variants -- `wh(y|ich) this is his
        #: and not mine` beside a bare `this is his and not mine` -- so killing
        #: one left the other matching the same entry and the mutation SURVIVED,
        #: reporting a redundancy as a gap in the guard. Removing the capability
        #: means removing all of its spellings at once.
        dead = block.replace(needle, "ZZZ_NEVER_MATCHES_ZZZ")
        out.append((f"{label} removed", block, dead))
    return out


def run_guard() -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                        "--no-header", "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=str(REPO))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    original = HOOK.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    ino = HOOK.stat().st_ino
    src = original.decode("utf-8")

    base_rc, base_out = run_guard()
    print(f"BASELINE: rc={base_rc}  {base_out.strip().splitlines()[-1] if base_out.strip() else ''}")
    if base_rc != 0:
        print("REFUSED: the guard is not green before any mutation, so no kill "
              "can be attributed to a mutation.")
        return 2

    muts = mutations(src)
    killed = applied = 0
    rows = []
    try:
        for name, find, repl in muts:
            if "ANCHOR ABSENT" in name or find == repl:
                rows.append((name, "NOT APPLIED", "anchor not found in the live file"))
                continue
            if src.count(find) != 1:
                rows.append((name, "NOT APPLIED",
                             f"anchor occurs {src.count(find)} times, not once"))
                continue
            applied += 1
            with open(HOOK, "w", encoding="utf-8") as fh:   # in-place: keeps the inode
                fh.write(src.replace(find, repl, 1))
            rc, out = run_guard()
            tail = out.strip().splitlines()[-1] if out.strip() else ""
            if rc != 0:
                killed += 1
                rows.append((name, "RED", tail))
            else:
                rows.append((name, "SURVIVED", tail))
    finally:
        with open(HOOK, "w", encoding="utf-8") as fh:
            fh.write(src)
        back = HOOK.read_bytes()
        ok = hashlib.sha256(back).hexdigest() == sha
        same_ino = HOOK.stat().st_ino == ino
        print(f"\nRESTORE: sha256 {'MATCHES' if ok else 'DIFFERS -- INVESTIGATE'}"
              f"  inode {'PRESERVED' if same_ino else 'BROKEN -- THE HARD LINK TO THE LIVE HOOK IS GONE'}")
        if not (ok and same_ino):
            return 3

    print()
    for name, verdict, tail in rows:
        print(f"  [{verdict:11s}] {name}")
        if verdict == "SURVIVED":
            print(f"                {tail}")
    print(f"\n{killed} of {applied} applied mutation(s) RED"
          f"  ({len(muts) - applied} not applied)")
    return 0 if applied and killed == applied else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    raise SystemExit(main())
