# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_quiet_run_is_not_the_lever_2026-10-25', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b9de54ea52044566d338213e1e5dee90723cc3e3ed5c9e996c9618744bbdcb85
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The quiet arm fires ONCE per run, so a per-window rate cannot price it.

WHAT THIS CORRECTS, and it is a correction to BOTH prior producers.

`bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py` computes
P(K quiet rounds | criticals demonstrably remained) over WINDOW POSITIONS.
`bench/what_should_the_quiet_run_be_2026-10-25.py` corrects the conditioning
direction and computes P(criticals remained | K quiet rounds) -- also over
WINDOW POSITIONS. Both denominators count every position in a report at which
the condition held.

THE LIVE GATE DOES NOT WORK THAT WAY. `reference_runner_v3.py` evaluates the
conjunction at the end of each round and, when it fires, the run CLOSES. So at
most ONE window position per run is ever reached. Every position after a run's
FIRST firing position is counterfactual: in a live run it does not exist,
because the run already ended. Counting those positions is not a stricter
measurement of the same thing -- it changes the estimand, and it changes it in
a K-dependent direction, because a long quiet tail contributes many positions
at small K and the run that generated it closed at the first one.

THE ESTIMAND THAT PRICES THE GATE is therefore one Bernoulli trial per run:

    fire(run, K)      = the first round index i with round number >=
                        gamma_alt_earliest_round at which rounds i-K+1 .. i all
                        had zero novel criticals
    premature(run, K) = fire(run, K) exists AND some round after i raised a
                        novel critical

    first_fire_rate(K) = |{runs : premature}| / |{runs : fire exists}|

One run, one trial, which also makes the Wilson interval admissible: the
per-window denominators are strongly dependent within a report (a run with a
10-round quiet tail contributes 8 overlapping positions at K=3), so a binomial
interval on 182 or on 63 positions is narrower than the evidence supports.

AND IT PRICES THE PROPOSED REPLACEMENT ON THE SAME RULER. The brief of
2026-10-25 recommends replacing the constant with the arrival-curve rule. That
rule is scored here by the identical first-firing construction, so the 2 are
comparable. The result decides that recommendation; it is not asserted.

NOTHING HERE CHANGES A DEFAULT. This file is a measurement.

USAGE
    python3 bench/the_gate_fires_once_per_run_2026-10-25.py
    python3 bench/the_gate_fires_once_per_run_2026-10-25.py --figures
    python3 bench/the_gate_fires_once_per_run_2026-10-25.py --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The collector is LOADED FROM THE OTHER PRODUCER, not retyped, so this file
#: reads exactly the same 63 reports with the same field names and the same
#: severity cut. Retyping it would make any disagreement unattributable. The
#: module name contains hyphens, so an `import` statement cannot bind it and the
#: load has to go through importlib by path.
_SRC = REPO / "bench" / "what_should_the_quiet_run_be_2026-10-25.py"


def _load_collector():
    spec = importlib.util.spec_from_file_location("wsqrb_2026_10_25", _SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: `RunnerConfig.gamma_alt_earliest_round` in `bench/reference_runner_v3.py`.
#: The gate may not fire before this round whatever the quiet run is, so a
#: first-firing measurement that ignored it would credit the gate with closes it
#: is forbidden to make.
EARLIEST_ROUND = 3

K_GRID = tuple(range(3, 10))


def wilson(k: int, n: int):
    if n == 0:
        return None
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 6), round(min(1.0, c + h), 6)]


def first_fire(recs, k: int, earliest: int = EARLIEST_ROUND):
    """(fire_index, premature) for one run, or (None, None) if it never fires.

    `recs` is the collector's list of (round_number, n_responded, n_raising,
    gamma) sorted by round. `n_raising` is the number of responding seats that
    raised a critical first opened in that round, so a round is quiet exactly
    when it is 0.
    """
    for i in range(k - 1, len(recs)):
        if recs[i][0] < earliest:
            continue
        if any(recs[j][2] != 0 for j in range(i - k + 1, i + 1)):
            continue
        return i, any(h > 0 for _, _, h, _ in recs[i + 1:])
    return None, None


