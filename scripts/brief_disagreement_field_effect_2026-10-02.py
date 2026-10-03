#!/usr/bin/env python3
"""Does naming disagreement as an OUTPUT FIELD change what seats return?

WHY THIS EXISTS. On 2026-10-02 a check was added to
`scripts/panel_brief_validate.py` refusing a brief whose output section does not
name disagreement. Its stated justification was ONE round -- the star round
`integrity_advisory_r2_2026-10-02`, where the field was absent and 1 of 2 seats
omitted a disagreement. One round is an anecdote. Worse, the figures first
written beside the check were measured on the WRONG POPULATION: "1 of the 3
briefs carrying an output section under the template" was asserted after looking
at 3 briefs by hand, and an archive-wide run refuses 12. That is the
check-one-member-then-assert-a-universal shape this project has withdrawn
claims for 11 times before.

So this script measures the whole archive, and it is committed beside every
number it produces (`measured-rate-travels-with-its-script`).

WHAT IT DECIDES, AND WHAT IT CANNOT. It reports the association between a
brief naming the field and its seats carrying a disagreement. Association is
NOT causation here: briefs that name the field are also later, longer and
written under the ruling, so any effect is confounded with time. The script
therefore reports the within-period breakdown as well, and states the
confound rather than hiding it.

DELIBERATELY NOT A SECOND DEFINITION. `carries_disagreement` is imported from
`scripts/panel_condition_compliance_2026-09-10.py`, the 1 module that decides
it, and the section scoping is imported from `panel_brief_validate` itself.
Two copies of a predicate is the defect this project found by executing two
forms against each other 4 times.

Attribution: no Wolfram result is used here; the cross-checks are scipy vs
mpmath and statsmodels vs an independent closed form.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# first version of this preamble inserted the repo ROOT and so worked when the
# file was RUN (sys.path[0] is the script dir) and failed when it was IMPORTED,
# which is how 13 scripts stopped importing on 2026-09-24.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
RULING = "2026-09-09"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def brief_rows():
    """One row per archived brief: (round, has_section, field_in_section, anywhere)."""
    pbv = _load("pbv_effect", "scripts/panel_brief_validate.py")
    rows = []
    for b in sorted((ROOT / "bench" / "logs").glob("*/BRIEF.md")):
        text = b.read_text(encoding="utf-8", errors="ignore")
        body = pbv._section(text, r"output|deliverable|what to return")
        rows.append((
            b.parent.name,
            body is not None,
            bool(body is not None and re.search(r"\bdisagree", body, re.I)),
            bool(re.search(r"\bdisagree", text, re.I)),
        ))
    return rows


def seat_rows():
    """One row per seat reply: (round, carries_disagreement)."""
    sys.path.insert(0, str(ROOT / "bench" / "tests"))
    tm = _load("pc_met", "bench/tests/test_panel_conditions_are_met_2026-09-10.py")
    return [(rnd, bool(tm.carries_disagreement(d.get("response", ""))))
            for rnd, d in tm._replies()], tm


def wilson(k: int, n: int):
    """Wilson score interval, computed twice by independent routes."""
    from statsmodels.stats.proportion import proportion_confint
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson") if n else (float("nan"),) * 2
    import mpmath as mp
    mp.mp.dps = 40
    if not n:
        return (float("nan"), float("nan")), (float("nan"), float("nan"))
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p = mp.mpf(k) / n
    d = 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return (float(lo_sm), float(hi_sm)), (float((c - h) / d), float((c + h) / d))


def fisher(a: int, b: int, c: int, d: int):
    """2x2 Fisher exact, scipy against an mpmath exact hypergeometric tail."""
    from scipy.stats import fisher_exact
    _, p_scipy = fisher_exact([[a, b], [c, d]])
    import mpmath as mp
    mp.mp.dps = 50
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def prob(x):
        return (mp.binomial(c1, x) * mp.binomial(n - c1, r1 - x)) / mp.binomial(n, r1)

    obs = prob(a)
    lo = max(0, r1 - (n - c1))
    tot = mp.mpf(0)
    for x in range(lo, min(r1, c1) + 1):
        pr = prob(x)
        if pr <= obs * (1 + mp.mpf("1e-30")):
            tot += pr
    return float(p_scipy), float(tot)


def main() -> int:
    briefs = {r[0]: r for r in brief_rows()}
    replies, tm = seat_rows()

    n = len(briefs)
    has_sec = sum(1 for r in briefs.values() if r[1])
    field = sum(1 for r in briefs.values() if r[2])
    refused = sum(1 for r in briefs.values() if r[1] and not r[2])
    anywhere_missing = sum(1 for r in briefs.values() if not r[3])

    print(f"ARCHIVED BRIEFS: {n}")
    print(f"  with an output section          : {has_sec}")
    print(f"  naming disagreement IN it       : {field}")
    print(f"  REFUSED by the section check    : {refused}")
    (l1, h1), (l2, h2) = wilson(refused, n)
    print(f"    rate {refused}/{n} = {100*refused/n:.4f}%  "
          f"Wilson statsmodels [{100*l1:.4f}%, {100*h1:.4f}%]  "
          f"mpmath [{100*l2:.4f}%, {100*h2:.4f}%]")
    print(f"  REFUSED by a WHOLE-DOCUMENT check: {anywhere_missing}")
    (l1, h1), (l2, h2) = wilson(anywhere_missing, n)
    print(f"    rate {anywhere_missing}/{n} = {100*anywhere_missing/n:.4f}%  "
          f"Wilson statsmodels [{100*l1:.4f}%, {100*h1:.4f}%]  "
          f"mpmath [{100*l2:.4f}%, {100*h2:.4f}%]")

    # Per-round seat outcome, restricted to rounds that HAVE both a brief and replies.
    rounds = {}
    for rnd, ok in replies:
        if rnd in briefs and briefs[rnd][1]:
            rounds.setdefault(rnd, []).append(ok)
    print(f"\nROUNDS WITH BOTH A BRIEF (with output section) AND REPLIES: {len(rounds)}")

    a = b = c = d = 0   # field present/absent x every seat disagreed / not
    for rnd, oks in rounds.items():
        allok = all(oks)
        if briefs[rnd][2]:
            a, b = a + (1 if allok else 0), b + (0 if allok else 1)
        else:
            c, d = c + (1 if allok else 0), d + (0 if allok else 1)
    print(f"  field named    : {a} all-seats-disagreed, {b} not  (n={a+b})")
    print(f"  field NOT named: {c} all-seats-disagreed, {d} not  (n={c+d})")
    if (a + b) and (c + d):
        p_sp, p_mp = fisher(a, b, c, d)
        print(f"  Fisher exact two-sided: scipy p = {p_sp:.6e}, mpmath p = {p_mp:.6e}")
        print(f"  AGREE to 1e-9: {abs(p_sp - p_mp) < 1e-9}")

    # The confound, stated rather than hidden.
    print("\nCONFOUND: the field appears in later briefs, so the comparison above is")
    print("not time-matched. Within rounds dated on or after the ruling "
          f"({RULING}):")
    a2 = b2 = c2 = d2 = 0
    for rnd, oks in rounds.items():
        if (tm._round_date(rnd) or "") < RULING:
            continue
        allok = all(oks)
        if briefs[rnd][2]:
            a2, b2 = a2 + (1 if allok else 0), b2 + (0 if allok else 1)
        else:
            c2, d2 = c2 + (1 if allok else 0), d2 + (0 if allok else 1)
    print(f"  field named    : {a2} all, {b2} not  (n={a2+b2})")
    print(f"  field NOT named: {c2} all, {d2} not  (n={c2+d2})")
    if (a2 + b2) and (c2 + d2):
        p_sp, p_mp = fisher(a2, b2, c2, d2)
        print(f"  Fisher exact two-sided: scipy p = {p_sp:.6e}, mpmath p = {p_mp:.6e}")
    else:
        print("  ONE ARM IS EMPTY -- no within-period comparison is possible, so the")
        print("  association above CANNOT be separated from the passage of time.")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NEVER COST ANYTHING (founder ruling, after 15 of 17
    # runners billed a live dispatch on an unrecognised argument). Without
    # this call the flag is ignored and the whole archive measurement runs
    # in answer to a request to be told what the script does -- which is
    # what made the survey guard take minutes.
    answer_help(__doc__, __file__)
    raise SystemExit(main())
