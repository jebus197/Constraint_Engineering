# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 11be150b3143d629efc7d6661256f807ca04d05673984ddc45839abd0ccc6431
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Falsifiers for bench/promotion_gate.py and for 3 figures in the 2026-10-08 brief.

Every test imports the REAL target module. Nothing is retyped.
Run: python3 -m pytest bench/test_promotion_gate.py -q
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import binom

from bench.promotion_gate import (
    Z95, RungRecord, derive_attempts_per_rung, derive_window_z,
    observed_difficulty, required_per_rung_pass, successes_required, wilson,
)
from bench.routing import route

ROOT = Path(__file__).resolve().parents[1]
RUNGS = 5


def _load(stem):
    p = ROOT / "bench" / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(stem.replace("-", "_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LADDER = _load("the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08")
COLD = _load("the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08")


# ---------------------------------------------------------------- F1 (framing)
def test_bound_gate_mechanism_strictly_dominates_one_success_on_BOTH_rates():
    """The brief says the bound gate is 'worse than the rule it replaces'.

    It compares true-positive rates only. Falsified if ANY (n, floor) beats the
    one-success rule on the true-positive rate AND the false-positive rate at
    once, because then the mechanism is not worse - only n=10, floor=0.50 is.
    """
    base_tpr = 0.90 ** RUNGS
    base_fpr = 0.50 ** RUNGS
    assert abs(base_tpr - 0.59049) < 1e-12
    assert abs(base_fpr - 0.03125) < 1e-12
    dominating = []
    for n in range(2, 31):
        for f in [i / 100 for i in range(5, 96, 5)]:
            k = successes_required(n, f)
            if k is None:
                continue
            tpr = float(binom.sf(k - 1, n, 0.90)) ** RUNGS
            fpr = float(binom.sf(k - 1, n, 0.50)) ** RUNGS
            if tpr > base_tpr and fpr < base_fpr:
                dominating.append((n * RUNGS, n, f, k, tpr, fpr))
    assert dominating, "no bound gate dominates -> the brief's framing stands"
    dominating.sort()
    cheapest = dominating[0]
    print(f"\n  {len(dominating)} gates dominate one-success on both rates; "
          f"cheapest cost={cheapest[0]} n={cheapest[1]} floor={cheapest[2]} "
          f"k*={cheapest[3]} TPR={cheapest[4]:.6f} FPR={cheapest[5]:.3e}")
    assert cheapest[4] > base_tpr and cheapest[5] < base_fpr


def test_the_briefs_own_parameterisation_is_the_defect_not_the_mechanism():
    """n=10, floor=0.50 forces k*=9, i.e. p-hat >= 0.90 == the good model's rate.

    A point-estimate threshold equal to the true rate puts the gate at its own
    coin-flip point, which is where 0.736 per rung and 0.21611302 overall come
    from. Reproduced against the real artefact, not restated.
    """
    d = LADDER.claim_a_bound_gate_fixes_the_asymmetry(RUNGS, 10, 0.50)
    assert d["successes_needed_per_rung"] == 9
    assert abs(d[0.90]["P_reaches_top_rung"] - 0.21611302) < 1e-8
    assert abs(9 / 10 - 0.90) < 1e-12, "implied threshold equals p_good"
    fpr = float(binom.sf(8, 10, 0.50)) ** RUNGS
    print(f"\n  n=10 gate FPR at p=0.50: {fpr:.3e} vs one-success 3.125e-02 "
          f"-- 8 orders of magnitude apart, so the TPRs are not comparable")
    assert fpr < 0.03125 / 1e6


# ---------------------------------------------------------------- F2 (derived n)
def test_derived_attempts_per_rung_meets_the_stated_false_negative_target():
    need = required_per_rung_pass(0.05, RUNGS)
    assert abs(need - 0.95 ** 0.2) < 1e-15
    g = derive_attempts_per_rung(p_good=0.90, floor=0.50, beta=0.05, rungs=RUNGS)
    print(f"\n  derived n={g.attempts_per_rung} k*={g.successes_per_rung} "
          f"P(top|0.90)={g.p_reaches_top:.6f} cost={g.attempts_to_climb}")
    assert g.attempts_per_rung == 19 and g.successes_per_rung == 14
    assert g.p_reaches_top >= 1 - 0.05
    # and it is the SMALLEST such n
    for n in range(1, g.attempts_per_rung):
        k = successes_required(n, 0.50)
        if k is None:
            continue
        assert float(binom.sf(k - 1, n, 0.90)) < need, f"n={n} also meets it"
    # the brief's n=10 does not
    assert float(binom.sf(8, 10, 0.90)) < need


def test_power_is_not_monotone_in_n_so_no_closed_form_may_be_used():
    """k*(n, floor) steps, so more attempts can mean LESS power.

    Falsified if Q(0.90) is monotone non-decreasing in n - in which case a
    closed-form solve would be safe and the scan in derive_attempts_per_rung
    would be unjustified complexity.
    """
    q = {}
    for n in range(4, 31):
        k = successes_required(n, 0.50)
        if k is not None:
            q[n] = float(binom.sf(k - 1, n, 0.90))
    drops = [(a, b) for a, b in zip(sorted(q), sorted(q)[1:]) if q[b] < q[a]]
    print(f"\n  non-monotone steps in n: {drops[:4]} "
          f"(e.g. n=16 Q={q[16]:.6f} > n=18 Q={q[18]:.6f})")
    assert drops, "Q monotone -> the scan is unnecessary"
    assert q[18] < q[16]


def test_gate_refuses_an_undecidable_rung_rather_than_returning_a_number():
    with pytest.raises(ValueError):
        derive_attempts_per_rung(p_good=0.50, floor=0.50, beta=0.05,
                                 rungs=RUNGS, max_n=400)


# ------------------------------------------------- F3 (bidirectionality / re-test)
def _ever_promotes(p, horizon, window, floor, z, trials, seed):
    rng = np.random.default_rng(seed)
    k = successes_required(window, floor, z)
    if k is None:
        return 0.0
    hits = 0
    for _ in range(trials):
        x = (rng.random(horizon) < p).astype(np.int64)
        cs = np.concatenate(([0], np.cumsum(x)))
        if np.any(cs[window:] - cs[:-window] >= k):
            hits += 1
    return hits / trials


def test_fixed_z_resliding_window_inflates_false_promotion_to_a_coin_flip():
    """Re-reading a z=1.96 gate on every attempt is an uncorrected sequential test."""
    r = _ever_promotes(0.50, 190, 19, 0.50, Z95, trials=4000, seed=101)
    lo, hi = wilson(round(r * 4000), 4000)
    print(f"\n  P(p=0.50 model promoted somewhere in 190 attempts) at z=1.96: "
          f"{r:.4f} Wilson [{lo:.4f}, {hi:.4f}] vs single-shot 0.0318")
    assert r > 0.30, "no inflation -> no multiplicity correction needed"


def test_derived_window_z_holds_false_promotion_at_alpha_at_no_cost_in_power():
    z = derive_window_z(window=19, horizon=190, alpha=0.05)
    assert abs(z - 3.440148) < 1e-5
    fp = _ever_promotes(0.50, 190, 19, 0.50, z, trials=4000, seed=202)
    tp = _ever_promotes(0.90, 190, 19, 0.50, z, trials=1000, seed=303)
    print(f"\n  derived z={z:.6f} (k*={successes_required(19,0.50,z)}): "
          f"FP(p=0.50 over 190)={fp:.4f} <= 0.05; TP(p=0.90 over 190)={tp:.4f}")
    assert fp <= 0.05
    assert tp >= 0.95, "the correction must not cost the capable model its climb"


def _demotion_lag(mode, z, trials=1500, pre=100, post=500, window=19,
                  floor=0.50, seed=404):
    rng = np.random.default_rng(seed)
    lags = []
    for _ in range(trials):
        x = np.concatenate([(rng.random(pre) < 0.90),
                            (rng.random(post) < 0.30)]).astype(np.int64)
        cs = np.concatenate(([0], np.cumsum(x)))
        for t in range(pre + window, pre + post + 1):
            k, n = ((int(cs[t]), t) if mode == "pooled"
                    else (int(cs[t] - cs[t - window]), window))
            if wilson(k, n, z)[1] < floor:
                lags.append(t - pre)
                break
        else:
            lags.append(np.nan)
    a = np.asarray(lags, dtype=float)
    return float(np.nanmedian(a)), float(np.mean(np.isnan(a)))


def test_sliding_window_dominates_a_pooled_record_on_capability_LOST():
    """The composability rule: compose only on a demonstrated advantage.

    Falsified if the pooled record detects capability loss as fast as the
    window - in which case pooling (simpler, no multiplicity) should be used.
    """
    wl, wmiss = _demotion_lag("window", Z95)
    pl, pmiss = _demotion_lag("pooled", Z95)
    print(f"\n  attempts to demote after a 0.90 -> 0.30 drop: "
          f"window median {wl}, never {wmiss:.4f}; "
          f"pooled median {pl}, never {pmiss:.4f}")
    assert wl < pl / 5, "pooling keeps up -> prefer pooling, it is simpler"
    assert wmiss == 0.0 and pmiss > 0.0


def test_the_rung_is_held_not_granted_so_there_is_no_absorbing_state():
    """One failure must not cap a model, and lost capability must be regainable."""
    z, floor, W = Z95, 0.50, 19
    k = successes_required(W, floor, z)
    rec = RungRecord(window=W)
    for i in range(W):                      # 18 of 19 - one unlucky failure
        rec.record(i != 3)
    assert rec.successes == W - 1 >= k
    assert rec.promotes(floor, z), "one failure caps a capable model"
    assert not rec.demotes(floor, z)
    for _ in range(W):                      # capability lost
        rec.record(False)
    assert rec.demotes(floor, z) and not rec.promotes(floor, z)
    for _ in range(W):                      # capability regained - same record
        rec.record(True)
    assert rec.promotes(floor, z) and not rec.demotes(floor, z)
    print("\n  promote -> demote -> re-promote on one record, no schedule needed")


def test_failing_a_higher_rung_does_not_touch_the_lower_rungs_record():
    """Open question 1, answered mechanically."""
    z, floor, W = Z95, 0.50, 19
    low, high = RungRecord(window=W), RungRecord(window=W)
    for _ in range(W):
        low.record(True)
    for _ in range(W):
        high.record(False)
    assert low.promotes(floor, z), "rung r lost because rung r+1 failed"
    assert high.demotes(floor, z)
    # and the higher rung cannot be accumulated once it cannot be held
    assert not high.promotes(floor, z)


# ---------------------------------------------------- F4 (rungs_tried censoring)
def test_rungs_tried_is_right_censored_at_max_rungs_so_it_is_not_a_label():
    """Against the REAL route() in bench/routing.py.

    Only the 4th-strongest model can confirm. Falsified (defect present) if the
    capped call reports a depth that is indistinguishable from a resolved
    depth of 2.
    """
    models = list(["Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable"])
    finding = {"finding_id": "C0001"}

    def resolve_fn(m, f):
        return f"# {m}"

    def reverify_fn(code):
        return "CONFIRMED" if code == "# Gemini" else "REFUTED"

    capped = route(finding, models, [], resolve_fn, reverify_fn,
                   lambda a, b: 0.0, max_rungs=2)
    exhaust = route(finding, models, [], resolve_fn, reverify_fn,
                    lambda a, b: 0.0, max_rungs=0)
    d_cap, cen_cap = observed_difficulty(capped, max_rungs=2)
    d_exh, cen_exh = observed_difficulty(exhaust, max_rungs=0)
    print(f"\n  capped:   verdict={capped.verdict} rungs_tried={capped.rungs_tried} "
          f"-> depth={d_cap} censored={cen_cap}")
    print(f"  exhausted: verdict={exhaust.verdict} rungs_tried={exhaust.rungs_tried} "
          f"-> depth={d_exh} censored={cen_exh}")
    assert capped.rungs_tried == 2 and not capped.resolved
    assert exhaust.resolved and exhaust.rungs_tried == 4
    assert cen_cap is True and cen_exh is False
    assert d_cap == 2 == d_exh - 2, "true depth 4 is unobservable under the cap"


def test_duplicate_path_reports_depth_zero_which_is_not_a_difficulty():
    r = route({"finding_id": "C0002", "title": "x"},
              ["Codex"], [{"finding_id": "C0003", "title": "x"}],
              lambda m, f: "code", lambda c: "CONFIRMED",
              lambda a, b: 1.0)
    assert r.verdict == "DUPLICATE" and r.rungs_tried == 0
    assert observed_difficulty(r, max_rungs=2) == (0, False)


# ----------------------------------------------- F5/F6 (cold-start artefact)
def test_wilson_interval_on_the_tuple_share_has_no_sampling_referent():
    """min(6,N)/N is a deterministic ratio, not an estimated proportion.

    Falsified if the artefact reports a non-degenerate interval on a quantity
    that does not vary across repeated evaluation.
    """
    a = COLD.claim_the_tuple_coverage_collapses()
    b = COLD.claim_the_tuple_coverage_collapses()
    assert a == b, "the quantity varies -> an interval could be meaningful"
    lo, hi = a[70]["wilson_on_the_share"]
    print(f"\n  share at N=70 is exactly 6/70={6/70:.6f} on every evaluation, "
          f"yet the artefact reports Wilson [{lo}, {hi}]")
    assert abs(a[70]["share"] - 6 / 70) < 1e-6   # artefact rounds to 6dp
    assert hi - lo > 0.1, "degenerate interval -> no misapplication"


def test_cold_start_price_is_a_modal_estimate_with_about_50_percent_power():
    """`attempts_to_separate` evaluates at round(p*n) - the modal outcome.

    So the reported attempts have no power margin. Falsified if the achieved
    probability of separation at the artefact's own n reaches 0.80.
    """
    rng = np.random.default_rng(505)
    out = {}
    for gap in (0.40, 0.20):
        hi, lo = 0.60 + gap / 2, 0.60 - gap / 2
        n = COLD.attempts_to_separate(hi, lo)
        kh = rng.binomial(n, hi, 3000)
        kl = rng.binomial(n, lo, 3000)
        power = float(np.mean([wilson(int(x), n)[0] > wilson(int(y), n)[1]
                               for x, y in zip(kh, kl)]))
        out[gap] = (n, power)
        print(f"\n  gap={gap:.2f}: artefact n={n}, achieved separation "
              f"probability {power:.3f}")
    for gap, (n, power) in out.items():
        assert power < 0.80, f"gap={gap} already powered at n={n}"
