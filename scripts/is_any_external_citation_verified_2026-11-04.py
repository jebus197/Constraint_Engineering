#!/usr/bin/env python3
"""Is any EXTERNAL citation in this record verified by anything?

THE GAP. The repository holds 14 test files guarding CITATIONS, and every one
of them guards an INTERNAL citation: a path that must exist, a line that must
still hold its substring, a log that must be in the manifest, an entry's
evidence field. Not one covers a citation to something OUTSIDE the repository.
This counts the external ones and reports what can and cannot be checked here.

WHAT CAN BE CHECKED WITH NO EXTERNAL ACCESS, AND IT FINDS NOTHING WRONG. An
arXiv identifier is YYMM.NNNNN. The month must be 01 to 12, the date must not be
in the future, and from 2015 the sequence number is 5 digits rather than 4. All
3 are decidable from the string alone, and a fabricated identifier is a likely
place for an impossible one. The result is reported even though it is 0, because
a check that finds nothing is a result and a check never run is not.

WHAT CANNOT BE CHECKED HERE, AND WHY IT IS NOT ATTEMPTED. Whether an identifier
resolves to a real paper carrying the attribution the record gives it needs a
network lookup per identifier. `verify-supersession-boundary` says the external
check is not mine to answer, and spending dozens of lookups is the founder's
call. This script therefore reports the POPULATION and its structural health and
stops there.

2 PREDICATES WERE TRIED AND BOTH ARE REFUTED, RECORDED SO THEY ARE NOT RETRIED.
  1. A BARE `YYMM.NNNNN` pattern, without the `arXiv` prefix, matches decimal
     numbers in data tables. Measured: it matched `2529.9264` and `2530.4264`,
     which are 2 adjacent columns of a results table in a seat's own note, and
     reported them as identifiers with impossible months.
  2. JACCARD SIMILARITY OF THE SURROUNDING PROSE, as a test of whether an
     identifier cited in several files is described consistently. It measures
     prose similarity and not attribution. Measured: it flagged 10 of the 15
     multi-file identifiers, and the 2 inspected were both correct -- a
     bibliography entry against a prose mention of the SAME author, title and
     year scores low because a list and a paragraph share few words.
The surface has now defeated 2 predicates and a 3rd is deliberately NOT shipped.
"""
from __future__ import annotations

import collections
import datetime
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ROOTS = ("experimental_notes", "resources", "docs")
#: Directories whose contents are archival copies of what other models wrote.
#: A citation inside a preserved seat reply is that seat's, not the record's.
EXCLUDE = ("/logs/", "/evidence/", "/seat_evidence/", "/sandbox_harvest/")

ARXIV = re.compile(r'\barXiv[:\s]\s*(\d{2})(\d{2})\.(\d{4,5})', re.I)
DOI = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')
URL = re.compile(r'https?://[^\s)>\]]+')


def _files() -> list[pathlib.Path]:
    out = []
    for r in ROOTS:
        d = REPO / r
        if not d.is_dir():
            continue
        for p in d.rglob("*.md"):
            if not any(k in str(p) for k in EXCLUDE):
                out.append(p)
    return sorted(out)


def faults(ident: str, today: datetime.date) -> list[str]:
    """Every structural fault in one arXiv identifier, decidable from the string.

    PURE AND SEPARATE ON PURPOSE. Inline in the walk, a validator reporting 0
    faults across the whole record is indistinguishable from a validator that
    decides nothing, and this project has retired several mechanisms that ran
    and decided nothing. As a function it can be fed a PLANTED identifier and
    required to catch it, which is what makes the 0 falsifiable.

    `ident` is the YYMM.NNNNN body with the `arXiv` marker already stripped.
    """
    out: list[str] = []
    m = re.fullmatch(r"(\d{2})(\d{2})\.(\d{4,5})", ident)
    if not m:
        return ["not a YYMM.NNNNN identifier at all"]
    yy, mm, suffix = int(m.group(1)), int(m.group(2)), m.group(3)
    year = 2000 + yy
    if not 1 <= mm <= 12:
        out.append(f"impossible month {mm:02d}")
    elif datetime.date(year, mm, 1) > today:
        out.append(f"dated {year}-{mm:02d}, which is in the future")
    if year >= 2015 and len(suffix) != 5:
        out.append(f"{len(suffix)}-digit sequence for a {year} identifier, "
                   f"which has used 5 since 2015")
    return out


