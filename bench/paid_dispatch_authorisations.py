#!/usr/bin/env python3
"""Which panel rounds the founder authorised paid seats for. One source, one rule.

THE CHANGE THIS MAKES, 2026-09-20. Two guards independently asserted that no
round dated after a cut holds a paid seat reply:

    bench/tests/test_panel_conditions_are_met_2026-09-10.py  (Section P, P1)
    bench/tests/test_panel_records_are_preserved_2026-09-11.py

That is an ABSENCE predicate, and it is the wrong proposition. It went red the
moment the founder authorised a paid review, and the 2 obvious ways to green it
-- move the cut forward, or delete the guard -- both silently license the NEXT
unauthorised spend. Spend is the one category the founder reserves entirely to
himself, so the guard must get stronger under pressure, not weaker.

An AUTHORISATION predicate is strictly stronger. "Every paid reply lies inside an
authorised round" implies the old statement over the old population AND extends
the check to rounds before the cut, which the absence form never examined.

WHY A MODULE RATHER THAN A CONSTANT IN EACH TEST. The record already carries the
lesson: the round-date rule was written down 4 times across this file's
neighbours, and the comment at
test_panel_records_are_preserved_2026-09-11.py:243-249 names it -- "A rule
written down 4 times is 4 rules." The authorisation list is a money constraint;
2 copies that could drift is exactly the shape to avoid.

The data lives at bench/directives/universal/paid_dispatch_authorisations.json,
beside the other universal directives, so it is reviewable as a document rather
than buried in test code.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUTHORISATIONS = REPO / "bench" / "directives" / "universal" / "paid_dispatch_authorisations.json"

#: Seats that cost money, per this project's routing table. `cc2` and `fable`
#: run on the founder's Max subscription and are free.
PAID_SEATS = ("cx", "cgpt", "ge", "ds", "kimi")


def _load() -> dict:
    if not AUTHORISATIONS.is_file():
        # FAIL CLOSED. A missing authorisation file must not read as "everything
        # is authorised"; it reads as "nothing is", which refuses rather than
        # permits. A guard that degrades to no guard is the defect this project
        # keeps recording.
        return {"authorisations": []}
    return json.loads(AUTHORISATIONS.read_text(encoding="utf-8"))


def authorised_rounds() -> set[str]:
    """The exact round directory names the founder authorised paid seats for.

    Names are matched EXACTLY. No prefix, no date range, no wildcard -- so the
    guard keeps asking "was this authorised?" rather than "is this recent?".
    """
    out: set[str] = set()
    for entry in _load().get("authorisations", []):
        out.update(entry.get("rounds", []))
    return out


def authorisation_for(round_name: str) -> dict | None:
    """The authorisation covering `round_name`, or None if there is none."""
    for entry in _load().get("authorisations", []):
        if round_name in entry.get("rounds", []):
            return entry
    return None


def is_authorised(round_name: str) -> bool:
    return authorisation_for(round_name) is not None


def ceiling_gbp(round_name: str) -> float | None:
    entry = authorisation_for(round_name)
    return None if entry is None else entry.get("ceiling_gbp")


def main(argv: list | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)
    rounds = sorted(authorised_rounds())
    print(f"Authorised paid rounds: {len(rounds)}")
    for r in rounds:
        entry = authorisation_for(r)
        print(f"  {r}  (ceiling {entry.get('ceiling_gbp')} GBP, {entry.get('date')})")
    print()
    print(f"Paid seats: {', '.join(PAID_SEATS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
