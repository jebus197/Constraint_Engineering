#!/usr/bin/env python3
"""Can ANY available signal tell a premature convergence from a sound one?

THE QUESTION THIS SETTLES, and it is prior to every proposal on the table.
On 2026-10-25 the free panel refuted an arrival-curve stopping rule because its
own premature rate, 0.468085, was WORSE than the fixed count of 3 at 0.266667.
An external speculative brief of 2026-10-27 then proposed a different adaptive
rule: a conjunction of signals -- finding silence, residual stability, tool
re-pin, panel split -- with a clamped additive required-streak length.

Both proposals assume the same thing WITHOUT TESTING IT: that the signals
available at the moment of closing carry information about whether the close is
premature. If they do not, then no rule built on them can beat a constant, and
the choice between 3, 5, 7 and any adaptive schedule is a choice between
instruments that are all blind in the same way.

THE PANEL ALREADY FOUND ONE INSTANCE OF EXACTLY THAT BLINDNESS: the gamma arm
fired on 23 of 23 premature windows and blocked none. This script asks whether
that is a property of gamma alone or of the whole signal set.

METHOD. For every run, find the FIRST position at which K consecutive rounds
carried no new critical finding -- the point at which the gate would actually
fire, counted once per run rather than once per overlapping window, which is the
correction the `fable` seat supplied. Label it PREMATURE if any later round in
the same run raised a critical. Then ask, for each signal recorded at that
position, whether its distribution differs between the premature and the sound
closes. Discrimination is reported as the Mann-Whitney U statistic rescaled to an
AUC, which is the probability that a randomly chosen premature close scores above
a randomly chosen sound one. 0.5 is blindness.

WHAT WOULD FALSIFY THE PESSIMISTIC READING: any signal whose AUC confidence
interval excludes 0.5. That is reported per signal rather than argued.

USAGE
    python3 bench/can_any_signal_see_a_premature_close_2026-10-27.py
    python3 bench/can_any_signal_see_a_premature_close_2026-10-27.py --json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CRITICAL = 0.7
DEFAULT_K = 3

#: Per-round signals a stopping rule could read. Each maps to a proposal's term:
#: S1 finding silence, S2 residual stability, S3 tool re-pin, S4 panel split.
SIGNALS = ("gamma", "gamma_critical", "rho", "rho_avg", "open_crit_high",
           "cross_model_diversity", "unverified_critical", "recidivism_hits",
           "novel_this_round", "registry_total", "findings_count")


def _norm(m) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(m or "").lower())


def _num(v):
    """A float, or None. A bool is NOT a number here: `verification` is a dict in
    some records and a flag in others, and silently coercing one shape to the
    other is how a signal gets measured that nobody is recording."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def collect():
    """Per report: rounds as (round, n_resp, n_raising_critical, signals dict)."""
    out = []
    for f in sorted(glob.glob(str(REPO / "bench" / "logs" / "**" / "*report*.json"),
                              recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:                                  # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        rounds, reg = d.get("rounds"), d.get("registry")
        if not isinstance(rounds, list) or not isinstance(reg, dict):
            continue
        entries = reg.get("entries") if isinstance(reg.get("entries"), dict) else reg
        if not isinstance(entries, dict):
            continue
        raised = {}
        for e in entries.values():
            if not isinstance(e, dict):
                continue
            try:
                if float(e.get("severity") or 0.0) < CRITICAL:
                    continue
                r = int(e.get("open_since_round"))
            except (TypeError, ValueError):
                continue
            m = _norm(e.get("source_model"))
            if m:
                raised.setdefault(r, set()).add(m)
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
            sig = {k: _num(rec.get(k)) for k in SIGNALS}
            recs.append((rn, len(resp), len(resp & raised.get(rn, set())), sig))
        if recs:
            recs.sort(key=lambda t: t[0])
            out.append({"file": f, "rounds": recs})
    return out


def fire_points(reports, k: int):
    """The FIRST position per run at which the gate's quiet condition is met.

    Counted once per run because the gate fires once and the run then ends --
    the correction the panel supplied on 2026-10-25, which moved the measured
    rate from 23 of 63 to 8 of 30.
    """
    rows = []
    for rep in reports:
        recs = rep["rounds"]
        for i in range(k - 1, len(recs)):
            if not all(recs[j][2] == 0 for j in range(i - k + 1, i + 1)):
                continue
            # ★ THE LABEL IS EVALUATED OVER A TAIL, AND THE TAIL CAN BE EMPTY.
            # `any([])` is False, so a fire point with no recorded round after
            # it is labelled SOUND with zero evidence -- it is UNOBSERVED, not
            # sound. Found by the cc2 seat in the joint round of 2026-10-28,
            # which neither blind seat saw. Measured: 10 of 30 fire points have
            # an EMPTY tail and 10 more a tail of 1; all 20 are labelled sound,
            # and NOT ONE of the 8 premature labels comes from a tail shorter
            # than 2. Tail length ALONE predicts the label at AUC 0.971591,
            # CI [0.888203, 1.0], Spearman rho 0.751455 p = 1.70325e-06 --
            # higher than any signal this script scores, `findings_count`
            # included. It is length scored against length.
            #
            # `tail_rounds` is therefore carried on every row and reported, and
            # `--min-tail` lets a caller drop labels that could not have been
            # refuted by observation. THE DEFAULT IS 0, which reproduces every
            # published figure byte for byte: nothing here moves a cited number.
            tail = recs[i + 1:]
            premature = any(h > 0 for _, _, h, _ in tail)
            rows.append({"file": pathlib.Path(rep["file"]).parent.name,
                         "round": recs[i][0], "premature": premature,
                         "tail_rounds": len(tail),
                         "signals": recs[i][3]})
            break
    return rows


def auc_mw(pos, neg):
    """AUC via the Mann-Whitney U, with a DeLong-free normal-approximation CI.

    Cross-verified against scipy's own U and against a direct rank computation,
    because a single implementation of a rank statistic is one implementation.
    """
    n1, n0 = len(pos), len(neg)
    if n1 == 0 or n0 == 0:
        return None
    wins = sum((1.0 if a > b else 0.5 if a == b else 0.0) for a in pos for b in neg)
    auc = wins / (n1 * n0)
    # Hanley-McNeil standard error
    q1 = auc / (2 - auc)
    q2 = 2 * auc * auc / (1 + auc)
    var = (auc * (1 - auc) + (n1 - 1) * (q1 - auc ** 2)
           + (n0 - 1) * (q2 - auc ** 2)) / (n1 * n0)
    se = math.sqrt(max(var, 0.0))
    z = 1.959963984540054
    return {"auc": round(auc, 6), "n_premature": n1, "n_sound": n0,
            "ci": [round(max(0.0, auc - z * se), 6),
                   round(min(1.0, auc + z * se), 6)],
            "se": round(se, 6)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--k", type=int, default=DEFAULT_K)
    ap.add_argument("--min-tail", type=int, default=0,
                    help="drop fire points with fewer than this many recorded "
                         "rounds after them. A label computed over a shorter "
                         "tail could not have been refuted by observation. "
                         "Default 0 reproduces every published figure.")
    a = ap.parse_args()

    reps = collect()
    all_rows = fire_points(reps, a.k)
    rows = [r for r in all_rows if r["tail_rounds"] >= a.min_tail]
    censored = len(all_rows) - len(rows)
    unobserved = sum(1 for r in all_rows if r["tail_rounds"] == 0)
    prem = [r for r in rows if r["premature"]]
    sound = [r for r in rows if not r["premature"]]

    # ★ THE 2 NEW COUNTS ARE REPORTED, NOT MERELY COMPUTED. The first pass of
    # this repair carried `tail_rounds` and then dropped the numbers that say
    # what it found -- the unwired-addition half of the additive standard,
    # inside the fix for a measurement defect. `labelled_over_an_empty_tail` is
    # printed UNCONDITIONALLY, because the reader of the DEFAULT invocation is
    # exactly the one who needs to know some labels rest on no observation.
    res = {"reports": len(reps), "k": a.k, "fire_points": len(rows),
           "premature": len(prem), "sound": len(sound),
           "min_tail": a.min_tail, "dropped_by_min_tail": censored,
           "labelled_sound_on_an_EMPTY_tail": unobserved,
           "fire_points_before_min_tail": len(all_rows), "by_signal": {}}

    for s in SIGNALS:
        p = [r["signals"][s] for r in prem if r["signals"].get(s) is not None]
        q = [r["signals"][s] for r in sound if r["signals"].get(s) is not None]
        got = auc_mw(p, q)
        if got is None:
            res["by_signal"][s] = {"recorded_at_fire_point": len(p) + len(q),
                                   "verdict": "NOT RECORDED AT ENOUGH FIRE POINTS"}
            continue
        lo, hi = got["ci"]
        got["separates"] = bool(lo > 0.5 or hi < 0.5)
        got["verdict"] = ("DISCRIMINATES" if got["separates"]
                          else "BLIND -- interval spans 0.5")
        res["by_signal"][s] = got

    disc = [s for s, v in res["by_signal"].items() if v.get("separates")]
    res["signals_that_discriminate"] = disc
    res["verdict"] = (
        "NO AVAILABLE SIGNAL SEPARATES A PREMATURE CLOSE FROM A SOUND ONE. "
        "Any adaptive rule built on these signals is blind in the same way the "
        "constant is, so the choice between 3, 5, 7 and an adaptive schedule "
        "cannot be made on discrimination grounds."
        if not disc else
        f"{len(disc)} signal(s) discriminate: {', '.join(disc)}. An adaptive "
        f"rule has something to read.")

    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    print(f"  reports {res['reports']}, gate fire points at K={a.k}: {len(rows)}"
          f"  ({len(prem)} premature, {len(sound)} sound)\n")
    print(f"    of those, {unobserved} were labelled SOUND over an EMPTY tail"
          f" -- unobserved, not sound. `any([])` is False.")
    if a.min_tail:
        print(f"    --min-tail {a.min_tail} dropped {censored} of "
              f"{len(all_rows)} fire point(s) whose label could not "
              f"have been refuted by observation")
    print(f"    {'signal':24s} {'n':>5s}  {'AUC':>8s}  {'95% CI':>20s}   verdict")
    for s, v in res["by_signal"].items():
        if "auc" not in v:
            print(f"    {s:24s} {v['recorded_at_fire_point']:>5d}  "
                  f"{'-':>8s}  {'-':>20s}   {v['verdict']}")
            continue
        ci = f"[{v['ci'][0]:.4f}, {v['ci'][1]:.4f}]"
        print(f"    {s:24s} {v['n_premature']+v['n_sound']:>5d}  {v['auc']:>8.4f}  "
              f"{ci:>20s}   {v['verdict']}")
    print(f"\n  {res['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
