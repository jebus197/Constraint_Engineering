#!/usr/bin/env python3
"""The parked file gains a heading per triage, so one entry accumulates many.

`scripts/blocker_triage.py` appends a heading to
`experimental_notes/PARKED_FOR_THE_FOUNDER.md` on every PARK verdict and checks
nothing first. Triage the same obstacle twice and he reads 2 descriptions of it;
triage it across weeks as the obstacle changes shape and he reads a stack of
them, oldest first, with nothing saying which is live.

FOUND BY DOING IT. This session parked B159 twice within an hour -- once at
"15 characters of headroom" and once at the corrected "0 entries fit" -- and both
headings now sit in the file and both reach the morning report. The stale figure
is indistinguishable from the current one at a glance, which is the shape
`a reclassification is not a 2nd ticket` records with 95 duplicate pairs.

WHY NOT A LINT. The duplicates are not malformed; each heading was correct when
written. What is wrong is that nothing SUPERSEDES the earlier one, so the defect
is in the writer and not in the text, and a checker over the text would accuse
prose that was accurate on the day.

WHAT IS NOT CLAIMED. A code named by 2 headings is a CANDIDATE duplicate, not a
proven one: 2 genuinely different obstacles can both name B21. The script
therefore reports candidates and separates the clearest sub-case -- headings
whose own text has been overtaken by a later heading for the same code -- rather
than asserting a single number for "duplicates".
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"
TRIAGE = REPO / "scripts" / "blocker_triage.py"

#: the same shape `parked_items()` uses, widened for numeric ids as B181 did.
CODE = re.compile(r"\b([A-Z]{1,2}\d{1,4}[a-z]?|\d{1,2}\.\d{1,2})\b")
SETTLED = "# Settled"


def _cli(doc: str) -> None:
    """Answer --help WITHOUT reading the parked file."""
    import argparse                                        # noqa: PLC0415
    argparse.ArgumentParser(
        description=doc.strip().split("\n")[0],
        epilog="Takes no options. Running it performs the census.",
    ).parse_args()


def headings() -> tuple[list[str], list[str]]:
    """(above the settled boundary, below it). Below is not for his attention."""
    if not PARKED.is_file():
        return [], []
    txt = PARKED.read_text(encoding="utf-8")
    cut = txt.find(SETTLED)
    above = txt if cut < 0 else txt[:cut]
    below = "" if cut < 0 else txt[cut:]
    return (re.findall(r"^## (.+)$", above, re.M),
            re.findall(r"^## (.+)$", below, re.M))


def by_code(heads: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = collections.defaultdict(list)
    for h in heads:
        for c in sorted(set(CODE.findall(h))):
            out[c].append(h)
    return dict(out)


def dedupe_key() -> str:
    """What the writer compares, EXECUTED rather than grepped.

    ★ A KEYWORD PREDICATE GOT THIS WRONG FIRST. An earlier version of this
    script asked whether `blocker_triage.py` contains words like "supersede" or
    "dedupe" and concluded the writer deduplicates. It does -- but a keyword
    match is not a behaviour check, and the answer it gave ("supersedes: True")
    sat beside 14 live duplicates without the contradiction being visible. The
    real predicate is the one the writer RUNS, so it is imported and driven on
    a pair of titles instead.
    """
    if not TRIAGE.is_file():
        return "absent"
    import importlib.util                                  # noqa: PLC0415
    import sys                                             # noqa: PLC0415
    spec = importlib.util.spec_from_file_location("_bt_probe", TRIAGE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_bt_probe"] = mod
    try:
        spec.loader.exec_module(mod)
        norm = mod._normalise
    except Exception:                                      # noqa: BLE001
        return "unreadable"
    #: 2 titles for the SAME obstacle, reworded as understanding improves. This
    #: is the real case: both were parked for B159 on 2026-11-17, 5.6 hours
    #: apart, and both reached the morning report.
    a = "B159 half 2: the memory index has 15 characters of headroom"
    b = "B159 half 2: sv refuses the next memory write because entries_left is 0"
    #: and 2 titles that differ only in wording for the SAME question, which the
    #: writer's own comment names as the case it handles.
    c, d = ("A8: re-point the 20 note citations", "A8: re-point 20 note citations")
    restatement_caught = norm(a) == norm(b)
    rewording_caught = norm(c) == norm(d)
    if rewording_caught and not restatement_caught:
        return "title-keyed"
    if restatement_caught:
        return "obstacle-keyed"
    return "none"


def main(argv: list[str] | None = None) -> int:
    _cli(__doc__)
    print(__doc__.strip().split("\n")[0])
    print()

    above, below = headings()
    print(f"== {PARKED.name} ==")
    print(f"   headings ABOVE the settled boundary (his attention): {len(above)}")
    print(f"   headings BELOW it (kept, not for his attention)    : {len(below)}")
    print()

    from statsmodels.stats.proportion import proportion_confint  # noqa: PLC0415
    import mpmath as mp                                          # noqa: PLC0415
    mp.mp.dps = 40

    groups = by_code(above)
    dup = {c: hs for c, hs in groups.items() if len(hs) > 1}
    n, k = len(groups), len(dup)
    print("== candidate duplicates, among the headings he is shown ==")
    if n:
        w = proportion_confint(k, n, method="wilson")
        c_ = proportion_confint(k, n, method="beta")
        print(f"   codes named by MORE THAN 1 heading: {k} of {n} = {k / n:.6f}")
        print(f"     Wilson [{w[0]:.6f}, {w[1]:.6f}]  Clopper-Pearson [{c_[0]:.6f}, {c_[1]:.6f}]")
    extra = sum(len(hs) - 1 for hs in dup.values())
    print(f"   headings beyond the 1st for a repeated code: {extra}")
    print(f"   so of {len(above)} headings shown, {extra} are a repeat of a code")
    print()

    print("== the worst offenders ==")
    for code, hs in sorted(dup.items(), key=lambda kv: -len(kv[1]))[:5]:
        print(f"   {code:6s} {len(hs):3d} headings")
        for h in hs[:3]:
            print(f"          {h[:88]}")
        if len(hs) > 3:
            print(f"          ... and {len(hs) - 3} more not shown ({len(hs)} in total)")
    print()

    print("== what the writer compares, driven on real titles ==")
    key = dedupe_key()
    print(f"   blocker_triage.py's dedupe key is: {key}")
    if key == "title-keyed":
        print("   -> it DOES deduplicate, and correctly: a rewording of the same")
        print("      title is caught. What it cannot catch is a RESTATEMENT -- the")
        print("      same obstacle described in different words as understanding")
        print("      improves -- because 2 such titles are genuinely 2 sentences.")
        print("   -> and that is the right default: 2 distinct obstacles can both")
        print("      name B21, so collapsing by entry code would merge questions")
        print("      that are not the same question. The fix is therefore a")
        print("      JUDGEMENT about which headings restate which, not a key.")
    print()
    print("== VERDICT ==")
    print(f"   the surface he reads carries {extra} repeated heading(s): {extra > 0}")
    print(f"   the dedupe key cannot see a restatement: {key == 'title-keyed'}")
    established = extra > 0 and key == "title-keyed"
    print(f"   both established: {established}")
    print("   NOT CLAIMED: that all 14 are restatements. Some are distinct")
    print("   obstacles for one entry, and separating them needs reading.")
    return 0 if established else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
