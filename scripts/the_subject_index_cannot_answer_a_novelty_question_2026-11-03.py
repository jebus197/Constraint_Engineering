#!/usr/bin/env python3
"""A 0 from the subject index is not evidence that a finding is new.

HIS QUESTION, 2026-11-03: whether this session revisited fixes he had already
ruled on, or that were already marked complete in the project's own issue
register. The answer is YES, twice, and this measures the half of the cause that
is mechanical rather than a lapse of discipline.

WHAT HAPPENED. Tonight the mechanism "blocker_triage.py returns PARK with no
permission flag for items that ARE his decision, and work_not_narrate.py reads
PARK as carry on" was presented to him as a discovery. It is ticket
148ebf10bbaa, status CLOSED, verified by commit 529dada432099793f815f42d87c534a4eacbfc37,
and its text states that mechanism in those terms. Separately, ticket
c15b3dbe595a is OPEN on the Stop gate asserting "nothing is blocking" from a
fact about the turn.

THE SEARCH THAT WAS RUN, AND WHY ITS 0 MEANT NOTHING. `register.py --subject
blocker_triage` returned 0 matches, and that was read as "nothing is
registered". But the subject index is almost empty: most tickets carry no
subject at all, so a 0 from it is UNINFORMATIVE rather than negative. The
closed ticket carries `subjects=[]` while its own text names the module, so no
subject query could ever have reached it.

THE SEARCH THAT WOULD HAVE WORKED, which is why the discipline half is the
larger half. `register.py --word "blocker_triage.py"` returns a handful of
matches and the ticket is among them. Searching the FILENAME as a word works;
searching it as a subject does not. The queries a reader would reach for
instead -- "triage gate", "permission flag", "needs his ruling" -- return
hundreds of word-overlap matches and are useless for deciding novelty.

SO THE RULE THIS PRODUCES, and it is checkable rather than a resolution: before
treating anything as a new finding, search the register with `--word` on the
exact FILENAME of each module involved, and never read a `--subject` 0 as
absence. The screen for whether a query is usable is its RESULT COUNT: a query
returning hundreds has not answered a novelty question.

WHAT THIS DOES NOT CLAIM. It does not claim the subject index is wrong to be
sparse, nor propose populating it -- that would change how every ticket is
indexed and is his decision. It measures the size of the blind spot so that a 0
from that route is read correctly.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve()
while REPO.name != "Constraint_Engineering" and REPO.parent != REPO:
    REPO = REPO.parent
if REPO.name != "Constraint_Engineering":
    REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
assert (REPO / "bench" / "ticket_store.py").is_file(), f"no repo at {REPO}"
sys.path.insert(0, str(REPO))

#: A module named in a ticket's own text. 4+ characters so `re.py` and the like
#: do not dominate, and a word boundary so `my_mod.pyc` cannot match.
MODULE = re.compile(r"\b([a-z_][a-z0-9_]{3,})\.py\b")

#: The 2 tickets this session re-derived, pinned so the claim cannot go stale.
RE_DERIVED = {
    "148ebf10bbaa": "CLOSED -- blocker_triage returns PARK with no permission "
                    "flag; work_not_narrate reads PARK as carry on",
    "c15b3dbe595a": "OPEN -- the Stop gate reads 'nothing is blocking' from a "
                    "fact about the turn",
}


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
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
        def _f(x):
            return mpmath.betainc(a, b, 0, x, regularized=True) - y
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(240):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if _f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def main() -> int:
    argparse.ArgumentParser(
        description=("Measure why a subject-index 0 cannot answer whether a "
                     "finding is already registered.")).parse_args()

    from bench.ticket_store import TicketStore
    st = TicketStore()
    st.load()
    rows = st.all()
    n = len(rows)

    no_subject = [t for t in rows if not t.subjects]
    names_code = [t for t in no_subject
                  if MODULE.search((t.verbatim or "") + " " + (t.title or ""))]

    print("=" * 78)
    print("WHY A SUBJECT-INDEX 0 IS NOT EVIDENCE THAT A FINDING IS NEW")
    print("=" * 78)
    print(f"\n  tickets in the register : {n}")
    for label, k in (("carry NO subject at all", len(no_subject)),
                     ("name a module in their text yet carry NO subject",
                      len(names_code))):
        (wl, wh), (cl, ch), d = _iv(k, n)
        print(f"\n  {label}: {k} of {n}, {k / n:.6f}")
        print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
        print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  "
              f"(2-route |diff| {d:.1e})")

    print("\n  THE 2 TICKETS THIS SESSION RE-DERIVED, each checked to still "
          "exist:")
    missing = []
    for tid, what in RE_DERIVED.items():
        t = st.get(tid)
        if t is None:
            missing.append(tid)
            print(f"    {tid}  NOT FOUND -- this claim has gone stale")
            continue
        subj = t.subjects or []
        print(f"    {tid}  status={t.status:10s} subjects={subj if subj else '[]'}")
        print(f"        {what}")
    if missing:
        print(f"\n  REFUSED: {len(missing)} pinned ticket(s) no longer exist, so "
              f"the central claim cannot be checked.")
        return 1

    print("\n  WHICH ROUTE FINDS THE CLOSED ONE. A query is usable for a novelty")
    print("  question only if its result set is small enough to read.")
    for q in ("blocker_triage.py", "triage gate", "permission flag",
              "needs his ruling"):
        hits = st.similar_by_words(q, threshold=0.5)
        found = any(getattr(h, "tid", "") == "148ebf10bbaa" for h in hits)
        verdict = ("USABLE" if found and len(hits) <= 20 else
                   "FOUND BUT UNREADABLE" if found else "MISSES IT")
        print(f"    --word {q!r:24s} {len(hits):4d} match(es)  "
              f"finds it={found}  -> {verdict}")

    print("\n  SO: the filename searched as a WORD is the route that answers the")
    print("  question. The subject route cannot, and its 0 must never be read as")
    print("  absence. The discipline half is the larger half, because a usable")
    print("  query existed and was not run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
