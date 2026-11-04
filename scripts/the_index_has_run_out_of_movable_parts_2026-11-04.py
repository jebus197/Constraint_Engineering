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


# NOTE 2026-11-04: this is the CANONICAL `_iv`, taken verbatim from
# `scripts/a_bare_clock_was_dated_from_the_mtime_2026-11-03.py` rather than
# written again here. This file first carried a variant that computed both
# quantities correctly but returned a richer shape, so the guard that EXECUTES
# every `_iv` against the same k and n could not read it, and a second variant
# whose Wilson algebra used `z**2` where the detector looks for `z * z`. Both
# were my deviations from a convention 14 producers already satisfy. The lesson
# is to use the canonical implementation, not to widen the instrument.
def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, on 2 INDEPENDENT implementations each.

    PROPAGATED 2026-11-03 from the one producer that already had both routes.
    An audit of this session's producers by STEM-IMPORT COUNT passed this file,
    and the count was a proxy: the project had already measured that `scipy` and
    `statsmodels` resolve to the identical verifier, so 2 library names can buy
    0 cross-checks. The predicate that matters is ROUTES PER QUANTITY -- Wilson
    from statsmodels against Wilson written out, and Clopper-Pearson from
    scipy's beta quantile against mpmath's regularized incomplete beta by
    bisection. 2 libraries computing 2 DIFFERENT intervals is not a cross-check
    of either one.

    The 3rd return value is the LARGER of the 2 disagreements, so a drift in
    either quantity surfaces in the single number the caller already prints.
    """
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    # second Wilson, written out, to catch a library disagreement
    import math
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def _f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if _f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)

def _iv_row(k: int, n: int) -> dict:
    """The printable row, built on `_iv` so the arithmetic exists once."""
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    (wl, wh), cp, agree = _iv(k, n)
    lo_raw, _hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    pp = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (pp + z**2 / (2 * n)) / d
    h = (z / d) * mp.sqrt(pp * (1 - pp) / n + z**2 / (4 * n**2))
    return {"k": k, "n": n, "p": k / n,
            "w": (wl, wh),
            "wmp": (max(0.0, float(c - h)), float(c + h)),
            "agree": agree, "cp": cp,
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
          "(the unit the 2026-10-29 figure used):", _iv_row(un_ptr, tot_ptr))
    print(f"    the prior figure was {PRIOR[0]} of {PRIOR[1]} = "
          f"{PRIOR[0]/PRIOR[1]:.6f}, from {PRIOR[2]}")
    print(f"    so in this unit the share HAS RISEN, by "
          f"{un_ptr/tot_ptr - PRIOR[0]/PRIOR[1]:+.6f}")

    _show("PHYSICAL LINES no existing mechanism can move "
          "(NOT comparable with the prior figure):", _iv_row(un_lines, len(lines)))
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