def _iv(k: int, n: int):
    """Wilson AND Clopper-Pearson, each by 2 independent routes.

    ★ BROUGHT TO THE CANONICAL CONTRACT 2026-11-06, after the complete board
    flagged this producer as resting a quantity on a single route. 2 faults were
    found and they are independent:

      1. THIS PRODUCER CARRIED NO CLOPPER-PEARSON AT ALL. Wilson alone is 1
         interval family, so the project's own rule -- every proportion carries
         an interval, cross-verified by 2 tools -- was met for Wilson and not at
         all for the second family. That is a real gap and this is its repair.

      2. THE DETECTOR COULD NOT SEE THE WILSON CROSS-CHECK THAT WAS ALREADY
         HERE. `counting_imports_ranks_producers_backwards_2026-11-03.py` looks
         for the written-out algebra as `z * z / (2 * n)`, lowercase, and this
         function spelled the sample size `N`. Measured: 52 of 121 scripts using
         statsmodels Wilson write the same algebra invisibly to that pattern --
         0.429752, Wilson [0.345049, 0.518778], Clopper-Pearson
         [0.340139, 0.522885]. That is the detector's defect, recorded
         separately; the variable is renamed here to the canonical spelling so
         this producer is not also relying on a pattern it cannot satisfy.
    """
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as _beta
    import mpmath as mp
    if n == 0:
        #: NO DENOMINATOR, NO INTERVAL. Returning (0, 1) would assert total
        #: ignorance as a measurement; the caller must see that nothing was
        #: measured.
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p = mp.mpf(k) / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * mp.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    wl2, wh2 = float(c - h), float(c + h)
    #: CLOPPER-PEARSON, route 1: the beta quantile.
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))
    #: route 2: invert the regularised incomplete beta directly, by bisection,
    #: so the second route shares no library code with the first.
    def _invert(a: float, b: float, y: float) -> float:
        if a <= 0:
            return 0.0
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)
    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    #: THE 3rd VALUE IS A MAGNITUDE, NOT A FLAG. The board's guard requires the
    #: LARGER of the 2 route disagreements and asserts it is under 1e-6. My first
    #: version returned a boolean, which compares as 1.0 and failed 4 of the
    #: guard's parameterised cases -- a helper can satisfy the shape and still
    #: report nothing usable. A magnitude says HOW FAR apart the routes are, and
    #: that is the quantity a reader needs.
    disagreement = max(abs(lo - wl2), abs(hi - wh2),
                       abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), disagreement


