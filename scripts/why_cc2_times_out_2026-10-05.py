#!/usr/bin/env python3
"""Why does the cc2 seat time out, and what cap would stop it?

THE OBSERVATION, founder, 2026-10-05: *"CC2 has also timed out a few times
recently. You should probably find out why that is and fix it going forward."*

THE HISTORY IS ALREADY IN THE DISPATCHER, and it is a sequence of raises rather than
a diagnosis. `bench/confer_maths_panel_2026-09-05.py` ~:658 records:

  * 300s was the function default. On 2026-09-06 the cc2 seat failed 3 attempts at
    300s each -- 900s of wall clock producing nothing -- on a brief fable completed
    in 237s. "The seat did not fail on merit; it ran out of clock."
  * raised to 900s, carrying across a fix `experiment_11_orchestrator.py:136` had
    already made for this same seat ("WP4a: 300->900s to prevent CC2 timeout cascade").
  * raised to 1800s on 2026-09-07, because BOTH seats hit the 900s wall with 0 chars.
    "The clock, not the task, was the binding constraint."

So the cap has been raised twice, each time AFTER a loss, and never set from the
observed distribution. This script asks what the distribution actually says.

WHAT IT MEASURES over every archived seat reply carrying `elapsed_s` and `model`:
per-model completion-time distributions, the share that would be lost at each
candidate cap, and whether the two free seats differ. A timeout is not a property of
a seat in isolation -- it is the interaction of a seat's speed with a cap -- so the
useful output is the cap that covers a stated fraction of real work, not a verdict
that one model is "slow".

Cross-verified per the two-tool rule: quantiles from NumPy and from statistics /
scipy, the group comparison by Mann-Whitney (scipy) with an independent rank
computation, and proportions with Wilson intervals from statsmodels and a closed form.

Run:  python3 scripts/why_cc2_times_out_2026-10-05.py
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

#: Caps this dispatcher has used, in order, per its own comment history.
CAP_HISTORY = (300, 900, 1800)
CANDIDATE_CAPS = (900, 1800, 2400, 3000, 3600, 5400)


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="why_cc2_times_out_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--logs", default=str(LOGS), help="bench/logs directory")
    return p.parse_args(argv)


def _wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"), True)
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import norm
    a = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = float(norm.ppf(0.975)); p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (a[0] * 100, a[1] * 100,
            abs(a[0] - (c - h)) < 1e-9 and abs(a[1] - (c + h)) < 1e-9)


def main(argv=None) -> int:
    args = _parse_args(argv)
    import numpy as np
    import statistics
    from scipy import stats

    rows = []
    for p in glob.glob(str(pathlib.Path(args.logs) / "*" / "*.json")):
        try:
            d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or "elapsed_s" not in d:
            continue
        # `elapsed_s` IS NOT ALWAYS A NUMBER. Some records carry a string marker
        # such as 'long-retry'. A float() on it raised and killed the scan, which
        # would have made this measurement impossible to run at all — so the
        # non-numeric values are COUNTED rather than crashed on or dropped
        # silently, since a seat whose duration was replaced by a marker is
        # exactly the population this script is about.
        raw = d.get("elapsed_s")
        try:
            elapsed = float(raw)
            marker = None
        except (TypeError, ValueError):
            elapsed, marker = 0.0, str(raw)
        model = str(d.get("model") or "?")
        route = str(d.get("route") or "?")
        rows.append({
            "round": pathlib.Path(p).parent.name,
            "model": model, "route": route,
            "elapsed": elapsed, "marker": marker,
            "ok": bool(d.get("ok")),
            "chars": int(d.get("chars") or 0),
            "tools": int(d.get("n_tool_calls") or 0),
            "attempts": d.get("attempts"),
        })
    if not rows:
        print("no seat replies found")
        return 1

    print("=" * 78)
    print("WHY THE cc2 SEAT TIMES OUT")
    print("=" * 78)
    markers = [r for r in rows if r.get("marker")]
    print(f"seat replies with a recorded duration : {len(rows)}")
    if markers:
        from collections import Counter
        c = Counter(r["marker"] for r in markers)
        print(f"  of which NON-NUMERIC duration        : {len(markers)}  {dict(c)}")
        print("  (excluded from the distributions below; a marker is not a time)")
    print(f"cap history in the dispatcher         : {CAP_HISTORY} seconds")
    print()

    cli = [r for r in rows if r["route"] == "claude_cli"]
    print(f"of those, dispatched over claude_cli  : {len(cli)}"
          f"  (the 2 free seats, cc2 and fable)")
    by_model = {}
    for r in cli:
        by_model.setdefault(r["model"], []).append(r)

    print()
    print("-" * 78)
    print("COMPLETION TIME BY MODEL, successful replies only")
    print("-" * 78)
    print(f"{'model':<10}{'n':>5}{'median':>9}{'mean':>9}{'p90':>9}{'p95':>9}{'max':>9}"
          f"{'tools/med':>10}")
    dists = {}
    for m, rs in sorted(by_model.items()):
        ok = [r for r in rs if r["ok"] and r["elapsed"] > 0]
        if not ok:
            continue
        xs = np.array([r["elapsed"] for r in ok], dtype=float)
        dists[m] = xs
        # TWO TOOLS for the central value: NumPy and the stdlib.
        med_np = float(np.median(xs)); med_py = float(statistics.median(xs))
        assert abs(med_np - med_py) < 1e-9, f"median disagreement for {m}"
        tl = [r["tools"] for r in ok]
        print(f"{m:<10}{len(xs):>5}{med_np:>9.1f}{xs.mean():>9.1f}"
              f"{float(np.percentile(xs,90)):>9.1f}{float(np.percentile(xs,95)):>9.1f}"
              f"{xs.max():>9.1f}{statistics.median(tl):>10.0f}")

    if len(dists) == 2:
        (ma, xa), (mb, xb) = sorted(dists.items())
        u = stats.mannwhitneyu(xa, xb, alternative="two-sided")
        # independent rank check
        allv = np.concatenate([xa, xb])
        order = stats.rankdata(allv)
        ra = order[:len(xa)].sum()
        u_manual = ra - len(xa) * (len(xa) + 1) / 2
        agree = abs(min(u_manual, len(xa) * len(xb) - u_manual)
                    - min(u.statistic, len(xa) * len(xb) - u.statistic)) < 1e-6
        print()
        print(f"  {ma} vs {mb}: Mann-Whitney U = {u.statistic:.1f}, "
              f"p = {u.pvalue:.6e}")
        print(f"    independent rank computation agrees: {agree}")
        print(f"    median difference: {float(np.median(xa) - np.median(xb)):+.1f} s")
        if u.pvalue < 0.05:
            slower = ma if np.median(xa) > np.median(xb) else mb
            print(f"    => the two seats DIFFER in speed; {slower} is slower.")
        else:
            print("    => no significant speed difference between the seats.")

    print()
    print("-" * 78)
    print("WHAT EACH CANDIDATE CAP WOULD COST, per model")
    print("-" * 78)
    print("A reply is LOST if its real duration exceeds the cap. Successful replies")
    print("are the only evidence of how long real work takes; a timed-out attempt")
    print("records the cap, not the work, so it is censored and excluded here.")
    print("That makes every figure below a LOWER BOUND on the loss.")
    print()
    for m, xs in sorted(dists.items()):
        print(f"  {m} (n={len(xs)})")
        for cap in CANDIDATE_CAPS:
            lost = int((xs > cap).sum())
            lo, hi, ok2 = _wilson(lost, len(xs))
            mark = "   <-- current" if cap == CAP_HISTORY[-1] else ""
            print(f"      cap {cap:>5}s : {lost:>3} of {len(xs)} lost "
                  f"= {100*lost/len(xs):>6.2f}%, Wilson [{lo:.2f}%, {hi:.2f}%]"
                  f"{'' if ok2 else ' *TOOLS DISAGREE*'}{mark}")
        need95 = float(np.percentile(xs, 95))
        need99 = float(np.percentile(xs, 99))
        print(f"      cap needed to cover 95% of observed work: {need95:>7.0f}s")
        print(f"      cap needed to cover 99%:                  {need99:>7.0f}s")
        print()

    print("-" * 78)
    print("RECORDED TIMEOUTS (an attempt whose duration sits at the cap)")
    print("-" * 78)
    at_cap = [r for r in cli if not r["ok"] or r["chars"] == 0]
    _CAP = 12
    for r in sorted(at_cap, key=lambda x: -x["elapsed"])[:_CAP]:
        print(f"  {r['round'][:44]:<44} {r['model']:<8} "
              f"{r['elapsed']:>7.1f}s ok={r['ok']} chars={r['chars']}")
    # A LIST CUT TO N UNDER A HEADING THAT READS AS COMPLETE IS A SILENT
    # FALSEHOOD. `test_no_script_prints_a_capped_listing_in_silence` caught this
    # one, and it matters more here than in most places: the whole argument of
    # this script is about which seats failed and when, so a withheld row is a
    # withheld counter-example.
    if len(at_cap) > _CAP:
        print(f"  (+{len(at_cap) - _CAP} further failed attempt(s) not shown, "
              f"{len(at_cap)} in total; raise _CAP to see them)")
    elif at_cap:
        print(f"  ({len(at_cap)} in total — the whole set is shown above)")
    if not at_cap:
        print("  none recorded in the archived seat files.")
    print()
    print("READING IT. A timeout is the interaction of a seat's speed with a cap,")
    print("not a property of the seat. The cap has been raised twice, each time")
    print("after a loss, and never set from this distribution.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
