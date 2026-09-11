#!/usr/bin/env python3
"""Task A12: every founder-ruled tracker item is either CARRIED or DECLARED EXCLUDED.

THE PROBLEM THE ENTRY NAMES. The master task list calls itself "the ordered
executable subset" of a 121-item inventory, so an item's absence is scoped rather
than silent -- but the list named none of the exclusions, and a reader cannot tell
a deliberate omission from a lost item.

WHAT THE TRACKER ACTUALLY HOLDS, read rather than restated. Fifteen numbered items
carry a founder ruling, in two kinds that have different correct treatments:

  STUDY PROGRAMME (4: items 14, 28, 29, 46) -- things to MEASURE DURING a
  simulated run. They are not executable task-list entries and never should be;
  the founder's words are "mark it in our simulated run programme of study".

  RUNWAY (11: items 17, 19, 20, 24, 31, 34, 36, 37, 38, 42, 43) -- work scheduled
  for a named point on the path to Bench Run 2, deliberately not on this list.

SO "ACCOUNTED FOR" MEANS ONE OF TWO THINGS, and conflating them is how the
original measurement read 11 as a defect rather than as a scope. An item is
accounted for when the list either CARRIES it as a worked entry or DECLARES it
excluded, with its kind named.

TWO REPRESENTATIONS WITH A COMPARATOR. The tracker says what is ruled; the list
says what it carries and what it excludes. This compares them. Nothing here
restates the tracker's contents, so an item added to the tracker cannot be
silently absent from the comparison.

AN INSTRUMENT DEFECT WORTH RECORDING, because it reported 0 of 15 and I nearly
believed it. The first version of this measurement used

    (in_a12 if pat.search(block) else []) and in_a12.append(n)

which short-circuits on an EMPTY list and never appends. It reported that A12
declared nothing at all, while the entry visibly names 11 items. A clever
one-liner that silently does nothing is the same failure as a guard that cannot
fire.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as tlm  # noqa: E402

TRACKER = REPO / "experimental_notes" / "CDSFL_Agent_Operational_Plan.md"
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: Tracker headings whose numbered rows carry a founder ruling, and the kind
#: each implies. Matched as a prefix so a reworded tail does not lose a section.
_RULED_SECTIONS = (
    ("Study programme for the SIMULATED RUN", "STUDY PROGRAMME"),
    ("Runway —", "RUNWAY"),
)


def ruled_items() -> dict[int, tuple[str, str]]:
    """{number: (kind, title)} read from the tracker's own tables."""
    out: dict[int, tuple[str, str]] = {}
    kind = None
    for line in TRACKER.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            head = line.strip("# ").strip()
            kind = next((k for prefix, k in _RULED_SECTIONS
                         if head.startswith(prefix)), None)
            continue
        if kind is None:
            continue
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|", line)
        if m:
            out.setdefault(int(m.group(1)), (kind, m.group(2).strip()))
    return out


def _a12_block() -> tuple[str, str]:
    """A12's own text, and everything else on the list."""
    lines = LIST.read_text(encoding="utf-8").splitlines()
    es = sorted(tlm.parse_entries(LIST), key=lambda e: e.line_no)
    for k, e in enumerate(es):
        if e.ident == "A12":
            end = es[k + 1].line_no - 1 if k + 1 < len(es) else len(lines)
            return ("\n".join(lines[e.line_no - 1:end]),
                    "\n".join(lines[:e.line_no - 1] + lines[end:]))
    raise SystemExit("entry A12 is gone from the task list")


def account(num: int, block: str, rest: str) -> str:
    # MARKDOWN EMPHASIS SITS BETWEEN THE WORD AND THE NUMBER. Writing the
    # declaration as `item **14 critical-severity ceiling**` -- which is how a
    # reader wants to see it -- put `**` between "item" and "14", and a pattern
    # requiring them adjacent reported the declaration absent. The text was
    # there; the pattern was not looking at the text a human sees. Same class as
    # every other formatting-versus-token miss in this project, in a new place.
    emph = r"[*_`\s]*"
    pat = re.compile(rf"\({num}\)|\bitem{emph}{num}\b|\bruling{emph}{num}\b")
    if pat.search(rest):
        return "CARRIED"
    if pat.search(block):
        return "DECLARED EXCLUDED"
    return "UNACCOUNTED"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quiet", action="store_true")
    ap.parse_args()

    items = ruled_items()
    block, rest = _a12_block()
    rows = [(n, k, t, account(n, block, rest)) for n, (k, t) in sorted(items.items())]

    print(f"founder-ruled numbered items in the tracker: {len(rows)}")
    for n, kind, title, state in rows:
        print(f"  {n:3d}  {kind:16s} {state:18s} {title[:52]}")

    unaccounted = [r for r in rows if r[3] == "UNACCOUNTED"]
    print(f"\nUNACCOUNTED -- neither carried nor declared: {len(unaccounted)}")
    for n, kind, title, _s in unaccounted:
        print(f"    {n}  ({kind})  {title[:60]}")
    if not unaccounted:
        print("    none. A reader can tell a deliberate omission from a lost item.")

    n_total, k = len(rows), len(unaccounted)
    if n_total:
        from statsmodels.stats.proportion import proportion_confint
        from scipy.stats import beta as sbeta
        lo, hi = proportion_confint(k, n_total, method="wilson")
        lo_c, hi_c = proportion_confint(k, n_total, method="beta")
        hi_s = 1.0 if k == n_total else sbeta.ppf(0.975, k + 1, n_total - k)
        print(f"\nunaccounted rate: {k}/{n_total} = {k / n_total:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy, agrees "
              f"to {abs(hi_s - hi_c):.1e})")

    print("\nTHE TRACKER IS READ, NOT RESTATED, so an item added there cannot be "
          "silently\nabsent from this comparison.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
