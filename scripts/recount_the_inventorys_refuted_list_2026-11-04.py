#!/usr/bin/env python3
"""A section header must agree with the list it heads. Recounted, not trusted.

★ SPECIFIED BY A FREE PANEL SEAT, 2026-11-04, AND NEVER LANDED. The seat's
recount found the refuted section of
`experimental_notes/Inventory_Since_His_First_Message_2026-11-04.md` headed "8"
against a list of 9. The correction landed and the note records it; this
producer, which keeps the two in agreement from now on, did not.

WHY A HEADER AND ITS OWN LIST CAN DISAGREE. The header is typed; the list grows.
Nothing recomputed one from the other, so the only thing standing between them
was attention -- and the project's own record is that attention is exactly what
fails: *"The failure was never the absence of a rule or a checker; it was never
running the checker."*

WHAT THIS DELIBERATELY DOES NOT ASSERT, and the restraint is the point. The same
section's item 5 cites a decisions count, which the seat annotated from 19 to 20.
That count is now 30. A producer that pinned a note's historical figure to the
LIVE count would go red every time the list grew, which is the sliding-figure
fault this project has met repeatedly -- a figure correct when written and stale
now. So the decisions figures are REPORTED here and never asserted. The only
invariant asserted is the one that must hold at every moment: a header's stated
count equals the number of items beneath it.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
DEFAULT = REPO / "experimental_notes" / "Inventory_Since_His_First_Message_2026-11-04.md"
HEADING = "## What the cross-check refuted"

#: a stated count may be a digit string or appear as "all N were mine"
STATED = re.compile(r"\b(\d+)\s+figures?\s+or\s+claims?\b")
ALL_N = re.compile(r"\ball\s+(\d+)\s+were\s+mine\b", re.I)
ITEM = re.compile(r"^(\d+)\.\s")


def section(text: str, heading: str = HEADING) -> list[str]:
    lines = text.splitlines()
    try:
        a = next(i for i, l in enumerate(lines) if l.startswith(heading))
    except StopIteration:
        raise SystemExit(f"ANCHOR ABSENT: no section headed {heading!r}")
    b = next((i for i, l in enumerate(lines[a + 1:], a + 1)
              if l.startswith("## ")), len(lines))
    return lines[a:b]


def recount(path: Path) -> dict:
    sec = section(path.read_text(encoding="utf-8"))
    body = "\n".join(sec)
    items = [m.group(1) for m in (ITEM.match(l) for l in sec) if m]
    stated = STATED.search(body)
    all_n = ALL_N.search(body)
    return {
        "items": len(items),
        "numbering": [int(x) for x in items],
        "stated": int(stated.group(1)) if stated else None,
        "all_n": int(all_n.group(1)) if all_n else None,
        "decisions_figures": sorted({int(x) for x in
                                     re.findall(r"\b(\d+)\s+decisions\b", body)}),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", default=str(DEFAULT))
    a = ap.parse_args()
    p = Path(a.file)
    r = recount(p)
    fails = []

    print(f"file   : {p.name}")
    print(f"items  : {r['items']}   numbering: {r['numbering']}")
    print(f"stated : {r['stated']}   'all N were mine': {r['all_n']}")

    def ck(label, got, want):
        ok = got == want
        print(f"  {'OK  ' if ok else 'FAIL'} {label:56s} {got!r}")
        if not ok: fails.append(label)

    ck("the header states a count at all", r["stated"] is not None, True)
    if r["stated"] is not None:
        ck("the stated count equals the item count", r["stated"], r["items"])
    if r["all_n"] is not None:
        ck("the 'all N were mine' figure agrees too", r["all_n"], r["items"])
    ck("the numbering is contiguous from 1",
       r["numbering"], list(range(1, r["items"] + 1)))

    print("\nREPORTED, NOT ASSERTED -- historical figures that legitimately age:")
    print(f"  decisions counts cited in this section: {r['decisions_figures']}")
    print("  these are statements about a past moment. Pinning them to the live")
    print("  count would make this producer red every time the list grew.")

    print()
    if fails:
        print(f"{len(fails)} FAILED: {fails}")
        return 1
    print("the header and its list agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
