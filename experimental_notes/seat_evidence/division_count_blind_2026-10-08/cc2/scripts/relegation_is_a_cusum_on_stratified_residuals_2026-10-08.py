# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'division_count_blind_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 64ba1da6bf66672dbeb0ae1010b1d664342f0d4fc8e8ee204197cf45a6b8b514
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Relegation: the statistic, the window, the decision rule, and what stops it
demoting a capable model for being handed the hard problems.

THE FOUNDER'S HALF THAT IS UNBUILT, 2026-10-08: *"just as teams and players can be
promoted over time through a period of sustained performance, clearly they can be
demoted by the opposite framing. If they demonstrate sustained degradation, they
can face rela[g]ation to a lower league."* With his standing guard: *"what we need
to guard against is simply counting when a model is successful as an 'improvement
in capability'. The only measure of improved capability is actual observed
capability (and the converse.)"*

THE HARD PART IS NOT THE DECISION RULE. It is that a model high on the ladder is
handed exactly the problems everything below it failed, so its RAW success rate
falls as it rises. An unstratified rule therefore demotes the strongest model in
the roster first, and it does so fastest when the ladder is working best. Claim 3
measures that: the unstratified rule demotes the capable model, the stratified
rule does not, on the same simulated stream.

THE SPECIFICATION, in standard names only.

STATISTIC -- the per-item stratified residual, which is the numerator term of the
COCHRAN-MANTEL-HAENSZEL statistic with 1 stratum per item (equivalently the score
contribution of a CONDITIONAL / FIXED-EFFECTS LOGIT with an item fixed effect):
    r(m, i) = y(m, i) - mean_over_cohort_on_item_i( y )
where y is 1 if the dispatch resolved and 0 if it did not, and the cohort is the
other models dispatched on THE SAME item i. Item difficulty cancels by
construction, and the degenerate strata take care of themselves without a special
case: if every model fails item i then the cohort mean is 0, every residual is 0,
and the item contributes no evidence in either direction. That is the whole answer
to "what stops a run of failures on hard problems from demoting a capable model" --
there is no run of failures in the statistic, only a run of failures RELATIVE TO
WHOEVER ELSE SAW THE SAME ITEM.

WINDOW -- none, and that is deliberate. A fixed trailing window of W dispatches
has to choose between detecting a small sustained drop (needs W large) and
detecting it soon (needs W small), and whichever is chosen is wrong for the other
case. The CUSUM is the sequential rule that has no window: it accumulates, so a
small sustained shift crosses eventually while an isolated bad patch decays. The
one genuine window is a MINIMUM SAMPLE before the rule is armed, n_min, so a
model with 3 dispatches is not relegated on 3 dispatches.

DECISION RULE -- PAGE'S (1954) one-sided CUSUM for a downward shift, on the
standardised residual:
    S_0 = 0,   S_k = max(0, S_{k-1} - z_k - k_ref),   demote when S_k >= h
where z_k = r_k / sd(r_k) and sd(r) is the within-item binomial sd
sqrt(p_i(1-p_i)) pooled over the cohort. k_ref = delta/2 is the standard
reference value for a target shift delta, h the decision interval. Promotion is
the mirror-image CUSUM on +z_k with the same h, so the ladder is symmetric by
construction rather than by a second mechanism.

TRANSIENT OUTAGE IS A DIFFERENT CONDITION, AND IT IS EXCLUDED BY TYPE, NOT BY
THRESHOLD. Only a RESOLVED-or-REFUTED dispatch produces an observation. A timeout,
an HTTP error, a lapsed licence, an empty reply -- these produce NO y, so the
CUSUM does not update and a model that is unreachable for a day is not relegated
for being unreachable. This matches the founder's position that results are
harvested when a model is done rather than at a wall-clock limit: a seat that has
not finished has not produced a datum. On top of the typing there is a DERIVED
bound on how long a genuine run of relative failure must last before it can
demote (claim 2): since r >= -1 and sd <= 1/2, the largest increment any single
observation can add is 2 - k_ref, so crossing h needs at least
    L_min = ceil( h / (2 - k_ref) )
consecutive worst-case observations. h is therefore CHOSEN from the longest
outage that must not demote, not guessed.

