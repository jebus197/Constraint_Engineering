# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_period_reviewed_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 07e1a07d453fbffcdfde49a9a7f727abdfef38e8c8a31b960e3ed10d8de76ab1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Recounts 2 figures in `Inventory_Since_His_First_Message_2026-11-04.md`
from the artefacts rather than restating them: (1) the number of enumerated
items in its what-the-cross-check-refuted list, which the header must match;
(2) the number of DECISION headings on each decision surface, which the
note's register section quotes. Exit 1 on any mismatch."""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
NOTE = REPO / "experimental_notes" / "Inventory_Since_His_First_Message_2026-11-04.md"
TXT = REPO / "experimental_notes" / "Decisions_Awaiting_You_2026-11-03.txt"
MD = REPO / "experimental_notes" / "Decisions_Awaiting_You_2026-11-03.md"


def main() -> int:
    body = NOTE.read_text()
    sect = body.split("## What the cross-check refuted", 1)[1]
    sect = sect.split("## ", 1)[0]
    items = re.findall(r"^\d+\.\s", sect, flags=re.M)
    m = re.search(r"(\d+) figures or claims did not survive", sect)
    header = int(m.group(1))
    txt_n = len(re.findall(r"^DECISION \d+\.", TXT.read_text(), flags=re.M))
    md_n = len(re.findall(r"DECISION \d+\.", MD.read_text()))
    print(f"enumerated refuted items : {len(items)}")
    print(f"header claims            : {header}")
    print(f"decision headings .txt   : {txt_n}")
    print(f"decision headings .md    : {md_n}")
    ok = header == len(items) and txt_n == md_n
    print(f"header matches list AND surfaces agree: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
