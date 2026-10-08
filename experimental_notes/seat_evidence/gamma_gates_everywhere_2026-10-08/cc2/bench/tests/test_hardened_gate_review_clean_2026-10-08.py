# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'gamma_gates_everywhere_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: bd26313fcf9adace854831489beb08b6852f8b5bf2edc89dad9aa08925e020e4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The hardened gate must not converge where the gate it imported from refuses.

PANEL REVIEW of 8f014a59 / ad2ae579 (opus seat, 2026-10-08).

The 2026-10-08 fix states, in the runner's own comment, that it imports "the
proven two-guard vacuity from the sibling gate ... imported rather than
re-invented". It imported the 2 guards and left behind the 2 BLOCKS that stand
in front of them in `_check_gamma_alt_convergence`: the A4 fail-safe (:8181) and
the contested block (:8219). `_check_hardened_convergence` receives the very
registry those blocks read and consulted neither, so the 2 gates returned
OPPOSITE verdicts on identical registries.

Every test here drives the REAL `FindingRegistry` through the REAL
`_settled_novelty_series`. The committed guards monkeypatch the series and pass a
stub carrying only `.entries`, which cannot express a registry where a critical
EXISTS but is invisible to the series -- and that is exactly the hole.

WHY UNCONFIRMED IS THE DANGEROUS CLASS, and the direction matters. UNCONFIRMED is
an UNRESOLVED status (:3140) that `_NON_NOVEL_TERMINAL_STATUSES` strips from the
settled series. So an unverified critical does not merely fail to block: it
DRIVES `cum_crit` DOWN and pushes the run INTO the sparse/vacuous branch. The
censoring runs toward convergence, not away from it.

BOTH BLOCKS ARE PRESENT BECAUSE NEITHER SUBSUMES THE OTHER, MEASURED. With the
A4 block alone, a registry carrying 0 unverified criticals and 4 contested
sub-criticals still converges here and is still refused by the sibling
(`test_contested_is_not_reached_by_the_a4_block`). That is the founder's
composability condition discharged by measurement rather than by judgement.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def R():
    spec = importlib.util.spec_from_file_location(
        "rr_review_clean", REPO / "bench" / "reference_runner_v3.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rr_review_clean"] = m
    spec.loader.exec_module(m)
    return m


class _Cfg:
    gamma_alt_threshold = 0.30
    gamma_alt_consecutive_zero_crit = 3
    gamma_crit_min_cumulative = 8
    gamma_alt_earliest_round = 3
    gamma_crit_sustain_rounds = 2
    gamma_crit_loo_tol = 0.05
    max_irreducible_queue = 3
    rho_threshold = 0.3
    falsifier_gate_enabled = False


def _reg(R, entries):
    """A REAL FindingRegistry. `verdicts` and `last_status_change_round` are
    present because `contested_count` reads both and a real entry always has
    them; omitting either tests a registry that cannot occur."""
    reg = R.FindingRegistry()
    for i, e in enumerate(entries):
        reg.entries[f"C{i:04d}"] = dict(
            status=e["st"], severity=e["sev"], open_since_round=e["r"],
            description=f"finding {i}", occasions=[],
            verdicts=e.get("v", []), last_status_change_round=0)
    return reg


def _both(R, reg, round_idx=5):
    """Drive BOTH gates on the identical registry and return both verdicts."""
    cfg = _Cfg()
    _all_s, crit_s = R._settled_novelty_series(reg, round_idx)
    a4 = reg.unverified_critical_count()
    ct = reg.contested_count(
        round_idx, subcritical_exclusion=bool(cfg.falsifier_gate_enabled))
    hard = R._check_hardened_convergence(round_idx, reg, cfg)
    sib = R._check_gamma_alt_convergence(
        round_idx, 0.0, crit_s, cfg, unresolved_critical=a4, contested=ct,
        rho_churn=False, irreducible_queue=0,
        gamma_critical=R._estimate_gamma(crit_s),
        total_findings=len(reg.entries))
    return hard, sib, dict(crit_s=crit_s, cum=sum(crit_s), a4=a4, contested=ct)


