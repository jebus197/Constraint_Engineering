#!/usr/bin/env python3
"""Across the 3 shakedown legs, how many adjudications were made by a TOOL?

WHY THIS SCRIPT EXISTS. Task entry B20 carried the figure "77 of 79
adjudications were tool-made rather than assertion-made, 97.4684%, Wilson
[91.2314%, 99.3030%]" with NO producer named. The project's rule is that a
measured rate may be cited only if the script that produced it is committed
alongside it: a number that exists solely as prose in a tracker is not evidence,
it is a claim about evidence. The commit-time check
`scripts/overstated_entries_2026-09-11.py` caught B20 as the one entry in the
list carrying a figure with no producer.

THE POPULATION. The 3 legs of the shakedown, by their log directories:
`free_run1_directive_whole`, `free_run2_severity_spec` and
`leg3_final_shakedown` -- 22, 19 and 38 registry entries, totalling 79, which is
the denominator the figure quotes.

WHAT COUNTS AS TOOL-MADE. Each entry records `status_adjudicator` and
`status_mechanism`. An adjudication is TOOL-MADE when the thing that settled it
was executable -- a falsifier verdict, an S_k computation, a discrimination
control -- and ASSERTION-MADE when it was a model saying so. The two are read
off the recorded fields rather than inferred from the description, and every
distinct value found is printed, so a value this script does not recognise
cannot be silently bucketed as either.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

LEGS = ("free_run1_directive_whole_20261015T061123Z_20261015T061124Z",
        "free_run2_severity_spec_20261015T073418Z_20261015T073418Z",
        "leg3_final_shakedown_20261015T220118Z")

#: Mechanisms that are EXECUTABLE. Listed explicitly so that an unrecognised
#: value is reported rather than bucketed.
TOOL_MECHANISMS = {
    "falsifier", "falsifier_verdict", "sk", "s_k", "sk_result",
    "discrimination", "discrimination_control", "tool", "computed",
    "computed_evidence", "verifier", "regression", "test",
}
ASSERTION_MECHANISMS = {
    "assertion", "model", "panel", "quorum", "vote", "seat", "consensus",
    "merge", "confirm",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    per_leg = {}
    mech = collections.Counter()
    adj = collections.Counter()
    tool = assertion = unknown = 0
    unknown_values = collections.Counter()
    total = 0

    for leg in LEGS:
        rs = LOGS / leg / "runner_state.json"
        if not rs.is_file():
            print(f"MISSING: {rs}")
            return 2
        ents = (json.loads(rs.read_text(errors="replace"))
                .get("registry") or {}).get("entries") or {}
        per_leg[leg] = len(ents)
        total += len(ents)
        for e in ents.values():
            if not isinstance(e, dict):
                continue
            m = str(e.get("status_mechanism") or "").strip().lower()
            ad = str(e.get("status_adjudicator") or "").strip().lower()
            mech[m or "(empty)"] += 1
            adj[ad or "(empty)"] += 1
            # THE RECORDED ADJUDICATOR IS THE AUTHORITY, and a first version of
            # this script got that wrong. It treated any entry carrying a
            # falsifier verdict or computed evidence as tool-made, which
            # returned 79 of 79 and FAILED to reproduce B20's 77. The record is
            # unambiguous: `status_adjudicator` reads "tool" on 77 entries and
            # "runner" on 2, and those same 2 carry the mechanism
            # "model_confirm_quorum (3/1 independent)" -- settled by a quorum of
            # models asserting, not by anything executable. Carrying a tool's
            # output is not the same as having been DECIDED by one, and the
            # broader predicate erased exactly the distinction the figure is
            # about.
            if ad == "tool":
                tool += 1
            elif ad:
                assertion += 1
                unknown_values[f"adjudicator={ad!r} mechanism={m!r}"] += 1
            else:
                unknown += 1
                unknown_values[(m or "(both empty)")] += 1

    print("THE 3 SHAKEDOWN LEGS")
    for leg, n in per_leg.items():
        print(f"  {leg[:52]:<52} {n:>3} entries")
    print(f"  {'TOTAL':<52} {total:>3} entries")
    print()
    print(f"tool-made adjudications ...... {tool}")
    print(f"assertion-made ............... {assertion}")
    print(f"unrecognised ................. {unknown}")
    if unknown_values and not a.quiet:
        print("  every NON-tool adjudication, named rather than bucketed:")
        for k, v in unknown_values.most_common():
            print(f"    {v:>3}  {k!r}")
    if not a.quiet:
        print()
        print("  status_mechanism values found:")
        for k, v in mech.most_common():
            print(f"    {v:>3}  {k!r}")
        print("  status_adjudicator values found:")
        for k, v in adj.most_common():
            print(f"    {v:>3}  {k!r}")

    denom = tool + assertion + unknown
    print()
    if denom:
        try:
            from statsmodels.stats.proportion import proportion_confint
            lo, hi = proportion_confint(tool, denom, method="wilson")
            blo, bhi = proportion_confint(tool, denom, method="beta")
            print(f"tool-made rate: {tool} of {denom} = {100*tool/denom:.4f}%")
            print(f"  Wilson          [{lo*100:.4f}%, {hi*100:.4f}%]")
            print(f"  Clopper-Pearson [{blo*100:.4f}%, {bhi*100:.4f}%]")
            import mpmath as mp
            mp.mp.dps = 30
            z = mp.mpf("1.959963984540054235524594430520")
            p = mp.mpf(tool) / denom
            c = z * z / denom
            m2lo = (p + c/2 - z*mp.sqrt(p*(1-p)/denom + c/(4*denom)))/(1+c)
            m2hi = (p + c/2 + z*mp.sqrt(p*(1-p)/denom + c/(4*denom)))/(1+c)
            print(f"  mpmath Wilson   [{float(m2lo)*100:.4f}%, {float(m2hi)*100:.4f}%]"
                  f"  (agrees to {abs(float(m2hi)-hi):.1e})")
        except Exception as exc:                        # noqa: BLE001
            print(f"  interval unavailable: {exc}")
    print()
    print(f"B20 QUOTED: 77 of 79 = 97.4684%, Wilson [91.2314%, 99.3030%]")
    print(f"THIS SCRIPT: {tool} of {denom}"
          f" = {100*tool/denom:.4f}%" if denom else "no entries")
    print(f"REPRODUCES: {'YES' if (tool, denom) == (77, 79) else 'NO'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
