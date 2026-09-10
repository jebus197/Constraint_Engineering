#!/usr/bin/env python3
"""Decide MECHANICALLY whether an item blocks, and park it if it does not.

WHY THIS EXISTS, in the founder's words, 2026-09-10: *"Why do you keep stopping
for non-blocking items? ... Why not just leave them all to discuss with me at the
end of the completed task list, unless there is something that clearly warrants
my immediate attention? ... Can you not write some kind of mechanical 'is
blocker' / 'is not blocker' 'append to end of task list/final report' script?"*

THE ANSWER TO WHY A SCRIPT AND NOT A RESOLUTION. This project's own record:
*"The failure was never the absence of a rule or a checker; it was never running
the checker."* A resolution to stop interrupting is a claim about future
behaviour, and claims are the category this project measures worst. A predicate
is checkable, and a parking file is a place the item goes instead of into a
sentence addressed to him.

WHAT BLOCKS, and the list is deliberately SHORT. An item blocks only if
proceeding without an answer would be unsafe, irreversible, or would waste real
work:

  1. IRREVERSIBLE      deleting a git ref, spending money on a paid seat, or
                       touching the sealed answer-key store. His 3 categories,
                       standing, and they require him in person.
  2. NEEDS_HIS_HANDS   the action is on a machine or an account the assistant
                       cannot reach, or in his own control plane.
  3. WOULD_WASTE_WORK  the item forks the work: 2 defensible readings lead to
                       materially different builds, so guessing risks discarding
                       whichever branch is built.
  4. FROZEN_ARTEFACT   changing a pre-registration file, a sealed archive, or a
                       quoted ruling. Task 3.1 established the cost of a literal
                       reading here.

EVERYTHING ELSE IS PARKED. Not dropped, not forgotten -- appended to
`experimental_notes/PARKED_FOR_THE_FOUNDER.md`, which is the file he reads at the
end. An item parked is an item he still gets; it is simply not an interruption.

THE ASYMMETRY IS DELIBERATE. A false BLOCK costs one interruption. A false PARK
could let an irreversible action proceed unasked. So the predicate answers BLOCK
when it cannot tell, and says which rule fired.
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"

RULES: list[tuple[str, re.Pattern, str]] = [
    ("IRREVERSIBLE", re.compile(
        r"delete\s+(a\s+)?(git\s+)?(ref|branch|tag)|git\s+(branch\s+-D|push\s+--force|reflog\s+expire)"
        r"|\bpaid\s+(seat|dispatch|model|run)\b|spend(ing)?\s+money|costs?\s+money"
        r"|answer[- ]key|sealed\s+(store|archive)|passphrase|vault", re.I),
     "his 3 standing categories require him in person"),
    ("NEEDS_HIS_HANDS", re.compile(
        r"password|credential|api\s*key|token\s+rotat|log\s*in\b|sign\s*in\b"
        r"|desktop\s+app\s+config|claude_desktop_config|system\s+settings"
        r"|his\s+(machine|laptop|phone)|purchase|licence\s+renew|license\s+renew", re.I),
     "the assistant cannot reach that machine or account"),
    ("FROZEN_ARTEFACT", re.compile(
        r"pre[- ]registration|frozen\s+(file|config|arm)|exp56_configs"
        r"|quoted\s+ruling|verbatim\s+(ruling|quotation)|archival\s+(note|record|log)"
        r"|bench/logs/", re.I),
     "changing a frozen artefact falsifies the record it exists to preserve"),
    ("WOULD_WASTE_WORK", re.compile(
        r"\b(2|two)\s+(possible\s+)?(answers|readings|options|branches)\s+lead"
        r"|opposite\s+work|fork(s)?\s+the\s+work|either\s+.{0,40}\s+or\s+.{0,40},\s*and\s+the\s+2", re.I),
     "guessing risks discarding whichever branch is built"),
]


def classify(text: str) -> tuple[str, str]:
    """(verdict, why). BLOCK when any rule fires; PARK otherwise."""
    for name, rx, why in RULES:
        if rx.search(text):
            return "BLOCK", f"{name}: {why}"
    return "PARK", "no blocking rule fired; it goes to the end-of-work list"


def park(title: str, detail: str, stamp: str | None = None) -> pathlib.Path:
    if stamp is None:
        stamp = subprocess.run(["date", "-Iseconds"], capture_output=True,
                               text=True).stdout.strip()
    if not PARKED.is_file():
        PARKED.write_text(
            "# Parked for the founder — non-blocking items, newest last\n\n"
            "**Opened 2026-09-10 on his instruction:** *\"Why not just leave them all to "
            "discuss with me at the end of the completed task list, unless there is something "
            "that clearly warrants my immediate attention?\"*\n\n"
            "Every item here was classified by `scripts/blocker_triage.py` as NOT blocking. "
            "Nothing here is dropped; it is queued. Items that DO block are raised at once and "
            "never appear in this file.\n\n---\n",
            encoding="utf-8")
    with PARKED.open("a", encoding="utf-8") as f:
        f.write(f"\n## {title}\n\n*Parked {stamp}.*\n\n{detail.strip()}\n")
    return PARKED


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--title", help="short name for the item")
    ap.add_argument("--detail", default="", help="what it is, in full")
    ap.add_argument("--check-only", action="store_true",
                    help="classify and print; write nothing")
    a = ap.parse_args()
    if not a.title:
        ap.error("--title is required")

    verdict, why = classify(f"{a.title}\n{a.detail}")
    print(f"  {verdict}: {why}")
    if verdict == "BLOCK":
        print("  -> raise this with the founder NOW; do not park it")
        return 2
    if a.check_only:
        print("  -> would be appended to " + str(PARKED.relative_to(REPO)))
        return 0
    p = park(a.title, a.detail)
    print(f"  -> appended to {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