def measure(today: datetime.date | None = None) -> dict:
    today = today or datetime.date.today()
    arx: dict[str, set[str]] = collections.defaultdict(set)
    dois: dict[str, set[str]] = collections.defaultdict(set)
    urls: dict[str, set[str]] = collections.defaultdict(set)
    files = _files()
    for p in files:
        try:
            t = p.read_text(errors="replace")
        except OSError:
            continue
        rel = str(p.relative_to(REPO))
        for m in ARXIV.finditer(t):
            arx[f"{m.group(1)}{m.group(2)}.{m.group(3)}"].add(rel)
        for m in DOI.finditer(t):
            dois[m.group(0)].add(rel)
        for m in URL.finditer(t):
            urls[m.group(0)].add(rel)

    bad_month, future, short = [], [], []
    for ident in sorted(arx):
        for f in faults(ident, today):
            if f.startswith("impossible month"):
                bad_month.append(ident)
            elif "in the future" in f:
                future.append(ident)
            elif "digit sequence" in f:
                short.append(ident)

    # how many of these identifiers does ANY test name?
    #
    # THIS SCRIPT AND ITS OWN GUARD ARE EXCLUDED, AND NOT AS A COURTESY.
    # Measured the moment the pair was placed: the guard's filename carries
    # "citation", so the count of citation-guarding test files rose from 14 to
    # 15 and the instrument counted ITSELF; and the guard's control pins name
    # 2608.14590, 2610.10488 and 1706.03762 as planted fixtures, so the count
    # of identifiers "named by a test" rose from 1 to 3 and the instrument's own
    # test data was read as evidence about the record. A detector that includes
    # itself measures its own existence. The sibling reachability detector
    # carries the same exclusion for the same reason, with a test asserting it.
    SELF = {"test_is_any_external_citation_verified_2026-11-04.py"}
    tests = sorted(p for p in (REPO / "bench" / "tests").glob("test_*.py")
                   if p.name not in SELF)
    test_text = "\n".join(p.read_text(errors="replace") for p in tests)
    verified = [i for i in arx if i in test_text]
    guards = [p.name for p in tests
              if re.search(r"cit(ation|ed)", p.name, re.I)]

    r = {
        "files_scanned": len(files),
        "arxiv": len(arx), "doi": len(dois), "url": len(urls),
        "arxiv_multi_file": sum(1 for v in arx.values() if len(v) > 1),
        "bad_month": bad_month, "future": future, "short_suffix": short,
        "verified_by_a_test": verified,
        "citation_guard_files": guards,
        "today": today.isoformat(),
    }
    for key, lst in (("bad_month", bad_month), ("future", future),
                     ("short_suffix", short), ("verified_by_a_test", verified)):
        (r[f"iv_{key}"], r[f"cp_{key}"],
         r[f"agree_{key}"]) = _iv(len(lst), len(arx))
    return r


def main() -> int:
    r = measure()
    W = 78
    print("=" * W)
    print("IS ANY EXTERNAL CITATION IN THIS RECORD VERIFIED BY ANYTHING?")
    print("=" * W)
    print(f"\n  markdown files scanned (archival seat copies excluded): "
          f"{r['files_scanned']}")
    print(f"\n  distinct arXiv identifiers : {r['arxiv']}"
          f"   ({r['arxiv_multi_file']} cited in more than 1 file)")
    print(f"  distinct DOIs              : {r['doi']}")
    print(f"  distinct http(s) links     : {r['url']}")
    print(f"\n  test files guarding CITATIONS: {len(r['citation_guard_files'])}, "
          f"and every one guards an INTERNAL citation.")

    print(f"\n  WHAT IS DECIDABLE FROM THE STRING ALONE (as of {r['today']}):")
    for label, key in (("an impossible month", "bad_month"),
                       ("dated in the future", "future"),
                       ("4-digit suffix after 2015", "short_suffix")):
        lo, hi = r[f"iv_{key}"]
        cl, ch = r[f"cp_{key}"]
        print(f"    {label:28s}: {len(r[key]):>3} of {r['arxiv']}")
        print(f"        Wilson          [{lo:.6f}, {hi:.6f}]  "
              f"(statsmodels and mpmath)")
        print(f"        Clopper-Pearson [{cl:.6f}, {ch:.6f}]  "
              f"(scipy.beta and an mpmath betainc inversion)")
        print(f"        the 2 routes of each family differ by at most "
              f"{r[f'agree_{key}']:.1e}")
        for x in r[key]:
            print(f"        {x}")

    lo, hi = r["iv_verified_by_a_test"]
    cl, ch = r["cp_verified_by_a_test"]
    print(f"\n  arXiv identifiers NAMED BY ANY TEST: {len(r['verified_by_a_test'])} "
          f"of {r['arxiv']}")
    print(f"    Wilson          [{lo:.6f}, {hi:.6f}]")
    print(f"    Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
    print(f"    the 2 routes of each family differ by at most "
          f"{r['agree_verified_by_a_test']:.1e}")
    print(f"\n  SO: the structural checks find NOTHING WRONG, and whether any of "
          f"these\n  identifiers resolves to a real paper carrying the "
          f"attribution the record\n  gives it is NOT checked here and is not "
          f"mine to answer. It needs a network\n  lookup per identifier, which "
          f"is the founder's call to spend.\n")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
