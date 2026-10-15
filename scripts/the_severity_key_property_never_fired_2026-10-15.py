#!/usr/bin/env python3
"""The severity specification's KEY PROPERTY was never exercised by either run.

WHAT SECTION 7.7 SAYS. `Sev(f) = W(class) x confidence x V(verification)` with
`V(True)=1.0, V(None)=0.5, V(False)=0.0`. The appendix's own stated KEY PROPERTY
is that a DISPROVED finding scores ZERO regardless of the model's confidence: a
tool outcome annihilates the model's number. That annihilation is what makes the
specification structurally unlike a vote, and it is the whole reason the founder
asked for it to be promoted out of shadow.

WHAT THE 2 FREE RUNS ACTUALLY EXERCISED. Both runs record a V-census in their
hardened-gate telemetry. Parsed with `ast.literal_eval` rather than by sniping
keys with a regex, because a regex that fails to match a key reports absence and
absence reads like zero:

    run 1 round 3: V_true 15, V_none 7, V_false 0 -> 22, total_findings 22
    run 2 round 3: V_true 14, V_none 5, V_false 0 -> 19, total_findings 19

Both censuses CLOSE against the finding count, so nothing is unaccounted for.
And **0 of 41 findings across both runs carried a disproved verification**, so
the annihilating case never arose.

THE CONSEQUENCE, AND IT SHARPENS A FIGURE ALREADY RECORDED. `crossed_downward`
is empty in both runs, and that now has TWO causes rather than 1: the low base
rate already measured over the archive (7 releases in 2,994 findings, needing
688 findings before a zero is informative), AND the absence of any V_false
finding, without which the specification's distinguishing term cannot bite. So
run 2 establishes that the promoted severity COMPUTES, AGREES and BREAKS
NOTHING -- `critical_spec` equals `critical_asserted` at 12, with 0
`key_property_violations` -- and it does NOT establish that the key property
works, because the input that would trigger it never occurred.

WHAT WOULD ESTABLISH IT. A finding whose falsifier RUNS and REFUTES, which is
V_false. On this target that is scarce for a reason recorded separately as B9:
the confinement guard refuses the falsifier's own review target 18 times per
run, so falsifiers on this target largely cannot reach a verdict at all. **B9
and this are the same gap seen from 2 ends** -- a verification that cannot run
cannot produce the V_false the severity specification needs.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNS = {
    "run1": "free_run1_directive_whole_20261015T061123Z_20261015T061124Z",
    "run2": "free_run2_severity_spec_20261015T073418Z_20261015T073418Z",
}
TELEM = re.compile(r"hardened-gate telemetry: (\{.*?\})\n", re.S)


def census(run_dir: pathlib.Path) -> dict | None:
    log = run_dir / "console.log"
    if not log.exists():
        return None
    blocks = TELEM.findall(log.read_text(encoding="utf-8", errors="replace"))
    for b in reversed(blocks):
        try:
            d = ast.literal_eval(b)
        except (ValueError, SyntaxError):
            continue
        s = d.get("severity_spec_shadow")
        if isinstance(s, dict) and "V_true" in s:
            return {
                "total_findings": d.get("total_findings"),
                "unresolved_critical": d.get("unresolved_critical"),
                "contested": d.get("contested"),
                "mode": d.get("mode"),
                "gamma_crit_settled": d.get("gamma_crit_settled"),
                "V_true": s.get("V_true"), "V_none": s.get("V_none"),
                "V_false": s.get("V_false"),
                "critical_asserted": s.get("critical_asserted"),
                "critical_spec": s.get("critical_spec"),
                "crossed_downward": s.get("crossed_downward"),
                "key_property_violations": s.get("key_property_violations"),
            }
    return None


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp

    out: dict = {}
    print("=" * 78)
    print("1. THE V-CENSUS IN EACH RUN, AND WHETHER IT CLOSES")
    print("=" * 78)
    tot_n = tot_false = 0
    for name, d in RUNS.items():
        c = census(REPO / "bench/logs" / d)
        if not c:
            print(f"  {name}: no gate telemetry carrying a V-census yet")
            continue
        out[name] = c
        s = (c["V_true"] or 0) + (c["V_none"] or 0) + (c["V_false"] or 0)
        closes = s == c["total_findings"]
        tot_n += c["total_findings"] or 0
        tot_false += c["V_false"] or 0
        print(f"\n  {name}: findings={c['total_findings']} unresolved_crit="
              f"{c['unresolved_critical']} contested={c['contested']} mode={c['mode']!r}")
        print(f"    V_true={c['V_true']} V_none={c['V_none']} V_false={c['V_false']} "
              f"-> {s}, closes against the finding count: {closes}")
        print(f"    critical_asserted={c['critical_asserted']} "
              f"critical_spec={c['critical_spec']} "
              f"equal: {c['critical_asserted'] == c['critical_spec']}")
        print(f"    crossed_downward={c['crossed_downward']} "
              f"key_property_violations={c['key_property_violations']}")
        out[name]["census_closes"] = closes

    print()
    print("=" * 78)
    print("2. WAS THE KEY PROPERTY EVER EXERCISED?")
    print("=" * 78)
    print(f"  findings with a DISPROVED verification (V_false): {tot_false} of {tot_n}")
    intervals = {}
    for meth, label in (("wilson", "Wilson"), ("beta", "Clopper-Pearson")):
        lo, hi = proportion_confint(tot_false, tot_n, method=meth)
        intervals[meth] = [lo, hi]
        print(f"    {label:<16} 95% [{lo*100:.4f}%, {hi*100:.4f}%]")
    cp_hi_closed = 1 - 0.025 ** (1 / tot_n)
    mp.mp.dps = 40
    cp_hi_mp = float(1 - mp.power(mp.mpf("0.025"), mp.mpf(1) / tot_n))
    sm_hi = intervals["beta"][1]
    agree = abs(cp_hi_closed - sm_hi) < 1e-9 and abs(cp_hi_mp - sm_hi) < 1e-9
    print(f"    closed form 1 - 0.025^(1/{tot_n}) = {cp_hi_closed*100:.4f}%")
    print(f"    mpmath at 40 digits               = {cp_hi_mp*100:.4f}%")
    print(f"    all 3 routes agree to 1e-9        : {agree}")
    print(f"\n  THE ANNIHILATING CASE NEVER AROSE: {tot_false == 0}")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print("  Run 2 establishes that the promoted severity COMPUTES, AGREES with the")
    print("  asserted critical count, and BREAKS NOTHING -- 0 key-property violations.")
    print("  It does NOT establish that the key property WORKS, because V_false never")
    print("  occurred. `crossed_downward` being empty therefore has 2 causes: the low")
    print("  base rate measured over the archive, AND the absence of any V_false.")
    print()
    print("  AND IT IS THE SAME GAP AS B9 SEEN FROM THE OTHER END: a falsifier that")
    print("  cannot read its own target cannot return a refutation, and a refutation")
    print("  is exactly what V_false is.")

    ok = (tot_n > 0 and all(v.get("census_closes") for v in out.values()) and agree)
    rec = {
        "runs": out,
        "v_false_of_total": [tot_false, tot_n],
        "wilson": intervals["wilson"],
        "clopper_pearson": intervals["beta"],
        "cp_upper_cross_checked_3_ways": agree,
        "key_property_exercised": tot_false > 0,
        "all_assertions_hold": ok,
    }
    dest = REPO / "experimental_notes/evidence/severity_key_property_never_fired_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, indent=2) + "\n")
    print(f"\n  evidence -> {dest.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