def arrival_first_fire(recs, floor: float = 0.25, min_rounds: int = 3,
                       earliest: int = EARLIEST_ROUND):
    """The arrival-curve rule, scored by the SAME first-firing construction.

    The fit is the brief's own: a least-squares line through log1p(n_raising)
    over rounds 0..i, stopping at the first i whose predicted next-round value
    falls under `floor`. Reproduced here rather than called because the original
    returns a round NUMBER and this needs the INDEX, to see what came after.
    """
    if len(recs) < min_rounds:
        return None, None
    ys = [math.log1p(h) for _, _, h, _ in recs]
    for i in range(min_rounds - 1, len(recs)):
        if recs[i][0] < earliest:
            continue
        xs = list(range(i + 1))
        yy = ys[:i + 1]
        n = len(xs)
        mx = sum(xs) / n
        my = sum(yy) / n
        var = sum((x - mx) ** 2 for x in xs)
        if var == 0:
            continue
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, yy)) / var
        if math.expm1(my + slope * (n - mx)) < floor:
            return i, any(h > 0 for _, _, h, _ in recs[i + 1:])
    return None, None


def max_quiet_run(recs) -> int:
    """Longest run of consecutive zero-novel-critical rounds in one report.

    This decides whether K=7's zero is safety or non-occurrence: if no report
    anywhere reaches 7, the K=7 row of either per-window table has an empty
    condition, and its 0 is the numerator of a conditional that never fires
    rather than a measured absence of premature closes.
    """
    best = cur = 0
    for _, _, h, _ in recs:
        cur = cur + 1 if h == 0 else 0
        best = max(best, cur)
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--figures", action="store_true")
    a = ap.parse_args()

    wsqrb = _load_collector()
    base = wsqrb.collect(wsqrb.LIVE_CRITICAL)
    res = {"reports": len(base), "earliest_round": EARLIEST_ROUND,
           "severity_cut": wsqrb.LIVE_CRITICAL}

    # THE ARCHIVE CAN BE ABSENT, and was: `bench/logs` was pruned mid-session on
    # 2026-10-25 and the recursive glob both producers depend on returned 0
    # files afterwards, after this file's figures had already been taken. A
    # measurement tool that tracebacks on an empty corpus is worse than one that
    # says the corpus is empty, because a traceback reads as a broken tool
    # rather than as missing data. The exit code is non-zero so a caller cannot
    # mistake it for a measurement of zero.
    if not base:
        print("ARCHIVE ABSENT: the recursive glob for bench/logs/**/*report*.json "
              "matched 0 readable reports, so nothing here is measurable. This is "
              "missing data, NOT a measured zero. The figures in this file's "
              "docstring and in bench/reference_runner_v3.py were taken on "
              "2026-10-25 against 63 reports; re-executing them needs that "
              "archive restored.", file=sys.stderr)
        return 2

    mq = [max_quiet_run(r["rounds"]) for r in base]
    lens = [len(r["rounds"]) for r in base]
    res["reachability"] = {
        "max_quiet_run_observed_anywhere": max(mq),
        "reports_with_a_quiet_run_of_at_least": {
            k: sum(1 for x in mq if x >= k) for k in K_GRID},
        "reports_with_fewer_than_k_usable_rounds": {
            k: sum(1 for n in lens if n < k) for k in K_GRID},
        "reports_long_enough_for_7_rounds": sum(1 for n in lens if n >= 7),
        "of_those_reaching_a_7_quiet_run": sum(
            1 for n, x in zip(lens, mq) if n >= 7 and x >= 7),
    }

    rows = {}
    for k in K_GRID:
        fired = prem = 0
        stops = []
        for rep in base:
            i, later = first_fire(rep["rounds"], k)
            if i is None:
                continue
            fired += 1
            prem += bool(later)
            stops.append(rep["rounds"][i][0])
        rows[k] = {"runs_where_it_fires": fired, "premature": prem,
                   "rate": round(prem / fired, 6) if fired else None,
                   "wilson": wilson(prem, fired),
                   "runs_where_it_never_fires": len(base) - fired,
                   "mean_stop_round": round(sum(stops) / len(stops), 4) if stops else None}
    res["first_fire_by_k"] = rows

    fired = prem = 0
    stops = []
    for rep in base:
        i, later = arrival_first_fire(rep["rounds"])
        if i is None:
            continue
        fired += 1
        prem += bool(later)
        stops.append(rep["rounds"][i][0])
    res["arrival_rule"] = {
        "runs_where_it_fires": fired, "premature": prem,
        "rate": round(prem / fired, 6) if fired else None,
        "wilson": wilson(prem, fired),
        "runs_where_it_never_fires": len(base) - fired,
        "mean_stop_round": round(sum(stops) / len(stops), 4) if stops else None,
        "median_stop_round": sorted(stops)[len(stops) // 2] if stops else None,
    }

    tot_findings = sum(len(r["finding_freqs"]) for r in base)
    tot_raising = sum(h for r in base for _, _, h, _ in r["rounds"])
    f1 = sum(1 for r in base for x in r["finding_freqs"] if x == 1)
    res["what_the_churn_figure_counts"] = {
        "critical_findings_in_the_registries": tot_findings,
        "sum_of_n_raising_over_all_rounds": tot_raising,
        "note": "n_raising counts SEATS raising a novel critical in a round, "
                "capped at the roster size -- not the number of criticals. The "
                "churn figures are seat-rounds per round, and 2 seats raising "
                "the same finding counts 2.",
        "findings_raised_by_exactly_one_seat": f1,
        "good_turing_f1_over_n": round(f1 / tot_findings, 6) if tot_findings else None,
    }

    if a.figures:
        rr = res["reachability"]
        print(f"reports = {res['reports']}")
        print(f"max_quiet_run_observed_anywhere = "
              f"{rr['max_quiet_run_observed_anywhere']}")
        print(f"reports_reaching_a_quiet_run_of_7 = "
              f"{rr['reports_with_a_quiet_run_of_at_least'][7]}")
        print(f"reports_shorter_than_7_rounds = "
              f"{rr['reports_with_fewer_than_k_usable_rounds'][7]} of {res['reports']}")
        for k in (3, 5, 7):
            r = rows[k]
            print(f"first_fire_k{k} = {r['premature']} of "
                  f"{r['runs_where_it_fires']} = {r['rate']} wilson {r['wilson']}")
        ar = res["arrival_rule"]
        print(f"arrival_rule_first_fire = {ar['premature']} of "
              f"{ar['runs_where_it_fires']} = {ar['rate']} wilson {ar['wilson']}")
        print(f"arrival_rule_mean_stop_round = {ar['mean_stop_round']}")
        w = res["what_the_churn_figure_counts"]
        print(f"critical_findings = {w['critical_findings_in_the_registries']}")
        print(f"good_turing_f1 = {w['findings_raised_by_exactly_one_seat']}")
        print(f"good_turing_f1_over_n = {w['good_turing_f1_over_n']}")
        return 0
    if a.json:
        print(json.dumps(res, indent=2, default=str))
        return 0

    rr = res["reachability"]
    print(f"\n  {res['reports']} reports, severity cut {res['severity_cut']}, "
          f"gate forbidden before round {EARLIEST_ROUND}\n")
    print("  1. IS A QUIET RUN OF K REACHABLE IN THIS ARCHIVE AT ALL?")
    print(f"     longest quiet run observed anywhere: "
          f"{rr['max_quiet_run_observed_anywhere']}")
    print(f"     {'K':>3}  {'reports reaching it':>20}  {'reports too short':>18}")
    for k in K_GRID:
        print(f"     {k:>3}  {rr['reports_with_a_quiet_run_of_at_least'][k]:>20}  "
              f"{rr['reports_with_fewer_than_k_usable_rounds'][k]:>18}")
    print(f"     reports long enough to HOLD a 7-window: "
          f"{rr['reports_long_enough_for_7_rounds']}; of those, reaching one: "
          f"{rr['of_those_reaching_a_7_quiet_run']}")

    print("\n  2. FIRST-FIRING PREMATURE RATE -- one trial per run, which is all")
    print("     the trials the live gate ever gets")
    print(f"     {'K':>3}  {'premature/fires':>16}  {'rate':>9}  "
          f"{'Wilson':>22}  {'never fires':>11}  {'mean stop':>9}")
    for k in K_GRID:
        r = rows[k]
        frac = f"{r['premature']}/{r['runs_where_it_fires']}"
        print(f"     {k:>3}  {frac:>16}  {str(r['rate']):>9}  "
              f"{str(r['wilson']):>22}  {r['runs_where_it_never_fires']:>11}  "
              f"{str(r['mean_stop_round']):>9}")

    ar = res["arrival_rule"]
    print("\n  3. THE PROPOSED REPLACEMENT ON THE SAME RULER")
    print(f"     arrival-curve rule: {ar['premature']}/{ar['runs_where_it_fires']} "
          f"= {ar['rate']}  Wilson {ar['wilson']}  "
          f"mean stop round {ar['mean_stop_round']}  "
          f"never fires on {ar['runs_where_it_never_fires']}")

    w = res["what_the_churn_figure_counts"]
    print("\n  4. WHAT THE CHURN FIGURE COUNTS")
    print(f"     critical findings in the registries: "
          f"{w['critical_findings_in_the_registries']}")
    print(f"     sum of n_raising over all rounds:    "
          f"{w['sum_of_n_raising_over_all_rounds']}")
    print(f"     {w['note']}")
    print(f"     f1 = {w['findings_raised_by_exactly_one_seat']}, "
          f"f1/n = {w['good_turing_f1_over_n']}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
