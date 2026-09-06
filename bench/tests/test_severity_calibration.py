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

    def test_demotion_retains_the_finding_but_no_longer_clears_the_fail_safe(self):
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
        assert reg.unverified_critical_count() == 1, (
            "a severity demotion cleared the A4 fail-safe -- the model vote is back")
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

    def test_calibration_no_longer_unblocks_convergence(self):
        """CONTRACT CHANGED 2026-09-06, founder ruling 23.

        This test previously asserted that demoting a latent critical's severity
        cleared the A4 block and let the gate converge. It cannot any more, and the
        reason is worth stating: severity calibration is a MODEL adjusting a MODEL's
        number in order to open a gate. That is the same vote ruling 23 abolished,
        one level down. Calibration still runs, still records what it changed, and
        still serves queue ordering and reporting -- it simply no longer decides
        convergence. Only a tool verdict does that now.
        """
        reg, cid = self._registry_blocked_by_one_latent_critical()
        cfg = _cfg(severity_calibration_enabled=True)
        assert _apply_severity_calibration(reg, cfg, round_idx=6) == 1
        assert reg.entries[cid]["severity_calibrated"] is True
        assert reg.entries[cid]["severity_original"] == 0.8
        # The demotion happened, and it did NOT clear the fail-safe.
        assert reg.unverified_critical_count() == 1, (
            "severity calibration cleared an A4 block -- the model vote is back")

    def test_a_tool_verdict_clears_what_calibration_cannot(self):
        reg, cid = self._registry_blocked_by_one_latent_critical()
        reg.entries[cid]["falsifier_code"] = "assert True"
        reg.entries[cid]["falsifier_verdict"] = "REFUTED"
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
