#!/usr/bin/env python3
"""What would the human-review trigger have done to the runs we already have?

Item 12, his order of 2026-10-11: *"12: Then build it and implement it."* The
condition he set is *"substantial evidence that an experimental run is unlikely to
converge under the given conditions and with the available resources"*, and his
standing constraint is that the HIL queue must not grow unmanageable. A trigger
that fires on runs which went on to converge fails both at once, so the rate is
measured here rather than argued.

THIS SCRIPT PRODUCES EVERY FIGURE QUOTED IN `bench/human_review_trigger.py` and in
the commit that wired it, under `measured-rate-travels-with-its-script`.

THE LABEL, AND ITS LIMITATION STATED PLAINLY. No archived report carries a
convergence field: 0 of 17 have `converged`, `convergence_reached` or
`convergence`. So convergence is DERIVED as "the run stopped short of its own
round cap" -- `len(per_round_counts) < max_rounds`. A run that halts early in this
harness did so because a gate closed; a run that reached its cap did not converge.
The derivation is sound for the cap case and is an INFERENCE for the early case,
because an early stop could in principle be an abort. It is labelled as derived
wherever it is used.

A --help COSTS NOTHING: reads committed JSON, no dispatch, no network.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))


def archived_runs() -> list[dict]:
    """Every archived report carrying BOTH a per-round count series and a cap."""
    out = []
    for f in glob.glob(str(REPO / "bench" / "logs" / "**" / "*report*.json"),
                       recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        prc, mx = d.get("per_round_counts"), d.get("max_rounds")
        if not isinstance(prc, list) or not prc:
            continue
        if not isinstance(mx, int) or mx <= 0:
            continue
        out.append({
            "run": f.split("/")[-2],
            "series": prc,
            "rounds_run": len(prc),
            "max_rounds": mx,
            # DERIVED, not recorded. See the module docstring.
            "converged": len(prc) < mx,
            "has_convergence_field": any(
                d.get(k) is not None
                for k in ("converged", "convergence_reached", "convergence")),
        })
    return out


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] in ("-h", "--help"):
        print(f"usage: {Path(argv[0]).name} [-h|--help]")
        print()
        print(__doc__)
        return 0

    from round_budget import project_optimal_rounds
    import human_review_trigger as HRT
    import reference_runner_v3 as R

    runs = archived_runs()
    cfg = R.RunnerConfig()
    K = cfg.gamma_alt_consecutive_zero_crit
    conv = [r for r in runs if r["converged"]]
    capped = [r for r in runs if not r["converged"]]

    print(f"archived reports with a per-round series AND a cap : {len(runs)}")
    print(f"  carrying an explicit convergence field           : "
          f"{sum(1 for r in runs if r['has_convergence_field'])} of {len(runs)}")
    print(f"  DERIVED converged (stopped short of the cap)     : {len(conv)}")
    print(f"  DERIVED not converged (reached the cap)          : {len(capped)}")
    print(f"  the gate's K (consecutive zero-novel-critical)   : {K}")
    print()

    # ── THE REFUTED DESIGN: trigger when n* exceeds the rounds remaining ──────
    naive_fires_on_converged = 0
    nstars = []
    for r in runs:
        b = project_optimal_rounds(r["series"], theta=1.0)
        if b.n_star is None:
            continue
        nstars.append(b.n_star)
        if b.n_star > (r["max_rounds"] - r["rounds_run"]) and r["converged"]:
            naive_fires_on_converged += 1
    naive_fires_total = sum(
        1 for r in runs
        for b in [project_optimal_rounds(r["series"], theta=1.0)]
        if b.n_star is not None and b.n_star > (r["max_rounds"] - r["rounds_run"]))
    print("REFUTED DESIGN — trigger when n* > rounds remaining:")
    print(f"  n* over the archive ranges {min(nstars):.2f} to {max(nstars):.2f} rounds")
    print(f"  it fires on {naive_fires_total} of {len(runs)} runs")
    print(f"  including {naive_fires_on_converged} of {len(conv)} that CONVERGED "
          f"-- a false-alarm rate of {naive_fires_on_converged}/{len(conv)}")
    print("  REJECTED: convergence here is the two-sided gate on CRITICAL findings,")
    print("  not total yield falling below theta, so n* answers a question the gate")
    print("  does not ask.")
    print()

    # ── WHAT SHIPPED ─────────────────────────────────────────────────────────
    fa = sum(1 for r in conv
             if HRT.assess(r["rounds_run"], r["max_rounds"], K).detail["signal_a"])
    tp = sum(1 for r in capped
             if HRT.assess(r["rounds_run"], r["max_rounds"], K).detail["signal_a"])
    print("WHAT SHIPPED — signal A, the deductive one:")
    print(f"  fires on {fa} of {len(conv)} runs that converged (false alarms)")
    print(f"  fires on {tp} of {len(capped)} runs that reached their cap")
    try:
        from statsmodels.stats.proportion import proportion_confint
        if conv:
            lo, hi = proportion_confint(fa, len(conv), method="wilson")
            print(f"  false-alarm rate Wilson 95% : [{lo:.4f}, {hi:.4f}]")
            print(f"  HONEST CLAIM: {fa} observed in {len(conv)}, NOT a demonstrated")
            print(f"  low rate -- {len(conv)} is a small denominator and the interval says so.")
    except ImportError:                                          # pragma: no cover
        print("  (statsmodels absent; interval not computed)")
    print()
    print("per-run detail:")
    print(f"  {'run':<38} {'ran':>4} {'cap':>4} {'converged*':>11} {'A':>5}")
    for r in sorted(runs, key=lambda x: -x["rounds_run"]):
        a = HRT.assess(r["rounds_run"], r["max_rounds"], K).detail["signal_a"]
        print(f"  {r['run'][:38]:<38} {r['rounds_run']:>4} {r['max_rounds']:>4} "
              f"{str(r['converged']):>11} {str(a):>5}")
    print("  * DERIVED from stopping short of the cap, not read from a field.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
