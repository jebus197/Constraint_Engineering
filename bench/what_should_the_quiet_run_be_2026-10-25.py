#!/usr/bin/env python3
"""Where should the required quiet run come from, and does it need to be fixed?

HIS QUESTIONS, 2026-10-25, each answered by a section below:

  1. Why add quiet rounds at all? 3 has stood for most of the project's life and
     convergence has triggered many times.
  2. Is the claim that convergence CANNOT trigger reliably at 3? If so, what has
     the project been doing all year?
  3. Must the count be FIXED, or can it be computed at the start of an experiment
     from that experiment's complexity? 4 + 4 should not need 7 rounds; a proof of
     the Riemann Hypothesis might need more than 7.
  4. Where does the number come from, and what would justify ANY value?
  5. Would a longer quiet run increase churn, which itself costs compute?
  6. Is the severity threshold of 0.7 against 0.5 the same topic, and would
     changing how severity is measured solve this instead?

WHAT THIS SCRIPT PROPOSES AND DOES NOT APPLY. Nothing here changes a default.
His instruction was explicit: no fixes without his approval.

THE CENTRAL CORRECTION IT MAKES, AND IT IS A CORRECTION TO CC1'S OWN FRAMING.
`bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py` measures

    P(K quiet rounds observed | more criticals demonstrably remained)

because its denominator is restricted to round positions where a LATER round in
the same report raised a new critical. That is the quiet detector's FALSE-NEGATIVE
rate, conditioned on there being something left to find. It is NOT

    P(criticals remained | the gate fired)

which is the quantity a decision needs, and the 2 differ by the base rate of
"findings remained" at the moment the gate could fire. Quoting the first number
as though it were the second overstates the case for a longer window, and that is
what was put to him. Section 2 computes the second number.

USAGE
    python3 bench/what_should_the_quiet_run_be_2026-10-25.py
    python3 bench/what_should_the_quiet_run_be_2026-10-25.py --json
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

#: The live severity cut for "critical". `bench/reference_runner_v3.py` applies it
#: in 5 places and `the_false_quiet_rate...py` hard-codes it as CRITICAL = 0.7.
LIVE_CRITICAL = 0.7

#: The sweep he asked about: does a LOWER severity cut at the longstanding quiet
#: run of 3 buy what a LONGER quiet run buys at 0.7?
SEVERITY_GRID = (0.5, 0.6, 0.7, 0.8)
K_GRID = tuple(range(3, 10))


def _norm(m) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(m or "").lower())


def collect(threshold: float):
    """Per report: rounds as (round, n_responded, n_raising, gamma), plus the
    per-finding model multiset needed for a species-richness estimate.

    Parameterised on the severity threshold, which the original producer
    hard-codes, because whether 0.7 is the right cut is part of his question.
    """
    reports = []
    for f in sorted(glob.glob(str(REPO / "bench" / "logs" / "**" / "*report*.json"),
                              recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:                                   # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        rounds, reg = d.get("rounds"), d.get("registry")
        if not isinstance(rounds, list) or not isinstance(reg, dict):
            continue
        entries = reg.get("entries") if isinstance(reg.get("entries"), dict) else reg
        if not isinstance(entries, dict):
            continue
        raised, per_finding = {}, []
        for e in entries.values():
            if not isinstance(e, dict):
                continue
            try:
                sev = float(e.get("severity") or 0.0)
            except (TypeError, ValueError):
                continue
            if sev < threshold:
                continue
            r, m = e.get("open_since_round"), _norm(e.get("source_model"))
            if r is None or not m:
                continue
            try:
                r = int(r)
            except (TypeError, ValueError):
                continue
            raised.setdefault(r, set()).add(m)
            # HOW MANY DISTINCT SEATS RAISED THIS FINDING, read from the field
            # that actually holds it. The first version of this looked for
            # `reviewers`, `confirmed_by` and `raised_by`, NONE of which exists on
            # a registry entry, so every finding came back as a singleton and the
            # coverage estimate was identically 0. The real field is
            # `source_aliases`, with `codiscovery` as its companion: inspected over
            # 1,345 critical findings, `source_aliases` has length 1 in 1,274 of
            # them and length greater than 1 in 71.
            al = e.get("source_aliases")
            co = e.get("codiscovery")
            seats = {m}
            for v in (al, co):
                if isinstance(v, dict):
                    seats |= {_norm(x) for x in v.keys()}
                elif isinstance(v, list):
                    seats |= {_norm(x) for x in v if isinstance(x, (str, int))}
            per_finding.append(len({x for x in seats if x}))
        # READ FROM THE ORIGINAL PRODUCER, NOT GUESSED. The first version of this
        # collector looked for `responded` / `n_responded` and returned 0 reports,
        # because the field is `models_responded`; and it counted len(raised),
        # where the original counts the INTERSECTION of models that responded with
        # models that raised a critical that round. Guessing a field name is the
        # single commonest error in this session's record, so the shape here is
        # copied from `the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py`
        # deliberately, which also makes the 2 sets of figures comparable.
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
            recs.append((rn, len(resp), len(resp & raised.get(rn, set())), g))
        if recs:
            recs.sort()
            reports.append({"file": f, "rounds": recs, "finding_freqs": per_finding})
    return reports


# --------------------------------------------------------------------------- #
# 1. THE CONDITIONAL RATE, reproduced so the comparison is like with like
# --------------------------------------------------------------------------- #
def conditional_rate(reports, k: int) -> tuple[int, int]:
    """P(K quiet rounds | findings demonstrably remained). The ORIGINAL quantity."""
    den = num = 0
    for rep in reports:
        recs = rep["rounds"]
        last = max([rn for rn, _, h, _ in recs if h > 0], default=-1)
        for i in range(k - 1, len(recs)):
            if recs[i][0] >= last:
                continue
            den += 1
            if all(recs[j][2] == 0 for j in range(i - k + 1, i + 1)):
                num += 1
    return num, den


# --------------------------------------------------------------------------- #
# 2. THE DECISION-RELEVANT RATE: P(findings remained | the window closed)
# --------------------------------------------------------------------------- #
def posterior_rate(reports, k: int) -> tuple[int, int]:
    """Of the positions where K quiet rounds HAD occurred, how many were followed
    by a further critical?

    THIS IS THE NUMBER A DECISION NEEDS. The denominator is every position where
    the quiet condition was satisfied -- which is what the gate actually keys on --
    and the numerator is those where a critical still came later. The original
    producer conditions the other way round and therefore cannot answer
    "if we close on K quiet rounds, how often are we wrong?".
    """
    den = num = 0
    for rep in reports:
        recs = rep["rounds"]
        for i in range(k - 1, len(recs)):
            if not all(recs[j][2] == 0 for j in range(i - k + 1, i + 1)):
                continue
            den += 1
            if any(h > 0 for _, _, h, _ in recs[i + 1:]):
                num += 1
    return num, den


# --------------------------------------------------------------------------- #
# 3. THE DYNAMIC RULE he asked for: estimate what has NOT been seen
# --------------------------------------------------------------------------- #
def arrival_stop(recs, floor: float = 0.25, min_rounds: int = 3):
    """Stop when the FITTED arrival rate of new criticals falls below `floor`.

    WHY A SECOND RULE. The coverage rule below rests on Good-Turing, which assumes
    the seats are drawing exchangeably from one pool of findings. A deliberately
    DIVERSE panel violates that by design -- low co-discovery is the point of
    running different models, not evidence of incompleteness -- so coverage alone
    cannot carry a decision. This rule uses only the quantity the harness already
    records and the gate already reads: how many new criticals arrived each round.

    THE FIT. New criticals per round decay roughly geometrically, which the archive
    supports directly: early rounds carry 1.524 criticals per round against 0.627
    in late rounds, a ratio of 2.43. A least-squares line through log(1 + h) gives
    a per-round decay; the rule stops at the first round whose PREDICTED next-round
    yield is under `floor`. On a trivial problem the first round exhausts the space
    and the prediction is immediately near 0; on a deep one the arrivals keep
    coming and the rule keeps going. That is the behaviour he asked for, read off
    the experiment rather than chosen for it.
    """
    if len(recs) < min_rounds:
        return None
    import math as _m
    ys = [_m.log1p(h) for _, _, h, _ in recs]
    for i in range(min_rounds - 1, len(recs)):
        xs = list(range(i + 1))
        yy = ys[:i + 1]
        n = len(xs)
        mx = sum(xs) / n
        my = sum(yy) / n
        var = sum((x - mx) ** 2 for x in xs)
        if var == 0:
            continue
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, yy)) / var
        pred = _m.expm1(my + slope * (n - mx))
        if pred < floor:
            return recs[i][0]
    return None


def coverage_stop(recs, freqs, target: float = 0.95, min_rounds: int = 2):
    """The round at which a Good-Turing coverage estimate first clears `target`.

    HIS QUESTION: must the count be fixed, or can it come from the experiment?

    THE PRINCIPLE, and it is not new mathematics. "Have we found everything?" is
    the UNSEEN-SPECIES problem, solved by Good and Turing in 1953 for exactly this
    shape of data. If f1 findings have been raised by exactly 1 seat and n findings
    have been raised in total, the probability that the NEXT finding is one never
    seen before is approximately f1 / n. So coverage, the probability that the next
    finding is already known, is 1 - f1 / n.

    WHY IT ANSWERS HIS 4 + 4 EXAMPLE. A trivial problem produces a handful of
    findings that every seat raises, so f1 is near 0, coverage is near 1, and the
    rule stops almost immediately. A deep problem keeps producing findings only 1
    seat has seen, so f1 stays high, coverage stays low, and the rule keeps going.
    The stopping point is read off the experiment instead of being chosen for it.

    A FIXED K CANNOT DO THIS, which is the real objection to any constant: 3 and 7
    are both answers to a question nobody asked of the data in front of them.
    """
    if not freqs:
        return None
    n = sum(freqs)
    f1 = sum(1 for x in freqs if x == 1)
    if n <= 0:
        return None
    coverage = 1.0 - f1 / n
    # The rule needs at least `min_rounds` of evidence before it may speak at all,
    # because coverage computed off 1 round is coverage of 1 round's sample.
    for i, (rn, _, _, _) in enumerate(recs):
        if i + 1 < min_rounds:
            continue
        if coverage >= target:
            return rn
    return None


def chao1(freqs):
    """Chao1 lower bound on the number of findings NEVER raised by any seat.

    Reported alongside coverage because the 2 answer different halves: coverage
    says how likely the next finding is new, Chao1 says how many are still out
    there. Both are 0 when every finding has been raised by several seats.
    """
    if not freqs:
        return None
    f1 = sum(1 for x in freqs if x == 1)
    f2 = sum(1 for x in freqs if x == 2)
    obs = len(freqs)
    if f2 > 0:
        unseen = f1 * f1 / (2.0 * f2)
    else:
        unseen = f1 * (f1 - 1) / 2.0
    return {"observed": obs, "f1": f1, "f2": f2,
            "estimated_unseen": round(unseen, 4),
            "estimated_total": round(obs + unseen, 4)}


# --------------------------------------------------------------------------- #
# 4. CHURN: does a longer window buy its rounds with rediscovery?
# --------------------------------------------------------------------------- #
def churn(reports):
    """How productive are LATE rounds compared with early ones?

    HIS POINT: 4 extra rounds cost seat time whether or not they find anything,
    and if they mostly re-raise what is known, the harness pays twice -- once to
    generate the duplicate and again to classify it.
    """
    early_h = early_n = late_h = late_n = 0
    for rep in reports:
        recs = rep["rounds"]
        if len(recs) < 4:
            continue
        cut = len(recs) // 2
        for i, (_, _, h, _) in enumerate(recs):
            if i < cut:
                early_h += h
                early_n += 1
            else:
                late_h += h
                late_n += 1
    return {"early_rounds": early_n, "criticals_in_early_rounds": early_h,
            "late_rounds": late_n, "criticals_in_late_rounds": late_h,
            "early_rate": round(early_h / early_n, 6) if early_n else None,
            "late_rate": round(late_h / late_n, 6) if late_n else None}


def first_fire_rate(reports, k: int) -> tuple[int, int]:
    """P(criticals remained | the gate FIRES) -- the corrected estimand.

    THE PANEL REFUTED THE EARLIER VERSION AND WAS RIGHT, 2026-10-25. The `fable`
    seat wrote: *"its denominator is overlapping window positions, not gate
    firings; the gate fires once, and the first-fire rate is 0.266667 (8/30)."*
    Reproduced exactly on an independent implementation.

    `posterior_rate` counts EVERY position at which a K-quiet window had closed,
    and those windows OVERLAP inside a run -- a 5-round quiet tail contains 3
    distinct 3-windows. The gate fires ONCE and then the run is over, so a run
    with a long quiet tail was being counted several times and the rate was
    inflated. **The published figure of 23 of 63 = 0.365079 was wrong by 37%;
    the correct figure is 8 of 30 = 0.266667.** The direction of every conclusion
    survives. The magnitude did not, and a reader quoting 0.365 as the error rate
    of K=3 would have been misled.

    `posterior_rate` is kept rather than deleted, because the 2 numbers side by
    side are what show the size of the error.
    """
    den = num = 0
    for rep in reports:
        recs = rep["rounds"]
        for i in range(k - 1, len(recs)):
            if not all(recs[j][2] == 0 for j in range(i - k + 1, i + 1)):
                continue
            den += 1
            if any(h > 0 for _, _, h, _ in recs[i + 1:]):
                num += 1
            break                      # the gate fires ONCE per run
    return num, den


def arrival_rule_premature_rate(reports) -> tuple[int, int]:
    """The arrival-curve rule's OWN premature rate, which was never measured.

    BOTH PANEL SEATS CONVICTED THE BRIEF OF EXACTLY THE OMISSION IT CONVICTED THE
    ORIGINAL PRODUCER OF. The `cc2` seat: *"Recommendation 1 rejects K=7 for
    resting on a mis-specified conditional; recommendation 2 then endorses the
    arrival-curve rule on `fired on 47, mean 4.7234` -- a cost statistic with no
    premature-rate attached at all ... The brief applied its own correction to
    the incumbent and not to the challenger. That asymmetry is how a replacement
    that nothing measured gets recommended, and this project has shipped 11 of
    those since 2026-08-01."*

    MEASURED: the rule closes prematurely in 22 of 47 runs, 0.468085, against
    K=3's 8 of 30, 0.266667 -- a point estimate 0.201418 WORSE. Fisher exact
    one-sided p = 0.062240 and a statsmodels normal approximation p = 0.038577,
    so the disadvantage is not established at 0.05 by the exact test. **But the
    rule has NO measured advantage on the metric the brief itself called
    decisive, so recommending it was an addition nothing had measured.
    Recommendation 2 is WITHDRAWN.**
    """
    num = den = 0
    for rep in reports:
        recs = rep["rounds"]
        stop = arrival_stop(recs)
        if stop is None:
            continue
        den += 1
        if any(h > 0 for rn, _, h, _ in recs if rn > stop):
            num += 1
    return num, den


def wilson(k: int, n: int):
    """Wilson interval, cross-verified against statsmodels where available."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--figures", action="store_true",
                    help="print the load-bearing figures in a stable form, for a "
                         "panel brief's declared-figure check to RE-EXECUTE")
    a = ap.parse_args()

    base = collect(LIVE_CRITICAL)
    res = {"reports_at_live_threshold": len(base), "live_critical": LIVE_CRITICAL}

    # 1 + 2: the 2 rates side by side, so the difference is visible
    rows = {}
    for k in K_GRID:
        cn, cd = conditional_rate(base, k)
        pn, pd = posterior_rate(base, k)
        fn, fd = first_fire_rate(base, k)
        rows[k] = {
            "conditional_num": cn, "conditional_den": cd,
            "conditional_rate": round(cn / cd, 6) if cd else None,
            "conditional_wilson": [round(x, 6) for x in wilson(cn, cd)],
            "posterior_num": pn, "posterior_den": pd,
            "posterior_rate": round(pn / pd, 6) if pd else None,
            "posterior_wilson": [round(x, 6) for x in wilson(pn, pd)],
            "first_fire_num": fn, "first_fire_den": fd,
            "first_fire_rate": round(fn / fd, 6) if fd else None,
            "first_fire_wilson": [round(x, 6) for x in wilson(fn, fd)],
        }
    res["by_k"] = rows

    # 6: the severity sweep he asked about
    sweep = {}
    for s in SEVERITY_GRID:
        reps = collect(s)
        inner = {}
        for k in (3, 5, 7):
            pn, pd = posterior_rate(reps, k)
            inner[k] = {"num": pn, "den": pd,
                        "rate": round(pn / pd, 6) if pd else None,
                        "wilson": [round(x, 6) for x in wilson(pn, pd)]}
        sweep[s] = {"reports": len(reps), "by_k": inner}
    res["severity_sweep"] = sweep

    # 3: what the dynamic rule would have chosen
    dyn = []
    for rep in base:
        stop = coverage_stop(rep["rounds"], rep["finding_freqs"])
        astop = arrival_stop(rep["rounds"])
        c = chao1(rep["finding_freqs"])
        dyn.append({"file": pathlib.Path(rep["file"]).parent.name,
                    "rounds_available": len(rep["rounds"]),
                    "coverage_stop_round": stop,
                    "arrival_stop_round": astop, "chao1": c})
    arr = [d["arrival_stop_round"] for d in dyn if d["arrival_stop_round"] is not None]
    cov = [d["coverage_stop_round"] for d in dyn if d["coverage_stop_round"] is not None]
    res["dynamic_rule"] = {
        "runs": len(dyn),
        "arrival_rule_fired": len(arr),
        "arrival_rule_never_fired": len(dyn) - len(arr),
        "arrival_stop_rounds": sorted(arr),
        "arrival_mean_round": round(sum(arr) / len(arr), 4) if arr else None,
        "arrival_median_round": (sorted(arr)[len(arr) // 2] if arr else None),
        "coverage_rule_fired": len(cov),
        "coverage_rule_never_fired": len(dyn) - len(cov),
        "rounds_available_mean": round(
            sum(d["rounds_available"] for d in dyn) / len(dyn), 4) if dyn else None,
        "detail": dyn[:10],
    }

    # 5: churn
    res["churn"] = churn(base)

    if a.figures:
        # STABLE STRINGS A BRIEF CAN DECLARE. A number typed into prose is never
        # re-executed; a declared figure is. This is how `gamma is 0.451` once
        # reached 2 seats when the true value was 0.415413.
        r3, r5 = rows[3], rows[5]
        ch = res["churn"]
        d = res["dynamic_rule"]
        print(f"posterior_k3 = {r3['posterior_num']} of {r3['posterior_den']} = "
              f"{r3['posterior_rate']}")
        print(f"posterior_k3_wilson = {r3['posterior_wilson']}")
        print(f"conditional_k3 = {r3['conditional_num']} of {r3['conditional_den']} = "
              f"{r3['conditional_rate']}")
        print(f"posterior_k5 = {r5['posterior_num']} of {r5['posterior_den']} = "
              f"{r5['posterior_rate']}")
        print(f"posterior_k7_denominator = {rows[7]['posterior_den']}")
        print(f"churn_early_rate = {ch['early_rate']}")
        print(f"churn_late_rate = {ch['late_rate']}")
        print(f"churn_ratio = {round(ch['early_rate'] / ch['late_rate'], 6)}")
        print(f"severity_sweep_k3 = "
              + ", ".join(f"{sv}:{res['severity_sweep'][sv]['by_k'][3]['rate']}"
                          for sv in SEVERITY_GRID))
        print(f"arrival_rule_fired = {d['arrival_rule_fired']} of {d['runs']}")
        print(f"arrival_mean_round = {d['arrival_mean_round']}")
        print(f"rounds_available_mean = {d['rounds_available_mean']}")
        print(f"reports = {len(base)}")
        f3 = rows[3]
        an, ad = arrival_rule_premature_rate(base)
        print(f"first_fire_k3 = {f3['first_fire_num']} of {f3['first_fire_den']} = "
              f"{f3['first_fire_rate']}")
        print(f"first_fire_k3_wilson = {f3['first_fire_wilson']}")
        print(f"arrival_rule_premature = {an} of {ad} = {round(an/ad, 6) if ad else None}")
        return 0
    if a.json:
        print(json.dumps(res, indent=2, default=str))
        return 0

    print(f"  reports at severity >= {LIVE_CRITICAL}: {len(base)}\n")
    print("  THE 3 RATES SIDE BY SIDE. The THIRD is the correct estimand; the")
    print("  second is kept only to show the size of the error the panel caught.")
    print(f"    {'K':>3}  {'P(quiet|remained)':>20}  {'overlapping(WRONG)':>20}"
          f"  {'first-fire(CORRECT)':>20}")
    for k, r in rows.items():
        c = f"{r['conditional_num']}/{r['conditional_den']}={r['conditional_rate']}"
        p = f"{r['posterior_num']}/{r['posterior_den']}={r['posterior_rate']}"
        ff = f"{r['first_fire_num']}/{r['first_fire_den']}={r['first_fire_rate']}"
        print(f"    {k:>3}  {c:>20}  {p:>20}  {ff:>20}")
    an, ad = arrival_rule_premature_rate(base)
    print(f"\n  THE ARRIVAL RULE'S OWN PREMATURE RATE, which the brief never measured:")
    print(f"    {an} of {ad} = {an/ad:.6f} against K=3 first-fire "
          f"{rows[3]['first_fire_rate']} -- the challenger is WORSE. Recommendation "
          f"WITHDRAWN.")
    print("\n  SEVERITY SWEEP: does a lower cut at K=3 buy what K=7 buys at 0.7?")
    for s, v in sweep.items():
        cells = "  ".join(
            f"K={k}:{v['by_k'][k]['rate']}" for k in (3, 5, 7))
        print(f"    severity >= {s}  ({v['reports']:3d} reports)   {cells}")
    d = res["dynamic_rule"]
    print(f"\n  DYNAMIC RULES over {d['runs']} runs "
          f"(mean {d['rounds_available_mean']} rounds available)")
    print(f"    arrival-curve rule : fired on {d['arrival_rule_fired']}, "
          f"median stop round {d['arrival_median_round']}, "
          f"mean {d['arrival_mean_round']}; never fired on "
          f"{d['arrival_rule_never_fired']}")
    print(f"    coverage rule      : fired on {d['coverage_rule_fired']}, "
          f"never fired on {d['coverage_rule_never_fired']} "
          f"(CONFOUNDED by seat diversity -- see its docstring)")
    ch = res["churn"]
    print(f"\n  CHURN: early rounds {ch['criticals_in_early_rounds']} criticals over "
          f"{ch['early_rounds']} rounds ({ch['early_rate']}); late rounds "
          f"{ch['criticals_in_late_rounds']} over {ch['late_rounds']} ({ch['late_rate']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
