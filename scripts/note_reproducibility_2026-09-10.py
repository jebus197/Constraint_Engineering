#!/usr/bin/env python3
"""Task 7.1: which notes would a technical reader find insufficient?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS RULING, verbatim: "Fix them all, or at least those that a technical reader
would be likely to find insufficient in the interests of reproducibility."

"ALL" IS 386 NOTES AND MOST OF THEM SHOULD NOT BE TOUCHED. A FULL_RECORD of a
panel session quoting a model's figures is a TRANSCRIPT -- a record of what was
said. Rewriting it would destroy the thing it exists to preserve. So the scope is
split at the start rather than at the debrief, which is this project's own rule.

THE BOUNDED SET, DERIVED NOT CHOSEN. A note is LIVE if a canonical document
points a reader at it: the master task list, the operational tracker,
`resources/RECOVERY.md`, `resources/ONBOARDING.md`, `.claude/CLAUDE.md`, or the
outcomes log. Those are the notes a technical reader actually reaches. Everything
else is archive, and is reported separately rather than silently dropped.

INSUFFICIENT MEANS ONE THING HERE, so the measurement is falsifiable: the note
states a PERCENTAGE or a P-VALUE and names no script that exists. A figure whose
producing code cannot be found is a claim about evidence rather than evidence,
which is the rule this project already carries.

WHAT THE FIRST MEASUREMENT GOT WRONG. A wider pattern -- counting "N of M" as a
figure -- returned 110 of 180 notes, 61.1111%. Most of those matches are ordinary
prose: "1 of 3 rounds", "2 of the 5 seats". A percentage or a p-value is a
claim about a measurement in a way that "one of three" is not, so the tighter
pattern is the honest one and the looser number is not quoted.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
NOTES = REPO / "experimental_notes"

#: Documents that point a reader at a note. Being IN this list does not make a
#: note live; being NAMED BY one does.
CANONICAL = (
    "experimental_notes/CDSFL_MASTER_TASK_LIST.md",
    "experimental_notes/CDSFL_Agent_Operational_Plan.md",
    "experimental_notes/CDSFL_OUTCOMES_LOG.md",
    "resources/RECOVERY.md",
    "resources/ONBOARDING.md",
    ".claude/CLAUDE.md",
)

#: A percentage or a p-value. NOT "N of M" -- see the docstring.
FIGURE = re.compile(r"\b\d{1,3}\.\d+\s*%|\bp\s*=\s*[\d.]+e?-?\d*")

#: A reference to code that could be run.
SCRIPT = re.compile(r"(scripts/[\w./-]+\.py|bench/tests/[\w./-]+\.py)")

#: A note may instead declare, in these words, where its figures came from.
PROVENANCE = "FIGURE PROVENANCE"


def canonical_text() -> str:
    out = []
    for rel in CANONICAL:
        p = REPO / rel
        if p.is_file():
            out.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(out)


def survey():
    canon = canonical_text()
    own = {pathlib.Path(c).name for c in CANONICAL}
    live, archive = [], []
    for n in sorted(NOTES.rglob("*.md")):
        if n.name in own:
            continue
        (live if n.name in canon else archive).append(n)
    return live, archive


def classify(note: pathlib.Path) -> dict:
    t = note.read_text(encoding="utf-8", errors="replace")
    figures = FIGURE.findall(t)
    scripts = [s for s in SCRIPT.findall(t) if (REPO / s).is_file()]
    return {"note": note, "figures": len(figures), "live_scripts": len(scripts),
            "declares_provenance": PROVENANCE in t,
            "sufficient": bool(scripts) or PROVENANCE in t or not figures}


def main() -> int:
    live, archive = survey()
    print(f"notes under experimental_notes : {len(live) + len(archive)}")
    print(f"  pointed at by a canonical doc: {len(live)}   (the bounded set)")
    print(f"  archive, reported not repaired: {len(archive)}\n")

    rows = [classify(n) for n in live]
    with_fig = [r for r in rows if r["figures"]]
    bad = [r for r in with_fig if not r["sufficient"]]
    print(f"live notes carrying a percentage or a p-value: {len(with_fig)}")
    print(f"  of those, naming no live script and declaring no provenance: {len(bad)}")

    if with_fig:
        from statsmodels.stats.proportion import proportion_confint
        k, n = len(bad), len(with_fig)
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        print(f"  {k}/{n} = {k / n:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, k, n - k + 1) if k else 0.0
        print(f"  Clopper-Pearson 95% : [{slo:.4%}, ...]  (scipy, cross-check; "
              f"agrees to {abs(slo - lo_c):.1e})")

    if bad:
        print("\n  insufficient, worst first:")
        for r in sorted(bad, key=lambda r: -r["figures"]):
            print(f"    {r['figures']:3d} figures  {r['note'].name}")
    else:
        print("\n  every live note carrying a figure either names a live script "
              "or declares its provenance.")
    return 0 if not bad else 1


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
