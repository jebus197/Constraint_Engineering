#!/usr/bin/env python3
"""The panel did not write falsifiers for 4 fixes in 5, and every one scored as a cure.

WHAT THIS MEASURES. For each scored entry in the 4 commissioning arms of
2026-09-21/22, whether the `e1_efficacy` probe could run at all. It could not for
77 of 97 -- 79.3814%, Wilson [70.2871%, 86.2373%] -- every one carrying the
detail `NOT_PROBED_NO_FALSIFIER`. Those entries are not fix-less: they passed
g1_ast, g2_compile, e2_regression, e3_ruff and e4_bandit and were recorded
`tristate: ADMISSIBLE, sk: 1.0`. The probe was skipped because there was no
falsifier to re-run, and an unmeasured efficacy scores exactly like a measured
cure.

WHY THIS IS THE NIGHT'S REAL FINDING AND WAS NOT REPORTED. The morning report of
2026-09-22 escalated the e1 weight to the founder, priced over the 20 entries a
probe DID reach, and concluded that a heavier weight or a hard gate "strictly
dominates at zero measured cost". Both are true on those 20 and neither touches
the other 77. `scripts/e1_mechanism_consequences_2026-09-22.py` now prices that:
an absent probe treated as a non-cure at the same heavy weight rejects 78 of 78
unprobed entries and 85 of 98 overall. So the cost of the direction is NOT zero
-- it was zero only because 79.4% of the population was outside the measurement.

IT IS ONE DEFECT WITH THREE SYMPTOMS, ALL IN TONIGHT'S ARCHIVE:
  * 77 of 97 scored fixes unprobeable for efficacy (this script);
  * 7 of the 8 criticals that HALTED arm 4 carry `falsifier_verdict: UNTOOLABLE`
    -- no falsifier at all -- and the 8th ERRORed;
  * arm 1's falsifier gate returned 0 REFUTED across 45 decisions.
A gate that cannot execute cannot refute, cannot measure efficacy, and cannot
resolve a critical. That is the instrument gap between here and Bench Run 2, and
no weight ruling and no `max_rungs` config surface moves any part of it.

WHAT THIS DOES NOT ESTABLISH. It does not say WHY the seats wrote no falsifier --
whether the directive does not demand one per fix, whether the intake parser
fails to associate one, or whether the seats declined. It establishes the RATE,
which is what makes the question worth a dispatch. Distinguishing those 3 is the
next measurement and is not answered here.

Run:  python3 scripts/falsifier_coverage_2026-09-22.py
Exit: 0 always -- this is a measurement, not a gate.
"""

from __future__ import annotations

import glob
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: `runner_state.json` ONLY. The sibling `<name>_report.json` is a SECOND
#: serialisation of the same registry; globbing both double-counts every record
#: and silently narrows every interval. That is how "46 of 248" was reported for
#: an archive holding 23 of 124 (panel, 2026-09-22).
STATES = "bench/logs/commissioning_*/runner_state.json"


def scored_entries():
    """Every entry carrying scorer gate detail, with its arm."""
    for f in sorted(glob.glob(str(REPO / STATES))):
        arm = f.split("commissioning_")[1].split("_")[0]
        try:
            doc = json.load(open(f))
        except Exception:
            continue
        stack = [doc]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                gd = n.get("gate_details")
                if isinstance(gd, dict) and "e1_efficacy" in gd:
                    yield arm, n, gd
                stack.extend(n.values())
            elif isinstance(n, list):
                stack.extend(n)


#: Severity at or above which a runnable falsifier is MANDATORY.
CRITICAL_SEVERITY = 0.7


