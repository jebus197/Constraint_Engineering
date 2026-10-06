"""Severity calibration — over-production bounding (gated, 2026-06-10).

A recurring failure mode: a real-but-LATENT defect (genuine, but it requires a
trigger absent from the actual usage contract) gets rated severity >= 0.7 and
perpetually re-blocks convergence / piles up in HIL. Severity calibration lowers
such an over-rated-but-genuine finding's EFFECTIVE severity just below the
critical threshold so it stops blocking — WITHOUT deleting it. The finding stays
in the registry with its original severity and the calibration reason recorded.

Criterion (conservative, principled): a finding is demoted iff it is
  (1) currently critical (severity >= 0.7), AND
  (2) a REAL defect by independent demonstration (falsifier_verdict == CONFIRMED),
      AND
  (3) explicitly flagged latent/conditional (entry["latent"] truthy), AND
  (4) NOT in a never-demote category (safety / core / security / data_loss).
Anything failing (2)-(4) is NEVER demoted.

NOTE: the mechanism is INERT without an upstream producer that tags entries
`latent`/`finding_category` — by design (fail-safe). These tests set those tags
directly to exercise the demotion path.
"""

from __future__ import annotations

import os
import sys

_project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._types import Finding
from bench.reference_runner_v3 import (
    severity_is_proven,
    CRITICAL_SEVERITY_THRESHOLD,
    FindingRegistry,
    RunnerConfig,
    _apply_severity_calibration,
    _check_gamma_alt_convergence,
    _is_demotion_eligible,
)


def _make_finding(**kwargs) -> Finding:
    defaults = dict(
        finding_id="f1",
        model_id="CC2",
        round_idx=0,
        flaw_class=2,
        severity=0.85,  # critical: >= 0.7
        abstraction_index=0.5,
        description="Test finding",
    )
    defaults.update(kwargs)
    return Finding(**defaults)


def _cfg(**overrides) -> RunnerConfig:
    cfg = RunnerConfig(
        experiment_name="sev-calib",
        models=["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"],
        gamma_alt_consecutive_zero_crit=3,
        gamma_alt_earliest_round=3,
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


def _register_critical(reg, *, fid, sev, open_round, model="CC2"):
    return reg.register(
        _make_finding(finding_id=fid, severity=sev, round_idx=open_round),
        model,
    )


def _mark(reg, cid, **flags):
    """Stamp the flags that make an entry demotion-eligible.

    UPDATED 2026-09-07, founder ruling of 2026-09-06 ("there are no votes in
    CDSFL"): a severity that cannot be recomputed from its own stated inputs may
    no longer buy a demotion, because demotion is the one place the number makes
    the gate LOOSER -- it lifts a blocking critical out of the count. These tests
    are about whether the calibration sweep FIRES, not about the proof rule, so
    the default entry now carries a severity that reproduces. A test that wants
    the unproven case passes severity_proof explicitly; the unproven behaviour is
    asserted directly in test_severity_proof_2026-09-07.py.
    """
    flags.setdefault("severity_proof",
                     {"status": "PASS", "model_rk": 0.31, "recomputed_rk": 0.31})
    reg.entries[cid].update(flags)


# ── Gate OFF — byte-identical (mutates nothing) ──────────────────────────────


class TestGateOffByteIdentical:
    def test_disabled_returns_zero_and_mutates_nothing(self):
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="f1", sev=0.85, open_round=1)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              finding_category="performance", status="CONFIRMED")
        before = dict(reg.entries[cid])
        cfg = _cfg(severity_calibration_enabled=False)
        n = _apply_severity_calibration(reg, cfg, round_idx=6)
        assert n == 0
        assert reg.entries[cid] == before
        assert reg.entries[cid]["severity"] == 0.85
        assert "severity_calibrated" not in reg.entries[cid]

    def test_disabled_default_config_is_off(self):
        cfg = RunnerConfig(experiment_name="x", models=["CC2"])
        assert cfg.severity_calibration_enabled is False
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="f1", sev=0.9, open_round=1)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              status="CONFIRMED")
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 0
        assert reg.entries[cid]["severity"] == 0.9


# ── Eligibility criterion ────────────────────────────────────────────────────


