#!/usr/bin/env python3
"""Correct 5 tickets that claimed to be his annotations when they are not.

WHAT WENT WRONG, and it was mine. The 6 proposals from the Gemini Web design
brief he attached on 2026-10-17 were raised with `source="responses"`, which in
this register means "an annotation the founder wrote in his Responses folder".
They are not that: they are proposals from a document he FORWARDED, recorded by
me. The brief itself is listed in the reader's `NOT_HIS_ANNOTATIONS` for exactly
this reason.

HOW IT WAS CAUGHT. Not by reading. `test_no_ruling_is_dropped_for_being_short`
asserts that the count of LIVE tickets whose source starts with "responses"
equals the count of annotations the reader finds, and it refused the commit:
323 against 318. A sibling assertion would have refused them again, because an
annotation ticket must carry an anchor and 4 of the 5 carry none.

WHY THE DATA IS CORRECTED RATHER THAN THE GUARD WIDENED. The guard encodes a
real invariant -- every live annotation ticket corresponds to an annotation that
exists -- and widening it to accommodate 5 rows I mislabelled would trade a
true invariant for a convenience. `source="chat"` is accurate: he sent the brief
in conversation. `source_ref` still names the brief, so nothing about where the
proposals came from is lost.

THE LOG IS APPEND-ONLY AND STAYS SO. A corrected record is appended under the
SAME tid, which is how `retitle` and the alias machinery already work, so the
prior record remains readable and the identity does not move.

Usage: python3 scripts/correct_the_brief_tickets_source_2026-10-17.py [--apply]
"""
from __future__ import annotations

import argparse
import dataclasses
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

BRIEF = "design_brief.txt"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="write the corrections; omit for a dry run")
    args = parser.parse_args(argv)

    from bench.ticket_store import TicketStore, Ticket

    store = TicketStore()
    store.load()
    wrong = [t for t in store.all()
             if (t.source or "").startswith("responses")
             and BRIEF in (t.source_ref or "")]
    print(f"  tickets claiming to be his annotations but sourced from the "
          f"brief: {len(wrong)}")
    for t in wrong:
        print(f"    {t.tid}  source={t.source!r} anchor={t.anchor!r}")
        print(f"        {t.title[:70]}")
    if not wrong:
        print("  nothing to correct.")
        return 0
    if not args.apply:
        print("\n  DRY RUN. Re-run with --apply to write the corrections.")
        return 0

    for t in wrong:
        fixed = Ticket(**{**dataclasses.asdict(t), "source": "chat"})
        store._append(fixed)
        print(f"    corrected {t.tid} -> source='chat'")

    again = TicketStore()
    again.load()
    still = [x for x in again.all()
             if (x.source or "").startswith("responses")
             and BRIEF in (x.source_ref or "")]
    print(f"\n  remaining mislabelled: {len(still)} (must be 0)")
    return 0 if not still else 1


if __name__ == "__main__":
    raise SystemExit(main())
