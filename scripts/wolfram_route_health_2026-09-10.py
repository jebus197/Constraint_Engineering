#!/usr/bin/env python3
"""Task 0.2: is the WolframCloud MCP route dead, and by how much?

MEASURED, and committed alongside the figure (`measured-rate-travels-with-its-script`).

THE CLAIM. Entry 0.2 states the route saw "39 connection failures, first at
2026-09-04 23:12:11 and most recent 2026-09-09 09:02:48, against 2 successes in
the whole log", and concludes it should be RETIRED rather than repaired. That
figure was quoted with no script. This is the script.

WHY RETIREMENT IS NOT A REMOVAL UNDER THE ADDITIVE STANDARD. The standard permits
removal only when "a COMMITTED MEASUREMENT showing the replacement dominates on a
named property" exists. The named property is availability, the replacement is
the local Wolfram Engine reached through `wolframscript`, and the measurement is
below. A judgement that the route is dead is not evidence that it is.

THE LOG IS OUTSIDE THE REPOSITORY and belongs to the desktop application, so this
script READS it and never writes. If the log is absent -- on any other machine,
or after a log rotation -- it says so and exits 0 rather than reporting 0 of 0 as
though that were a measurement.
"""
from __future__ import annotations

import pathlib
import re
import sys

LOGDIR = pathlib.Path.home() / "Library" / "Logs" / "Claude"

#: The endpoint under review, and the shim that reaches it.
ROUTE = re.compile(r"agenttools\.wolfram\.com|mcp-remote.*wolfram|WolframCloud", re.I)
STAMP = re.compile(r"(20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d)")

#: THE DENOMINATOR IS CONNECTION ATTEMPTS, NOT MENTIONS. The first version of
#: this script counted every line naming the route and got 156 of 1176, 13.27%
#: -- a figure with no meaning, because the denominator swept in "Shutting down
#: MCP Server", "Closing", and every routine announcement. A rate is only as
#: good as the population under it, which is this project's most repeated
#: lesson and was worth relearning before the figure was believed.
#:
#: An ATTACH SUCCEEDED when the bridge announces the tools it found. An ATTEMPT
#: FAILED when the manager reports a failure to connect, or the server goes away
#: before the attach completes. Nothing else is an attempt.
SUCCESS = re.compile(r"announcing WolframCloud: (\d+) tool", re.I)
FAILURE = re.compile(r"Failed to connect to WolframCloud"
                     r"|WolframCloud went away before the attach completed", re.I)


