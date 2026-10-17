#!/usr/bin/env python3
"""Does each harvested ticket title name the entry it belongs to?

WHY THIS IS A DEFECT AND NOT A COSMETIC COMPLAINT. The founder's ruling of
2026-10-17 is that every issue and every resolution carries a hashed
identifier in a searchable registry, and that the registry MUST be searched
before any new work is proposed or suggested. A title describing a
neighbouring entry defeats that search at the point of use: a lookup of B11
returns prose about B10, so the reader either re-proposes settled work or
passes over work still open.

THE CAUSE, measured rather than asserted. `from_task_list` takes the title as
the first 160 characters of the block lying between the previous marker and
this one. Several entries SHARE a block, so an addendum prepended to that
block precedes the heading of the entry that owns the marker. The title is
then whatever was most recently written above the entry, which on an actively
edited list is usually a different entry's addendum.

THE TEST CALLS THE HARVESTER, it does not re-implement it (`execute-do-not-grep`).
For each harvested record it asks which identifier the title names FIRST. Three
outcomes are distinguished, because they are not equally harmful:

  OWN        the title's leading identifier is the entry's own -- correct
  FOREIGN    it leads with a DIFFERENT entry's identifier -- actively
             misdirecting, and the case that breaks the pre-work search
  NEITHER    it leads with no identifier at all -- uninformative, not wrong

Only FOREIGN is counted as the defect rate, so the figure cannot be inflated
by entries whose prose simply opens without an identifier.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))


def _load(name: str, path: pathlib.Path):
    """Import a module whose filename is not a legal identifier."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


H = _load("harvest_tickets", REPO / "scripts" / "harvest_tickets_2026-10-17.py")

#: An identifier in HEADING position: optionally preceded by a star marker,
#: then the identifier, then a dot or a word boundary. Matched against the
#: title with asterisks already stripped, which is the form the harvester
#: stores.
#: CORRECTED 2026-10-17 AFTER THE INSTRUMENT UNDER-REPORTED. The first form
#: omitted the trailing-letter identifiers, so `R5a` and `3.1a` were scored
#: "names no identifier" when both titles in fact lead with their own. The
#: harvester was right and the measurer was wrong, which is the recorded
#: `my_instruments_are_the_weak_point` shape: check the predicate before
#: believing the rate it produces.
_LEAD = re.compile(
    r"^\s*(?:★\s*)?([A-Z]{1,2}\d{1,3}[a-z]?|\d{1,2}\.\d{1,2}[a-z]?)(?:\.|\b)")


def leading_ident(title: str) -> str:
    """The identifier a title names first, or '' if it names none."""
    m = _LEAD.match(title)
    return m.group(1) if m else ""


def main() -> int:
    # ARGUMENT PARSING EXISTS SO `--help` ANSWERS INSTEAD OF MEASURING. The
    # project's rule is that a help flag must never do the work, and the guard
    # that enforces it caught this script with the flag silently ignored.
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true",
                    help="print the rate only, omitting the per-entry listing")
    a = ap.parse_args()

    records = H.from_task_list()
    if not records:
        print("FATAL: the harvester returned 0 task-list records.")
        return 2

    own, foreign, neither = [], [], []
    for r in records:
        ident = r.get("task_ref") or ""
        lead = leading_ident(r.get("title") or "")
        if not lead:
            neither.append((ident, r.get("title", "")[:70]))
        elif lead == ident:
            own.append(ident)
        else:
            foreign.append((ident, lead, r.get("title", "")[:70]))

    n = len(records)
    print(f"harvested task-list records : {n}")
    print(f"  title names its OWN entry : {len(own)}")
    print(f"  title names ANOTHER entry : {len(foreign)}   <== the defect")
    print(f"  title names no identifier : {len(neither)}")

    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(len(foreign), n, method="wilson")
        ci = f", Wilson [{lo * 100:.4f}%, {hi * 100:.4f}%]"
    except Exception:
        ci = ""
    print(f"\nmisattribution rate: {len(foreign)} of {n} "
          f"= {len(foreign) / n * 100:.4f}%{ci}")

    if foreign and not a.quiet:
        print("\nevery misattributed title, so none is hidden behind the rate:")
        for ident, lead, title in sorted(foreign):
            print(f"  {ident:<6} title leads with {lead:<6} | {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
