# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cbbfc560e3f6dcc358f86cc540d3beda15f759faaee466c040851ec74ac59a60
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Revision 6: the precision defect that dominates the archive, which C4 could
not see from 2 runs.

MEASURED over the 20 archived run directories that still report CONFIRMED access
after revisions 1-5: 672 of the 705 remaining hits -- 95.3% -- are
"parent-directory traversal in a read/list construct", and the matched text is

    Path(__file__).resolve().parent.parent

the standard idiom every Python file in this repository uses to locate the
repository root, including `bench/falsifier_verify.py` itself. `_PARDIR` lists
`\\bparent\\.parent\\b`, and `RELATIVE_ESCAPE` only requires a read/list verb
within 120 characters, which `Path(` satisfies.

WHY IT IS NOT EGRESS. The rule's own justification is that "a panel has no
legitimate reason to climb out of its own directory: the target is the single
file it stands beside". That argument is about a path relative to the WORKING
DIRECTORY. `__file__` is relative to the module being executed, so
`parent.parent` of it is repository-root discovery, not an escape -- and what it
may then open is decided by the staging and observer layers, not by this string.
A real `../../` climb is untouched; so is `parent.parent` on any other base.

Demoted to SUSPICION, not dropped: the hit stays on the Report and in the
advisory's set-aside census.

Usage:  python3 scripts/apply_forensics_pardir_fileroot_rev6_2026-10-02.py [--check]
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECK = "--check" in sys.argv
F = REPO / "bench" / "key_access_forensics.py"
text = F.read_text(encoding="utf-8")
applied = []


def patch(anchor: str, new: str, tag: str) -> None:
    global text
    if new in text:
        print(f"  = {tag} (already applied)")
        return
    if text.count(anchor) != 1:
        raise SystemExit(f"ANCHOR NOT UNIQUE for {tag}: {text.count(anchor)}")
    text = text.replace(anchor, new, 1)
    applied.append(tag)


patch('''        for m in RELATIVE_ESCAPE.finditer(buf):
            record(CONFIRMED, "parent-directory traversal in a read/list construct",
                   m.start(), m.end())''',
      '''        for m in RELATIVE_ESCAPE.finditer(buf):
            # `__file__`-ROOTED IS NOT A CLIMB OUT OF THE WORKING DIRECTORY.
            # See scripts/apply_forensics_pardir_fileroot_rev6_2026-10-02.py for
            # the measurement: 672 of the 705 CONFIRMED hits surviving the other
            # repairs are `Path(__file__).resolve().parent.parent`, the idiom
            # every module in this repository uses to find its own root.
            if "__file__" in m.group(0):
                record(SUSPECT,
                       "parent-directory traversal rooted at __file__ "
                       "(repository-root discovery, not egress) "
                       "[demoted to suspicion, NOT exempted]",
                       m.start(), m.end())
                continue
            record(CONFIRMED, "parent-directory traversal in a read/list construct",
                   m.start(), m.end())''',
      "rev6: __file__-rooted parent.parent is suspicion, not confirmed egress")

if CHECK:
    print("WOULD APPLY:")
else:
    F.write_text(text, encoding="utf-8")
    print("APPLIED:")
for a in applied:
    print("  +", a)
