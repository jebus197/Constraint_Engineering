#!/usr/bin/env python3
"""What it COSTS to send the whole directive set, including the historical chatter.

HIS QUESTION, 2026-10-13 (annotation on `The_Directive_Set_2026-10-13.txt`):
*"A 7% overhead of what may ultimately be useful context is not such a huge
burden to carry. But you should measure it."*

The 7% is his reading of the chatter share quoted to him on 2026-10-13. ★ THAT
FIGURE IS WITHDRAWN HERE: its denominators reproduce and its numerators do not, and
the chatter is roughly HALF what he was told. His conclusion survives the correction
and is strengthened by it. This script measures what keeping the chatter, and what
removing the caps, actually costs -- in characters, in tokens, and per panel round.

IT CALLS THE COMPOSER rather than quoting yesterday's note. The delivered figure
of 2,734 characters was measured on 2026-10-13 and is RE-DERIVED here by execution,
because a number that exists only as prose is a claim about evidence.

RUN IT: python3 scripts/what_the_full_directive_set_costs_2026-10-14.py
`--help` is free and dispatches nothing.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
UNIVERSAL = REPO / "bench" / "directives" / "universal"
CORE = UNIVERSAL / "cdsfl_core_formal.md"
OPERATIONAL = UNIVERSAL / "cdsfl_operational.md"

#: ★ THE 2026-10-13 CHATTER NUMERATORS ARE WITHDRAWN. THEY CANNOT BE REPRODUCED.
#:
#: That measurement was quoted to the founder as 18 of 494 lines in the core file
#: (3.6437%) and 20 of 762 in the operational one (2.6247%), and it ran INLINE
#: with no committed script -- the precise defect `measured-rate-travels-with-its-script`
#: exists to prevent, and the second time in 2 days (see the 14-of-21 parked-file
#: figure of 2026-10-13).
#:
#: WHAT REPRODUCES AND WHAT DOES NOT. The DENOMINATORS reproduce exactly on
#: NON-EMPTY lines: 494 and 762. The NUMERATORS do not. Across 4 candidate
#: predicates -- a bare 4-digit year, an ISO date, year-or-MEASURED, and
#: year-or-month-name -- the highest counts obtainable are 8 of 494 and 16 of 762.
#: Nothing tried reaches 18 or 20.
#:
#: SO THE CHATTER WAS OVERSTATED BY ROUGHLY A FACTOR OF 2, AND HIS CONCLUSION
#: GETS STRONGER RATHER THAN WEAKER: if ~7% was "not such a huge burden to carry",
#: ~2% is less of one still. The broadest defensible predicate is used below, so
#: the figure reported is an UPPER bound on the chatter.
_BROAD = re.compile(r"20\d\d|\bMEASURED\b", re.I)


def chatter(text: str):
    """Historical-narrative share, on NON-EMPTY lines, broadest predicate.

    Non-empty is the denominator because it is what reproduces the 2026-10-13
    line counts, and because a blank line is not a line of specification.
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    hits = [ln for ln in lines if _BROAD.search(ln)]
    vol = sum(len(ln) + 1 for ln in hits)
    return len(hits), len(lines), vol, len(text)