class TestTheTwoGatesCannotDisagreeOnReviewCleanliness:
    def test_unverified_criticals_block_the_vacuous_path(self, R):
        """6 UNCONFIRMED criticals + 12 OPEN sub-criticals. cum_crit reads 0
        because the series strips UNCONFIRMED, so guard 1 is satisfied and
        guard 2 (18 findings) is satisfied -- yet 6 critical claims are
        untested."""
        reg = _reg(R, [dict(st="UNCONFIRMED", sev=0.9, r=i % 4) for i in range(6)]
                      + [dict(st="OPEN", sev=0.2, r=i % 4) for i in range(12)])
        (ok, why, telem), (sib_ok, _sw), facts = _both(R, reg)
        assert facts["cum"] == 0 and facts["a4"] == 6, facts
        assert ok is False, (
            f"converged with 6 unverified critical candidates pending "
            f"(mode={telem.get('mode')}); the 2 guards cannot see them because "
            f"the settled series strips UNCONFIRMED")
        assert telem["mode"] == "refused_a4_unverified_critical", telem
        assert telem["unverified_critical"] == 6
        assert sib_ok is False, "fixture invalid: the sibling must refuse too"

    def test_the_a4_gap_was_not_confined_to_the_new_vacuous_path(self, R):
        """9 CONFIRMED criticals in round 0 puts cum_crit at 9, so this is the
        `full` branch, not the branch the 2026-10-08 fix added."""
        reg = _reg(R, [dict(st="CONFIRMED", sev=0.9, r=0) for _ in range(9)]
                      + [dict(st="UNCONFIRMED", sev=0.9, r=2) for _ in range(3)])
        (ok, _why, telem), (sib_ok, _sw), facts = _both(R, reg)
        assert facts["cum"] == 9 >= _Cfg.gamma_crit_min_cumulative, facts
        assert facts["a4"] == 3
        assert ok is False and sib_ok is False
        assert telem["mode"] == "refused_a4_unverified_critical", telem

    def test_contested_is_not_reached_by_the_a4_block(self, R):
        """THE COMPOSABILITY MEASUREMENT. A4 is 0 here, so the A4 block alone
        leaves this case converging while the sibling refuses it. Both blocks are
        required; neither subsumes the other."""
        reg = _reg(R, [dict(st="OPEN", sev=0.2, r=0,
                            v=[{"verdict": "CHALLENGE", "round": 0}])
                       for _ in range(4)]
                      + [dict(st="OPEN", sev=0.2, r=1) for _ in range(14)])
        (ok, _why, telem), (sib_ok, _sw), facts = _both(R, reg)
        assert facts["a4"] == 0, "fixture must isolate contested from A4"
        assert facts["contested"] == 4 and facts["cum"] == 0, facts
        assert ok is False, "the contested block is what refuses this one"
        assert telem["mode"] == "refused_contested", telem
        assert sib_ok is False

    def test_a_genuinely_clean_run_still_converges(self, R):
        """The repair must not cost the success criterion it protects: 3
        consecutive clean convergences on the prose target. Nothing unverified,
        nothing contested, no critical ever found."""
        reg = _reg(R, [dict(st="CLOSED", sev=0.2, r=i % 4) for i in range(18)])
        (ok, why, telem), _sib, facts = _both(R, reg)
        assert facts == dict(crit_s=[0] * 6, cum=0, a4=0, contested=0), facts
        assert ok is True, (why, telem)
        assert telem["mode"] == "vacuous_curve_converged", telem
        assert telem["review_clean_source"] == "registry"

    def test_the_preconditions_are_on_the_round_record(self, R):
        """A block nobody can audit afterwards is the defect the 2026-10-08 fix
        itself named when it moved the telemetry onto the round record."""
        reg = _reg(R, [dict(st="CLOSED", sev=0.2, r=i % 4) for i in range(18)])
        _ok, _why, telem = R._check_hardened_convergence(5, reg, _Cfg())
        for k in ("review_clean_source", "unverified_critical", "contested"):
            assert k in telem, (k, telem)

    def test_a_registry_that_cannot_answer_says_so(self, R):
        """The duck-typed path must NAME itself. 52 existing guards drive this
        gate with a stub carrying only `.entries`; they must keep passing, and a
        reader must not mistake "never asked" for "asked and clean"."""
        class _Stub:
            entries = {f"C{i:04d}": {} for i in range(18)}
        _ok, _why, telem = R._check_hardened_convergence(5, _Stub(), _Cfg())
        assert telem["review_clean_source"] == "unavailable", telem


