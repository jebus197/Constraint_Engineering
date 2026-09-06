"""A4 verifier fail-safe — proof test (panel blocking condition, 2026-05-23).

Correctness-critical. An UNVERIFIED critical-severity candidate (status
UNCONFIRMED, severity >= 0.7) must NOT silently count as "zero new critical."

Mechanism. ``_settled_novelty_series`` EXCLUDES UNCONFIRMED entries
(``_NON_NOVEL_TERMINAL_STATUSES``), so a critical the system gave up on
(finalize sweep / grace-period reopen) vanishes from the critical novelty
series and would let the K-consecutive-zero-novel-critical streak accrue. The
fail-safe is ``FindingRegistry.unverified_critical_count()``: the runner reads
it each round and passes it to ``_check_gamma_alt_convergence`` as
``unresolved_critical``. While > 0, the streak does NOT accrue and convergence
is blocked, and the count is logged for HIL (never dropped silently).

This file PROVES: a sequence with an UNCONFIRMED critical-severity candidate
must NOT converge via the count; once that candidate is resolved/adjudicated,
convergence proceeds.

Status-lifecycle map (FindingRegistry + finalize block ~line 5784):
  OPEN/CONTESTED/REOPENED  in-play, counted by the settled series + state gate
                           (NOT silent) -> NOT an A4 trigger.
  CONFIRMED/CLOSED         resolved (verified) -> NOT an A4 trigger.
  MERGED/DUPLICATE/REFUTED adjudicated terminal -> NOT an A4 trigger.
  UNCONFIRMED              system gave up WITHOUT verification, excluded from
                           the settled series -> THE silent-drop danger -> A4
                           fires while any critical-severity UNCONFIRMED exists.
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
    _check_gamma_alt_convergence,
)


def _make_finding(**kwargs) -> Finding:
    defaults = dict(
        finding_id="f1",
        model_id="CC2",
        round_idx=0,
        flaw_class=2,
        severity=0.8,  # critical: >= 0.7
        abstraction_index=0.5,
        description="Test finding",
    )
    defaults.update(kwargs)
    return Finding(**defaults)


def _cfg(**overrides) -> RunnerConfig:
    cfg = RunnerConfig(
        experiment_name="a4-proof",
        models=["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"],
        gamma_alt_consecutive_zero_crit=3,
        gamma_alt_earliest_round=3,
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# unverified_critical_count() — the A4 signal
# ─────────────────────────────────────────────────────────────────────────────


class TestUnverifiedCriticalCount:
    def test_unconfirmed_critical_counted(self):
        reg = FindingRegistry()
        cid = reg.register(_make_finding(severity=0.9), "CC2")
        reg.resolve(cid, "UNCONFIRMED", round_idx=6)
        assert reg.unverified_critical_count() == 1

    def test_unconfirmed_below_threshold_IS_now_counted(self):
        """CONTRACT CHANGED 2026-09-06, founder ruling 23: "There are no votes in
        CDSFL." A4 no longer reads the model-assigned severity float. A low
        severity no longer excuses a finding from the fail-safe, because that
        number is the source model's opinion and was measured uninformative in
        the band where it decided (AUC 0.464 against 0.5 for chance).

        What clears the block now is a tool verdict -- see the test below."""
        reg = FindingRegistry()
        cid = reg.register(_make_finding(severity=0.5), "CC2")
        reg.resolve(cid, "UNCONFIRMED", round_idx=6)
        assert reg.unverified_critical_count() == 1

    def test_a_resolved_falsifier_clears_the_block_at_any_severity(self):
        """The replacement criterion, executed: whether a tool ran and returned a
        verdict. That is a fact; severity was an opinion."""
        reg = FindingRegistry()
        for sev in (0.1, 0.5, 0.95):
            cid = reg.register(_make_finding(finding_id=f"f{sev}", severity=sev), "CC2")
            reg.resolve(cid, "UNCONFIRMED", round_idx=6)
            reg.entries[cid]["falsifier_code"] = "assert False"
            reg.entries[cid]["falsifier_verdict"] = "CONFIRMED"
        assert reg.unverified_critical_count() == 0

    def test_a_refuted_critical_still_blocks(self):
        """REGRESSION (panel, 2026-09-06). apply_falsifier_verdicts demotes a
        CRITICAL whose falsifier returned REFUTED to UNCONFIRMED and escalates it,
        because CONFIRM-only refuses to trust a passive clean exit (Exp 42: 2/3 of
        REFUTED criticals were real defects). If A4 counted REFUTED as "resolved"
        it released precisely those entries -- blocking FEWER than the severity
        rule did, which is the one thing the replacement promised it could not do."""
        reg = FindingRegistry()
        cid = reg.register(_make_finding(finding_id="refcrit", severity=0.9), "CC2")
        reg.resolve(cid, "UNCONFIRMED", round_idx=6)
        reg.entries[cid]["falsifier_code"] = "assert True"
        reg.entries[cid]["falsifier_verdict"] = "REFUTED"
        reg.entries[cid]["escalated"] = True
        assert reg.unverified_critical_count() == 1

    def test_an_absent_falsifier_blocks_at_any_severity(self):
        """The conservative direction. Measured over 87 archived reports: the new
        rule blocks MORE in 36.8%, identically in 63.2%, and FEWER in 0 of 87,
        Wilson [0.0%, 4.2%] -- so convergence can only get harder."""
        reg = FindingRegistry()
        for sev in (0.1, 0.95):
            cid = reg.register(_make_finding(finding_id=f"g{sev}", severity=sev), "CC2")
            reg.resolve(cid, "UNCONFIRMED", round_idx=6)
        assert reg.unverified_critical_count() == 2

    def test_open_critical_not_counted(self):
        """OPEN is in-play (settled series counts it) -> NOT an A4 trigger."""
        reg = FindingRegistry()
        reg.register(_make_finding(severity=0.9), "CC2")  # stays OPEN
        assert reg.unverified_critical_count() == 0

    def test_confirmed_and_closed_not_counted(self):
        reg = FindingRegistry()
        c1 = reg.register(_make_finding(finding_id="f1", severity=0.9), "CC2")
        c2 = reg.register(_make_finding(finding_id="f2", severity=0.9), "CC2")
        reg.resolve(c1, "CONFIRMED", round_idx=4)
        reg.resolve(c2, "CLOSED", round_idx=4)
        assert reg.unverified_critical_count() == 0

    def test_adjudicated_terminal_not_counted(self):
        """MERGED / DUPLICATE / REFUTED are adjudicated -> NOT A4 triggers."""
        reg = FindingRegistry()
        for i, st in enumerate(("MERGED", "DUPLICATE", "REFUTED")):
            cid = reg.register(
                _make_finding(finding_id=f"f{i}", severity=0.9), "CC2"
            )
            reg.resolve(cid, st, round_idx=4)
        assert reg.unverified_critical_count() == 0

    def test_threshold_constant_is_authoritative(self):
        """Boundary exactly at the threshold counts (>=)."""
        reg = FindingRegistry()
        cid = reg.register(
            _make_finding(severity=CRITICAL_SEVERITY_THRESHOLD), "CC2"
        )
        reg.resolve(cid, "UNCONFIRMED", round_idx=6)
        assert reg.unverified_critical_count() == 1


# ─────────────────────────────────────────────────────────────────────────────
# End-to-end proof: registry signal -> gate decision
# ─────────────────────────────────────────────────────────────────────────────


class TestA4BlocksConvergenceEndToEnd:
    """The required proof: an UNCONFIRMED critical must block the count;
    once resolved/adjudicated, convergence proceeds."""

    def _build_registry_with_pending_critical(self) -> FindingRegistry:
        """Registry mirroring a quiet-tail run that nonetheless abandoned a
        critical candidate WITHOUT verification (status UNCONFIRMED)."""
        reg = FindingRegistry()
        # Two verified criticals discovered early, properly closed.
        c0 = reg.register(
            _make_finding(finding_id="early1", round_idx=0, severity=0.85),
            "CC2",
        )
        c1 = reg.register(
            _make_finding(finding_id="early2", round_idx=0, severity=0.9),
            "Codex",
        )
        reg.resolve(c0, "CLOSED", round_idx=3)
        reg.resolve(c1, "CONFIRMED", round_idx=3)
        # A critical candidate raised at round 1 that the system never
        # verified — ends UNCONFIRMED (the silent-drop danger).
        self.pending_cid = reg.register(
            _make_finding(finding_id="unverified_crit", round_idx=1, severity=0.8),
            "Gemini",
        )
        reg.resolve(self.pending_cid, "UNCONFIRMED", round_idx=6)
        return reg

    def test_pending_unconfirmed_critical_blocks_count(self):
        cfg = _cfg()
        reg = self._build_registry_with_pending_critical()
        # The SETTLED critical series excludes the UNCONFIRMED candidate, so
        # the tail looks all-zero — exactly the silent-drop the streak would
        # wrongly reward.
        settled_critical_history = [2, 0, 0, 0, 0, 0, 0]
        unresolved = reg.unverified_critical_count()
        assert unresolved == 1, "fixture must leave one UNCONFIRMED critical"

        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=settled_critical_history,
            cfg=cfg,
            unresolved_critical=unresolved,
        )
        assert converged is False, (
            "A4: an UNCONFIRMED critical must NOT converge via the count"
        )
        assert "A4 BLOCK" in reason
        assert "HIL review required" in reason  # surfaced, not dropped

    def test_after_resolution_convergence_proceeds(self):
        cfg = _cfg()
        reg = self._build_registry_with_pending_critical()
        # Resolve the previously-UNCONFIRMED critical (e.g. verified this
        # round, or explicitly adjudicated).
        reg.resolve(self.pending_cid, "CONFIRMED", round_idx=6)
        unresolved = reg.unverified_critical_count()
        assert unresolved == 0, "resolved candidate must clear the A4 signal"

        settled_critical_history = [2, 0, 0, 0, 0, 0, 0]
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=settled_critical_history,
            cfg=cfg,
            unresolved_critical=unresolved,
        )
        assert converged is True, (
            "once resolved/adjudicated, convergence proceeds"
        )
        assert "CRITICAL_QUIESCENCE_CONVERGED" in reason

    def test_adjudicated_terminal_also_unblocks(self):
        """Explicit adjudication to a terminal status (e.g. REFUTED/DENIED
        analogue) also clears A4 — the candidate is no longer pending."""
        cfg = _cfg()
        reg = self._build_registry_with_pending_critical()
        reg.resolve(self.pending_cid, "REFUTED", round_idx=6)
        assert reg.unverified_critical_count() == 0

        converged, _ = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[2, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=reg.unverified_critical_count(),
        )
        assert converged is True
