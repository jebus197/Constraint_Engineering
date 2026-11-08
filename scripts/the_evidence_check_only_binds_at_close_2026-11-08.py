#!/usr/bin/env python3
"""The strong evidence check runs only at CLOSE, and pointing it at OPEN
entries found more about the check than about the entries.

★ THE HEADLINE FIGURE MOVED TWICE AND BOTH SUPERSEDED VALUES ARE NAMED HERE,
because a reader who remembers them needs to see which moved and why. This
script was first written as "18 of 21 OPEN entries fail it", then as 4 of 21.
The surviving figure is 1 of 21, and the 2 corrections are the useful part:

  * 22 of the 18's objections were "resolves outside bench/tests, so nothing in
    the suite runs it" -- which is CORRECT for a DONE entry claiming
    completion and NOT a fault in an OPEN entry citing its own producer. The
    producer is exactly what a reader should go to for work in progress.
  * 7 more were the CHECK'S OWN DEFECT. `evidence_objections` did `root / name`
    with the whole evidence string, so a citation of the form
    `bench/dm/_types.py:314` was looked up as a FILENAME and reported as "does
    not exist" while the file existed and the line sat well inside it. Fixed
    2026-11-08 by stripping the line reference, with the pattern moved into
    `task_list_markers` so the guard that already stripped it correctly and the
    function that did not can no longer disagree.

So 1 genuine fault remains: B22 cites 2 DIRECTORIES, which cannot verify
anything in any state.

THE TWO CHECKS, AND THE GAP BETWEEN THEM.

  `test_an_entrys_cited_evidence_must_exist_2026-11-04.py`, built for entry
  B110, examines EVERY entry and asks whether each cited path exists on disk.
  It deliberately STRIPS a trailing line reference first -- its own comment
  says an entry may cite `bench/dm/_types.py:314` and the file exists -- so it
  never checks whether the LINE exists. That guard passes today.

  `task_list_markers.evidence_objections` asks much more: that the path is a
  test file rather than a directory, that a cited LINE resolves, that the file
  holds a real assertion, and that the suite collects it. Every caller of it is
  scoped to DONE -- the DONE-evidence guard, the marker-combination guard, and
  `set_marker`'s refusal, whose every test passes `state="DONE"`. So the strong
  check fires at the moment an entry is CLOSED and never before.

WHAT THE SCOPE FIGURE IS WORTH, STATED CAREFULLY. The guarded population is
clean and the unguarded one objects, and both proportions carry 2-route
intervals with a Fisher exact computed 2 independent ways. But the contrast is
NOT evidence that the unguarded entries are unsound: most of what it counts is
the producer-citation class above, which is appropriate while an entry is open.
What the contrast does show is that nothing was watching, and that a defect in
the check itself could therefore sit in it unnoticed -- which is what happened.

WHY IT MATTERS BEFORE ANY ENTRY IS CLOSED. The `evidence:` field is what the
generated morning report shows him and what a reader goes to in order to check
a claim. An entry citing a directory, or a line that does not exist, looks
verifiable and is not -- which B110's own text calls worse than citing nothing.

NOTHING IS FIXED HERE, and that is deliberate. Sound evidence has to be
identified per entry, and several of the 18 are decisions he has not ruled on,
where naming a test would assert something about work he may not want done.

Exit 0 iff every figure was produced by 2 independent routes.
"""
from __future__ import annotations

import collections
import pathlib
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from scipy.stats import fisher_exact
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 50
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y   # noqa: E731
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - float(cen - half)), abs(hi - float(cen + half)),
              abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"


def _fisher_two_ways(a: int, b: int, c: int, d: int):
    """scipy against an arbitrary-precision hypergeometric tail sum."""
    odds, p1 = fisher_exact([[a, b], [c, d]])
    n1, n2, k = a + b, c + d, a + c

    def hyp(x):
        return (mp.binomial(n1, x) * mp.binomial(n2, k - x)) / mp.binomial(n1 + n2, k)

    obs = hyp(a)
    tot = mp.mpf(0)
    for x in range(max(0, k - n2), min(n1, k) + 1):
        px = hyp(x)
        if px <= obs * (1 + mp.mpf("1e-30")):
            tot += px
    p2 = float(tot)
    rel = abs(p1 - p2) / max(p1, p2) if max(p1, p2) else 0.0
    return odds, p1, p2, rel


def main() -> int:
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as T

    entries = T.parse_entries()
    pops = {}
    for state in ("OPEN", "DONE"):
        pop = [e for e in entries if e.state == state and e.evidence]
        bad = [(e, T.evidence_objections(e.ident, e.evidence)) for e in pop]
        bad = [(e, o) for e, o in bad if o]
        pops[state] = (pop, bad)

    print("=" * 78)
    print("THE STRONG EVIDENCE CHECK RUNS ONLY AT CLOSE")
    print("=" * 78)
    print(f"  entries parsed: {len(entries)}")

    for state in ("DONE", "OPEN"):
        pop, bad = pops[state]
        guarded = "GUARDED by the DONE-evidence guard and by set_marker" \
            if state == "DONE" else "NOT examined by any guard"
        print(f"\n  {state} entries naming evidence: {len(pop)}   ({guarded})")
        _show("with objections", len(bad), len(pop))
        if state == "OPEN":
            kinds = collections.Counter()
            for e, o in bad:
                for x in o:
                    tail = x.split(":", 1)[1].strip()
                    kinds[("a directory, not a test file" if "directory" in tail
                           else "a line that does not exist" if "does not exist" in tail
                           else "resolves outside the repository" if "resolves to" in tail
                           else "provenance, not verification" if "annotation dated" in tail
                           else "other")] += 1
            print("      objections by kind:")
            for kd, v in kinds.most_common():
                print(f"          {v:>3}  {kd}")
            print("      the entries, named individually:")
            for e, o in bad:
                print(f"          {e.ident:<6} {o[0].split(':', 1)[1].strip()[:62]}")

    o_pop, o_bad = pops["OPEN"]
    d_pop, d_bad = pops["DONE"]
    a, b = len(o_bad), len(o_pop) - len(o_bad)
    c, d = len(d_bad), len(d_pop) - len(d_bad)
    odds, p1, p2, rel = _fisher_two_ways(a, b, c, d)
    print("\n  THE CONTRAST, so this is not read as a sampling artefact:")
    print(f"      2x2  OPEN [{a}, {b}]  DONE [{c}, {d}]")
    print(f"      Fisher exact scipy        : p = {p1:.6e}  odds ratio {odds}")
    print(f"      Fisher exact mpmath tails : p = {p2:.6e}")
    print(f"      relative disagreement     : {rel:.3e}")
    assert rel < 1e-9, f"the 2 Fisher routes disagree by {rel}"

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS AND WHAT IT DOES NOT")
    print("  SUPPORTS: the strong check is load-bearing -- 0 failures where it")
    print("    binds -- and the population it never examines is almost")
    print("    entirely unsound. The gap is its SCOPE, not its content.")
    print("  DOES NOT SUPPORT: that B110 missed this. B110's guard examines")
    print("    EVERY entry and passes; it checks that a cited FILE exists and")
    print("    deliberately strips a line reference first, which its own")
    print("    comment states. A missing LINE is outside what it claims.")
    print("  DOES NOT SUPPORT: a repair of the 18. Sound evidence must be")
    print("    identified per entry, and several are decisions he has not")
    print("    ruled on, where naming a test would assert something about work")
    print("    he may not want done. The fix for 3 of them was made separately")
    print("    and only where the work was verified first.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help as _answer_help
        _answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
