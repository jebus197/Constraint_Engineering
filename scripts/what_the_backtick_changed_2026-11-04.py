#!/usr/bin/env python3
"""What did adding a backtick to the disagreement predicate actually change?

THE FIGURE THIS REPLACES. Entry B120 stated `Fisher exact p = 1.108513e-11` for
the concentration of replies that a 1-character fix changes. That figure was
WITHDRAWN on 2026-11-04: no script produced it and its 2x2 table was never
recorded, so it could not be recomputed. 6 candidate tables consistent with the
entry's prose were tested and none reproduces it, the nearest giving
9.526969e-11. This script measures the question the entry was asking, states its
table explicitly, and computes every quantity by 2 independent routes.

AND THE TEST THE ENTRY NAMED WAS THE WRONG ONE. "The fix flips exactly N replies
and 0 in the losing direction" is a statement about a BEFORE and AFTER verdict on
the SAME replies, which is a PAIRED design. Fisher's exact test is for 2
INDEPENDENT samples; applied to a paired table it answers a different question
and its denominator is wrong. The exact test for a paired binary comparison is
McNemar's, which conditions on the DISCORDANT pairs alone -- the replies whose
verdict changed -- and under the null that a change is equally likely in either
direction is a binomial on those pairs. Both are reported here: McNemar because
it is the right test, and Fisher on the unpaired table because that is what the
entry claimed, so the difference is visible rather than asserted.

THE DENOMINATOR DOES NOT REPRODUCE EITHER, AND THAT IS REPORTED NOT HIDDEN. The
entry says 392 archive replies. The instrument it describes,
`scripts/panel_condition_compliance_2026-09-10.py`, enumerates its replies as 7
named seats across every archived round, and today that is a different number.
Whether the population definition changed or the figure was wrong cannot be
settled from the record, so this script prints what it counts and names the
discrepancy.

THE PREDICATE IS TAKEN FROM THE LIVE MODULE, NEVER COPIED. The variant is built
by removing the backtick from the module's own compiled pattern, so the
comparison cannot drift from the thing it measures.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MODULE = REPO / "scripts" / "panel_condition_compliance_2026-09-10.py"


def _load():
    sys.path.insert(0, str(MODULE.parent))
    spec = importlib.util.spec_from_file_location("_pcc", MODULE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _without_backtick(pattern: str) -> str:
    """The predicate as it stood BEFORE the fix: the markup class loses its backtick.

    Derived from the live pattern rather than retyped, and the derivation is
    asserted to have changed exactly 1 character so a silent no-op is impossible.
    """
    before = pattern.replace("[*`]", "[*]", 1)
    if before == pattern:
        raise SystemExit("the markup class `[*`]` is not in the live pattern any "
                         "more, so the pre-fix form cannot be derived from it")
    if len(pattern) - len(before) != 1:
        raise SystemExit(f"the derivation changed {len(pattern) - len(before)} "
                         f"characters, not 1")
    return before


def replies(m) -> list[tuple[str, str]]:
    """Every archived reply as (label, response text), by the module's own walk."""
    out = []
    for d in m.rounds():
        for s in m.SEATS:
            f = d / f"{s}.json"
            if not f.is_file():
                continue
            try:
                j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            out.append((f"{d.name}/{s}", j.get("response", "") or ""))
    return out


def mcnemar_exact(gained: int, lost: int) -> tuple[float, float]:
    """2-sided exact McNemar on the discordant pairs, by scipy and by mpmath."""
    from scipy.stats import binomtest
    import mpmath as mp
    n = gained + lost
    if n == 0:
        return float("nan"), float("nan")
    p_scipy = float(binomtest(gained, n, 0.5, alternative="two-sided").pvalue)
    mp.mp.dps = 50
    k = min(gained, lost)
    tail = sum(mp.binomial(n, i) for i in range(0, k + 1)) / mp.mpf(2) ** n
    p_mp = float(min(mp.mpf(1), 2 * tail))
    return p_scipy, p_mp


def fisher_unpaired(a: int, b: int, c: int, d: int, m) -> tuple[float, float]:
    """Fisher 2-sided on the UNPAIRED table, by scipy and by the module's mpmath."""
    from scipy.stats import fisher_exact
    _or, p_scipy = fisher_exact([[a, b], [c, d]], alternative="two-sided")
    return float(p_scipy), float(m.fisher_two_sided_mpmath(a, b, c, d))


