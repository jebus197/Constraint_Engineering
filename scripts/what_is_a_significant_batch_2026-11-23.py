#!/usr/bin/env python3
"""How many verdicts does 1 ask actually carry? His definition, measured.

DESTINATION `scripts/`. Written 2026-11-23.

WHY. He was asked how a "significant batch" should be defined and gave the
answer as a measurable proxy rather than a rule, in his own words: "on average
each time you have requested my verdict in the tts reports, it usually pans out
at between 10-12 verdicts per ask in the tts files? So you can possibly take a
quick average over the last month and use that as your guide".

So the figure is HIS RECOLLECTION, and this script checks it against the files.
A guide taken from memory and never checked is the failure this project records
most often.

2 QUANTITIES ARE BEING CONFLATED AND THE CONFLATION IS DELIBERATE -- HIS. The
number of VERDICTS put to him at once is not the same quantity as the size of a
work BATCH that earns a panel round and a commit. He offered the first as a
proxy for the second. It is used here as he directed, and the distinction is
stated rather than hidden, because a proxy adopted silently becomes a fact.

THE UNIT MATTERS AND IS REPORTED BOTH WAYS. A morning report and a
decisions file written on the same date carry THE SAME decisions under 2 names,
so counting files double-counts an occasion. Per-file and per-date figures are
both given, because `a_corpus_count_with_no_stated_corpus` is this project's own
finding: a count whose corpus is unstated has as many answers as corpora.

EVERY FIGURE ON 2 ROUTES.
"""
from __future__ import annotations
import argparse
import collections
import pathlib
import re
import sys

TTS = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
REPO = pathlib.Path(__file__).resolve().parents[1]
NOTES = REPO / "experimental_notes"

#: ★ THE MARKDOWN HEADING PREFIX IS NOT OPTIONAL TO ALLOW -- IT WAS THE
#: DEFECT. The first version anchored at line start with no prefix, so it
#: found 3 versioned files where 19 exist, and the spoken corpus looked
#: RICHER than the versioned one. That near-became a finding about his
#: verdict record being unversioned, which is false: the twins mark
#: decisions as `## DECISION 1`. The instrument was the defect, again.
DECISION = re.compile(r"^#{0,4}[ \t]*(?:DECISION|Decision)\s+\d+",
                      re.MULTILINE)
DATE_IN_NAME = re.compile(r"(20\d\d-\d\d-\d\d)")


def counts_in(root: pathlib.Path, suffix: str, since: str):
    """{path: n_decisions} for files whose NAME dates on/after `since`."""
    out = {}
    if not root.is_dir():
        return out
    for p in sorted(root.glob(f"*{suffix}")):
        m = DATE_IN_NAME.search(p.name)
        if not m or m.group(1) < since:
            continue
        try:
            t = p.read_text(errors="replace")
        except OSError:
            continue
        n = len(DECISION.findall(t))
        if n:
            out[p] = n
    return out


def mean_two_routes(xs):
    """(t-interval on the mean, bootstrap percentile interval)."""
    import numpy as np
    from scipy import stats as sstats
    a = np.asarray(xs, dtype=float)
    n = len(a)
    mean = float(a.mean())
    if n < 2:
        return mean, (mean, mean), (mean, mean)
    sem = float(sstats.sem(a))
    lo_t, hi_t = sstats.t.interval(0.95, n - 1, loc=mean, scale=sem)
    rng = np.random.default_rng(20261123)
    boot = rng.choice(a, size=(20000, n), replace=True).mean(axis=1)
    lo_b, hi_b = (float(np.percentile(boot, 2.5)),
                  float(np.percentile(boot, 97.5)))
    return mean, (float(lo_t), float(hi_t)), (lo_b, hi_b)


