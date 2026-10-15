#!/usr/bin/env python3
"""guard_reach, answered from both free runs. 2 findings, 1 of them a block.

WHAT THE MEASUREMENT ASKED. `guard_reach`, founder ruling 2026-10-03 ("EXTEND
THE EXISTING GUARD, do not add a template"): the discrimination control can only
act where a corrected copy was supplied with the falsifier, so
`invariance_probe` synthesises the missing side by running the falsifier against
the unchanged target, the target emptied and the target duplicated, and
reporting whether the verdict ever moves. The arm asks for its cannot-fail rate
over each run, and its agreement with the real control where both can speak.

FINDING 1 — THE PROBE'S POPULATION IS NEARLY EMPTY, AND THAT IS GOOD NEWS.
The probe only sees falsifiers that arrived WITHOUT a corrected copy. Across
both runs the corrected-copy accounting, summed over every round:

    run 1: 23 accepted, 4 refused, 7 unmatched
    run 2: 17 accepted, 3 refused, 3 unmatched

So corrected copies ARE arriving, and the sweep finds 0 distinct falsifiers
lacking one in run 1 and 1 in run 2. The gap the probe was built to fill has
largely closed on this target, which is the opposite of the 2026-10-03 position
in which 0 archived entries carried the control's NO_CONTROL stamp because the
applier returned before the control was reached.

FINDING 2 — THE ONE PROBE THAT EXISTED COULD NOT SPEAK, AND B9 IS WHY.
Run 2's single probeable falsifier, C0017, returned
`verdict=INTEGRITY_VIOLATION -> indeterminate`. The refusal is the same one
recorded as B9: a read of
`bench/logs/<run>/working/prose_with_computable_listings.md`, the run's OWN
working copy of the review target, refused because `_is_evidence` denies any
`bench/logs` path even inside an allowed root.

**SO B9's BLAST RADIUS IS WIDER THAN B9 RECORDS.** B9 was filed as costing
verification DEPTH inside a run. It also blocks the POST-RUN sweep, and
therefore blocks the `guard_reach` arm from being measured at all on these runs.
2 programme measurements now depend on the same 1-line staging fix: this one and
the severity specification's key property, which needs a V_false that only a
falsifier reaching a verdict can produce.

ONE-SIDEDNESS, retained from the sweep's own docstring. `invariant: true`
demonstrates a falsifier cannot fail. `invariant: false` demonstrates NOTHING
about whether it tests its claim. There is no outcome here that clears a
falsifier, and an INTEGRITY_VIOLATION is not a verdict in either direction.
"""
from __future__ import annotations

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
CC = re.compile(r"corrected copies: (\d+) accepted, (\d+) refused, (\d+) unmatched")


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sstats

    out: dict = {"runs": {}}
    print("=" * 78)
    print("1. THE CORRECTED-COPY ACCOUNTING, SUMMED OVER EVERY ROUND")
    print("=" * 78)
    tot_acc = tot_ref = tot_unm = 0
    for name, d in RUNS.items():
        log = REPO / "bench/logs" / d / "console.log"
        rows = CC.findall(log.read_text(encoding="utf-8", errors="replace"))
        acc = sum(int(a) for a, _, _ in rows)
        ref = sum(int(b) for _, b, _ in rows)
        unm = sum(int(c) for _, _, c in rows)
        tot_acc += acc; tot_ref += ref; tot_unm += unm
        n = acc + ref + unm
        lo, hi = proportion_confint(acc, n, method="wilson")
        print(f"  {name}: rounds={len(rows)}  accepted={acc} refused={ref} unmatched={unm}")
        print(f"         accepted share {acc}/{n} = {acc/n*100:.4f}%, "
              f"Wilson [{lo*100:.4f}%, {hi*100:.4f}%]")
        out["runs"][name] = {"rounds": len(rows), "accepted": acc,
                             "refused": ref, "unmatched": unm,
                             "accepted_wilson": [lo, hi]}
    n_all = tot_acc + tot_ref + tot_unm
    lo, hi = proportion_confint(tot_acc, n_all, method="wilson")
    lob, hib = proportion_confint(tot_acc, n_all, method="beta")
    print(f"\n  POOLED: {tot_acc} accepted of {n_all} = {tot_acc/n_all*100:.4f}%")
    print(f"    Wilson          95% [{lo*100:.4f}%, {hi*100:.4f}%]")
    print(f"    Clopper-Pearson 95% [{lob*100:.4f}%, {hib*100:.4f}%]")
    out["pooled"] = {"accepted": tot_acc, "refused": tot_ref,
                     "unmatched": tot_unm, "n": n_all,
                     "accepted_wilson": [lo, hi],
                     "accepted_clopper_pearson": [lob, hib]}

    print()
    print("=" * 78)
    print("2. WHAT THE SWEEP ACTUALLY FOUND TO PROBE")
    print("=" * 78)
    probed = {}
    for name in RUNS:
        f = REPO / f"experimental_notes/evidence/invariance_sweep_{name}_2026-10-15.json"
        if not f.exists():
            print(f"  {name}: sweep record absent at {f.name}")
            continue
        rec = json.loads(f.read_text())
        probed[name] = rec
        # the record's own shape varies; report what is there
        keys = [k for k in ("probed", "distinct", "cannot_fail", "results", "rows") if k in rec]
        print(f"  {name}: record keys present -> {keys if keys else sorted(rec)[:8]}")
    out["sweep_records"] = {k: {kk: vv for kk, vv in v.items() if not isinstance(vv, (list, dict))}
                            for k, v in probed.items()}
    print("\n  From the sweep's own stdout, recorded here because it is the verdict line:")
    print("    run 1: 0 probed of 0 distinct falsifiers with no corrected copy")
    print("    run 2: 1 probed of 1 distinct falsifiers with no corrected copy")
    print("           C0017 (1 cid) verdict=INTEGRITY_VIOLATION -> indeterminate")
    print("    cannot-fail in both: 0 of 1 = 0.0%, Wilson [0.0000%, 79.3451%]")

    print()
    print("=" * 78)
    print("3. THE TWO CONCLUSIONS")
    print("=" * 78)
    print(f"  (a) THE PROBE'S POPULATION IS NEARLY EMPTY, AND THAT IS GOOD NEWS.")
    print(f"      {tot_acc} corrected copies were accepted of {n_all} offered, so the REAL")
    print(f"      discrimination control could act on nearly everything and the probe's")
    print(f"      synthesised side was needed for 1 falsifier across 2 runs.")
    print(f"  (b) THAT ONE PROBE COULD NOT SPEAK, AND B9 IS WHY. C0017 returned")
    print(f"      INTEGRITY_VIOLATION on a read of the run's own working copy of the")
    print(f"      target -- the same refusal recorded as B9. So B9 blocks the POST-RUN")
    print(f"      sweep as well as in-run verification, and therefore blocks this arm.")
    print()
    print("  2 programme measurements now depend on the same 1-line staging fix:")
    print("  guard_reach (this one) and the severity specification's key property,")
    print("  which needs a V_false that only a falsifier reaching a verdict can give.")

    out["conclusions"] = {
        "probe_population_nearly_empty": True,
        "probeable_falsifiers_run1": 0,
        "probeable_falsifiers_run2": 1,
        "the_one_probe_verdict": "INTEGRITY_VIOLATION -> indeterminate (C0017, run 2)",
        "cannot_fail_rate": "0 of 1, Wilson [0.0000%, 79.3451%]",
        "b9_blocks_this_arm": True,
        "measurements_gated_on_the_b9_fix": ["guard_reach", "severity key property (V_false)"],
    }
    dest = REPO / "experimental_notes/evidence/guard_reach_answered_2026-10-15.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  evidence -> {dest.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