def measure() -> dict:
    m = _load()
    live = m.DISAGREEMENT_RE
    before_src = _without_backtick(live.pattern)
    before_re = re.compile(before_src, live.flags)

    rows = replies(m)
    gained, lost, both, neither = [], [], 0, 0
    for label, text in rows:
        after = m.carries_disagreement(text)
        m.DISAGREEMENT_RE = before_re          # the module's own body reads this
        try:
            prior = m.carries_disagreement(text)
        finally:
            m.DISAGREEMENT_RE = live
        if prior and after:
            both += 1
        elif not prior and not after:
            neither += 1
        elif after and not prior:
            gained.append(label)
        else:
            lost.append(label)

    n = len(rows)
    r = {
        "n_replies": n,
        "entry_claims_n": 392,
        "gained": gained, "lost": lost,
        "n_gained": len(gained), "n_lost": len(lost),
        "both": both, "neither": neither,
        "live_pattern_len": len(live.pattern),
        "before_pattern_len": len(before_src),
    }
    r["mcnemar_scipy"], r["mcnemar_mpmath"] = mcnemar_exact(len(gained), len(lost))
    r["mcnemar_gap"] = (abs(r["mcnemar_scipy"] - r["mcnemar_mpmath"])
                        if r["n_gained"] + r["n_lost"] else float("nan"))
    # the unpaired table the entry's Fisher framing implies: changed vs unchanged
    # against the direction of change
    a, b = len(gained), len(lost)
    c, d = both, neither
    r["fisher_table"] = [[a, b], [c, d]]
    r["fisher_scipy"], r["fisher_mpmath"] = fisher_unpaired(a, b, c, d, m)
    r["fisher_gap"] = abs(r["fisher_scipy"] - r["fisher_mpmath"])
    return r


def main() -> int:
    r = measure()
    W = 78
    print("=" * W)
    print("WHAT THE BACKTICK ACTUALLY CHANGED IN THE DISAGREEMENT PREDICATE")
    print("=" * W)
    print(f"\n  the pre-fix pattern is DERIVED from the live one, and the")
    print(f"  derivation changes exactly 1 character: "
          f"{r['live_pattern_len']} -> {r['before_pattern_len']}")
    print(f"\n  replies enumerated by the module's own walk : {r['n_replies']}")
    print(f"  the entry states                            : {r['entry_claims_n']}")
    if r["n_replies"] != r["entry_claims_n"]:
        print(f"  THESE DISAGREE by {abs(r['n_replies'] - r['entry_claims_n'])}. "
              f"Whether the population definition\n  changed or the figure was "
              f"wrong cannot be settled from the record.")

    print(f"\n  THE PAIRED TABLE, which is what a before-and-after comparison is:")
    print(f"    verdict gained by the fix (false -> true) : {r['n_gained']}")
    print(f"    verdict lost by the fix   (true -> false) : {r['n_lost']}")
    print(f"    true under both forms                     : {r['both']}")
    print(f"    false under both forms                    : {r['neither']}")
    print(f"    closes: {r['n_gained']} + {r['n_lost']} + {r['both']} + "
          f"{r['neither']} = "
          f"{r['n_gained'] + r['n_lost'] + r['both'] + r['neither']}")
    for lbl in r["gained"]:
        print(f"      gained: {lbl}")
    for lbl in r["lost"]:
        print(f"      LOST  : {lbl}")

    print(f"\n  EXACT McNEMAR on the {r['n_gained'] + r['n_lost']} discordant "
          f"pairs -- the RIGHT test for a paired design:")
    print(f"    p = {r['mcnemar_scipy']:.6e}  (scipy binomtest; an mpmath exact "
          f"tail agrees to {r['mcnemar_gap']:.1e})")

    print(f"\n  FISHER on the unpaired table {r['fisher_table']}, which is what the")
    print(f"  entry's framing implied and is the WRONG test here:")
    print(f"    p = {r['fisher_scipy']:.6e}  (scipy; the module's own mpmath "
          f"route agrees to {r['fisher_gap']:.1e})")
    print(f"\n  NEITHER REPRODUCES 1.108513e-11, and that figure stays withdrawn.")
    print(f"  What is established is the COUNT and its DIRECTION: the fix gains "
          f"{r['n_gained']}\n  verdicts and loses {r['n_lost']}, which is the "
          f"claim the entry rests on.\n")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