class TestTheSentinelNoLongerReachesTheta:
    """`_gamma_is_estimable` was added for exactly this and applied in 1 of the
    4 places the estimator's output meets a threshold."""

    def test_maximal_decay_is_not_refused_by_an_all_zero_sub_series(self, R):
        series = [9, 0, 0, 0, 0, 0]
        assert R._estimate_gamma(series) == 1.0
        dropped = series[1:]
        assert R._estimate_gamma(dropped) == 0.0
        assert R._gamma_is_estimable(dropped) is False, (
            "fixture invalid: the leave-one-out series must be UNESTIMABLE, so "
            "its 0.0 is the sentinel and carries no robustness evidence")

        class _Stub:
            entries = {f"C{i:04d}": {} for i in range(20)}
        orig = R._settled_novelty_series
        try:
            R._settled_novelty_series = lambda _r, _i: (series, series)
            ok, why, telem = R._check_hardened_convergence(5, _Stub(), _Cfg())
        finally:
            R._settled_novelty_series = orig
        assert telem["mode"] == "full", telem
        assert telem["gamma_crit_settled"] == 1.0
        assert telem["sustained"] is True
        assert telem["zero_crit_ok"] is True
        assert telem["loo_ok"] is True, (
            f"loo_min={telem['loo_min']} came from an UNESTIMABLE sub-series; "
            f"comparing the sentinel to theta refuses a run that has "
            f"demonstrably exhausted its critical error space")
        assert ok is True, (why, telem)

    def test_the_silent_robustness_arm_is_recorded_not_assumed(self, R):
        """Where no sub-series is estimable the check has NO evidence. That must
        read as silence on the record, not as satisfaction."""
        series = [9, 0, 0]

        class _Stub:
            entries = {f"C{i:04d}": {} for i in range(20)}
        orig = R._settled_novelty_series
        try:
            R._settled_novelty_series = lambda _r, _i: (series, series)
            _ok, _why, telem = R._check_hardened_convergence(3, _Stub(), _Cfg())
        finally:
            R._settled_novelty_series = orig
        assert "loo_estimable_n" in telem and "sustain_estimable_n" in telem, telem
        assert telem["loo_estimable_n"] == 0, telem

    def test_an_estimable_fragile_sub_series_still_refuses(self, R):
        """The repair is a domain restriction, NOT a relaxation. A sub-series
        that IS estimable and IS below theta must still fail the robustness
        arm."""
        found = None
        for a in range(1, 6):
            for b in range(1, 6):
                for c in range(0, 6):
                    s = [a, b, c, 0, 0, 0, 0, 0, 0]
                    if sum(s) < _Cfg.gamma_crit_min_cumulative:
                        continue
                    if R._estimate_gamma(s) < _Cfg.gamma_alt_threshold:
                        continue
                    for i in range(len(s)):
                        loo = s[:i] + s[i + 1:]
                        if (R._gamma_is_estimable(loo)
                                and R._estimate_gamma(loo)
                                < _Cfg.gamma_alt_threshold - _Cfg.gamma_crit_loo_tol):
                            found = (s, loo)
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        if found is None:
            pytest.skip("no estimable-and-fragile sub-series in the swept space")
        s, loo = found

        class _Stub:
            entries = {f"C{i:04d}": {} for i in range(20)}
        orig = R._settled_novelty_series
        try:
            R._settled_novelty_series = lambda _r, _i: (s, s)
            ok, _why, telem = R._check_hardened_convergence(
                len(s) - 1, _Stub(), _Cfg())
        finally:
            R._settled_novelty_series = orig
        assert telem["loo_estimable_n"] > 0, telem
        assert telem["loo_ok"] is False, (s, loo, telem)
        assert ok is False