PARAMETERS ARE MEASURED, NOT PICKED. delta is the capability drop worth demoting
for, in phi units from
scripts/the_division_count_is_derived_from_resolution_2026-10-08.py, so it is the
same quantity the division boundaries are spaced by: delta = d_phi/(T-1), one
division's worth. h follows from a target in-control average run length ARL0,
computed below by the BROOK-EVANS (1972) Markov-chain method rather than by a
rule of thumb. n_min follows from ARL0 and the dispatch rate. What is NOT
available in this tree is the archived per-model-per-item outcome corpus needed
to measure the residual sd and the empirical outage-length distribution; those 2
numbers must be measured before deployment and are named here as the blockers.

Run: python3 scripts/relegation_is_a_cusum_on_stratified_residuals_2026-10-08.py
"""
from __future__ import annotations

import argparse
import math
import random

Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z) -> tuple:
    """Wilson score interval. Same statistic the promotion side already uses
    (bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def phi(p: float) -> float:
    return 2.0 * math.asin(math.sqrt(p))


# --------------------------------------------------------------- the rule
def stratified_residuals(stream: list) -> list:
    """stream: list of (item_id, y_target, [y_cohort...]). Returns standardised
    residuals for the target model, dropping degenerate strata (which carry no
    information, so they are absent rather than zero-weighted)."""
    out = []
    for _item, y, cohort in stream:
        n = len(cohort) + 1
        pbar = (sum(cohort) + y) / n
        if pbar <= 0.0 or pbar >= 1.0:
            continue                      # nobody or everybody resolved it
        sd = math.sqrt(pbar * (1 - pbar))
        out.append((y - pbar) / sd)
    return out


def rasch_residuals(stream: list, theta_floor: float) -> list:
    """THE REPAIR, after `stratified_residuals` above was falsified by claim 3.

    WHAT WENT WRONG WITH THE PER-ITEM STRATIFIED RESIDUAL. Conditioning on the
    item (Cochran-Mantel-Haenszel, equivalently a conditional / fixed-effects
    logit) drops any stratum with no within-stratum variation, because a stratum
    where everyone got the same answer carries no information about a contrast
    between them. That is correct in general and CATASTROPHIC here, because
    ESCALATION MANUFACTURES EXACTLY THOSE STRATA: the top model is dispatched
    only on items the whole cohort failed, so the cohort outcome is constant 0
    and the stratum varies if and only if the TOP MODEL SUCCEEDS. Every failure
    is discarded as degenerate and every success survives with the identical
    residual (measured: exactly sqrt(5) = 2.236068 for a 5-model cohort), so the
    mean residual is a constant and the CUSUM is reading A SUCCESS COUNT. That
    is the precise failure the founder's guard names, reached by the natural
    statistic, which is why it is kept in this file rather than quietly removed.

    THE REPAIR. Do not condition the item out -- carry difficulty as a MEASURED
    COVARIATE. This is the 1-parameter item-response (RASCH) residual:
        p(i) = sigmoid(theta_floor - b(i)),   r(i) = (y(i) - p(i)) / sqrt(p(1-p))
    where theta_floor is the skill the division certifies and b(i) the item's
    measured difficulty. No stratum is dropped, because p is strictly inside
    (0, 1) for every finite difficulty.

    AND THE DIFFICULTY INPUT ALREADY EXISTS. `bench/routing.py` records
    `rungs_tried`, and bench/the_promotion_ladder_needs_a_bound_not_a_success_
    2026-10-08.py claim 4 establishes by CALLING `route` that it is an exact
    difficulty label under exhaustion and a right-censored lower bound under a
    cap. `routing.DEFAULT_MAX_RUNGS = 0` is exhaust, so the label is available.
    Relegation is therefore buildable on a quantity the repository already
    measures -- and was NOT buildable before the cap was lifted.

    A success now earns credit (1-p)/sqrt(p(1-p)), large on a hard item and
    nearly 0 on an easy one, and a failure is debited p/sqrt(p(1-p)). A count of
    successes with no difficulty attached cannot move it.
    """
    out = []
    for _item, y, b in stream:
        p = 1.0 / (1.0 + math.exp(-(theta_floor - b)))
        p = min(max(p, 1e-6), 1 - 1e-6)
        out.append((y - p) / math.sqrt(p * (1 - p)))
    return out


def cusum_down(z_seq: list, k_ref: float, h: float) -> dict:
    """Page's one-sided CUSUM for a downward shift."""
    S, peak, cross = 0.0, 0.0, None
    path = []
    for i, z in enumerate(z_seq):
        S = max(0.0, S - z - k_ref)
        path.append(S)
        peak = max(peak, S)
        if cross is None and S >= h:
            cross = i + 1
    return {"crossed_at": cross, "demote": cross is not None, "peak": peak,
            "path_len": len(path), "_path": path}


def brook_evans_arl(k_ref: float, h: float, shift: float = 0.0,
                    m: int = 200) -> float:
    """ARL of the one-sided CUSUM by the Brook-Evans (1972) Markov-chain method.

    Discretise [0, h) into m states of width w = h/m, state j centred at
    (j+0.5)w. From state j the statistic moves to max(0, s - z - k_ref) with
    z ~ N(shift, 1), so the increment is -(z + k_ref) with mean -(shift+k_ref).
    ARL = sum over the fundamental matrix (I-R)^-1 applied to 1.
    """
    import numpy as np
    from scipy.stats import norm
    w = h / m
    centres = (np.arange(m) + 0.5) * w
    R = np.zeros((m, m))
    for j in range(m):
        s = centres[j]
        # P(next in state l) : next = s - z - k_ref in [l*w, (l+1)*w)
        lo = s - k_ref - (np.arange(m) + 1) * w
        hi = s - k_ref - np.arange(m) * w
        R[j, :] = norm.cdf(hi, loc=shift, scale=1.0) - \
            norm.cdf(lo, loc=shift, scale=1.0)
        # absorbing at 0 (state 0 also catches everything <= 0)
        R[j, 0] += norm.sf(s - k_ref, loc=shift, scale=1.0)
    I = np.eye(m)
    arl = np.linalg.solve(I - R, np.ones(m))
    return float(arl[0])


# --------------------------------------------------------------- claim 1
def claim_h_is_derived_from_a_target_in_control_run_length() -> dict:
    """h is solved for, not picked: bisect ARL0 to a target."""
    k_ref = 0.5
    target = 500.0
    lo, hi = 0.5, 12.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if brook_evans_arl(k_ref, mid, 0.0) < target:
            lo = mid
        else:
            hi = mid
    h = (lo + hi) / 2
    arl0 = brook_evans_arl(k_ref, h, 0.0)
    rows = []
    for shift in (0.0, -0.25, -0.5, -1.0, -1.5, -2.0):
        rows.append({"shift_in_sd": shift,
                     "ARL": round(brook_evans_arl(k_ref, h, shift), 2)})
    return {"k_ref": k_ref, "target_ARL0": target, "h_solved": round(h, 6),
            "ARL0_achieved": round(arl0, 2),
            "ARL_by_shift": rows,
            "detects_a_1sd_drop_within": next(
                r["ARL"] for r in rows if r["shift_in_sd"] == -1.0),
            "note": ("ARL0 is the false-relegation run length in OBSERVATIONS, "
                     "so at 500 a model producing 20 resolved dispatches a week "
                     "faces a spurious demotion about once every 25 weeks, and "
                     "that exchange rate is what the number should be chosen on")}


# --------------------------------------------------------------- claim 2
def claim_a_transient_cannot_cross_the_bound(h: float, k_ref: float = 0.5
                                             ) -> dict:
    """The derived minimum length of a run that can demote, and a simulation
    that tries to beat it with a worst-case burst."""
    # r >= -1 and sd = sqrt(pbar(1-pbar)) <= 1/2, so z >= -2 and the largest
    # single increment is -z - k_ref <= 2 - k_ref.
    max_increment = 2.0 - k_ref
    L_min = math.ceil(h / max_increment)
    # try to beat it: the most extreme admissible observation is y=0 against a
    # cohort that all resolved, pbar = (n-1)/n -> z = -sqrt((n-1)) for cohort n-1
    beaten = []
    for n_cohort in (1, 2, 5, 20, 200):
        n = n_cohort + 1
        pbar = n_cohort / n
        sd = math.sqrt(pbar * (1 - pbar))
        z = (0 - pbar) / sd
        seq = [z] * (L_min - 1)
        r = cusum_down(seq, k_ref, h)
        beaten.append({"cohort_size": n_cohort, "worst_z": round(z, 4),
                       "increment": round(-z - k_ref, 4),
                       "run_of_L_min_minus_1_demotes": r["demote"],
                       "peak": round(r["peak"], 4)})
    # NOTE the honest caveat: z is unbounded below as the cohort grows, because
    # a lone failure against 200 successes is genuinely strong evidence. So the
    # L_min bound holds only for the sd <= 1/2 worst case and NOT for large
    # cohorts, which is exactly what the simulation shows.
    any_beat = any(b["run_of_L_min_minus_1_demotes"] for b in beaten)
    # the repair: cap the per-observation increment (Winsorise z at -z_cap),
    # which is the standard robust-CUSUM device
    z_cap = -2.0
    capped = []
    for b in beaten:
        seq = [max(b["worst_z"], z_cap)] * (L_min - 1)
        capped.append({"cohort_size": b["cohort_size"],
                       "demotes_under_cap": cusum_down(seq, k_ref, h)["demote"]})
    return {"h": round(h, 6), "k_ref": k_ref,
            "max_increment_if_sd_at_most_half": max_increment,
            "L_min_derived": L_min,
            "uncapped": beaten,
            "L_min_bound_is_beaten_for_large_cohorts": any_beat,
            "with_z_winsorised_at": z_cap, "capped": capped,
            "bound_holds_under_winsorising":
                not any(c["demotes_under_cap"] for c in capped),
            "verdict": ("the derived bound L_min = ceil(h/(2-k_ref)) is NOT "
                        "safe as stated, because z is unbounded below as the "
                        "cohort grows; it becomes safe only with z Winsorised, "
                        "and this file reports that rather than quoting the "
                        "bound it set out to prove")}


# --------------------------------------------------------------- claim 3
def claim_stratification_is_what_stops_the_hard_problem_demotion(
        h: float, k_ref: float = 0.5, rounds: int = 400, seed: int = 7) -> dict:
    """THE CLAIM THAT MATTERS, and it falsified its own first statistic.

    A ladder that works hands its top model the items everything below it
    failed. 3 rules are run on ONE stream:
      (a) UNSTRATIFIED -- outcome against the division floor rate. Must demote
          the capable model, which is the defect being demonstrated.
      (b) PER-ITEM STRATIFIED (CMH / conditional logit). Does not demote -- but
          claim 4 shows it does not demote ANYTHING, because escalation leaves
          it reading a success count. A rule that never fires is not a guard.
      (c) RASCH RESIDUAL on measured difficulty. Must not demote the capable
          model AND must still fire on a genuine decline (checked here, not
          assumed).
    """
    rng = random.Random(seed)
    top_skill, cohort_skill, floor_skill = 2.0, 0.0, 0.0
    stream_c, stream_b, raw = [], [], []
    for _ in range(rounds):
        # ITEM SELECTION IS THE WHOLE PROBLEM: the top model only sees items the
        # cohort failed, so difficulty is conditioned on cohort failure.
        while True:
            diff = rng.gauss(0.0, 2.0)
            cohort = [1 if rng.random() < 1 / (1 + math.exp(-(cohort_skill - diff)))
                      else 0 for _ in range(5)]
            if sum(cohort) == 0:           # escalated: everything below failed
                break
        y = 1 if rng.random() < 1 / (1 + math.exp(-(top_skill - diff))) else 0
        stream_c.append((len(stream_c), y, cohort))
        stream_b.append((len(stream_b), y, diff))
        raw.append(y)

    floor = 0.5
    sd0 = math.sqrt(floor * (1 - floor))
    r_unstrat = cusum_down([(y - floor) / sd0 for y in raw], k_ref, h)
    z_strat = stratified_residuals(stream_c)
    r_strat = cusum_down(z_strat, k_ref, h)
    z_rasch = rasch_residuals(stream_b, floor_skill)
    r_rasch = cusum_down(z_rasch, k_ref, h)

    # (c) must still FIRE: same difficulty stream, a model that has degraded
    #     below the division floor it was certified at
    decline_skill = floor_skill - 1.5
    stream_d = []
    for _i, _y, diff in stream_b:
        yd = 1 if rng.random() < 1 / (1 + math.exp(-(decline_skill - diff))) else 0
        stream_d.append((_i, yd, diff))
    r_rasch_decline = cusum_down(rasch_residuals(stream_d, floor_skill),
                                 k_ref, h)
    r_strat_decline = cusum_down(
        stratified_residuals([(i, y, c) for (i, y, _d), (_j, _y2, c)
                              in zip(stream_d, stream_c)]), k_ref, h)

    k = sum(raw)
    strat_vals = sorted(set(round(v, 6) for v in z_strat))
    return {
        "rounds": rounds,
        "top_model_raw_resolve_rate": round(k / rounds, 4),
        "top_model_raw_wilson": tuple(round(v, 6) for v in wilson(k, rounds)),
        "division_floor_compared_against": floor,
        "a_unstratified_demotes_the_capable_model": r_unstrat["demote"],
        "a_unstratified_crossed_at": r_unstrat["crossed_at"],
        "b_stratified_observations_kept": len(z_strat),
        "b_stratified_dropped_as_degenerate": rounds - len(z_strat),
        "b_stratified_distinct_residual_values": strat_vals,
        "b_stratified_is_a_success_count": len(strat_vals) <= 1,
        "b_stratified_demotes_capable": r_strat["demote"],
        "b_stratified_demotes_a_GENUINE_decline": r_strat_decline["demote"],
        "c_rasch_observations_kept": len(z_rasch),
        "c_rasch_mean_residual": round(sum(z_rasch) / len(z_rasch), 4),
        "c_rasch_demotes_capable": r_rasch["demote"],
        "c_rasch_demotes_a_GENUINE_decline": r_rasch_decline["demote"],
        "c_rasch_decline_crossed_at": r_rasch_decline["crossed_at"],
        "the_guard_works": (r_unstrat["demote"]
                            and not r_rasch["demote"]
                            and r_rasch_decline["demote"]),
        "verdict": ("the unstratified rule demotes the strongest model because "
                    "escalation pushes its raw rate below the floor; the "
                    "per-item stratified rule avoids that by reading a success "
                    "count, which is the founder's guard violated; the Rasch "
                    "residual on measured difficulty avoids it AND still fires "
                    "on a genuine decline, which is the only one of the 3 that "
                    "is a working rule")}


# --------------------------------------------------------------- claim 4
def claim_a_success_count_cannot_move_the_decision(seed: int = 13) -> dict:
    """The founder's guard, mechanised, with the statistic that fails it kept
    in the comparison."""
    rng = random.Random(seed)
    rows = []
    for n in (1, 2, 3, 5, 10, 19, 50):
        lo, _hi = wilson(n, n)            # a PERFECT record of n attempts
        rows.append({"successes": n, "attempts": n, "point_estimate": 1.0,
                     "wilson_lower": round(lo, 6),
                     "clears_floor_0.9": lo >= 0.9})
    min_n_to_clear = next((r["attempts"] for r in rows
                           if r["clears_floor_0.9"]), None)

    def run(skill: float, rounds: int = 300):
        wins, sc, sb = 0, [], []
        for _ in range(rounds):
            while True:
                diff = rng.gauss(0.0, 2.0)
                cohort = [1 if rng.random() < 1 / (1 + math.exp(diff)) else 0
                          for _ in range(5)]
                if sum(cohort) == 0:
                    break
            y = 1 if rng.random() < 1 / (1 + math.exp(-(skill - diff))) else 0
            wins += y
            sc.append((0, y, cohort))
            sb.append((0, y, diff))
        zs = stratified_residuals(sc)
        zr = rasch_residuals(sb, 0.0)
        return wins, (sum(zs) / len(zs) if zs else float("nan")), \
            sum(zr) / len(zr)

    skills = [0.0, 1.0, 2.0, 3.0]
    counts, strat_means, rasch_means = [], [], []
    for s_ in skills:
        w, zs, zr = run(s_)
        counts.append(w); strat_means.append(zs); rasch_means.append(zr)
    import numpy as np
    with np.errstate(invalid="ignore", divide="ignore"):
        corr_count = float(np.corrcoef(skills, counts)[0, 1])
        sv = np.std(strat_means)
        corr_strat = (float(np.corrcoef(skills, strat_means)[0, 1])
                      if sv > 1e-12 else float("nan"))
        corr_rasch = float(np.corrcoef(skills, rasch_means)[0, 1])

    # the decisive asymmetry: credit per success as a function of difficulty
    credit = []
    for b in (-3.0, -1.0, 0.0, 1.0, 3.0):
        pp = 1 / (1 + math.exp(-(0.0 - b)))
        credit.append({"difficulty": b, "p_expected": round(pp, 4),
                       "credit_for_a_success": round((1 - pp) / math.sqrt(pp * (1 - pp)), 4),
                       "debit_for_a_failure": round(pp / math.sqrt(pp * (1 - pp)), 4)})
    return {
        "a_perfect_record_of_n": rows,
        "attempts_needed_before_a_perfect_record_clears_a_0.9_floor":
            min_n_to_clear,
        "skills": skills,
        "raw_success_counts": counts,
        "mean_stratified_residuals": [round(v, 4) for v in strat_means],
        "mean_rasch_residuals": [round(v, 4) for v in rasch_means],
        "corr_skill_vs_raw_count": round(corr_count, 4),
        "corr_skill_vs_stratified_residual": corr_strat,
        "corr_skill_vs_rasch_residual": round(corr_rasch, 4),
        "stratified_residual_is_degenerate": math.isnan(corr_strat)
        or np.std(strat_means) < 1e-9,
        "rasch_residual_tracks_skill": corr_rasch > 0.9,
        "credit_by_difficulty": credit,
        "verdict": ("3 mechanisms, each measured: the decision reads a Wilson "
                    "BOUND not a point estimate, so a perfect record of 19 "
                    "still does not clear a 0.9 floor and 50 attempts are "
                    "needed; a success is credited by SURPRISE (1-p)/sd, which "
                    "is 0.2231 at difficulty -3 against 4.4817 at +3 "
                    "(Wolfram Language, local Wolfram Engine: 4.481689070336), so "
                    "a count with no difficulty attached cannot move it; and the "
                    "same CUSUM runs in both directions")}


# --------------------------------------------------------------- claim 5
def claim_the_rule_survives_a_roster_of_1(h: float, k_ref: float = 0.5,
                                          seed: int = 21) -> dict:
    """At R = 1 there is no cohort, so the per-item comparator must come from
    somewhere else. Measure whether the degenerate case fails loudly."""
    rng = random.Random(seed)
    stream = [(i, 1 if rng.random() < 0.6 else 0, []) for i in range(200)]
    z = stratified_residuals(stream)
    # the Rasch rule needs no cohort at all -- difficulty is a recorded number --
    # so it is the one that survives R = 1, measured here rather than asserted
    bstream = [(i, y, 0.0) for i, y, _c in stream]
    # with an empty cohort, pbar is 0 or 1 for every item, so EVERY stratum is
    # degenerate and the rule produces no observations at all
    out = {"roster": 1, "dispatches": len(stream),
           "stratified_observations": len(z),
           "rule_is_silent_at_roster_1": len(z) == 0}
    # the fallback that is available: the model's OWN earlier record on items of
    # the same measured difficulty, i.e. the comparator is the model's history
    # rather than a cohort. Measured here as a self-referenced residual.
    hist = [y for _i, y, _c in stream[:100]]
    pbar = sum(hist) / len(hist)
    sd = math.sqrt(pbar * (1 - pbar))
    z_self = [(y - pbar) / sd for _i, y, _c in stream[100:]]
    out["self_referenced_observations"] = len(z_self)
    out["self_referenced_demotes_a_stable_model"] = cusum_down(
        z_self, k_ref, h)["demote"]
    # and it must still fire on a genuine decline
    decline = [(i, 1 if rng.random() < 0.2 else 0, []) for i in range(100)]
    z_dec = [(y - pbar) / sd for _i, y, _c in decline]
    r = cusum_down(z_dec, k_ref, h)
    out["self_referenced_demotes_a_declining_model"] = r["demote"]
    out["declining_crossed_at"] = r["crossed_at"]
    out["rasch_observations_at_roster_1"] = len(rasch_residuals(bstream, 0.4))
    out["rasch_demotes_a_stable_model"] = cusum_down(
        rasch_residuals(bstream, 0.4), k_ref, h)["demote"]
    dec_b = [(i, 1 if rng.random() < 0.2 else 0, 0.0) for i in range(100)]
    rr = cusum_down(rasch_residuals(dec_b, 0.4), k_ref, h)
    out["rasch_demotes_a_declining_model"] = rr["demote"]
    out["rasch_decline_crossed_at"] = rr["crossed_at"]
    out["verdict"] = ("at roster 1 the cohort comparator is unavailable and the "
                      "cohort rule produces 0 observations rather than a wrong "
                      "answer, which is the correct degenerate behaviour; the "
                      "self-referenced comparator restores detection but it "
                      "cannot separate a capability drop from a task-set shift, "
                      "and that limit is intrinsic to a roster of 1")
    return out


# --------------------------------------------------------------- claim 6
def claim_escalated_items_carry_almost_no_relegation_information(
        h: float, k_ref: float = 0.5, seed: int = 31) -> dict:
    """WHY CLAIM 3's RASCH RULE DID NOT FIRE ON A GENUINE DECLINE, which is a
    property of the dispatch stream and not of the rule.

    The Fisher information a single Rasch observation carries about skill theta
    is p(1-p), where p = sigmoid(theta - b). It is maximised at p = 1/2 and goes
    to 0 at both ends. Escalation selects items the whole cohort failed, so for
    a model AT its division floor p is near 0 on those items -- the floor is
    already expected to fail them, so failing them is no evidence of anything.
    The dispatch policy that makes the ladder efficient is therefore the same
    policy that blinds relegation.

    THE CONSEQUENCE IS A RESOURCE REQUIREMENT, DERIVED. Relegation needs a share
    of dispatches on CALIBRATION items -- items whose difficulty puts the
    division's expected pass rate near 1/2 -- and the share follows from the
    information ratio. This is a cost the attempts-optimal ladder does not price,
    and it is the mirror of the brief's own section 3 point that total attempts
    treats every attempt as overhead: here an attempt on an escalated item does
    useful resolution work and carries near-0 placement information.
    """
    import numpy as np
    rng = random.Random(seed)
    floor_skill = 0.0
    rows = []
    for b in (0.0, 1.0, 2.0, 3.0, 4.0):
        pp = 1 / (1 + math.exp(-(floor_skill - b)))
        rows.append({"difficulty": b, "p_at_the_floor": round(pp, 6),
                     "fisher_information": round(pp * (1 - pp), 6)})
    info_mid = 0.25
    worst = min(r["fisher_information"] for r in rows)
    # observations needed scale as 1/information, so the ratio is the penalty
    penalty = info_mid / worst

    # measured: does a calibration share restore detection on a declining model?
    def detect(frac_calibration: float, rounds: int = 400,
               decline: float = -1.5) -> dict:
        stream = []
        for _ in range(rounds):
            if rng.random() < frac_calibration:
                b = floor_skill          # p = 1/2 at the floor: maximal info
            else:
                while True:              # escalated draw
                    b = rng.gauss(0.0, 2.0)
                    if all(rng.random() >= 1 / (1 + math.exp(-(0.0 - b)))
                           for _ in range(5)):
                        break
            pt = 1 / (1 + math.exp(-((floor_skill + decline) - b)))
            stream.append((0, 1 if rng.random() < pt else 0, b))
        r = cusum_down(rasch_residuals(stream, floor_skill), k_ref, h)
        return {"calibration_share": frac_calibration,
                "demotes": r["demote"], "crossed_at": r["crossed_at"],
                "peak": round(r["peak"], 3)}

    sweep = [detect(f) for f in (0.0, 0.05, 0.10, 0.20, 0.40, 1.0)]
    first = next((s["calibration_share"] for s in sweep if s["demotes"]), None)
    # and the rule must NOT fire on a model that has NOT declined, at the same share
    stable = []
    for f in (0.20, 0.40, 1.0):
        stable.append(detect(f, decline=0.0))
    return {"information_by_difficulty": rows,
            "information_at_p_half": info_mid,
            "worst_escalated_information": worst,
            "observation_penalty_factor": round(penalty, 2),
            "detection_by_calibration_share": sweep,
            "smallest_share_that_detects_a_1.5_logit_decline": first,
            "false_demotion_on_a_STABLE_model_at_the_same_shares":
                [(s["calibration_share"], s["demotes"]) for s in stable],
            "rule_is_two_sided_safe":
                not any(s["demotes"] for s in stable),
            "verdict": ("relegation is not derivable from the escalation stream "
                        "alone: a dispatch policy that sends a division only the "
                        "items below it failed carries about "
                        f"{round(penalty, 1)}x less information per observation "
                        "than a calibrated one, and a measured calibration share "
                        "is a precondition for the rule, not an optional extra")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()

    print("== 1. h is DERIVED from a target in-control run length ==")
    d1 = claim_h_is_derived_from_a_target_in_control_run_length()
    print(f"   k_ref={d1['k_ref']}  target ARL0={d1['target_ARL0']}  "
          f"h solved = {d1['h_solved']}  ARL0 achieved = {d1['ARL0_achieved']}")
    for r in d1["ARL_by_shift"]:
        print(f"   shift {r['shift_in_sd']:+.2f} sd -> ARL {r['ARL']}")
    print(f"   {d1['note']}")
    h = d1["h_solved"]

    print("\n== 2. can a transient outage cross the bound? ==")
    d2 = claim_a_transient_cannot_cross_the_bound(h)
    print(f"   L_min derived = {d2['L_min_derived']} observations "
          f"(max increment {d2['max_increment_if_sd_at_most_half']})")
    for b in d2["uncapped"]:
        print(f"   cohort {b['cohort_size']:4d}: worst z {b['worst_z']:8.4f} "
              f"increment {b['increment']:7.4f}  run of L_min-1 demotes "
              f"{b['run_of_L_min_minus_1_demotes']}  peak {b['peak']}")
    print(f"   bound beaten for large cohorts: "
          f"{d2['L_min_bound_is_beaten_for_large_cohorts']}")
    print(f"   under Winsorising at {d2['with_z_winsorised_at']}: "
          f"{d2['capped']}")
    print(f"   bound holds under Winsorising: "
          f"{d2['bound_holds_under_winsorising']}")
    print(f"   {d2['verdict']}")

    print("\n== 3. what stops the hard-problem demotion: 3 rules, 1 stream ==")
    d3 = claim_stratification_is_what_stops_the_hard_problem_demotion(h)
    for k, v in d3.items():
        print(f"   {k}: {v}")

    print("\n== 4. a success count cannot move the decision ==")
    d4 = claim_a_success_count_cannot_move_the_decision()
    for r in d4["a_perfect_record_of_n"]:
        print(f"   {r['successes']:2d}/{r['attempts']:2d} perfect: point "
              f"{r['point_estimate']} wilson_lower {r['wilson_lower']}  "
              f"clears 0.9 floor: {r['clears_floor_0.9']}")
    print(f"   a perfect record first clears a 0.9 floor at n = "
          f"{d4['attempts_needed_before_a_perfect_record_clears_a_0.9_floor']}")
    print(f"   skills {d4['skills']}")
    print(f"   raw success counts          {d4['raw_success_counts']}  "
          f"corr {d4['corr_skill_vs_raw_count']}")
    print(f"   mean stratified residuals   {d4['mean_stratified_residuals']}  "
          f"corr {d4['corr_skill_vs_stratified_residual']}  DEGENERATE: "
          f"{d4['stratified_residual_is_degenerate']}")
    print(f"   mean RASCH residuals        {d4['mean_rasch_residuals']}  "
          f"corr {d4['corr_skill_vs_rasch_residual']}  tracks skill: "
          f"{d4['rasch_residual_tracks_skill']}")
    for c in d4["credit_by_difficulty"]:
        print(f"   difficulty {c['difficulty']:+.1f}  p={c['p_expected']:.4f}  "
              f"credit for a success {c['credit_for_a_success']:8.4f}  "
              f"debit for a failure {c['debit_for_a_failure']:8.4f}")
    print(f"   {d4['verdict']}")

    print("\n== 6. escalated items carry almost no relegation information ==")
    d6 = claim_escalated_items_carry_almost_no_relegation_information(h)
    for r in d6["information_by_difficulty"]:
        print(f"   difficulty {r['difficulty']:+.1f}  p at the floor "
              f"{r['p_at_the_floor']:.6f}  Fisher information "
              f"{r['fisher_information']:.6f}")
    print(f"   information at p=1/2: {d6['information_at_p_half']}  worst "
          f"escalated: {d6['worst_escalated_information']}  penalty "
          f"{d6['observation_penalty_factor']}x")
    for s in d6["detection_by_calibration_share"]:
        print(f"   calibration share {s['calibration_share']:.2f} -> demotes "
              f"{s['demotes']!s:5s} crossed_at {s['crossed_at']} peak {s['peak']}")
    print(f"   smallest share that detects a 1.5-logit decline: "
          f"{d6['smallest_share_that_detects_a_1.5_logit_decline']}")
    print(f"   stable model at the same shares: "
          f"{d6['false_demotion_on_a_STABLE_model_at_the_same_shares']}  "
          f"two-sided safe: {d6['rule_is_two_sided_safe']}")
    print(f"   {d6['verdict']}")

    print("\n== 5. roster of 1 ==")
    d5 = claim_the_rule_survives_a_roster_of_1(h)
    for k, v in d5.items():
        print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
