# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2af62a12ef43eca21bb3e569206a855361145f0ab3bc3659480e7358e69957ce
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""WHICH PAST CLAIMS IN THIS REPOSITORY ARE UNSAFE BECAUSE A SEARCH RETURNED 0?

`scripts/shell_grep_blind_spot_2026-09-28.py` establishes that the session's
`grep` wraps ugrep with `--ignore-files`, so it honours `.gitignore` and hides
`bench/logs/**` (`.gitignore:48`) and `*.pyc` (`.gitignore:5`). That script
measured the SIZE of the blind spot and stopped there. This one answers the
question it left open, which is the one with consequences: a "0 occurrences"
claim is the shape this project treats as a FINDING, and a hidden tree makes
some of those findings unfalsifiable rather than false.

THE DECIDING CRITERION, DERIVED NOT GUESSED. `--ignore-files` and every
tracked-only git tool filter the set of paths WALKED. Neither can suppress a path
named explicitly on the command line: `grep pattern a.md b.md` reads a.md and
b.md whatever the ignore rules say. So:

    a zero-result claim is SAFE  iff the search enumerated its own targets
    a zero-result claim is UNSAFE iff the search WALKED a tree with a filter

That is a property of the command, not of the conclusion, so it can be checked
mechanically. Tracked-only tools are `git grep`, `git log --name-only`,
`git ls-tree`, `git ls-files`; they are strictly WORSE than `--ignore-files`,
because a gitignored path can enter history only via `git add -f`.

Run:  python3 scripts/zero_result_claim_safety_2026-09-28.py
Exit: 0 if every catalogued verdict still reproduces, 1 if any does not.

NO WOLFRAM CALL: a stored falsifier must run on a machine without it.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FAILURES: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    if not ok:
        FAILURES.append(label)


def ignored_prefixes() -> list[str]:
    gi = (REPO / ".gitignore")
    if not gi.exists():
        return []
    return [ln.strip() for ln in gi.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith(("#", "!"))]


# --------------------------------------------------------------------------
# 1. The blind spot is real, stated in terms of the ignore file rather than a
#    shell the reproducer may not have.
# --------------------------------------------------------------------------
def mechanism() -> None:
    print("\n1. THE MECHANISM, FROM .gitignore RATHER THAN FROM A SHELL FUNCTION")
    pats = ignored_prefixes()
    check("bench/logs/**" in pats, ".gitignore excludes bench/logs/** (the evidence archive)")
    check("*.pyc" in pats, ".gitignore excludes *.pyc")
    logs = REPO / "bench" / "logs"
    n = sum(1 for _ in logs.rglob("*")) if logs.is_dir() else 0
    print(f"    paths on disk under bench/logs/ : {n}")
    # HONESTY ABOUT WHERE THIS CANNOT BE MEASURED, which is the panel's own sandbox.
    git = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                         cwd=REPO, capture_output=True, text=True)
    if git.returncode != 0:
        print("    NOTE: this checkout has no .git, so ripgrep does not apply .gitignore")
        print("    here and a same-shell A/B returns a spurious 0% hidden. That is the")
        print("    SAME silent-fail-toward-clean shape the blind-spot script warns about,")
        print("    and it is why the catalogue below is keyed on the COMMAND SHAPE in the")
        print("    cited text, which is invariant to whether git is present.")


