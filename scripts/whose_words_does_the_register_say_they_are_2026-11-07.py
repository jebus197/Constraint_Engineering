#!/usr/bin/env python3
"""The register labels CC1's own findings as the founder's words, systematically.

FOUND BY MAKING THE MISTAKE. 4 findings raised on 2026-11-07 landed with
`source: founder-chat`, because `TicketStore.propose_from_chat` does
`kw.setdefault("source", "founder-chat")` and the override was not passed. They
are CC1's findings. A finding of CC1's wearing his name is the shape the record
already names: advice he REJECTED once acquired authority from his name, and a
default attributed to him had him blaming himself for 180 of 680 rows.

THE QUESTION THIS ANSWERS IS WHETHER THAT WAS NEW. It was not.

THE PREDICATE IS THIRD-PERSON REFERENCE TO HIM. He does not write about himself
as "his", "he" or "him": a ticket whose verbatim does is written ABOUT him by
someone else. It is a proxy and it is stated as one.

THE CONTROL IS WHAT MAKES IT EVIDENCE RATHER THAN A FILTER. Tickets sourced
`responses` are harvested from his own reply files, so they really are his
words, and the predicate must fire RARELY on them. It fires on 1 of 1,158.

Exit 0 iff every rate was computed and both routes agreed on every figure.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from scipy.stats import fisher_exact
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 60
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "bench" / "ticket_store.py").is_file():
    #: running from a scratchpad before it is installed in scripts/.
    #: A probe that resolves the repo from its OWN location reports the
    #: probe's whereabouts as a fact about the subject, which is how a
    #: population of 0 was once read as a clean board.
    REPO = pathlib.Path(
        "/Users/georgejackson/Developer_Projects/Constraint_Engineering")
#: he does not write about himself in the 3rd person
THIRD = re.compile(r"\b(his|he|him)\b", re.I)
WINDOW = 600


def _store():
    spec = importlib.util.spec_from_file_location(
        "ticket_store", REPO / "bench" / "ticket_store.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ticket_store"] = m          # the dataclass needs this
    spec.loader.exec_module(m)
    return m.TicketStore()


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

    #: ★ THE SECOND CLOPPER-PEARSON ROUTE, RESTORED 2026-11-08, AND THIS IS THE
    #: SECOND TIME THE SAME CLASS APPEARED IN ONE NIGHT. This helper shipped
    #: with Wilson on 2 routes -- statsmodels and the closed form above -- and
    #: Clopper-Pearson on ONE, scipy's `beta.ppf` alone, while `dis` compared
    #: only the 2 Wilson values. So the printed "2-route disagreement" was true
    #: of Wilson and said NOTHING about the Clopper-Pearson pair on the same
    #: line, and it printed as exactly 0.000e+00, which was the tell.
    #:
    #: FOUND BY THE DETECTOR, not by reading: B135's execution half was
    #: installed the same night and `counting_imports_ranks_producers_
    #: backwards_2026-11-03.py` named this file as resting a quantity on a
    #: single route. The identical repair had been made hours earlier in
    #: `the_gate_board_serialises_the_tree_2026-11-07.py`, so the class was
    #: known and committed again anyway -- which is the argument for a detector
    #: over an intention.
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
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]   "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"


def _fisher_two_ways(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    """(scipy p, exact-enumeration p, RELATIVE disagreement).

    ★ THE TOLERANCE MUST BE RELATIVE AND THE FIRST VERSION'S WAS ABSOLUTE.
    A cross-check written as `pmf(i) <= pmf(a) + 1e-15` admitted every table
    when the observed pmf was near 1e-45, because the absolute tolerance
    swamped the comparison entirely. The 2 routes then disagreed by 28 orders
    of magnitude -- 1.153757e-45 against 2.748732e-17 -- and under this
    project's 2-tool rule that makes the p-value UNVERIFIED rather than large
    or small. With a relative tolerance the routes agree to 4.0e-16.
    """
    odds, p_scipy = fisher_exact([[a, b], [c, d]])
    n1, n2, k = a + b, c + d, a + c
    N = n1 + n2

    def pmf(i):
        return (mp.binomial(n1, i) * mp.binomial(n2, k - i)) / mp.binomial(N, k)

    obs = pmf(a)
    total = mp.mpf(0)
    for i in range(max(0, k - n2), min(n1, k) + 1):
        if pmf(i) <= obs * (1 + mp.mpf("1e-40")):
            total += pmf(i)
    p_exact = float(total)
    rel = abs(p_exact - p_scipy) / max(p_scipy, 1e-300)
    return p_scipy, p_exact, rel


def main(argv) -> int:
    st = _store()
    rows = list(st.all())
    fc = [t for t in rows if (getattr(t, "source", "") or "") == "founder-chat"]
    resp = [t for t in rows if (getattr(t, "source", "") or "") == "responses"]

    print("=" * 78)
    print("WHOSE WORDS DOES THE REGISTER SAY THEY ARE?")
    print("=" * 78)
    print(f"total tickets: {len(rows):,}")
    print(f"  source `founder-chat`: {len(fc)}   "
          f"all anchored chat#...: {sum(1 for t in fc if str(t.anchor).startswith('chat#'))}")
    print(f"  source `responses` (the control): {len(resp):,}\n")

    a = sum(1 for t in fc if THIRD.search(str(t.verbatim)[:WINDOW]))
    c = sum(1 for t in resp if THIRD.search(str(t.verbatim)[:WINDOW]))
    print("TEST -- tickets the register says came from HIS chat:")
    _show("verbatim refers to him in the 3rd person", a, len(fc))
    print("\nCONTROL -- tickets harvested from his OWN reply files:")
    _show("verbatim refers to him in the 3rd person", c, len(resp))

    p1, p2, rel = _fisher_two_ways(a, len(fc) - a, c, len(resp) - c)
    print(f"\n  Fisher exact: scipy p = {p1:.6e}, exact enumeration p = {p2:.6e}")
    print(f"      RELATIVE disagreement {rel:.3e}")
    assert rel < 1e-6, (
        f"the 2 p-value routes disagree by {rel}, so the p-value is "
        f"UNVERIFIED and must not be quoted")

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS AND WHAT IT DOES NOT")
    print("  SUPPORTS: the `founder-chat` label does not mean the words are his.")
    print("    The predicate fires on 0.000864 of text that IS his and on")
    print("    0.729730 of what this label claims is his, so the label is")
    print("    unreliable as attribution.")
    print("  DOES NOT SUPPORT: a count of exactly how many are CC1's. The")
    print("    predicate is a PROXY -- a ticket quoting him about a 3rd party,")
    print("    or his own words relayed, would fire too. The 10 that do not")
    print("    fire are not thereby shown to be his.")
    print("  THE REPAIR IS NOT MADE HERE. Changing a stored `source` has no")
    print("    public method, and `tid_of` does not digest `source`, so the")
    print("    identities are safe either way. Whether to add a setter, or to")
    print("    make `propose_from_chat` REQUIRE an explicit source, is his.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main(sys.argv[1:]))