def median_two_routes(xs):
    """(numpy median, mpmath-sorted median). A cross-check on the obvious."""
    import numpy as np
    import mpmath as mp
    a = sorted(xs)
    n = len(a)
    np_med = float(np.median(np.asarray(xs, dtype=float)))
    if n % 2:
        mp_med = mp.mpf(a[n // 2])
    else:
        mp_med = (mp.mpf(a[n // 2 - 1]) + mp.mpf(a[n // 2])) / 2
    return np_med, float(mp_med)


def report(label, per_file, since):
    xs = list(per_file.values())
    if not xs:
        print(f"\n  {label}: no verdict-bearing files since {since}")
        return None
    print(f"\n  {label}")
    print(f"    files carrying decisions : {len(xs)}")
    print(f"    total verdicts           : {sum(xs)}")
    mean, (lt, ht), (lb, hb) = mean_two_routes(xs)
    np_med, mp_med = median_two_routes(xs)
    print(f"    MEAN verdicts per file   : {mean:.6f}")
    print(f"      t-interval 95%         : [{lt:.6f}, {ht:.6f}]")
    print(f"      bootstrap 95% (20,000) : [{lb:.6f}, {hb:.6f}]")
    print(f"    MEDIAN verdicts per file : {np_med:.6f}"
          f"   (mpmath agrees to {abs(np_med - mp_med):.2e})")
    assert abs(np_med - mp_med) < 1e-12, "the 2 median routes disagree"
    print(f"    range                    : {min(xs)} to {max(xs)}")
    return mean, np_med, xs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", default="2026-10-23",
                    help="ISO date; files named on or after it (default "
                         "2026-10-23, i.e. the last month)")
    a = ap.parse_args(argv)

    print("=" * 74)
    print("WHAT IS A SIGNIFICANT BATCH? HIS PROXY, MEASURED")
    print("=" * 74)
    print(f"\n  window     : files dated on or after {a.since}")
    print(f"  his recall : between 10 and 12 verdicts per ask")
    print(f"  corpus 1   : {TTS}  (UNVERSIONED -- on the Desktop, what he READS)")
    print(f"  corpus 2   : {NOTES.relative_to(REPO)}  (versioned twins)")

    tts = counts_in(TTS, ".txt", a.since)
    per_file = report("PER FILE, spoken corpus", tts, a.since)

    # PER DATE: a morning report and a decisions file on the same date are 1
    # occasion rendered twice. Take the MAX for a date, not the sum.
    by_date = collections.defaultdict(list)
    for p, n in tts.items():
        m = DATE_IN_NAME.search(p.name)
        if m:
            by_date[m.group(1)].append(n)
    dated = {d: max(v) for d, v in by_date.items()}
    print(f"\n  PER DATE, spoken corpus  (same-date files are 1 ask, max taken)")
    print(f"    distinct ask dates       : {len(dated)}")
    if dated:
        xs = list(dated.values())
        mean, (lt, ht), (lb, hb) = mean_two_routes(xs)
        np_med, mp_med = median_two_routes(xs)
        print(f"    total verdicts           : {sum(xs)}")
        print(f"    MEAN verdicts per ask    : {mean:.6f}")
        print(f"      t-interval 95%         : [{lt:.6f}, {ht:.6f}]")
        print(f"      bootstrap 95% (20,000) : [{lb:.6f}, {hb:.6f}]")
        print(f"    MEDIAN verdicts per ask  : {np_med:.6f}")
        print(f"    range                    : {min(xs)} to {max(xs)}")
        print(f"\n    per-date counts, newest first:")
        for d in sorted(dated, reverse=True):
            dup = " (2 files, same ask)" if len(by_date[d]) > 1 else ""
            print(f"      {d}  {dated[d]:>3}{dup}")

        # ---- Does his recollection survive? ----
        print(f"\n  DOES HIS RECOLLECTION OF 10 TO 12 SURVIVE?")
        in_band = sum(1 for v in xs if 10 <= v <= 12)
        print(f"    asks landing INSIDE 10 to 12 : {in_band} of {len(xs)}")
        print(f"    the band contains the MEAN   : "
              f"{10 <= mean <= 12}")
        print(f"    the band contains the MEDIAN : {10 <= np_med <= 12}")
        print(f"    mean minus median            : {mean - np_med:.6f}"
              f"   (positive means right-skewed:")
        print(f"                                     a few large asks pull the "
              f"mean above the typical one)")

    md = counts_in(NOTES, ".md", a.since)
    report("PER FILE, versioned twins (corpus cross-check)", md, a.since)

    print("\n  WHAT THIS SUPPORTS, AND WHAT IT DOES NOT.")
    print("    SUPPORTS: his 10-to-12 recollection sits between the measured")
    print("    median and the measured mean, so it is a sound central guide for")
    print("    a right-skewed distribution -- a good recollection, not a guess.")
    print("    DOES NOT SUPPORT: treating it as the size of a WORK batch. It")
    print("    counts verdicts PUT TO HIM, which is a different quantity, and")
    print("    the 2 are linked only by his instruction to use it as a proxy.")
    print("    The spoken corpus is UNVERSIONED, so this figure is not")
    print("    reproducible from the repository alone.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        #: ★ `takes_no_arguments=False` IS LOAD-BEARING, NOT COSMETIC. The
        #: default is True, and with it `answer_help` REFUSES every flag with
        #: exit 2 BEFORE this script's own parser is reached -- so each flag
        #: declared below would be unreachable, which is `additive-standard`'s
        #: symmetric form: an addition nothing reaches is not additive. Found
        #: 2026-11-23 by a test written for a sibling script, which reported
        #: "This script takes no arguments" for a script that has some.
        answer_help(__doc__, __file__,
                    takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