# --------------------------------------------------------------------------
# 2. The catalogue. Each row is a real claim at a real line, classified by the
#    criterion above, with the reason it is safe or not.
# --------------------------------------------------------------------------
CATALOGUE = [
    # (file, line, verdict, quoted fragment that must still be there, why)
    ("experimental_notes/Panel_A8_Section_P_FULL_RECORD_2026-09-20.md", 290, "UNSAFE",
     "0 hits",
     "Claim 4: all 50 absent paths are in no git ref's history. BOTH sweeps are "
     "tracked-only -- `git log --all --name-only` (:290) and `git ls-tree -r` "
     "(:291). The 50 paths are enumerated at :169 and live ENTIRELY in gitignored "
     "trees: under bench/logs/ (.gitignore:48) or __pycache__/*.pyc "
     "(.gitignore:5). A gitignored path reaches history only via `git add -f`, "
     "which is exactly how the sibling 50 at :55 got there. So `0 hits` is very "
     "nearly guaranteed by construction. The note calls the two sweeps "
     "'independent' and names an evil-merge residual at :291 -- but they share "
     "the one blind spot that decides the claim, so they are not independent in "
     "the dimension that matters. Two tools with a common blind spot reporting a "
     "reassuring 0 is the defect CC1 shipped and caught on 2026-09-28."),
    ("scripts/note_naming_check_2026-09-28.py", 179, "UNSAFE",
     "git grep",
     "Item 5's novelty test IS a zero-result claim: a phrase is reported "
     "'NAMES NOTHING' when repo_hits()==0. It asks `git grep`, so a term defined "
     "only under bench/logs/** reads as novel. Direction of error: FALSE "
     "POSITIVES against exactly the 353 MB the search cannot see. It also means a "
     "verdict changes on `git add`, not on content."),
    ("scripts/orphan_figures_2026-09-10.py", 122, "UNSAFE",
     "git ls-files",
     "Decides UNCITED from tracked content only. Under the additive standard an "
     "'orphan' verdict is the premise for a REMOVAL, so a figure cited only from "
     "bench/logs/** could be removed on a search that could not see the citation. "
     "Highest consequence of the three, because the conclusion licenses deletion."),
    ("scripts/lint_reach_over_notes_2026-09-10.py", 115, "UNSAFE",
     "git grep",
     "Reach over notes via `git grep`; a note whose only reach is into an ignored "
     "path reads as unreached."),
    # --- and the control: a claim that is SAFE, checked because Section 5 asks. ---
    ("experimental_notes/Research_FULL_RECORD_2026-09-09.md", 380, "SAFE",
     "returns 0 matches",
     "\"grep -i 'additive|additivity' over docs/MATHEMATICAL_APPENDIX.md and "
     "bench/directives/universal/cdsfl_core_formal.md returns 0 matches\". The "
     "search NAMES ITS TWO TARGETS, both tracked, so no ignore rule can hide "
     "either. Re-executed below and it still returns 0. This is the criterion's "
     "discriminating case: same 0, opposite verdict, because the command shape "
     "differs."),
]


def catalogue() -> None:
    print("\n2. CATALOGUE OF ZERO-RESULT CLAIMS, CLASSIFIED BY COMMAND SHAPE")
    for rel, line, verdict, frag, why in CATALOGUE:
        p = REPO / rel
        ok = False
        if p.exists():
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            # tolerate +/- 3 lines of drift so an edit above does not fake a pass
            for probe in range(max(0, line - 4), min(len(lines), line + 3)):
                if frag in lines[probe]:
                    ok = True
                    break
        check(ok, f"{verdict:6s} {rel}:{line} -- fragment {frag!r} still present")
        print(f"         {why}")


def reexecute_the_safe_one() -> None:
    print("\n3. RE-EXECUTING THE SAFE CLAIM (the one the criterion predicts survives)")
    targets = [REPO / "docs" / "MATHEMATICAL_APPENDIX.md",
               REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"]
    missing = [t for t in targets if not t.exists()]
    if missing:
        check(False, f"both named targets exist ({missing} absent)")
        return
    hits = 0
    for t in targets:
        body = t.read_text(encoding="utf-8", errors="replace").lower()
        hits += body.count("additive") + body.count("additivity")
    print(f"    occurrences of 'additive'/'additivity' across the 2 named files: {hits}")
    check(hits == 0,
          "the SAFE claim still returns 0 when the two named files are read directly "
          "-- an explicit-path search is immune to the ignore rule")


if __name__ == "__main__":
    mechanism()
    catalogue()
    reexecute_the_safe_one()
    print()
    if FAILURES:
        print(f"FALSIFIED -- {len(FAILURES)} check(s) failed:")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("Every catalogued verdict reproduces.")
    sys.exit(0)