class TestEligibilityCriterion:
    def _eligible_entry(self):
        return {
            "severity": 0.85,
            "falsifier_verdict": "CONFIRMED",
            "latent": True,
            "finding_category": "performance",
            "status": "CONFIRMED",
        }

    def test_fully_eligible(self):
        assert _is_demotion_eligible(self._eligible_entry()) is True

    def test_non_critical_not_eligible(self):
        e = self._eligible_entry(); e["severity"] = 0.5
        assert _is_demotion_eligible(e) is False

    def test_not_confirmed_not_eligible(self):
        for verdict in ("", "REFUTED", "ERROR", "UNTOOLABLE", "CHALLENGE"):
            e = self._eligible_entry(); e["falsifier_verdict"] = verdict
            assert _is_demotion_eligible(e) is False, verdict

    def test_not_latent_not_eligible(self):
        for latent in (False, None, 0, ""):
            e = self._eligible_entry(); e["latent"] = latent
            assert _is_demotion_eligible(e) is False

    def test_never_demote_categories(self):
        for cat in ("safety", "Safety", "core", "core_functionality",
                    "security", "data_loss", "DATA_LOSS"):
            e = self._eligible_entry(); e["finding_category"] = cat
            assert _is_demotion_eligible(e) is False, cat

    def test_threshold_boundary_is_critical(self):
        e = self._eligible_entry(); e["severity"] = CRITICAL_SEVERITY_THRESHOLD
        assert _is_demotion_eligible(e) is True


# ── Demotion mechanics — retained, recorded, drops out of counts ─────────────


class TestDemotionRetainsAndRecords:
    def test_real_but_latent_demoted_and_retained(self):
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="latent_crit", sev=0.85, open_round=1)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              finding_category="performance", status="CONFIRMED")
        cfg = _cfg(severity_calibration_enabled=True, severity_calibration_floor=0.69)
        n = _apply_severity_calibration(reg, cfg, round_idx=6)
        assert n == 1
        e = reg.entries[cid]
        assert cid in reg.entries
        assert e["severity"] == 0.69 and e["severity"] < CRITICAL_SEVERITY_THRESHOLD
        assert e["severity_calibrated"] is True
        assert e["severity_original"] == 0.85
        assert "LATENT" in e["calibration_reason"]
        assert e["calibration_round"] == 6

    def test_a_proven_demotion_retains_the_finding_and_clears_the_fail_safe(self):
        """CONTRACT CHANGED 2026-09-06, founder ruling 23.

        The retention half of this test is unchanged and still matters: a demoted
        finding is KEPT, with its original severity and a reason recorded. What
        changed is the second half. Demoting a number no longer clears the A4
        block, because A4 no longer reads that number. A verdict from a tool does.

        Note what this entry looks like: it carries falsifier_verdict CONFIRMED but
        no falsifier_code, so no tool ever actually ran on it. Under the old rule a
        severity demotion was enough to let the loop close around it. That is the
        gap ruling 23 shuts.
        """
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="latent_crit", sev=0.9, open_round=4)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              finding_category="robustness", status="UNCONFIRMED")
        assert reg.unverified_critical_count() == 1
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 1
        # RESTORED 2026-10-06. This asserted == 1 ("the model vote is back") under
        # the 2026-09-06 removal the founder rejected the same day and has now
        # rejected again. A PROVEN demotion is not a vote: `_apply_severity_
        # calibration` will not demote an entry whose severity carries no worked
        # proof, so reaching this line at all means the number reproduced from the
        # model's own stated inputs. `test_an_unproven_demotion_cannot_clear_the_
        # fail_safe` holds the other half.
        assert reg.unverified_critical_count() == 0, (
            "a PROVEN sub-critical demotion did not clear the A4 fail-safe, so the "
            "severity test is not reaching the counter")
        assert cid in reg.entries          # retention is unchanged
        assert reg.entries[cid]["severity_original"] == 0.9

    def test_idempotent_re_sweep_does_not_double_lower(self):
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="latent_crit", sev=0.85, open_round=1)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              finding_category="performance", status="CONFIRMED")
        cfg = _cfg(severity_calibration_enabled=True)
        n1 = _apply_severity_calibration(reg, cfg, round_idx=6)
        sev1 = reg.entries[cid]["severity"]
        n2 = _apply_severity_calibration(reg, cfg, round_idx=7)
        assert n1 == 1 and n2 == 0
        assert reg.entries[cid]["severity"] == sev1
        assert reg.entries[cid]["severity_original"] == 0.85

    def test_floor_clamped_below_threshold_even_if_misconfigured(self):
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="latent_crit", sev=0.95, open_round=1)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              status="CONFIRMED")
        cfg = _cfg(severity_calibration_enabled=True, severity_calibration_floor=0.80)
        _apply_severity_calibration(reg, cfg, round_idx=6)
        assert reg.entries[cid]["severity"] < CRITICAL_SEVERITY_THRESHOLD