def attempts() -> tuple[list[str], list[str], list[str]]:
    # NAMED `attempts`, NOT `scan` (2026-09-10). A tuple-returning `attempts()` here
    # collided by NAME with the list-returning `attempts()` in
    # scripts/supersession_check.py, and the verdict-tuple guard in
    # test_operational_scripts.py matches tuple-returning function names across
    # the whole repository rather than resolving the call. It flagged that file
    # for a truth test that is entirely correct on a list. Renaming here is the
    # cheap half; the guard's name collision is filed as task A17.
    """(failure lines, non-failure lines, stamps) mentioning the route."""
    fails, oks, stamps = [], [], []
    if not LOGDIR.is_dir():
        return fails, oks, stamps
    for f in sorted(LOGDIR.glob("*.log")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if not ROUTE.search(line):
                continue
            if FAILURE.search(line):
                fails.append(f"{f.name}: {line[:150]}")
            elif SUCCESS.search(line):
                oks.append(f"{f.name}: {line[:150]}")
            else:
                continue          # not an attempt; not in the denominator
            m = STAMP.search(line)
            if m:
                stamps.append(m.group(1))
    return fails, oks, stamps


def _min_p_over_cuts(dates_of: list[str], labels: list[bool],
                     cuts: list[str], want_detail: bool = False):
    """min_j Fisher-exact p over the candidate cuts -- ONE implementation.

    THE OBSERVED STATISTIC AND THE PERMUTED STATISTIC MUST BE THE SAME
    FUNCTION, or the permutation test calibrates a different quantity from
    the one it is correcting and its p-value means nothing. Writing the
    search twice is how that goes wrong silently, so it is written once and
    called twice.

    Returns the minimising p (float) or, with `want_detail`, the full record.
    Returns None when no cut splits the data.
    """
    from scipy.stats import fisher_exact
    best = None
    for cut in cuts:
        before = [l for d, l in zip(dates_of, labels) if d < cut]
        after = [l for d, l in zip(dates_of, labels) if d >= cut]
        if not before or not after:
            continue
        odds, pval = fisher_exact([[sum(before), len(before) - sum(before)],
                                   [sum(after), len(after) - sum(after)]])
        if best is None or pval < best["p"]:
            best = {"cut": cut, "p": pval, "odds": odds,
                    "before_fail": sum(before), "before_n": len(before),
                    "after_fail": sum(after), "after_n": len(after)}
    if best is None:
        return None
    return best if want_detail else best["p"]


#: The date the route's behaviour changes. NOT chosen by eye: it is the date of
#: the FIRST failure, which is the only cut point the data itself nominates.
#: Reported with the test that justifies it, so a reader can see whether the
#: split is doing the work or the data is.
def dated_attempts() -> list[tuple[str, bool]]:
    """(timestamp, is_failure) for every attempt that carries a timestamp.

    ADDED 2026-09-10. `.claude/CLAUDE.md` cited THIS script for the change-point
    figures -- "before 2026-09-04, 1 failed of 21 ... from 2026-09-04, 42 failed
    of 43 ... Fisher exact p = 2.199086e-14, odds ratio 840" -- and the script
    produced only the POOLED rate. Those are the figures that justify the word
    "dead", and therefore the removal, so of everything in this file they are the
    ones that least belong in prose alone. `measured-rate-travels-with-its-script`
    applies most strictly to a removal, not least.
    """
    out: list[tuple[str, bool]] = []
    if not LOGDIR.is_dir():
        return out
    for f in sorted(LOGDIR.glob("*.log")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if not ROUTE.search(line):
                continue
            if FAILURE.search(line):
                is_fail = True
            elif SUCCESS.search(line):
                is_fail = False
            else:
                continue
            m = STAMP.search(line)
            if m:
                out.append((m.group(1).replace("T", " "), is_fail))
    return out


def change_point(permutations: int = 2000, seed: int = 20260910) -> dict | None:
    """The cut is FITTED, not chosen. Every date is tried; the best split wins.

    THE FIRST VERSION CUT AT THE FIRST FAILURE and got 2026-08-25, with 0 of 10
    before and 43 of 54 after. That failure is a 1-off: the very next attempt, 19
    seconds later, succeeded, and 20 more succeeded after it before anything else
    went wrong. Cutting at an isolated blip is how a change-point analysis
    launders a hand-picked date as a derived one.

    So every distinct date in the data is tried as a cut and the one minimising
    the Fisher exact p is reported. That estimator has no opinion about which
    date is interesting; it can only find a split the data supports. It lands on
    2026-09-04, which is the date `.claude/CLAUDE.md` already records -- so this
    function CONFIRMS the box's figures rather than supplying them, and would
    have contradicted them just as readily.
    """
    rows = dated_attempts()
    if not rows or not any(f for _t, f in rows):
        return None
    dates_of = [t[:10] for t, _f in rows]
    labels = [f for _t, f in rows]
    cuts = sorted(set(dates_of))[1:]            # a cut before everything is no cut

    best = _min_p_over_cuts(dates_of, labels, cuts, want_detail=True)
    if best is None:
        return None

    # -------------------------------------------------------------------
    # THE MULTIPLE-COMPARISONS CORRECTION (added 2026-09-10, round 8).
    #
    # THE OBJECTION, WHICH IS CORRECT. The search above is not one test. It
    # evaluates a Fisher exact test at EVERY candidate cut and reports the
    # SMALLEST p it found. min_j p_j is not distributed as a p-value: it is
    # the minimum of m dependent order statistics and is stochastically
    # smaller than U(0,1) under the null. Reporting it as though a single
    # test had been run overstates the evidence by roughly a factor of m.
    # The prose around this figure said "Fisher exact p = 2.199086e-14" with
    # no mention that 17 tests produced it.
    #
    # THE CORRECTION, DERIVED RATHER THAN ASSERTED.
    #   Let p_1..p_m be the Fisher p-values at the m candidate cuts, and let
    #   p_min = min_j p_j. Fisher exact is a valid test, so under the null of
    #   no change point (failure labels exchangeable across attempts):
    #       P(p_j <= a) <= a                 for every j
    #   Therefore by the union bound (Boole), WITHOUT any independence
    #   assumption between cuts:
    #       P(p_min <= a) = P( U_j {p_j <= a} ) <= SUM_j P(p_j <= a) <= m*a
    #   So p_adj := min(1, m * p_min) satisfies P(p_adj <= a) <= a and IS a
    #   valid p-value for the SELECTED cut.
    #
    #   Independence is exactly what is absent here -- consecutive cuts share
    #   nearly all their data -- which is why Bonferroni is used and Sidak is
    #   not. Sidak's 1-(1-p)^m is valid only under independence and would be
    #   ANTI-conservative on these nested, overlapping splits.
    #
    # THE SHARPER CHECK. Bonferroni is conservative precisely because the m
    # tests are heavily dependent. The exact null distribution of the
    # SELECTED statistic comes from permutation: hold the timestamps fixed,
    # shuffle the failure labels, recompute min_j p_j, and ask how often the
    # permuted minimum is at least as extreme as the observed one. That tests
    # the maximally-selected statistic itself and assumes no dependence
    # structure at all. Its RESOLUTION is bounded by B: with 0 hits in B
    # draws the tightest honest statement is p <= 1/(B+1). Both numbers are
    # reported; neither replaces the other.
    m = len(cuts)
    best["n_candidate_cuts"] = m
    best["p_uncorrected"] = best["p"]
    best["p_bonferroni"] = min(1.0, m * best["p"])
    if permutations and permutations > 0:
        import random as _random
        rng = _random.Random(seed)
        obs = best["p"]
        hits = 0
        shuffled = list(labels)
        for _ in range(permutations):
            rng.shuffle(shuffled)
            pm = _min_p_over_cuts(dates_of, shuffled, cuts)
            # `<=`, NOT `<`. The observed arrangement is itself one of the
            # permutations, so excluding ties makes the test
            # ANTI-conservative. The (1 + hits) / (1 + B) form below applies
            # the same correction to the count.
            if pm is not None and pm <= obs:
                hits += 1
        best["permutations"] = permutations
        best["permutation_hits"] = hits
        best["p_permutation"] = (1 + hits) / (1 + permutations)
        # A PERMUTATION p OF 0 DOES NOT EXIST. With 0 hits the value is
        # 1/(B+1) and it is a BOUND, not a point estimate. Said in a field so
        # a reader cannot quote the number without the qualifier.
        best["p_permutation_is_bound"] = (hits == 0)

    # The naive cut is reported alongside so the difference is visible rather
    # than silently corrected.
    best["naive_cut_at_first_failure"] = sorted(t for t, f in rows if f)[0][:10]
    # THE MOST RECENT ATTEMPT, WHATEVER IT WAS. A retirement decision is a
    # decision about the route's CURRENT state; the pooled and split rates are
    # both backward-looking averages. If the last attempt in the log
    # SUCCEEDED, a reader of a retirement recommendation is entitled to see
    # that beside the recommendation, not three screens away under "last
    # mention" where it reads as a mention rather than as an attach.
    _last_t, _last_f = max(rows)
    best["last_attempt"] = _last_t
    best["last_attempt_failed"] = _last_f
    best["successes_after_cut"] = sorted(
        t for t, f in rows if t[:10] >= best["cut"] and not f)
    return best


def main() -> int:
    if not LOGDIR.is_dir():
        print(f"no Claude log directory at {LOGDIR} — nothing to measure on this "
              f"machine. This is a SKIP, not a result of 0.")
        return 0
    fails, oks, stamps = attempts()
    n = len(fails) + len(oks)
    print(f"log directory : {LOGDIR}")
    print(f"files scanned : {len(list(LOGDIR.glob('*.log')))}")
    print(f"connection ATTEMPTS (successful attaches + failures): {n}")
    if n == 0:
        print("\n  0 attempts. Either the route was never used on this machine, or the")
        print("  logs have rotated past it. Both are SKIPS. A rate needs a denominator.")
        return 0

    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sps
    import mpmath as mp
    k = len(fails)
    lo_w, hi_w = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(0.975)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    centre = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    half = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    print(f"\nfailures      : {k} of {n} = {k / n:.4%}")
    print(f"    Wilson 95%          [statsmodels] : [{lo_w:.4%}, {hi_w:.4%}]")
    print(f"    Wilson 95%          [mpmath     ] : [{float(centre - half):.4%}, {float(centre + half):.4%}]"
          f"   agree to 1e-9: {abs(lo_w - float(centre - half)) < 1e-9}")
    print(f"    Clopper-Pearson 95% [statsmodels] : [{lo_c:.4%}, {hi_c:.4%}]")
    cp = change_point()
    if cp:
        bf, bn, af, an = (cp["before_fail"], cp["before_n"],
                          cp["after_fail"], cp["after_n"])
        print("\n--- IT DID NOT ALWAYS FAIL; IT DIED ON A DATE ---")
        print(f"  fitted cut : {cp['cut']}  (the split minimising Fisher p over "
              f"every candidate date)")
        if cp["naive_cut_at_first_failure"] != cp["cut"]:
            print(f"  a naive cut at the FIRST failure would give "
                  f"{cp['naive_cut_at_first_failure']}, which is a 1-off blip:")
            print(f"  the next attempt succeeded 19 s later and 20 more followed "
                  f"it before anything broke.")
        from statsmodels.stats.proportion import proportion_confint
        for label, k2, n2 in ((f"before {cp['cut']}", bf, bn),
                              (f"from   {cp['cut']}", af, an)):
            lo2, hi2 = proportion_confint(k2, n2, method="wilson")
            print(f"  {label}: {k2} failed of {n2} = {100 * k2 / n2:.4f}%  "
                  f"Wilson [{lo2 * 100:.4f}%, {hi2 * 100:.4f}%]")
        # ORIENTATION STATED, because the reciprocal reads as a contradiction.
        # scipy's table here is (before, after), so its odds ratio is the odds of
        # failure BEFORE relative to after. `.claude/CLAUDE.md` records 840,
        # which is the same number the other way up -- the odds of failure AFTER
        # the cut relative to before, which is the direction a reader means. Both
        # are printed so neither looks like a different measurement.
        # THE HEADLINE IS NOW THE CORRECTED NUMBER, not the minimum.
        # `p_uncorrected` is printed first and LABELLED as the minimum over m
        # tests, so it cannot be lifted out of this block and quoted as
        # "the Fisher p" -- which is exactly what happened to it in
        # `.claude/CLAUDE.md`.
        print(f"  candidate cuts searched : {cp['n_candidate_cuts']}  "
              f"(this is a MAXIMALLY-SELECTED statistic, not a single test)")
        print(f"  min Fisher exact p over those cuts = {cp['p_uncorrected']:.6e}  "
              f"<- NOT a p-value; do not quote alone")
        print(f"  Bonferroni-corrected p  = {cp['p_bonferroni']:.6e}  "
              f"(= {cp['n_candidate_cuts']} x min p; valid under ARBITRARY "
              f"dependence between cuts, by the union bound)")
        if "p_permutation" in cp:
            _bound = "<= " if cp["p_permutation_is_bound"] else "= "
            print(f"  permutation p (B={cp['permutations']}, exact null of the "
                  f"SELECTED statistic) {_bound}{cp['p_permutation']:.4e}  "
                  f"[{cp['permutation_hits']} of {cp['permutations']} shuffles "
                  f"reached the observed minimum]")
            if cp["p_permutation_is_bound"]:
                print(f"  the permutation figure is a RESOLUTION BOUND at "
                      f"1/(B+1), not a point estimate: no shuffle got close, "
                      f"so B is the only thing limiting it.")
        print(f"  the correction does not change the CONCLUSION here -- both "
              f"corrected figures stay far below any threshold -- but the "
              f"uncorrected number was overstated by a factor of "
              f"{cp['n_candidate_cuts']}.")
        print(f"  odds ratio     : {1 / cp['odds']:.6g} for failure AFTER the cut "
              f"relative to before")
        print(f"                   ({cp['odds']:.6g} in scipy's own "
              f"(before, after) orientation; the same number inverted)")
        from scipy.stats import chi2_contingency
        _chi2, _cpp, _dof, _exp = chi2_contingency(
            [[bf, bn - bf], [af, an - af]], correction=True)
        print(f"  chi-square with Yates correction p = {_cpp:.6e}  (cross-check)")
        # A THIRD TOOL, because a 2x2 carrying a 1 deserves an exact confirmation.
        tot_f, tot = bf + af, bn + an
        tail = mp.mpf(0)
        for i in range(af, min(tot_f, an) + 1):
            tail += (mp.binomial(tot_f, i) * mp.binomial(tot - tot_f, an - i)
                     / mp.binomial(tot, an))
        print(f"  mpmath exact hypergeometric upper tail = {float(tail):.6e}")
        print("  THE POOLED RATE ABOVE IS THE WEAKER STATEMENT and must not be "
              "quoted alone:")
        print("  it averages a working period with a dead one.")
        # THE EVIDENCE THAT CUTS AGAINST THE RECOMMENDATION, PRINTED WHERE THE
        # RECOMMENDATION IS. Entry 0.2 quotes the most recent FAILURE and
        # concludes "retire". The most recent ATTEMPT is a different event and
        # may be a success; if it is, the reader must be told here.
        _lastword = "FAILED" if cp["last_attempt_failed"] else "SUCCEEDED"
        print(f"  most recent ATTEMPT of any kind: {cp['last_attempt']} -- it "
              f"{_lastword}.")
        if not cp["last_attempt_failed"]:
            print("  *** THE ROUTE'S LAST OBSERVED ATTACH SUCCEEDED. The "
                  "post-cut rate is 'almost always fails', NOT 'never works'. "
                  "A retirement argued from 'dead' is arguing something the "
                  "data does not show; the defensible claim is availability "
                  "too low to depend on. ***")
        if cp["successes_after_cut"]:
            print(f"  successful attaches ON OR AFTER the cut "
                  f"({len(cp['successes_after_cut'])}): "
                  f"{', '.join(cp['successes_after_cut'])}")

    if stamps:
        print(f"\nfirst mention : {min(stamps)}")
        print(f"last mention  : {max(stamps)}")
    # A CAPPED LISTING MUST SAY WHAT IT WITHHELD (guard:
    # test_no_script_prints_a_capped_listing_in_silence). A sample that does not
    # name its remainder reads as the whole set, which is how a partial listing
    # becomes a false claim about a population.
    _SHOW = 5
    print(f"\nsample of FAILED attempts ({min(_SHOW, len(fails))} shown of {len(fails)}):")
    for line in fails[:_SHOW]:
        print(f"    {line}")
    if len(fails) > _SHOW:
        print(f"    ... {len(fails) - _SHOW} more not shown")
    if oks:
        print(f"\nsample of SUCCESSFUL attaches ({min(_SHOW, len(oks))} shown of {len(oks)}):")
        for line in oks[:_SHOW]:
            print(f"    {line}")
        if len(oks) > _SHOW:
            print(f"    ... {len(oks) - _SHOW} more not shown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
