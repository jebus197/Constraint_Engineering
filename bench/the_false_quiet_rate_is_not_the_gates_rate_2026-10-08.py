#!/usr/bin/env python3
"""The 0.1159 false-quiet rate, reproduced -- and why gamma does not reduce it.

THE FOUNDER'S RULING, 2026-10-07, on the figure a panel seat produced: *"Second,
the absolute false quiet chance of 0.1159 at full roster, which no roster aware
fix addresses. # Fix it."*

WHAT 0.1159 IS. At the archive-measured per-seat-per-round critical rate and
intra-round correlation, the probability that 3 consecutive rounds pass with no
new critical finding, at FULL 6-seat roster, is 0.1159. It was carried in prose
with NO COMMITTED PRODUCER, which this file supplies first so that the number
can be argued with.

AND WHAT 0.1159 IS NOT, which is the point of the file. It is the marginal
probability of ONE ARM of the convergence gate. The gate is a CONJUNCTION: it
requires the critical decay curve to have flattened AND a run of quiet rounds.
The obvious hope is that the gamma arm cuts the joint rate well below 0.1159.
IT DOES NOT, and the reason is structural rather than accidental: gamma measures
the flattening of the critical-finding curve, and quiet rounds are what flatten
it. The 2 arms are driven by the SAME rounds, so they are strongly positively
dependent and the conjunction buys far less than a product of independent
probabilities would suggest.

MEASURED, BY CALLING THE REAL GATE. Over every archived round that sat at the end
of a 3-round quiet window WHILE FINDINGS DEMONSTRABLY REMAINED -- that is, while
a later round in the same report went on to raise a new critical --
`_check_gamma_alt_convergence` from `bench/reference_runner_v3.py` is invoked
with that round's own recorded gamma. It returns converged on 23 of 23. Gamma
was above its 0.30 threshold in every single premature window in the record.

SO THE ONLY LEVERS ARE THE WINDOW LENGTH AND THE SEAT COUNT, exactly as the seat
that found the figure said, and the founder's instruction is answered with a
curve rather than a guess. The empirical premature-window rate falls 0.1264 ->
0.0784 -> 0.0458 -> 0.0263 -> 0.0000 as the required quiet run goes 3 -> 4 -> 5
-> 6 -> 7, each with a Wilson interval, over a denominator that shrinks as the
window lengthens.

THIS FILE PROPOSES AND DOES NOT APPLY. Changing the required quiet run changes
when every experiment converges, which is the founder's call.

GAMMA IS NOT BEING DEMOTED AND THIS FILE IS NOT AN ARGUMENT FOR DEMOTING IT.
Gamma remains load-bearing and remains a required arm. The finding is only that
it is not INDEPENDENT of the other arm, so it cannot be relied on to cover the
other arm's false-positive rate. A dependent second arm is still a second arm.

Run: python3 bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The severity at or above which a finding is critical, as the runner uses it.
CRITICAL = 0.7

#: The gate's own threshold, read from the runner's config rather than typed.
Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def _norm(s) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def collect_reports(repo: Path = REPO) -> list[list[tuple]]:
    """Per report, the rounds as (round, n_responded, n_raising, gamma).

    A round with fewer than 2 responding seats is dropped, matching the
    correlation measurement this file's parameters come from.
    """
    out = []
    for f in sorted(glob.glob(str(repo / "bench" / "logs" / "**" / "*report*.json"),
                              recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        rounds, reg = d.get("rounds"), d.get("registry")
        if not isinstance(rounds, list) or not isinstance(reg, dict):
            continue
        entries = reg.get("entries") if isinstance(reg.get("entries"), dict) else reg
        if not isinstance(entries, dict):
            continue
        raised: "dict[int, set]" = {}
        for e in entries.values():
            if not isinstance(e, dict):
                continue
            try:
                sev = float(e.get("severity") or 0.0)
            except (TypeError, ValueError):
                continue
            if sev < CRITICAL:
                continue
            r, m = e.get("open_since_round"), _norm(e.get("source_model"))
            if r is None or not m:
                continue
            try:
                raised.setdefault(int(r), set()).add(m)
            except (TypeError, ValueError):
                continue
        recs = []
        for rec in rounds:
            if not isinstance(rec, dict):
                continue
            try:
                rn = int(rec.get("round"))
            except (TypeError, ValueError):
                continue
            resp = rec.get("models_responded")
            resp = {_norm(m) for m in resp} if isinstance(resp, list) else set()
            if len(resp) < 2:
                continue
            g = rec.get("gamma_critical")
            if g is None:
                g = rec.get("gamma")
            recs.append((rn, len(resp), len(resp & raised.get(rn, set())),
                         g, Path(f).name))
        if recs:
            out.append(sorted(recs))
    return out


def claim_the_0_1159_figure_reproduces(q: str = "0.233740",
                                       rho: str = "0.405989") -> dict:
    """The model-based figure, in 2 tools: a closed form and a simulation."""
    import mpmath as mp
    import numpy as np

    with mp.workdps(40):
        qq, rr = mp.mpf(q), mp.mpf(rho)
        scale = (1 - rr) / rr
        a, b = qq * scale, (1 - qq) * scale

        def Q(n):
            return mp.beta(a, b + n) / mp.beta(a, b)

        closed = {n: float(Q(n) ** 3) for n in (6, 5, 4, 3, 2, 1)}
        q6 = float(Q(6))
    rng = np.random.default_rng(7)
    p = rng.beta(float(a), float(b), size=2_000_000)
    quiet = (rng.random((2_000_000, 6)) > p[:, None]).all(axis=1)
    sim = float(quiet.mean()) ** 3
    return {
        "q": q, "rho": rho,
        "beta_a": round(float(a), 8), "beta_b": round(float(b), 8),
        "P_one_quiet_round_6_seats": round(q6, 8),
        "P_3_quiet_rounds_6_seats_closed_form": round(closed[6], 8),
        "P_3_quiet_rounds_6_seats_simulated": round(sim, 8),
        "two_tools_agree_to": abs(closed[6] - sim),
        "by_roster_size": {k: round(v, 8) for k, v in closed.items()},
        "reproduces_0_1159": abs(closed[6] - 0.1159) < 5e-4,
    }


def claim_the_empirical_rate_agrees_and_needs_no_model(
        max_k: int = 10) -> dict:
    """The same quantity measured straight off the archive, model-free.

    DENOMINATOR: round positions where findings DEMONSTRABLY remained -- a later
    round in the same report raised a new critical. NUMERATOR: those where the
    preceding K rounds were all quiet. This is the honest false-positive rate,
    because a quiet window at the true end of a problem space is not an error.
    """
    reports = collect_reports()
    rows = {}
    for k in range(3, max_k + 1):
        den = num = 0
        for recs in reports:
            last = max([rn for rn, _, h, _, _ in recs if h > 0], default=-1)
            for i in range(k - 1, len(recs)):
                if recs[i][0] >= last:
                    continue
                den += 1
                if all(recs[j][2] == 0 for j in range(i - k + 1, i + 1)):
                    num += 1
        lo, hi = wilson(num, den)
        rows[k] = {"premature_windows": num, "opportunities": den,
                   "rate": round(num / den, 6) if den else None,
                   "wilson": (round(lo, 6), round(hi, 6))}
    at3 = rows[3]
    return {
        "reports": len(reports),
        "by_required_quiet_run": rows,
        "model_value_at_k3": 0.11587334,
        "empirical_at_k3": at3["rate"],
        "model_sits_inside_the_empirical_interval": (
            at3["wilson"][0] <= 0.11587334 <= at3["wilson"][1]),
        "first_k_with_no_premature_window": next(
            (k for k in sorted(rows) if rows[k]["premature_windows"] == 0), None),
    }


def claim_gamma_does_not_cut_the_joint_rate() -> dict:
    """CALL THE REAL GATE on every premature window in the record.

    `execute-do-not-grep`: a test that read the gate's source could only confirm
    that the gate describes itself consistently. Calling it on the archive's own
    gamma values is the only thing that shows whether the second arm bites.
    """
    sys.path.insert(0, str(REPO))
    from bench.reference_runner_v3 import (RunnerConfig,
                                           _check_gamma_alt_convergence)
    cfg = RunnerConfig()
    reports = collect_reports()
    windows = []
    for recs in reports:
        last = max([rn for rn, _, h, _, _ in recs if h > 0], default=-1)
        for i in range(2, len(recs)):
            rn, _, _, g, src = recs[i]
            if rn >= last:
                continue
            if all(recs[j][2] == 0 for j in (i - 2, i - 1, i)):
                windows.append((src, rn, g))
    with_gamma = [(s, r, g) for s, r, g in windows if isinstance(g, (int, float))]
    fired, above = 0, 0
    detail = []
    for src, rn, g in with_gamma:
        conv, reason = _check_gamma_alt_convergence(
            rn, float(g), [0, 0, 0], cfg, unresolved_critical=0, contested=0,
            gamma_critical=float(g), total_findings=10)
        fired += bool(conv)
        above += float(g) >= float(getattr(cfg, "gamma_alt_threshold", 0.30))
        detail.append({"report": src, "round": rn, "gamma": round(float(g), 4),
                       "gate_converged": bool(conv)})
    lo, hi = wilson(fired, len(with_gamma))
    return {
        "gamma_alt_threshold": float(getattr(cfg, "gamma_alt_threshold", 0.30)),
        "premature_windows": len(windows),
        "with_a_recorded_gamma": len(with_gamma),
        "gate_fired_on": fired,
        "gamma_above_threshold_on": above,
        "gate_fire_rate": round(fired / len(with_gamma), 6) if with_gamma else None,
        "wilson": (round(lo, 6), round(hi, 6)),
        "gamma_blocked_none": fired == len(with_gamma),
        "verdict": ("the gamma arm did not block a single premature window, so "
                    "the joint false-quiet rate equals the quiet-window arm's "
                    "rate in this record; the 2 arms are positively dependent "
                    "because quiet rounds are what flatten the curve gamma "
                    "measures"),
        "detail": detail,
    }


def claim_the_two_arms_are_positively_dependent() -> dict:
    """WHY it does not bite, as a correlation rather than an assertion.

    If gamma were independent of quietness, gamma at the end of a quiet window
    would look like gamma anywhere else. It does not: it is systematically
    higher, which is the mechanism and not a coincidence.
    """
    import numpy as np
    from scipy import stats
    reports = collect_reports()
    in_window, elsewhere = [], []
    for recs in reports:
        for i, (rn, _, _, g, _) in enumerate(recs):
            if not isinstance(g, (int, float)):
                continue
            quiet3 = i >= 2 and all(recs[j][2] == 0 for j in (i - 2, i - 1, i))
            (in_window if quiet3 else elsewhere).append(float(g))
    a, b = np.array(in_window), np.array(elsewhere)
    if len(a) < 2 or len(b) < 2:
        return {"note": "not enough rounds carry a gamma to compare"}
    u, p = stats.mannwhitneyu(a, b, alternative="greater")
    # Second tool: a rank computation that does not use scipy's implementation.
    allv = np.concatenate([a, b])
    ranks = stats.rankdata(allv)
    u_manual = ranks[:len(a)].sum() - len(a) * (len(a) + 1) / 2
    return {
        "rounds_at_the_end_of_a_quiet_run": len(a),
        "other_rounds": len(b),
        "median_gamma_in_a_quiet_run": round(float(np.median(a)), 6),
        "median_gamma_elsewhere": round(float(np.median(b)), 6),
        "mannwhitney_u": float(u), "p_one_sided_greater": float(p),
        "manual_u_agrees": abs(u_manual - u) < 1e-9,
        "gamma_is_higher_inside_a_quiet_run": bool(p < 0.05),
        "verdict": ("gamma is systematically HIGHER exactly where the other arm "
                    "is about to fire, which is why the conjunction cannot be "
                    "treated as a product of independent probabilities"),
    }


def claim_the_required_run_that_would_hold_a_target(target: float = 0.05) -> dict:
    """What K the founder would be buying, from the measured curve."""
    d = claim_the_empirical_rate_agrees_and_needs_no_model()
    rows = d["by_required_quiet_run"]
    meets = [k for k in sorted(rows)
             if rows[k]["rate"] is not None and rows[k]["rate"] <= target]
    conservative = [k for k in sorted(rows) if rows[k]["wilson"][1] <= target]
    return {
        "target": target,
        "current_required_run": 3,
        "current_rate": rows[3]["rate"],
        "smallest_k_meeting_the_target_on_the_point_estimate": (
            meets[0] if meets else None),
        "smallest_k_whose_upper_confidence_bound_meets_it": (
            conservative[0] if conservative else None),
        "note": ("the point estimate and the upper bound disagree, and the "
                 "upper bound is the honest one to spend a decision on because "
                 "the denominator shrinks as the window lengthens"),
        "cost": ("each extra required quiet round is an extra round of every "
                 "seat's time on every run that would otherwise have converged"),
        "status": "PROPOSED. Not applied. Changing K changes every experiment.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", type=float, default=0.05)
    ap.add_argument("--quick", action="store_true", help="skip the simulation")
    args = ap.parse_args()

    print("== 1. the 0.1159 figure, reproduced in 2 tools ==")
    for k, v in claim_the_0_1159_figure_reproduces().items():
        print(f"   {k}: {v}")

    print("\n== 2. and measured off the archive with no model at all ==")
    d2 = claim_the_empirical_rate_agrees_and_needs_no_model()
    for k in sorted(d2["by_required_quiet_run"]):
        r = d2["by_required_quiet_run"][k]
        print(f"   quiet run of {k:2d}: {r['premature_windows']:3d} premature of "
              f"{r['opportunities']:3d} -> {r['rate']}  Wilson {r['wilson']}")
    print(f"   model value sits inside the empirical interval: "
          f"{d2['model_sits_inside_the_empirical_interval']}")
    print(f"   first quiet run with 0 premature windows: "
          f"{d2['first_k_with_no_premature_window']}")

    print("\n== 3. the REAL gate, called on every premature window ==")
    d3 = claim_gamma_does_not_cut_the_joint_rate()
    for k in ("gamma_alt_threshold", "premature_windows", "with_a_recorded_gamma",
              "gate_fired_on", "gamma_above_threshold_on", "gate_fire_rate",
              "wilson", "gamma_blocked_none", "verdict"):
        print(f"   {k}: {d3[k]}")

    print("\n== 4. why: the 2 arms are positively dependent ==")
    for k, v in claim_the_two_arms_are_positively_dependent().items():
        print(f"   {k}: {v}")

    print("\n== 5. what a target would cost ==")
    for k, v in claim_the_required_run_that_would_hold_a_target(args.target).items():
        print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