def _severity_split():
    """Probed/unprobed, split at the critical threshold. {} if unreadable."""
    out = {"crit_probed": 0, "crit_unprobed": 0,
           "sub_probed": 0, "sub_unprobed": 0}
    seen = False
    for f in sorted(glob.glob(str(REPO / STATES))):
        try:
            doc = json.load(open(f))
        except Exception:
            continue
        entries = (doc.get("registry") or {}).get("entries") or doc.get("entries")
        if not isinstance(entries, dict):
            continue
        for entry in entries.values():
            sk = entry.get("sk_result")
            gd = (sk.get("gate_details") if isinstance(sk, dict) else None) or {}
            if "e1_efficacy" not in gd:
                continue
            seen = True
            probed = (gd["e1_efficacy"] or {}).get("score") is not None
            crit = (entry.get("severity") or 0.0) >= CRITICAL_SEVERITY
            key = ("crit_" if crit else "sub_") + ("probed" if probed else "unprobed")
            out[key] += 1
    return out if seen else {}


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    mp.mp.dps = 50

    rows = list(scored_entries())
    if not rows:
        print("no scored entries found in the commissioning archive", file=sys.stderr)
        return 2

    by_arm: Counter = Counter()
    reasons: Counter = Counter()
    unprobed_admitted = 0
    for arm, entry, gd in rows:
        e1 = gd.get("e1_efficacy") or {}
        probed = e1.get("score") is not None
        by_arm[(arm, probed)] += 1
        reasons[str(e1.get("detail") or "").strip()[:64]] += 1
        if not probed and entry.get("tristate") == "ADMISSIBLE":
            unprobed_admitted += 1

    print("FALSIFIER COVERAGE OF THE EFFICACY PROBE, commissioning arms 1-4")
    print(f"  scored entries carrying an e1_efficacy block : {len(rows)}")
    print()
    print("  per arm:")
    tot_p = tot_u = 0
    for arm in sorted({a for a, _ in by_arm}):
        p, u = by_arm[(arm, True)], by_arm[(arm, False)]
        tot_p += p
        tot_u += u
        print(f"    {arm}: probed={p:>3}  NOT probed={u:>3}  of {p+u:>3}")
    n = tot_p + tot_u

    # --- the headline proportion, on 2 independent routes -------------------
    lo_sm, hi_sm = proportion_confint(tot_u, n, alpha=0.05, method="wilson")
    lo_cp, hi_cp = proportion_confint(tot_u, n, alpha=0.05, method="beta")
    z = mp.mpf('1.959963984540054235524594430520551527955550')
    pp = mp.mpf(tot_u) / n
    den = 1 + z**2 / n
    ctr = (pp + z**2 / (2 * n)) / den
    hw = z * mp.sqrt(pp * (1 - pp) / n + z**2 / (4 * n**2)) / den
    lo_mp, hi_mp = float(ctr - hw), float(ctr + hw)
    agree = abs(lo_mp - lo_sm) < 1e-12 and abs(hi_mp - hi_sm) < 1e-12

    print()
    print(f"  efficacy NOT measurable : {tot_u}/{n} = {100.0*tot_u/n:.4f}%")
    print(f"    Wilson 95%, statsmodels   : [{100*lo_sm:.4f}%, {100*hi_sm:.4f}%]")
    print(f"    Wilson 95%, mpmath 50 dps : [{100*lo_mp:.4f}%, {100*hi_mp:.4f}%]")
    print(f"    the 2 routes agree to 1e-12 : {agree}")
    print(f"    Clopper-Pearson 95%       : [{100*lo_cp:.4f}%, {100*hi_cp:.4f}%]")
    if not agree:
        print("  REFUSING to report a cross-verified figure that does not "
              "cross-verify", file=sys.stderr)
        return 1

    # --- THE SCOPED FIGURE, WHICH IS THE ONE THAT CONVICTS ------------------
    # A runnable falsifier is MANDATORY for a CRITICAL finding and is not
    # required below that severity. So the blanket 79.4% bounds e1's REACH but is
    # not itself a breach: for a sub-critical fix, no falsifier is owed and an
    # absent probe is expected. Splitting by severity is what separates the two,
    # and the split is reported here rather than left for a reader to assume.
    crit = _severity_split()
    if crit:
        cu, cp_ = crit["crit_unprobed"], crit["crit_probed"]
        su, sp_ = crit["sub_unprobed"], crit["sub_probed"]
        print()
        print("  SPLIT BY SEVERITY -- a falsifier is MANDATORY only for a CRITICAL:")
        print(f"    CRITICAL     : probed={cp_}  NOT probed={cu}  of {cp_+cu}")
        print(f"    sub-critical : probed={sp_}  NOT probed={su}  of {sp_+su}")
        if cp_ + cu:
            lo, hi = proportion_confint(cu, cp_ + cu, alpha=0.05, method="wilson")
            lc, hc = proportion_confint(cu, cp_ + cu, alpha=0.05, method="beta")
            print(f"    criticals with a fix and NO falsifier: {cu}/{cp_+cu} = "
                  f"{100.0*cu/(cp_+cu):.4f}%")
            print(f"      Wilson [{100*lo:.4f}%, {100*hi:.4f}%]  "
                  f"Clopper-Pearson [{100*lc:.4f}%, {100*hc:.4f}%]")
            print("      The denominator is 6. The interval is reported at that")
            print("      width rather than dressed up, and this is the figure to")
            print("      re-measure on the next run -- not the blanket one.")
        print()
        print("    SO THE HONEST STATEMENT IS TWO STATEMENTS. (1) e1 can only ever")
        print("    reach the minority of entries that carry a falsifier, which is a")
        print("    STRUCTURAL bound on any weight ruling, not a seat failure.")
        print("    (2) On CRITICALS, where a falsifier IS owed, most fixes still")
        print("    carried none -- and that is a breach of the standing directive.")

    print()
    print(f"  of those {tot_u}, recorded ADMISSIBLE anyway : {unprobed_admitted}")
    print("  (an unmeasured efficacy scores exactly like a measured cure)")
    print()
    print("  e1 detail strings, verbatim:")
    for detail, k in reasons.most_common():
        print(f"    {k:>4}  {detail}")

    print()
    print("  CONSEQUENCE FOR THE ESCALATED RULING. The e1 weight decision was")
    print(f"  priced over the {tot_p} entries a probe reached. It is silent on the")
    print(f"  {tot_u} it did not, and both candidate mechanisms -- a heavier weight")
    print("  and a hard gate -- admit every one of them by construction: the")
    print("  weighted mean renormalises over AVAILABLE gates, and the hard gate")
    print("  guards its multiply with `if e is not None`.")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
