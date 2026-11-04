#!/usr/bin/env python3
"""How many ticket previews truncate his words without saying so?

THE DEFECT, OBSERVED 2026-11-03. `scripts/register.py:261` prints a ticket's
title as `r['title'][:96]` with NO truncation marker. The line BELOW it, at :263,
marks its own truncation as "... N more", so the inconsistency is inside 1
function: the row count says when it is hiding rows and the text does not say
when it is hiding words.

THE CONFIRMED HARM, 1 INSTANCE, and it is his ruling. Ticket 06f04be9b412 holds
his annotation of 2026-10-30. The preview shows:

    No. a free panel, or simulated experiment has never previously needed any
    additional permissions

which reads as a finished ruling: free panels need no permission. His full words,
read through `scripts/read_founder_responses_2026-10-11.py` from
`All_Verdicts_Consolidated_2026-10-30.txt` line 27, continue:

    ..., beyond that that I issue when I  tell you to run them.

That clause INVERTS the operative content. The rule is not that no permission is
needed; it is that the permission IS his instruction to run it. Acting on the
preview would have treated an unasked run as pre-authorised.

WHAT IS MEASURED HERE, AND WHAT IS NOT. The RATE of silent truncation is
mechanically decidable and is measured. Whether a given truncation changes
MEANING is not, so it is not claimed as a rate: the meaning-changing case above
is reported as 1 OBSERVED instance. What IS decidable is a necessary condition
for that harm, and it is reported separately:

  1. the title exceeds 96 characters, so the preview drops text at all
  2. the cut falls at a WORD BOUNDARY, so no half-word betrays it -- a cut
     mid-word is visibly broken and warns the reader by itself
  3. the dropped remainder opens with, or contains, a qualifier able to
     restrict or reverse what survives: beyond, unless, except, but, however,
     only, provided, rather, instead, although, apart from, other than

Condition 3 is a SCREEN, not a verdict. It over-counts, because a qualifier may
qualify something harmless. It is reported as an upper bound and labelled so.

NOTHING PINS THE WIDTH, CHECKED BEFORE MEASURING. No test asserts on the 96, so
a marker can be added without breaking a guard: the tests that invoke this CLI
assert on its `usage:` text and its exit codes.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

#: Resolved by walking up from this file WHEN it lives in the repo, with an
#: explicit fallback for running it from the scratchpad before it is committed.
REPO = pathlib.Path(__file__).resolve()
while REPO.name != "Constraint_Engineering" and REPO.parent != REPO:
    REPO = REPO.parent
if REPO.name != "Constraint_Engineering":
    REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
assert (REPO / "bench" / "ticket_store.py").is_file(), f"no repo at {REPO}"
sys.path.insert(0, str(REPO))

WIDTH = 96
QUALIFIER = re.compile(
    r"\b(beyond|unless|except|but|however|only|provided|rather|instead|"
    r"although|though|besides|apart\s+from|other\s+than|save\s+for|not)\b",
    re.IGNORECASE)


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    import math

    import mpmath
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
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


def main() -> int:
    #: ★ ARGUMENTS ARE PARSED BEFORE ANY WORK, AND THAT ORDER IS THE POINT.
    #: `--help` must never cost money or time. The first version of this file
    #: had no parser at all, so `--help` was consumed as an unknown argument and
    #: the script loaded all 3,383 tickets to answer it -- caught by
    #: `test_help_is_answered_2026-09-11.py::TestTheWiringIsReal`, which runs any
    #: script whose source it cannot vouch for and requires a usage line. The
    #: project already measured this class once: 15 of 17 runners billed to
    #: answer `--help`. The import below sits INSIDE main, after the parse, so
    #: the parser answers and exits before the store is touched.
    argparse.ArgumentParser(
        description=("Measure how many ticket previews truncate his words "
                     "without marking the truncation.")).parse_args()

    from bench.ticket_store import TicketStore
    st = TicketStore()
    st.load()
    tickets = st.all()

    total = len(tickets)
    truncated, at_boundary, screened = [], [], []
    for t in tickets:
        title = str(getattr(t, "title", "") or "")
        if len(title) <= WIDTH:
            continue
        truncated.append(t)
        shown, dropped = title[:WIDTH], title[WIDTH:]
        # A cut at a word boundary leaves no half-word to warn the reader.
        boundary = (shown[-1:].strip() != "" and
                    (dropped[:1] in (" ", ",", ";", ":", ".") or
                     shown[-1:] in (" ", ",")))
        if boundary:
            at_boundary.append(t)
            if QUALIFIER.search(dropped):
                screened.append((t, shown, dropped))

    print("=" * 78)
    print("HOW MANY TICKET PREVIEWS TRUNCATE HIS WORDS WITHOUT SAYING SO?")
    print("=" * 78)
    print(f"\n  tickets in the store                      : {total}")
    print(f"  titles longer than {WIDTH} chars (truncated) : {len(truncated)}")
    print(f"  cut at a WORD BOUNDARY (reads as complete): {len(at_boundary)}")
    print(f"  ... and the dropped text carries a qualifier: {len(screened)}")

    for label, k in (("truncated at all", len(truncated)),
                     ("cut at a word boundary", len(at_boundary)),
                     ("qualifier in dropped text (UPPER BOUND)",
                      len(screened))):
        (wl, wh), (cl, ch), d = _iv(k, total)
        print(f"\n  {label}: {k} of {total}, {k / total if total else 0:.6f}")
        print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
        print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  "
              f"(2-route |diff| {d:.1e})")

    print("\n  THE SCREENED SET IS AN UPPER BOUND, NOT A COUNT OF HARMS. A")
    print("  qualifier in dropped text MAY restrict what survives; it need not.")
    print("  Sample, so the screen can be judged rather than trusted:")
    for t, shown, dropped in screened[:6]:
        print(f"\n    {getattr(t, 'tid', '?')}  {getattr(t, 'kind', '?')}")
        print(f"      SHOWN   : ...{shown[-62:]}")
        print(f"      DROPPED : {dropped[:72]}")

    print("\n  THE CONFIRMED MEANING-CHANGING CASE IS 1, HIS RULING 06f04be9b412,")
    print("  and it is reported as an instance rather than folded into a rate,")
    print("  because whether a truncation changes meaning is not mechanically")
    print("  decidable and a rate would imply it is.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