# ── Safety / core / unproven are NOT demoted ─────────────────────────────────


class TestNeverDemoted:
    def test_safety_finding_not_demoted(self):
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="safety_crit", sev=0.9, open_round=4)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              finding_category="safety", status="UNCONFIRMED")
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 0
        assert reg.entries[cid]["severity"] == 0.9
        assert reg.unverified_critical_count() == 1

    def test_unconfirmed_latent_critical_not_demoted(self):
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="unproven", sev=0.9, open_round=4)
        _mark(reg, cid, falsifier_verdict="REFUTED", latent=True,
              finding_category="performance", status="UNCONFIRMED")
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 0
        assert reg.entries[cid]["severity"] == 0.9

    def test_terminal_entries_skipped(self):
        reg = FindingRegistry()
        for i, st in enumerate(("MERGED", "CLOSED", "DUPLICATE", "REFUTED")):
            cid = _register_critical(reg, fid=f"term{i}", sev=0.9, open_round=1)
            _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
                  finding_category="performance", status=st)
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 0
        for e in reg.entries.values():
            assert e["severity"] == 0.9


# ── End-to-end: demotion unblocks the gate the registry would have A4-blocked ─


class TestEndToEndUnblocksConvergence:
    def _registry_blocked_by_one_latent_critical(self):
        reg = FindingRegistry()
        cid = _register_critical(reg, fid="latent_blocker", sev=0.8, open_round=1)
        _mark(reg, cid, falsifier_verdict="CONFIRMED", latent=True,
              finding_category="performance", status="UNCONFIRMED")
        return reg, cid

    def test_before_calibration_gate_is_a4_blocked(self):
        reg, _cid = self._registry_blocked_by_one_latent_critical()
        cfg = _cfg()
        assert reg.unverified_critical_count() == 1
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6, gamma=0.20, novel_critical_history=[2, 0, 0, 0, 0, 0, 0],
            cfg=cfg, unresolved_critical=reg.unverified_critical_count(),
            gamma_critical=0.61,
        )
        assert converged is False
        assert "A4 BLOCK" in reason

    def test_calibration_unblocks_convergence_when_the_severity_is_PROVEN(self):
        """CONTRACT RESTORED 2026-10-06 ON THE FOUNDER'S RULING.

        THE HISTORY MATTERS, BECAUSE THIS TEST ENCODED A REJECTED RULING FOR A
        MONTH. The severity test was removed from `unverified_critical_count` in
        commit 6c10fe4 on 2026-09-06 16:21:48 under "founder ruling 23", and this
        test was rewritten the same day to assert the post-removal behaviour. The
        founder REJECTED that removal at 22:15 THAT SAME DAY. He re-rejected it on
        2026-10-06: *"This is now at least the 3rd or 4th time I have rejected this
        change. This change is rejected. You should fix it."*

        THE OBJECTION THIS TEST CARRIED WAS REAL AND IS NOW ANSWERED BY MECHANISM,
        NOT BY OVERRULING IT. Its wording was that calibration is "a MODEL adjusting
        a MODEL's number in order to open a gate ... the same vote ruling 23
        abolished, one level down", and `no-model-voting` is a standing project
        rule. The answer is that BOTH sides now gate on `severity_is_proven`:
        `_apply_severity_calibration` refuses to demote an entry whose severity
        carries no worked proof that reproduces, and the restored test in
        `unverified_critical_count` exempts a sub-critical only when its severity is
        proven. Measured by execution against this file's own fixture: with a proof
        (status PASS, model_rk 0.31 recomputed 0.31) the demotion runs and A4 goes
        1 -> 0; with the proof stripped, 0 are demoted, severity stays 0.80 and A4
        stays 1. A model cannot open the gate by asserting a number. It can open it
        by DEMONSTRATING one, which is the repair the founder specified when he
        rejected the removal ("worked proofs instead").

        `test_an_unproven_demotion_cannot_clear_the_fail_safe` below holds that
        distinction directly, so the property this test used to protect is still
        protected — by the test that actually measures it.
        """
        reg, cid = self._registry_blocked_by_one_latent_critical()
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 1
        assert reg.entries[cid]["severity_calibrated"] is True
        assert reg.entries[cid]["severity_original"] == 0.8
        # The demotion happened on a PROVEN severity, so it DOES clear the
        # fail-safe. That is the restored contract.
        assert reg.unverified_critical_count() == 0, (
            "a PROVEN severity demotion did not clear the A4 block")

    def test_an_already_subcritical_unproven_finding_still_blocks(self):
        """THE COUNTER-LEVEL ANTI-VOTE PROPERTY, and the first version of this
        file did not test it.

        Mutation-checked and FOUND WANTING: replacing `severity_is_proven(e)` with
        a bare `_sev < CRITICAL_SEVERITY_THRESHOLD` — which reopens exactly the
        model-vote hole the old contract feared — left all 19 tests GREEN. The
        reason is that `_apply_severity_calibration` refuses to demote an unproven
        entry, so no test reached the counter with a sub-critical UNPROVEN finding.
        A finding can arrive that way without calibration touching it: the model
        simply states 0.45 and never proves it.

        So this goes straight at the counter: a sub-critical severity that the
        model merely ASSERTED must keep blocking, and only a severity it
        DEMONSTRATED may stop blocking.
        """
        reg = FindingRegistry()
        base = {
            "canonical_id": "C0001", "status": "UNCONFIRMED", "severity": 0.45,
            "verified": False, "verdicts": [], "description": "asserted, not proven",
            "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
            "last_status_change_round": 0, "computed_evidence": [],
            "routing_history": [], "falsifier_code": "", "falsifier_verdict": "",
        }
        reg.entries = {"C0001": dict(base)}
        assert severity_is_proven(reg.entries["C0001"]) is False
        assert reg.unverified_critical_count() == 1, (
            "a sub-critical severity the model only ASSERTED stopped blocking — "
            "the gate is reading the raw float, so a model can open it by naming "
            "a number it never computed")

        proven = dict(base)
        proven["severity_proof"] = {"status": "PASS", "model_rk": 0.31,
                                    "recomputed_rk": 0.31}
        reg.entries = {"C0001": proven}
        assert severity_is_proven(reg.entries["C0001"]) is True
        assert reg.unverified_critical_count() == 0, (
            "a PROVEN sub-critical still blocks, so the restored severity test is "
            "not reaching the counter at all")

    def test_an_unproven_demotion_cannot_clear_the_fail_safe(self):
        """THE HALF THE OLD CONTRACT WAS PROTECTING, held directly.

        `no-model-voting` is a standing project rule, and the test this replaced
        feared the restored severity path reopens it. It does not, and the reason is
        mechanical rather than argued: `_apply_severity_calibration` refuses to
        demote an entry whose severity carries no worked proof. Strip the proof and
        nothing moves — no demotion, no change in severity, no change in the count.
        """
        reg, cid = self._registry_blocked_by_one_latent_critical()
        reg.entries[cid].pop("severity_proof", None)
        reg.entries[cid]["severity_proof_history"] = []
        assert severity_is_proven(reg.entries[cid]) is False, (
            "the fixture still proves its severity, so this test asserts nothing")
        before = reg.unverified_critical_count()
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 0, (
            "an UNPROVEN severity was demoted — a model opened the gate by "
            "asserting a number, which is the vote this rule forbids")
        assert reg.entries[cid]["severity"] == 0.8
        assert reg.unverified_critical_count() == before == 1

    def test_a_tool_verdict_clears_what_calibration_cannot(self):
        reg, cid = self._registry_blocked_by_one_latent_critical()
        reg.entries[cid]["falsifier_code"] = "assert True"
        reg.entries[cid]["falsifier_verdict"] = "CONFIRMED"
        assert reg.unverified_critical_count() == 0

    def _retired_after_calibration_gate_converges(self):
        reg, cid = self._registry_blocked_by_one_latent_critical()
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 1
        assert reg.unverified_critical_count() == 0
        assert reg.entries[cid]["severity_calibrated"] is True
        assert reg.entries[cid]["severity_original"] == 0.8
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6, gamma=0.20, novel_critical_history=[2, 0, 0, 0, 0, 0, 0],
            cfg=cfg, unresolved_critical=reg.unverified_critical_count(),
            gamma_critical=0.61,
        )
        assert converged is True
        assert "CRITICAL_QUIESCENCE_CONVERGED" in reason