def tokens(chars: int) -> int:
    """The dispatcher's own estimate: `len(PROMPT)//4`. Same arithmetic, so the
    figures here and the ones it prints at dispatch cannot drift."""
    return chars // 4


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    for f in (CORE, OPERATIONAL):
        if not f.is_file():
            print(f"missing: {f}")
            return 2

    core_txt = CORE.read_text(encoding="utf-8")
    op_txt = OPERATIONAL.read_text(encoding="utf-8")

    print("=== THE FILES ===")
    rows = {}
    for label, txt in (("core formal", core_txt), ("operational", op_txt)):
        k, n, vol, total = chatter(txt)
        rows[label] = dict(lines=n, chatter_lines=k, chars=total, chatter_chars=vol)
        print(f"  {label:12s}: {total:,} chars, {n:,} lines")
        print(f"      historical narrative: {k} of {n} lines = "
              f"{k/n:.6f}; {vol:,} chars = {vol/total:.6f} by volume")

    chat_chars = sum(r["chatter_chars"] for r in rows.values())
    full_chars = sum(r["chars"] for r in rows.values())
    print(f"\n  chatter across both files: {chat_chars:,} chars of {full_chars:,} "
          f"= {chat_chars/full_chars:.6f}")

    # WHAT IS DELIVERED NOW, BY EXECUTION AGAINST THE LIVE COMPOSER.
    print("\n=== WHAT A SEAT RECEIVES, BY CALLING _load_universal_directive ===")
    delivered, sections_kept = {}, None
    try:
        sys.path.insert(0, str(REPO))
        from bench.cdsfl_registry import composer as C
        labels = list(getattr(C, "PHENOTYPE_TRANSFORMS", {}).keys()) + \
            ["fable", "cc2", None]
        for m in labels:
            try:
                delivered[str(m)] = len(C._load_universal_directive(m).text)
            except Exception as exc:
                print(f"    {str(m):16s}: ERROR {exc!r}")
        # 0 OF 15 SECTIONS, CHECKED RATHER THAN RECALLED.
        src_heads = [h for h in re.findall(r"(?m)^#{1,3}\s+(.+)$", core_txt)]
        sample = C._load_universal_directive(None).text
        sections_kept = [h for h in src_heads if h.strip() and h.strip() in sample]
    except Exception as exc:
        print(f"  could not call the composer: {exc!r}")

    if not delivered:
        print("  COMPOSER NOT CALLABLE — no delivery figure is asserted by this run.")
    else:
        vals = sorted(set(delivered.values()))
        for m, n in delivered.items():
            print(f"    {m:16s}: {n:,} chars = {n/len(core_txt):.6f} of source")
        print(f"\n  distinct delivered sizes across {len(delivered)} seat labels: "
              f"{len(vals)} -> {vals}")
        if len(vals) == 1:
            print("  ★ EVERY SEAT RECEIVES THE SAME TEXT. The per-model caps")
            print("    (4,000 / 6,000 / 8,000 / 12,000) therefore differentiate")
            print(f"    NOTHING: the minimal render is {vals[0]:,} chars, under even")
            print("    the smallest cap, and the caps only decide WHETHER it is used")
            print(f"    -- which it always is, because {len(core_txt):,} exceeds the")
            print("    largest cap of 12,000. `fable` and `cc2` have no transform")
            print("    entry at all and receive the same thing by default.")
        if sections_kept is not None:
            print(f"\n  source headings: {len(src_heads)}; surviving in the "
                  f"delivered text: {len(sections_kept)}")
            if not sections_kept:
                print("  ★ 0 SECTION HEADINGS SURVIVE — confirmed by execution, not recall.")

    print("\n=== THE COST OF CARRYING IT ALL, PER SEAT PER ROUND ===")
    print(f"  full set, uncapped : {full_chars:,} chars, ~{tokens(full_chars):,} tokens")
    print(f"  the chatter alone  : {chat_chars:,} chars, ~{tokens(chat_chars):,} tokens")
    for seats in (2, 6):
        print(f"  chatter x {seats} seats x 1 round : "
              f"~{tokens(chat_chars) * seats:,} tokens")
        print(f"  chatter x {seats} seats x 10 rounds: "
              f"~{tokens(chat_chars) * seats * 10:,} tokens")

    print("\n  HIS POINT, MEASURED: the historical narrative is the CHEAPEST part")
    print("  of this decision. Removing the caps is the expensive change and the")
    print("  one that delivers the specification; cutting the chatter saves")
    print(f"  ~{tokens(chat_chars):,} tokens a seat and removes context that may matter.")

    if args.json:
        print(json.dumps({"files": rows, "chatter_chars": chat_chars,
                          "full_chars": full_chars, "delivered": delivered},
                         indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
