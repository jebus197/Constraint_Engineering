# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_severity_ruler_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ba524b996e9afd56c0765815ca521ade2855ef9c90ca43e6ad92c1c148a33ed6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Do the 2 severity de-coarsening fixes compose? NO -- measured, 0/62 and a
lost guarantee. Joint round 2026-10-18, fable seat.

The two blind fixes: cc2's smoothing (Phi((sev-0.7)/sigma) in place of the
hard indicator) and fable's pooling (star-median severity into the same
indicator). The natural composition is Phi((star_median-0.7)/(sigma*c_k)).
Executed over every archived catalogue with a settled registry (62):

  * the composition changes NO quiescence verdict relative to the smoothing
    alone (0/62), tail predicate and all-rounds predicate alike;
  * the pooled indicator changes NO quiescence verdict relative to the hard
    ruler (0/62);
  * at the 0.5 decision line the composition disagrees with the smoothing on
    exactly 14 archived entries -- ALL 14 falsifier-CONFIRMED criticals pulled
    BELOW 0.5, none pulled above. The composition loses the smoothing's
    one-way (conservative) guarantee and loses it in the anti-tool direction.

Under the founder's composability ruling (2026-10-02): no measured advantage,
one measured regression -> build the smoothing alone. These tests pin both
halves of that measurement so the refusal stays evidenced.
"""
from __future__ import annotations

import json
import math
import pathlib
import statistics
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

import reference_runner_v3 as rr  # noqa: E402
import severity_instrument as si  # noqa: E402

LEG3 = "leg3_final_shakedown_20261015T220118Z"
FREE1 = "free_run1_directive_whole_20261015T061123Z_20261015T061124Z"

#: SD of the median of k independent normal assessments, as a multiple of the
#: per-assessment sigma. k=1 exact; k=2 exact (median of 2 IS the mean of 2);
#: k=3,5 by quadrature on the order-statistic density (SciPy), confirmed to 10
#: digits by Wolfram Language (local Wolfram Engine): 0.6698291607404084,
#: 0.5355685405302014. k=4,6,8 by seeded Monte Carlo (4e6 draws).
MEDIAN_SD = {1: 1.0, 2: 1 / math.sqrt(2), 3: 0.66983, 4: 0.54605,
             5: 0.53557, 6: 0.46325, 7: 0.45880, 8: 0.41005}


class _Reg:
    def __init__(self, entries):
        self.entries = entries


def _catalogues():
    out = []
    for p in sorted((ROOT / "bench" / "logs").glob("*/runner_state.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        entries = (d.get("registry") or {}).get("entries")
        if not entries:
            continue
        nc = d.get("novelty_counts") or []
        mr = max(len(nc) - 1,
                 max((e.get("open_since_round") or 0) for e in entries.values()))
        out.append((p.parent.name, entries, mr))
    return out


CATS = _catalogues()


def _entries(run):
    return json.loads((ROOT / "bench" / "logs" / run /
                       "runner_state.json").read_text())["registry"]["entries"]


def _star(cid, entries):
    members = [cid]
    for occ in entries[cid].get("occasions") or []:
        fc = occ.get("from_canonical")
        if (occ.get("via") == "codiscovery" and fc and fc != cid
                and fc in entries and fc not in members):
            members.append(fc)
    return members


def _pooled(cid, entries):
    ms = _star(cid, entries)
    return statistics.median(
        float(entries[m].get("severity") or 0.0) for m in ms), len(ms)


def _composed_weight(cid, entries):
    e = entries[cid]
    if str(e.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
        return 0.0
    med, k = _pooled(cid, entries)
    sd = si.SEVERITY_INSTRUMENT_SIGMA * MEDIAN_SD[min(k, 8)]
    return si._phi((med - si.CRITICAL_SEVERITY_THRESHOLD_MIRROR) / sd)


def _soft_series(entries, mr, weight_of):
    s = [0.0] * (mr + 1)
    for cid, e in entries.items():
        r = e.get("open_since_round")
        if r is None or r < 0 or r > mr:
            continue
        if e.get("status") in si.NON_NOVEL_TERMINAL_STATUSES_MIRROR:
            continue
        s[r] += weight_of(cid, e)
    return s


def test_the_mirrored_constants_match_production():
    assert si.CRITICAL_SEVERITY_THRESHOLD_MIRROR == rr.CRITICAL_SEVERITY_THRESHOLD
    assert si.NON_NOVEL_TERMINAL_STATUSES_MIRROR == frozenset(
        rr._NON_NOVEL_TERMINAL_STATUSES)


def test_the_sigma_zero_member_is_the_production_ruler():
    """Additive-standard discharge: nothing is removed -- the hard indicator
    is the sigma=0 member of the Phi family, value-for-value, every catalogue.

    REFUTED-verdict entries are the one deliberate divergence (annihilation);
    they are excluded from this comparison and pinned by their own test."""
    assert CATS, "no archived catalogues discovered"
    for name, entries, mr in CATS:
        live = {cid: e for cid, e in entries.items()
                if str(e.get("falsifier_verdict") or "").strip().upper()
                != "REFUTED"}
        _, hard = rr._settled_novelty_series(_Reg(live), mr)
        limit = si.expected_critical_series(_Reg(live), mr, sigma=0.0)
        assert [int(w) for w in limit] == hard, (
            f"sigma->0 series diverges from production on {name}: "
            f"{limit} != {hard}")


def test_phi_at_the_threshold_is_exactly_half():
    w = si.critical_weight({"severity": rr.CRITICAL_SEVERITY_THRESHOLD})
    assert w == pytest.approx(0.5, abs=1e-15)


def test_refuted_is_annihilated_exactly():
    e = _entries(LEG3)["C0018"]
    assert str(e.get("falsifier_verdict")).upper() == "REFUTED"
    assert si.critical_weight(e) == 0.0, (
        "a disproved finding must be ANNIHILATED, not merely reduced")


def test_the_one_way_property_holds_on_the_whole_archive():
    """Theorem: countable, sev >= thr, not REFUTED => w >= 1/2. Hence a
    quiescent soft tail implies a quiescent hard tail. Checked per-entry and
    per-run over all 62 catalogues."""
    violations = []
    for name, entries, mr in CATS:
        for cid, e in entries.items():
            if e.get("status") in si.NON_NOVEL_TERMINAL_STATUSES_MIRROR:
                continue
            if str(e.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
                continue
            if float(e.get("severity") or 0.0) >= rr.CRITICAL_SEVERITY_THRESHOLD:
                if si.critical_weight(e) < 0.5:
                    violations.append((name, cid))
        _, hard = rr._settled_novelty_series(_Reg(entries), mr)
        soft = si.expected_critical_series(_Reg(entries), mr)
        hard_tail = hard[-3:] if len(hard) >= 3 else hard
        if si.tail_is_quiescent_soft(soft) and not all(c == 0 for c in hard_tail):
            violations.append((name, "RUN-LEVEL"))
    assert not violations, (
        f"ONE-WAY PROPERTY VIOLATED -- the soft rule permitted where the hard "
        f"rule refused: {violations}")


def test_the_smoothing_reaches_7_runs_all_in_the_strict_direction():
    stricter, looser = [], []
    for name, entries, mr in CATS:
        prof = si.instrument_noise_profile(_Reg(entries), mr)
        if prof["quiescence_verdict_differs"]:
            (stricter if prof["tail_is_quiescent_hard"] else looser).append(name)
    assert looser == []
    assert sorted(stricter) == [
        "commissioning_arm1_panel_20260929T194414Z",
        "commissioning_arm3_contrast_20260930T051219Z",
        "exp35_pe_20260406T152126Z",
        "exp40_slice_collision_20260518T130744Z",
        FREE1,
        "sim45_memory_20260830T235237Z",
        "sim45_postfix_20260901T231824Z_20260901T231827Z",
    ], f"reach changed: {sorted(stricter)}"


def test_leg3_through_the_production_caller():
    prof = rr.gamma_threshold_profile(_Reg(_entries(LEG3)), 4)
    blk = prof["instrument_noise_profile"]
    assert "error" not in blk, blk
    assert blk["gamma_hard"] == 1.0
    assert blk["gamma_soft"] == 0.9597          # cc2's blind number, reproduced
    assert blk["soft_tail"] == [0.2541, 0.1184, 0.4248]
    assert blk["quiescence_verdict_differs"] is False
    assert blk["deciding"] is False


def test_the_pooled_indicator_changes_no_quiescence_verdict():
    """fable's blind fix, driven through the PRODUCTION counter: 0/62 reach on
    the quiescence channel. Star-median assertions from the blind round
    reproduce (C0001 -> 0.875, C0011 -> 0.64)."""
    ents = _entries(LEG3)
    assert _pooled("C0001", ents) == (0.875, 6)
    assert _pooled("C0011", ents) == (0.64, 2)
    diffs = []
    for name, entries, mr in CATS:
        _, hard = rr._settled_novelty_series(_Reg(entries), mr)
        pooled_entries = {cid: {**e, "severity": _pooled(cid, entries)[0]}
                          for cid, e in entries.items()}
        _, pooled = rr._settled_novelty_series(_Reg(pooled_entries), mr)
        th, tp = hard[-3:], pooled[-3:]
        if (all(c == 0 for c in th)) != (all(c == 0 for c in tp)):
            diffs.append(name)
    assert diffs == [], f"pooling now reaches the quiescence verdict: {diffs}"


def test_the_composition_is_refused_on_measurement():
    """(a) 0/62: the composition never changes a quiescence verdict relative
    to the smoothing alone, under BOTH the production last-3 tail predicate
    and the all-rounds predicate. (b) Every archived entry where the two
    disagree at the 0.5 line is a falsifier-CONFIRMED critical pulled DOWN --
    the lost one-way guarantee, demonstrated on leg3 C0006."""
    verdict_diffs, crossers = [], []
    for name, entries, mr in CATS:
        soft = _soft_series(entries, mr, lambda cid, e: si.critical_weight(e))
        comp = _soft_series(entries, mr,
                            lambda cid, e: _composed_weight(cid, entries))
        for tail in (lambda s: s[-3:] if len(s) >= 3 else s, lambda s: s):
            if (all(w < 0.5 for w in tail(soft))) != \
               (all(w < 0.5 for w in tail(comp))):
                verdict_diffs.append(name)
        for cid, e in entries.items():
            if e.get("status") in si.NON_NOVEL_TERMINAL_STATUSES_MIRROR:
                continue
            w_s, w_c = si.critical_weight(e), _composed_weight(cid, entries)
            if (w_s >= 0.5) != (w_c >= 0.5):
                crossers.append((name, cid, e.get("falsifier_verdict")))
    assert verdict_diffs == [], (
        f"the composition now moves a verdict beyond the smoothing alone -- "
        f"re-run the composability measurement: {verdict_diffs}")
    assert len(crossers) == 14 and all(v == "CONFIRMED" for _, _, v in crossers), (
        f"the crosser population changed: {crossers}")
    # the sharpest single counterexample, pinned
    ents = _entries(LEG3)
    assert ents["C0006"]["falsifier_verdict"] == "CONFIRMED"
    assert float(ents["C0006"]["severity"]) == 0.9
    assert si.critical_weight(ents["C0006"]) == pytest.approx(0.9206, abs=5e-4)
    assert _composed_weight("C0006", ents) < 0.01, (
        "composition must weight this CONFIRMED 0.9-severity critical below "
        "0.01 (star [0.9, 0.45, 0.45]); if it no longer does, the refusal's "
        "evidence base has changed")
