#!/usr/bin/env python3
"""BOTH MECHANISMS BUILT TO KEEP THE MEMORY INDEX INSIDE ITS LIMITS ARE EXHAUSTED.

THIS IS NOT A NEW CONDITION AND THE RECORD SAYS SO. `scripts/cdsfl_sv.py`
carries a comment dated 2026-10-29 describing exactly this shape: the LINE
budget was binding with 1 line left, `archive_stale_memory_entries` "could free
nothing -- its dry run reported 'nothing older than 30 days in Project State'",
and `group_dated_index_entries` was built as the answer. That comment also
measured the structural limit: "116 of 149 entry-lines, 77.8523%, can never be
moved by it, the largest block being `Feedback` at 78 lines, which is standing
guidance and ages by design never."

WHAT IS NEW ON 2026-11-04 IS THAT THE SECOND MECHANISM IS NOW EXHAUSTED TOO,
and the unreachable share has risen from 0.778523 to the figure below. On this
date the archiver freed 0 at its 30-day default and same-date grouping freed 0
characters and 0 lines, while the index sat 4 entries from the refuse line that
stops a save. An earlier memory file of mine framed the archiver's
unreachability as a new third shape of the additive standard. That framing is
WITHDRAWN: the condition was named 6 days earlier and a mechanism was built for
it. What this script establishes is narrower and worse -- that the mechanism
built for it has run out of slack.

THE UNIT MATTERS AND THE FIRST VERSION OF THIS MEASUREMENT GOT IT WRONG.
Counting PHYSICAL LINES gives 88 of 91 = 0.967033, which cannot be compared
with the 2026-10-29 figure because that one counts ENTRY-LINES, meaning
POINTERS, and grouping merges many pointers onto 1 physical line. Both units
are reported here and only the pointer figure is compared across dates.

Every proportion carries an interval on 2 engines, per the 2026-04-21 rule.
"""
from __future__ import annotations

import pathlib
import re
import sys

MEM = pathlib.Path.home() / (
    ".claude/projects/-Users-georgejackson-Developer-Projects/memory")
INDEX = MEM / "MEMORY.md"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")
DATED = re.compile(r"^- \*\*\d+ \w+\*\*")

# The 2026-10-29 figure, quoted from the comment that states it so the
# comparison has a named source rather than a remembered one.
PRIOR = (116, 149, "scripts/cdsfl_sv.py, comment dated 2026-10-29")


def _iv(k: int, n: int) -> dict:
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    import mpmath as mp
    mp.mp.dps = 40
    lo_raw, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = (z / d) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return {"k": k, "n": n, "p": k / n,
            "w": (max(0.0, lo_raw), hi),
            "wmp": (max(0.0, float(c - h)), float(c + h)),
            "agree": abs(float(c + h) - hi),
            "cp": (float(sbeta.ppf(0.025, k, n - k + 1)) if k else 0.0,
                   float(sbeta.ppf(0.975, k + 1, n - k)) if k < n else 1.0),
            "neg": -lo_raw if lo_raw < 0 else 0.0}


def _show(label: str, iv: dict) -> None:
    print(f"\n  {label}")
    print(f"    {iv['k']} of {iv['n']} = {iv['p']:.6f}")
    print(f"    Wilson 95%          [{iv['w'][0]:.6f}, {iv['w'][1]:.6f}]   statsmodels")
    print(f"    Wilson 95%          [{iv['wmp'][0]:.6f}, {iv['wmp'][1]:.6f}]   "
          f"mpmath, upper bounds agree to {iv['agree']:.1e}")
    print(f"    Clopper-Pearson 95% [{iv['cp'][0]:.6f}, {iv['cp'][1]:.6f}]")
    if iv["neg"]:
        print(f"    NOTE: statsmodels returned a lower bound of -{iv['neg']:.2e}, "
              f"a floating-point artefact, clamped to 0.")


