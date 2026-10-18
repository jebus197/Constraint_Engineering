# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_severity_ruler_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1437459ff2c099dfa474f82f20c22fdcb512aa409289c82738cfa9191efcbb48
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The joint round's two open questions, decided by execution on the archive.

Q1 DO THE 2 FIXES COMPOSE? Answered NO, by measurement: composing pooled
   severity with the expected-count rule moves the quiescence verdict on 0 runs
   BEYOND the expected-count rule alone, at every swept sigma.
Q2 IS VERDICT MOVEMENT EVIDENCE OF REACH, OR OF FITTING? Answered: it is
   evidence of reach IFF the departing set is monotonically nested in the free
   parameter. On this archive it is, at all 14 swept sigmas.

Every test drives production code: `gamma_threshold_profile`,
`_settled_novelty_series`, `_estimate_gamma`, `_gamma_is_estimable`,
`_NON_NOVEL_TERMINAL_STATUSES`, `spec_verification_factor`,
`effective_severity`.
"""
import glob
import json
import math
import os
import statistics
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import bench.reference_runner_v3 as rr3                       # noqa: E402
from bench.severity_noise_sweep import (                      # noqa: E402
    SWEPT_SIGMAS, critical_weight, expected_critical_series,
    noise_robustness_profile, tail_is_quiescent_soft,
)

LOGS = os.path.join(os.path.dirname(__file__), "..", "logs")
C_K = {1: 1.0, 2: 0.7071067812, 3: 0.6698291607, 4: 0.5460765683,
       5: 0.5355685405, 6: 0.4634033519}


class _Reg:
    def __init__(self, entries):
        self.entries = entries


def _runs():
    out = []
    for p in sorted(glob.glob(os.path.join(LOGS, "*", "runner_state.json"))):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        ents = ((d.get("registry") or {}).get("entries") or {})
        if not isinstance(ents, dict) or not ents:
            continue
        rounds = [e.get("open_since_round") for e in ents.values()
                  if isinstance(e, dict) and e.get("open_since_round") is not None]
        if not rounds:
            continue
        out.append((os.path.basename(os.path.dirname(p)), _Reg(ents), max(rounds)))
    return out


RUNS = _runs()


def _star(entries):
    """fable's DIRECT codiscovery star. Reproduces that seat's published leg3
    k-distribution and C0001 -> 0.875 / C0011 -> 0.64 exactly."""
    out = {}
    for tid, t in entries.items():
        if not isinstance(t, dict):
            continue
        sevs = [float(t.get("severity") or 0.0)]
        for occ in (t.get("occasions") or []):
            if not isinstance(occ, dict) or occ.get("via") != "codiscovery":
                continue
            did = occ.get("from_canonical")
            if not did or did == tid or did not in entries:
                continue
            d = entries[did]
            if (not isinstance(d, dict) or t.get("open_since_round") is None
                    or d.get("open_since_round") is None):
                continue
            sevs.append(float(d.get("severity") or 0.0))
        out[tid] = (sevs, len(sevs))
    return out


def _series(reg, max_round, ruler, naive=False, sigma=0.1419):
    """hard / soft / pooled / composed, sharing ONE admission filter."""
    stars = _star(reg.entries) if ruler in ("pooled", "composed") else None
    buckets = [[] for _ in range(max_round + 1)]
    for e in reg.entries.values():
        if not isinstance(e, dict):
            continue
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in rr3._NON_NOVEL_TERMINAL_STATUSES:
            continue
        buckets[r].append(e)
    out = []
    for bucket in buckets:
        tot = 0.0
        for e in bucket:
            sev, k = float(e.get("severity") or 0.0), 1
            if stars is not None:
                sevs, k = stars.get(e.get("canonical_id") or "", ([sev], 1))
                sev = statistics.median(sevs)
            if ruler in ("hard", "pooled"):
                tot += 1.0 if sev >= rr3.CRITICAL_SEVERITY_THRESHOLD else 0.0
            else:
                s = sigma if (ruler == "soft" or naive) else sigma * C_K.get(
                    k, C_K[6] * math.sqrt(6.0 / max(k, 1)))
                tot += critical_weight(sev, e.get("falsifier_verdict") or "",
                                       rr3.CRITICAL_SEVERITY_THRESHOLD, s)
        out.append(tot)
    return out


def _q_hard(s):
    tail = s[-3:] if len(s) >= 3 else list(s)
    return bool(tail) and all(c == 0 for c in tail)


# ---------------------------------------------------------------- Q1: compose?
def test_composition_moves_no_verdict_beyond_the_expected_count_rule_alone():
    """WOULD PRINT, if composing earned its place: a non-empty list of runs
    where the composed verdict differs from the expected-count rule alone."""
    extra, pooled_only = [], []
    for run, reg, mr in RUNS:
        h = _series(reg, mr, "hard")
        s, c = _series(reg, mr, "soft"), _series(reg, mr, "composed")
        p = _series(reg, mr, "pooled")
        if tail_is_quiescent_soft(c) != tail_is_quiescent_soft(s):
            extra.append(run)
        if _q_hard(p) != _q_hard(h):
            pooled_only.append(run)
    assert extra == [], (
        f"COMPOSITION EARNS ITS PLACE after all -- it moves the verdict beyond "
        f"the expected-count rule alone on {len(extra)} run(s): {extra}")
    assert pooled_only == [], (
        f"POOLING ALONE moves the quiescence verdict on {pooled_only}; the "
        f"brief's premise that it does not would be refuted")


def test_the_composition_null_is_robust_across_the_whole_sigma_band():
    """Not an accident of 0.1419: the composition adds nothing at ANY sigma."""
    offenders = {}
    for sig in SWEPT_SIGMAS:
        for run, reg, mr in RUNS:
            s = _series(reg, mr, "soft", sigma=sig)
            c = _series(reg, mr, "composed", sigma=sig)
            if tail_is_quiescent_soft(c) != tail_is_quiescent_soft(s):
                offenders.setdefault(sig, []).append(run)
    assert offenders == {}, (
        f"the composition's null result is sigma-dependent: {offenders}")


def test_pooling_cannot_reach_the_deciding_tail_structurally():
    """WHY the composition is null: pooling acts on 9 of 734 tail entries."""
    tail_entries = multi = 0
    for _run, reg, mr in RUNS:
        stars = _star(reg.entries)
        buckets = [[] for _ in range(mr + 1)]
        for e in reg.entries.values():
            if not isinstance(e, dict):
                continue
            r = e.get("open_since_round")
            if (r is None or r < 0 or r > mr
                    or e.get("status") in rr3._NON_NOVEL_TERMINAL_STATUSES):
                continue
            buckets[r].append(e)
        for b in (buckets[-3:] if len(buckets) >= 3 else buckets):
            for e in b:
                tail_entries += 1
                if stars.get(e.get("canonical_id") or "", ([0.0], 1))[1] >= 2:
                    multi += 1
    assert tail_entries == 734, f"archive shape changed: {tail_entries}"
    assert multi == 9, f"k>=2 entries in deciding tails moved: {multi}"
    assert multi / tail_entries < 0.05, "pooling now reaches the tail -- RE-TEST"


# ----------------------------------------------------- Q2: reach, or fitted?
def test_the_departing_set_is_monotonically_nested_in_sigma():
    """THE DISCRIMINATOR. A fitted de-coarsening departs near the committed
    sigma and returns either side. WOULD PRINT, if fitted: the run and the
    sigma at which it stopped departing."""
    sets = []
    for sig in SWEPT_SIGMAS:
        f = set()
        for run, reg, mr in RUNS:
            h, s = _series(reg, mr, "hard"), _series(reg, mr, "soft", sigma=sig)
            if tail_is_quiescent_soft(s) != _q_hard(h):
                f.add(run)
        sets.append((sig, f))
    for (s1, a), (s2, b) in zip(sets, sets[1:]):
        assert a <= b, (
            f"NOT NESTED -- fitted signature: runs {sorted(a - b)} depart at "
            f"sigma={s1} and stop departing at sigma={s2}")
    counts = {s: len(f) for s, f in sets}
    assert counts[0.04] == 0, counts
    assert counts[0.1241] == 4, counts          # measured CI floor
    assert counts[0.1419] == 7, counts          # committed point estimate
    assert counts[0.1575] == 9, counts          # measured CI ceiling


def test_production_caller_emits_the_sweep_and_the_hard_verdict_is_untouched():
    """The addition is REACHED: gamma_threshold_profile, which the report path
    already invokes, now carries it."""
    reg, mr = next((r, m) for n, r, m in RUNS
                   if n == "free_run1_directive_whole_20261015T061123Z_20261015T061124Z")
    prof = rr3.gamma_threshold_profile(reg, mr, 3)
    nr = prof["noise_robustness"]
    assert "error" not in nr, nr
    assert nr["verdict_flip_sigma"] == 0.1241, nr["verdict_flip_sigma"]
    assert nr["flip_inside_measured_ci"] is True
    assert nr["departs_monotonically"] is True
    assert nr["live_gate_unchanged"] is True
    # the hard profile the gate reads is byte-identical to the archived one
    live = prof["thresholds"][repr(float(rr3.CRITICAL_SEVERITY_THRESHOLD))]
    _all, crit = rr3._settled_novelty_series(reg, mr)
    assert live["critical_novelty_series"] == list(crit)
    # hard PERMITS quiescence here; the expected-count rule REFUSES it. That is
    # the one-way direction, observed rather than assumed.
    assert live["tail_is_quiescent"] is True
    assert tail_is_quiescent_soft(expected_critical_series(
        reg, mr, rr3.CRITICAL_SEVERITY_THRESHOLD,
        rr3._NON_NOVEL_TERMINAL_STATUSES)) is False


def test_sigma_to_zero_is_exactly_the_production_indicator_on_every_run():
    """The additive claim, executed value-for-value rather than asserted."""
    for run, reg, mr in RUNS:
        _all, crit = rr3._settled_novelty_series(reg, mr)
        soft0 = expected_critical_series(
            reg, mr, rr3.CRITICAL_SEVERITY_THRESHOLD,
            rr3._NON_NOVEL_TERMINAL_STATUSES, sigma=0.0)
        # sigma=0 differs from the indicator ONLY by REFUTED annihilation
        refuted = [0] * (mr + 1)
        for e in reg.entries.values():
            if not isinstance(e, dict):
                continue
            r = e.get("open_since_round")
            if (r is None or r < 0 or r > mr
                    or e.get("status") in rr3._NON_NOVEL_TERMINAL_STATUSES):
                continue
            if (str(e.get("falsifier_verdict") or "").strip().upper() == "REFUTED"
                    and (e.get("severity") or 0.0) >= rr3.CRITICAL_SEVERITY_THRESHOLD):
                refuted[r] += 1
        assert [int(a) for a in soft0] == [c - d for c, d in zip(crit, refuted)], run


def test_refuted_is_annihilated_exactly_and_phi_at_threshold_is_one_half():
    assert critical_weight(0.99, "REFUTED", 0.7, 0.1419) == 0.0
    assert critical_weight(0.7, "", 0.7, 0.1419) == pytest.approx(0.5, abs=1e-12)
    # THE NESTING CLAIM FAILS AT EXACTLY sev == thr, AND THAT IS NOT A MEASURE
    # ZERO CAVEAT. The production indicator is `sev >= thr`, so it scores a
    # finding at exactly 0.7 as 1; lim_{sigma->0+} Phi(0) is 1/2 for every
    # sigma. 0.7 is the archive's THIRD most common severity -- 174 of 3237
    # entries, 5.3753%, Wilson [4.6500%, 6.2065%] -- because models anchor on
    # the published cut itself. So "the current ruler is the sigma=0 member of
    # this family" holds for sev != thr and fails on 5.4% of the population.
    assert critical_weight(0.7, "CONFIRMED", 0.7, 1e-9) == 0.5
    assert critical_weight(0.7001, "CONFIRMED", 0.7, 1e-9) == 1.0
    assert critical_weight(0.6999, "CONFIRMED", 0.7, 1e-9) == 0.0


# ------------------------------- the other seat's fix, measured on the archive
def test_pooling_can_destroy_gamma_ESTIMABILITY_which_the_other_seat_did_not_report():
    """fable measured gamma invariance on 3 runs. Over 62 it is not invariant:
    on 1 run pooling converts an estimable gamma into the 0.0 sentinel."""
    degraded = []
    for run, reg, mr in RUNS:
        h = [int(x) for x in _series(reg, mr, "hard")]
        p = [int(x) for x in _series(reg, mr, "pooled")]
        if (rr3._gamma_is_estimable(h, 3)
                and not rr3._gamma_is_estimable(p, 3)):
            degraded.append(run)
    assert degraded == ["commissioning_arm1_panel_20260929T214647Z"], degraded
    reg, mr = next((r, m) for n, r, m in RUNS
                   if n == "commissioning_arm1_panel_20260929T214647Z")
    h = [int(x) for x in _series(reg, mr, "hard")]
    p = [int(x) for x in _series(reg, mr, "pooled")]
    assert h == [1, 0, 0, 1, 0, 0, 0, 4]
    assert p == [0, 0, 0, 0, 0, 0, 0, 4]
    assert rr3._estimate_gamma(h, 3) == pytest.approx(0.3236, abs=5e-4)
    assert rr3._estimate_gamma(p, 3) == 0.0          # the sentinel, not a slope


def test_both_seats_published_numbers_reproduce_from_this_reimplementation():
    """Cross-validation: neither seat's module exists in this sandbox, so their
    numbers are the only check that these reconstructions are theirs."""
    reg, mr = next((r, m) for n, r, m in RUNS
                   if n == "leg3_final_shakedown_20261015T220118Z")
    st = _star(reg.entries)
    assert statistics.median(st["C0001"][0]) == 0.875          # fable
    assert st["C0001"][1] == 6
    assert statistics.median(st["C0011"][0]) == 0.64           # fable
    assert [int(x) for x in _series(reg, mr, "hard")] == [12, 0, 0, 0, 0]
    assert [int(x) for x in _series(reg, mr, "pooled")] == [7, 0, 0, 0, 0]
    soft = _series(reg, mr, "soft")
    assert [round(x, 4) for x in soft[-3:]] == [0.2541, 0.1184, 0.4248]   # cc2
    assert rr3._estimate_gamma(soft, 3) == pytest.approx(0.9597, abs=5e-5)  # cc2
    # cc2's refutation condition 3, reproduced
    reg2, mr2 = next((r, m) for n, r, m in RUNS
                     if n == "prose_convergence_run1b_2026-10-02_20261002T044234Z")
    assert [int(x) for x in _series(reg2, mr2, "hard")] == [9, 4, 8]
    assert [round(x, 2) for x in _series(reg2, mr2, "soft")] == [8.78, 2.77, 7.27]
    # the §7.7 collapse both seats established, on the live instrument
    e18 = reg.entries["C0018"]
    assert rr3.spec_verification_factor(e18) == 0.0
    assert rr3.effective_severity(e18) == 0.5                  # spec off


def test_the_modal_severity_is_where_the_nesting_claim_fails_and_it_costs_a_sixth():
    """HOW MUCH the sev == threshold discontinuity costs, measured.

    Harmless for the QUIESCENCE predicate -- derived: Phi(0) = 1/2 exactly, and
    1/2 is not < 1/2, so a tail round holding such a finding is non-quiescent
    under both rulers. Measured: 0 verdict differences between the limit rule
    and the production indicator across all runs. The 0.5 cut is therefore
    better chosen than its author argued, for a reason its author did not give.

    NOT harmless for the expected-count MAGNITUDE, which a future gate may read:
    each such finding contributes 1.0 hard and 0.5 soft, and that single point
    carries 16.12% of the archive's total |hard - soft| mass. This is the
    mechanism behind the other seat's own refutation condition 3.
    """
    at_thr = total = 0
    d_total = d_mode = 0.0
    verdict_diffs = []
    for run, reg, mr in RUNS:
        for e in reg.entries.values():
            if not isinstance(e, dict) or e.get("severity") is None:
                continue
            total += 1
            if abs(float(e["severity"]) - 0.7) < 1e-12:
                at_thr += 1
        for b in ([[e for e in reg.entries.values()
                    if isinstance(e, dict)
                    and e.get("open_since_round") == r
                    and e.get("status") not in rr3._NON_NOVEL_TERMINAL_STATUSES]
                   for r in range(mr + 1)]):
            for e in b:
                sev = float(e.get("severity") or 0.0)
                w = critical_weight(sev, e.get("falsifier_verdict") or "",
                                    rr3.CRITICAL_SEVERITY_THRESHOLD, 0.1419)
                hard = 1.0 if sev >= rr3.CRITICAL_SEVERITY_THRESHOLD else 0.0
                d_total += abs(hard - w)
                if abs(sev - 0.7) < 1e-12:
                    d_mode += abs(hard - w)
        # the limit rule moves NO verdict despite the discontinuity
        lim = expected_critical_series(
            reg, mr, rr3.CRITICAL_SEVERITY_THRESHOLD,
            rr3._NON_NOVEL_TERMINAL_STATUSES, sigma=1e-9)
        _all, crit = rr3._settled_novelty_series(reg, mr)
        if tail_is_quiescent_soft(lim) != _q_hard(list(crit)):
            verdict_diffs.append(run)
    assert at_thr == 174 and total == 3237, (at_thr, total)
    assert verdict_diffs == [], (
        "the sev == threshold discontinuity MOVES a quiescence verdict on "
        f"{verdict_diffs}; the 0.5 cut no longer absorbs it")
    assert 0.15 < d_mode / d_total < 0.17, d_mode / d_total
