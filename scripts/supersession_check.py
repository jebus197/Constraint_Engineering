#!/usr/bin/env python3
"""Detect a document still asserting a HOLD whose named decisions have since been RULED.

WHY THIS EXISTS, AND THE CLAIM IT REFUTES. On 2026-08-25 this assistant wrote, in a
test file and in a note on the founder's desk, that cross-document supersession is
"not mechanically detectable and is not attempted". The founder asked: "For sure?"

It was too strong. GENERAL supersession — any assertion anywhere overturned by any
later text — is indeed not detectable. But the pattern that actually bit this project
is highly structured and therefore is:

    2026-08-24  RUNWAY_to_BR2_2026-08-18.md line 57 read
                "EVERYTHING IS ON HOLD PENDING NINE FOUNDER DECISIONS"
                and line 58 NAMED the file holding them,
                experimental_notes/Decisions_Inventory_2026-08-22.md,
                which had carried "# FOUNDER RULINGS, 22 August 2026" for two days.

Both halves are machine-readable: a hold assertion, and a named file that contains a
rulings marker. That is enough. This does not detect supersession in general and does
not claim to; it detects THIS project's own convention for recording a hold.

Exit 0 when clean, 1 when a stale hold is found. Reports, never edits.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# A block asserting that work is held pending a decision.
HOLD = re.compile(
    r"\b(ON HOLD PENDING|IS ON HOLD|AWAITING (?:A )?(?:FOUNDER )?(?:RULING|DECISION)"
    r"|PENDING (?:\w+ ){0,3}(?:FOUNDER )?(?:RULING|DECISION)S?"
    r"|NOTHING IS BUILT AND NOTHING IS RUN UNTIL)\b",
    re.I,
)
# A marker that decisions in a file have been answered.
RULED = re.compile(r"\b(FOUNDER RULINGS|## Disposition|RULINGS? (?:GIVEN|RECORDED)"
                   r"|\bRULED:)\b", re.I)
# An explicit supersession marker excuses the block.
SUPERSEDED = re.compile(r"\b(SUPERSEDED|HOLD IS LIFTED|NO LONGER (?:IN )?FORCE"
                        r"|RETAINED AS (?:THE )?(?:RECORD|TRAIL))\b", re.I)

DOC_REF = re.compile(r"`?((?:experimental_notes|resources|docs)/[\w./-]+\.md)`?")

# A dated log entry header, e.g.  - **EXP 40 PRE-LAUNCH ... (2026-04-22, 02:15 BST):**
ENTRY = re.compile(r"^\s*[-*]\s+\*\*.*?\((20\d\d-\d\d-\d\d)")

BLOCK_LINES = 12  # how far around a hold assertion to look for a named file


def _is_in_a_superseded_log_entry(lines, i):
    """True when the hold sits inside a DATED entry that a LATER dated entry follows.

    MEASURED 2026-08-26, and this is the falsification that shaped the tool. The
    first version fired on resources/ONBOARDING.md line 514, which reads
    "Pending founder decisions. (1) Scope of focused confer round ...". That is a
    real hold assertion naming a real file — and it is four months old, recorded
    inside the dated entry "EXP 40 PRE-LAUNCH OVERSIGHT Q&A - FOUNDER DEBRIEF
    (2026-04-22)". ONBOARDING's "Current State" section is 2,400 lines of such
    entries; line 523 of the same file already says in prose that its entries are
    "left intact as historical record; it is not a current-state claim".

    A record of what was pending in April is not a claim that it is pending now.
    So the rule is not an exclusion list, which would silence the check: it is the
    document convention itself. A hold in the newest entry, or in no entry at all
    (the RUNWAY's banner sits above every entry), is LIVE and still fires.
    """
    own = None
    for j in range(i, -1, -1):
        m = ENTRY.match(lines[j])
        if m:
            own = m.group(1)
            break
    if own is None:
        return False  # not inside any dated entry -> a live banner, e.g. the RUNWAY
    return any(m.group(1) > own for m in (ENTRY.match(l) for l in lines) if m)


def scan(paths):
    findings = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if not HOLD.search(line):
                continue
            lo, hi = max(0, i - BLOCK_LINES), min(len(lines), i + BLOCK_LINES)
            block = "\n".join(lines[lo:hi])
            if SUPERSEDED.search(block):
                continue  # the document already says the hold is off
            if _is_in_a_superseded_log_entry(lines, i):
                continue  # a dated record of a past hold, not an assertion of a live one
            for ref in set(DOC_REF.findall(block)):
                target = REPO / ref
                if not target.is_file():
                    continue
                try:
                    body = target.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                m = RULED.search(body)
                if m:
                    findings.append({
                        "file": str(path.relative_to(REPO)) if REPO in path.parents else str(path),
                        "line": i + 1,
                        "assertion": line.strip()[:110],
                        "names": ref,
                        "but_that_file_contains": m.group(0),
                    })
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--path", action="append", default=[],
                    help="extra file or directory to scan")
    args = ap.parse_args()

    roots = [REPO / "experimental_notes", REPO / "resources", REPO / "docs"]
    roots += [pathlib.Path(p) for p in args.path]
    paths = []
    for r in roots:
        if r.is_file():
            paths.append(r)
        elif r.is_dir():
            paths.extend(sorted(r.glob("*.md")))

    findings = scan(paths)
    print(f"  scanned {len(paths)} markdown files under "
          f"{', '.join(r.name for r in roots if r.is_dir())}")
    if not findings:
        print("  no stale holds: every hold assertion either names no ruled file, "
              "or is already marked superseded.")
        return 0
    print(f"\n  ** {len(findings)} STALE HOLD(S) — a document still asserts a hold "
          f"whose named decisions have been ruled: **\n")
    for f in findings:
        print(f"    {f['file']}:{f['line']}")
        print(f"      says   : {f['assertion']}")
        print(f"      names  : {f['names']}")
        print(f"      which contains: {f['but_that_file_contains']}")
        print(f"      -> mark the block SUPERSEDED, or lift the hold.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