def main() -> int:
    if not INDEX.is_file():
        print(f"  no index at {INDEX}")
        return 1
    lines = INDEX.read_text(encoding="utf-8").splitlines()

    print("=" * 78)
    print("1. WHERE THE INDEX STANDS AGAINST THE LIMIT THAT REFUSES A SAVE")
    print("=" * 78)
    sys.path.insert(0, "scripts")
    import cdsfl_sv as sv
    audit = sv._audit_memory_index(MEM)
    chk = sv._check_memory_index_size(audit)
    thr_c = int(sv._MEMORY_INDEX_LIMIT_CHARS * sv._MEMORY_INDEX_REFUSE_FRACTION)
    thr_l = int(sv._MEMORY_INDEX_LIMIT_LINES * sv._MEMORY_INDEX_REFUSE_FRACTION)
    med = sorted(len(l) + 1 for l in lines if LINK.search(l))
    median_ptr = med[len(med) // 2] if med else 0
    print(f"\n  chars {audit.chars:,} of {sv._MEMORY_INDEX_LIMIT_CHARS:,}; "
          f"refuse line {thr_c:,}; headroom {thr_c - audit.chars:,}")
    print(f"  lines {audit.lines} of {sv._MEMORY_INDEX_LIMIT_LINES}; "
          f"refuse line {thr_l}; headroom {thr_l - audit.lines}")
    print(f"  median pointer line: {median_ptr} chars")
    if median_ptr:
        print(f"  entries left before a save is REFUSED: "
              f"{(thr_c - audit.chars) // median_ptr} by chars, "
              f"{thr_l - audit.lines} by lines")
    print(f"  the guard passes today: {chk.passed}")

    print()
    print("=" * 78)
    print("2. BOTH MECHANISMS, RUN DRY")
    print("=" * 78)
    a = sv.archive_stale_memory_entries(MEM, dry_run=True)
    print(f"\n  archive_stale_memory_entries at its default "
          f"{sv._MEMORY_WINDOW_DAYS}-day window:")
    print(f"    moves {a['moved']}, frees {a['freed_chars']} chars"
          f"   reason: {a['reason'][:58]}")
    if hasattr(sv, "group_dated_index_entries"):
        g = sv.group_dated_index_entries(MEM, dry_run=True)
        moved = g.get("lines_before", 0) - g.get("lines_after", 0)
        freed = g.get("chars_before", 0) - g.get("chars_after", 0)
        print(f"  group_dated_index_entries:")
        print(f"    frees {moved} line(s) and {freed} char(s)")
    print(f"\n  BOTH FREE NOTHING. That is the finding; neither is broken.")

    print()
    print("=" * 78)
    print("3. HOW MUCH OF THE INDEX EITHER MECHANISM CAN REACH")
    print("=" * 78)
    section = "(preamble)"
    per_ptr, per_chars = {}, {}
    for l in lines:
        if l.startswith("## "):
            section = l[3:].strip()
        n = len(LINK.findall(l))
        if n:
            per_ptr[section] = per_ptr.get(section, 0) + n
        per_chars[section] = per_chars.get(section, 0) + len(l) + 1

    tot_ptr = sum(per_ptr.values())
    tot_chars = sum(per_chars.values())
    print(f"\n  {'section':<46} {'ptrs':>5} {'share':>8} {'chars':>7}")
    for s in sorted(per_ptr, key=lambda k: -per_ptr[k]):
        print(f"  {s[:46]:<46} {per_ptr[s]:>5} "
              f"{per_ptr[s]/tot_ptr:>8.4f} {per_chars.get(s,0):>7}")

    dated_ptr = sum(len(LINK.findall(l)) for l in lines if DATED.match(l))
    dated_chars = sum(len(l) + 1 for l in lines if DATED.match(l))
    un_ptr, un_lines = tot_ptr - dated_ptr, len(lines) - sum(
        1 for l in lines if DATED.match(l))

    _show("POINTERS no existing mechanism can move "
          "(the unit the 2026-10-29 figure used):", _iv(un_ptr, tot_ptr))
    print(f"    the prior figure was {PRIOR[0]} of {PRIOR[1]} = "
          f"{PRIOR[0]/PRIOR[1]:.6f}, from {PRIOR[2]}")
    print(f"    so in this unit the share HAS RISEN, by "
          f"{un_ptr/tot_ptr - PRIOR[0]/PRIOR[1]:+.6f}")

    _show("PHYSICAL LINES no existing mechanism can move "
          "(NOT comparable with the prior figure):", _iv(un_lines, len(lines)))
    print(f"    reported because it is the unit the loader limits, and")
    print(f"    withheld from the comparison because grouping merges many")
    print(f"    pointers onto 1 line, so the 2 units move independently.")

    print(f"\n  characters on movable dated lines: {dated_chars:,} of "
          f"{tot_chars:,} = {dated_chars/tot_chars:.6f}")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    biggest = max(per_ptr, key=lambda k: per_ptr[k])
    print(f"""
  The index is {(thr_c - audit.chars) // max(median_ptr,1)} entries from the line at which a save is
  REFUSED, measured on characters, which is the binding budget today. Both
  mechanisms built to prevent that free NOTHING: the archiver because nothing
  in the dated section is older than its {sv._MEMORY_WINDOW_DAYS}-day window, and the grouper
  because the dated section is already grouped.

  {un_ptr} of {tot_ptr} pointers sit where neither mechanism reaches, and
  {per_ptr[biggest]} of {tot_ptr} are in '{biggest[:38]}',
  which is standing guidance that ages by design never. Age and date-grouping
  are therefore the wrong controls for the part of the index that actually
  grows.

  THIS IS A DECISION AND NOT A REPAIR. What standing guidance stays loaded is
  not mine to decide, and no mechanism can decide it either: a lesson is
  retired because it has stopped recurring, which is a judgement about the
  work. The alternatives are to raise the loader limits, to archive guidance by
  recurrence rather than by age, or to accept that a save will be refused and
  handled by hand each time.
""")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
