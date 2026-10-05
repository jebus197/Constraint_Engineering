#!/usr/bin/env python3
"""Were the convergence blockers ever offered to a model IN-ROUND, or only by the sweep?

THE SETUP. The closing sweep's channels are nearly all reachable inside the round
loop — `scripts/sweep_channels_are_post_verdict_2026-10-05.py` attributes all 5
disposition channels and finds 0 of 5 exclusive to the sweep. Only ONE capability is
sweep-only: the id-addressed `FALSIFIER: Cxxxx` + fenced-code parse, which lets a
model attach a runnable falsifier to ANY residual by name, many in one reply. In-round,
`_extract_routing_falsifier` takes a falsifier only for the single finding the routing
ladder is currently handing out.

SO THE QUESTION IS NOT where the sweep sits. It is whether the in-round machinery
ever OFFERED the blocking findings to a model at all. If routing reached them and
they survived, the sweep's placement is the problem. If routing never reached them,
the sweep is a symptom and the routing reach is the defect.

WHAT THIS MEASURES, on real archived checkpoints: for every finding that was
non-terminal at the convergence point, whether it carries `routing_history`,
`falsifier_code`, `verdicts`, and `computed_evidence`. A finding with none of these
was never put in front of a model by any in-round channel.

Run:  python3 scripts/why_the_blockers_were_never_offered_2026-10-05.py
      python3 scripts/why_the_blockers_were_never_offered_2026-10-05.py --run <dir>
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

TERMINAL = frozenset({"MERGED", "CLOSED", "REFUTED", "DUPLICATE"})
CRITICAL_SEVERITY_THRESHOLD = 0.7


def wilson(k: int, n: int):
    """95% Wilson score interval, as a percentage pair."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / d) * 100.0, min(1.0, (c + m) / d) * 100.0)


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="why_the_blockers_were_never_offered_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--run", default=None,
                   help="a run directory under bench/logs (default: all with a checkpoint)")
    return p.parse_args(argv)


def _findings(state: dict):
    """Registry entries, keyed by canonical id.

    THE PREDICATE WAS WRONG ONCE. `checkpoint.json`'s `all_findings` is a list of
    per-round lists of RAW model findings: it carries no `status`, no
    `routing_history` and no canonical id, so it cannot answer this question at
    all. The deduplicated registry lives in `runner_state.json` under
    `registry.entries`. Measured on study_run1b: 8 round-lists there against 75
    registry entries here.
    """
    reg = state.get("registry")
    if isinstance(reg, dict) and isinstance(reg.get("entries"), dict):
        return reg["entries"]
    return {}


def main(argv=None) -> int:
    args = _parse_args(argv)
    if args.run:
        paths = [pathlib.Path(args.run) / "runner_state.json"]
    else:
        paths = [pathlib.Path(p) for p in sorted(
            glob.glob(str(LOGS / "*" / "runner_state.json")))]
    paths = [p for p in paths if p.is_file()]
    if not paths:
        print("no state found under bench/logs/*/runner_state.json")
        return 1

    print("=" * 78)
    print("WAS A BLOCKING FINDING EVER PUT IN FRONT OF A MODEL IN-ROUND?")
    print("=" * 78)
    print(f"runner_state.json files: {len(paths)}")
    print()

    tot_resid = tot_untouched = 0
    tot_sweeponly = [0]
    tot_crit = tot_crit_untouched = 0
    per_run = []

    for p in paths:
        try:
            state = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ents = _findings(state)
        if not ents:
            continue
        resid = {c: e for c, e in ents.items()
                 if str(e.get("status", "")).upper() not in TERMINAL}
        if not resid:
            continue

        # PROVENANCE MATTERS, AND MY FIRST PREDICATE IGNORED IT. `falsifier_code`
        # and `computed_evidence` are written by the SWEEP as well as in-round
        # (`_post_convergence_sweep` sets falsifier_code at :7476 and records
        # evidence at :7508/:7543). Counting those as "offered in-round" credits
        # the round loop with the sweep's work and understates the gap. Only
        # `routing_history` and `verdicts` are in-round by construction.
        def _offered_in_round(e) -> bool:
            return bool(e.get("routing_history") or e.get("verdicts"))

        def _sweep_only(e) -> bool:
            if _offered_in_round(e):
                return False
            return bool(e.get("resolved_by_sweep") or e.get("withdrawn_by_sweep")
                        or e.get("computed_evidence") or e.get("falsifier_code"))

        _touched = _offered_in_round
        untouched = {c: e for c, e in resid.items() if not _touched(e)}
        crit = {c: e for c, e in resid.items()
                if float(e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD}
        crit_un = {c: e for c, e in crit.items() if not _touched(e)}
        sweeponly = {c: e for c, e in resid.items() if _sweep_only(e)}
        tot_sweeponly[0] += len(sweeponly)

        tot_resid += len(resid)
        tot_untouched += len(untouched)
        tot_crit += len(crit)
        tot_crit_untouched += len(crit_un)
        per_run.append((p.parent.name, (state.get("post_convergence_sweep") or {}).get("rounds", "-"),
                        len(ents), len(resid), len(untouched),
                        len(crit), len(crit_un)))

    print("-" * 78)
    print(f"{'run':<44} {'swp':>4} {'all':>4} {'resid':>5} {'never':>5} {'crit':>4}")
    print("-" * 78)
    for name, conv, n_all, n_res, n_un, n_cr, n_cu in per_run:
        print(f"{name[:44]:<44} {str(conv)[:4]:>4} {n_all:>4} "
              f"{n_res:>5} {n_un:>5} {n_cr:>4}")

    print()
    print("=" * 78)
    print("POOLED")
    print("=" * 78)
    if tot_resid:
        lo, hi = wilson(tot_untouched, tot_resid)
        print(f"residual findings at the stop point      : {tot_resid}")
        print(f"of those, NEVER offered to any model     : {tot_untouched} "
              f"= {100.0 * tot_untouched / tot_resid:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
    if tot_crit:
        lo, hi = wilson(tot_crit_untouched, tot_crit)
        print(f"CRITICAL residuals                       : {tot_crit}")
        print(f"of those, NEVER offered                  : {tot_crit_untouched} "
              f"= {100.0 * tot_crit_untouched / tot_crit:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
    print()
    if tot_resid:
        lo, hi = wilson(tot_sweeponly[0], tot_resid)
        print(f"touched ONLY by the post-verdict sweep   : {tot_sweeponly[0]} "
              f"= {100.0 * tot_sweeponly[0] / tot_resid:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
    print()
    print("READING IT. A residual that was never offered to a model is not evidence")
    print("that the panel failed to resolve it — it is evidence that nothing asked.")
    print("Moving the sweep earlier would not help such a finding unless the thing")
    print("that moves is the OFFER, not the disposition.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
