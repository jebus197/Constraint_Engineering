"""Tests for reference_runner status transition fixes (Exp 38 findings).

Covers: F0/F4, F2/F5, F6, F7/F8, F9, F11, F12, F13, F14/F17/F22,
F18, F19, F23, F24.
"""
from __future__ import annotations

import re

import pytest

from bench.dm._types import Finding
from bench.reference_runner import (
    FindingRegistry,
    RunnerConfig,
    _update_finding_statuses,
    _evaluate_gate_conditions,
    _VERDICT_RE,
)


def _make_finding(**kwargs) -> Finding:
    defaults = dict(
        finding_id="f1", model_id="CC2", round_idx=0,
        flaw_class=2, severity=0.8, abstraction_index=0.5,
        description="Test finding",
    )
    defaults.update(kwargs)
    return Finding(**defaults)


def _register(reg: FindingRegistry, finding: Finding) -> str:
    """Register a finding and return its canonical ID."""
    return reg.register(finding, finding.model_id)


# =============================================================================
# F2/F5/F9: add_verdict must NOT update last_status_change_round
# =============================================================================

class TestAddVerdictNoTimerCorruption:
    def test_verdict_does_not_update_last_status_change_round(self):
        """add_verdict should record the verdict but leave the timer untouched."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        original_round = reg.entries[cid]["last_status_change_round"]
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=5)
        assert reg.entries[cid]["last_status_change_round"] == original_round

    def test_resolve_does_update_timer(self):
        """resolve() should update last_status_change_round."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.resolve(cid, "CONFIRMED", round_idx=7)
        assert reg.entries[cid]["last_status_change_round"] == 7


# =============================================================================
# F6: escalate_stale_contested and auto_resolve_contested use resolve()
# =============================================================================

class TestEscalationUsesResolve:
    def test_escalate_stale_updates_round(self):
        """escalate_stale_contested should update last_status_change_round."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.resolve(cid, "CONTESTED", round_idx=1)
        reg.escalate_stale_contested(current_round=10, max_contested_rounds=5)
        assert reg.entries[cid]["status"] == "UNCONFIRMED"
        assert reg.entries[cid]["last_status_change_round"] == 10

    def test_auto_refute_updates_round(self):
        """auto_resolve_contested should update last_status_change_round."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.resolve(cid, "CONTESTED", round_idx=1)
        # Add 3 challenges in recent rounds, 0 confirms
        for r in range(3, 6):
            reg.add_verdict(cid, f"M{r}", "CHALLENGE", round_idx=r)
        reg.auto_resolve_contested(current_round=5)
        assert reg.entries[cid]["status"] == "REFUTED"
        assert reg.entries[cid]["last_status_change_round"] == 5


# =============================================================================
# F0/F4: challenges must be checked BEFORE closing
# =============================================================================

class TestChallengeBeforeClose:
    def test_confirmed_verified_with_challenge_contests_not_closes(self):
        """A CONFIRMED+verified finding with unresolved challenges should
        transition to CONTESTED, not CLOSED."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.resolve(cid, "CONFIRMED", round_idx=1)
        reg.mark_verified(cid)
        # Challenge comes in the same round or later
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=2)
        _update_finding_statuses(reg, round_idx=2)
        assert reg.entries[cid]["status"] == "CONTESTED"

    def test_confirmed_verified_no_challenges_closes(self):
        """CONFIRMED+verified with no challenges should close normally."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        # Need 2 external confirms for CONFIRMED status
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=1)
        reg.add_verdict(cid, "Codex", "CONFIRM", round_idx=1)
        reg.resolve(cid, "CONFIRMED", round_idx=1)
        reg.mark_verified(cid)
        _update_finding_statuses(reg, round_idx=2)
        assert reg.entries[cid]["status"] == "CLOSED"


# =============================================================================
# F24: same-round challenges count as unresolved
# =============================================================================

class TestSameRoundChallenge:
    def test_same_round_challenge_and_confirm_counts_as_unresolved(self):
        """A challenge in the same round as the latest confirm should be
        treated as unresolved (>= not >)."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=3)
        reg.add_verdict(cid, "Codex", "CONFIRM", round_idx=3)
        reg.resolve(cid, "CONFIRMED", round_idx=3)
        # Challenge in same round as latest confirm
        reg.add_verdict(cid, "DeepSeek", "CHALLENGE", round_idx=3)
        _update_finding_statuses(reg, round_idx=3)
        assert reg.entries[cid]["status"] == "CONTESTED"


# =============================================================================
# F8: MERGE requires quorum (2+ distinct models)
# =============================================================================

class TestMergeQuorum:
    def test_single_merge_on_full_panel_does_not_kill(self):
        """A single MERGE verdict with 2+ external models available should not merge."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(model_id="CC2"))
        # Two external models have verdicts — full panel
        reg.add_verdict(cid, "Gemini", "MERGE", round_idx=1,
                       evidence="merged_into=C0002")
        reg.add_verdict(cid, "Codex", "CONFIRM", round_idx=1)  # Not a merge
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] != "MERGED"

    def test_two_merges_from_different_models_merges(self):
        """Two MERGE verdicts from different models should merge."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "MERGE", round_idx=1,
                       evidence="merged_into=C0002")
        reg.add_verdict(cid, "Codex", "MERGE", round_idx=1,
                       evidence="merged_into=C0002")
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] == "MERGED"


# =============================================================================
# F11: confirmation quorum requires 2 independent external models
# =============================================================================

class TestConfirmationQuorum:
    def test_one_external_confirm_not_enough(self):
        """1 external confirm should not promote OPEN to CONFIRMED."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(model_id="CC2"))
        # One external confirm
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=1)
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] == "OPEN"

    def test_two_external_confirms_promotes(self):
        """2 external confirms should promote OPEN to CONFIRMED."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(model_id="CC2"))
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=1)
        reg.add_verdict(cid, "Codex", "CONFIRM", round_idx=1)
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] == "CONFIRMED"

    def test_source_model_confirm_not_counted(self):
        """Confirm from the source model should not count toward quorum."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(model_id="CC2"))
        reg.add_verdict(cid, "CC2", "CONFIRM", round_idx=1)
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=1)
        _update_finding_statuses(reg, round_idx=1)
        # CC2 is source, so only 1 external (Gemini) — not enough
        assert reg.entries[cid]["status"] == "OPEN"


# =============================================================================
# F18: REOPENED -> OPEN uses resolve() (updates timer)
# =============================================================================

class TestReopenedTransition:
    def test_reopened_to_open_updates_timer(self):
        """REOPENED -> OPEN should go through resolve() to update timer."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.resolve(cid, "REOPENED", round_idx=5)
        _update_finding_statuses(reg, round_idx=6)
        assert reg.entries[cid]["status"] == "OPEN"
        assert reg.entries[cid]["last_status_change_round"] == 6


# =============================================================================
# F14/F17/F22: contested_count skips terminal statuses
# =============================================================================

class TestContestedCountTerminal:
    def test_closed_finding_with_old_challenges_not_counted(self):
        """CLOSED findings should not contribute to contested count."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=1)
        reg.resolve(cid, "CLOSED", round_idx=5)
        assert reg.contested_count(current_round=10) == 0

    def test_refuted_finding_not_counted(self):
        """REFUTED findings should not contribute to contested count."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=1)
        reg.resolve(cid, "REFUTED", round_idx=5)
        assert reg.contested_count(current_round=10) == 0

    def test_open_finding_with_unresolved_challenge_counted(self):
        """OPEN findings with old unresolved challenges should be counted."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=1)
        # Challenge is > 1 round old and unresolved
        assert reg.contested_count(current_round=5) == 1


# =============================================================================
# F7/F23: max_open_crit_high threshold is enforced
# =============================================================================

class TestMaxOpenCritHigh:
    def test_gate_fails_when_over_threshold(self):
        """Gate should fail when open_ch exceeds cfg.max_open_crit_high."""
        reg = FindingRegistry()
        # Register a recent critical finding (severity >= 0.7, status OPEN)
        _register(reg, _make_finding(severity=0.9, round_idx=12))
        cfg = RunnerConfig(
            max_open_crit_high=0,  # default: no open critical/high allowed
            earliest_stop_round=0,
        )
        # Round 15: finding is only 3 rounds old — not exhausted (threshold 8)
        passed, msg = _evaluate_gate_conditions(
            round_idx=15, registry=reg, novel_this_round=0,
            gamma=0.5, cfg=cfg, open_ch_history=[],
        )
        assert not passed
        assert "open_ch=1 > max=0" in msg


# =============================================================================
# F12: evaluate_gate_conditions idempotent history append
# =============================================================================

class TestIdempotentHistoryAppend:
    def test_double_call_does_not_duplicate(self):
        """Calling _evaluate_gate_conditions twice in one round should not
        duplicate the open_ch_history entry."""
        reg = FindingRegistry()
        cfg = RunnerConfig(earliest_stop_round=0)
        history: list = []
        _evaluate_gate_conditions(
            round_idx=15, registry=reg, novel_this_round=0,
            gamma=0.5, cfg=cfg, open_ch_history=history,
        )
        _evaluate_gate_conditions(
            round_idx=15, registry=reg, novel_this_round=0,
            gamma=0.5, cfg=cfg, open_ch_history=history,
        )
        assert len(history) == 1  # not 2


# =============================================================================
# F13/F19: Verdict regex supports 4+ digit IDs and clean character class
# =============================================================================

class TestVerdictRegex:
    def test_four_digit_id(self):
        """Standard 4-digit ID should match."""
        m = _VERDICT_RE.search("CONFIRM C0042")
        assert m is not None
        assert m.group(2) == "C0042"

    def test_five_digit_id(self):
        """5-digit ID should match (F13 fix)."""
        m = _VERDICT_RE.search("CONFIRM C10001")
        assert m is not None
        assert m.group(2) == "C10001"

    def test_three_digit_id_does_not_match(self):
        """3-digit ID should not match (minimum 4 digits)."""
        m = _VERDICT_RE.search("CONFIRM C042")
        assert m is None


# =============================================================================
# Contextual fixes (Round 2 confer design)
# =============================================================================

class TestContextualMergeQuorum:
    """F8 contextual: target consensus + small-panel + HIL flag."""

    def test_target_disagreement_defers_merge(self):
        """Merge votes with different targets should NOT merge."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "MERGE", round_idx=1,
                       evidence="merged_into=C0002")
        reg.add_verdict(cid, "Codex", "MERGE", round_idx=1,
                       evidence="merged_into=C0003")  # Different target
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] != "MERGED"

    def test_same_target_consensus_merges(self):
        """Two models agreeing on same target should merge."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "MERGE", round_idx=1,
                       evidence="merged_into=C0002")
        reg.add_verdict(cid, "Codex", "MERGE", round_idx=1,
                       evidence="merged_into=C0002")
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] == "MERGED"

    def test_single_merge_on_small_panel_hil_flagged(self):
        """Single merge on small panel should merge but flag for HIL."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(model_id="CC2"))
        # Only one external model has ANY verdict — small panel
        reg.add_verdict(cid, "Gemini", "MERGE", round_idx=1,
                       evidence="merged_into=C0002")
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] == "MERGED"
        assert reg.entries[cid].get("hil_escalated") is True


class TestContextualConfirmationQuorum:
    """F11 contextual: severity-based thresholds."""

    def test_low_severity_one_confirm_enough(self):
        """Medium/Low severity finding needs only 1 external confirm."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(model_id="CC2", severity=0.4))
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=1)
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] == "CONFIRMED"

    def test_high_severity_one_confirm_not_enough(self):
        """Critical/High severity still needs 2 external confirms."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(model_id="CC2", severity=0.9))
        reg.add_verdict(cid, "Gemini", "CONFIRM", round_idx=1)
        _update_finding_statuses(reg, round_idx=1)
        assert reg.entries[cid]["status"] == "OPEN"


class TestExhaustedBypass:
    """F7/F23 GE design: stalled findings bypass gate as EXHAUSTED."""

    def test_stalled_finding_excluded_from_open_ch(self):
        """Finding stalled >= threshold rounds should be EXHAUSTED."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.9))
        # Finding opened at round 0, now at round 10 — stalled 10 rounds
        count = reg.open_crit_high_count(
            exhausted_round_threshold=8, current_round=10)
        assert count == 0
        assert reg.entries[cid].get("exhausted") is True

    def test_recent_finding_not_exhausted(self):
        """Finding not yet at threshold should still count."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.9))
        count = reg.open_crit_high_count(
            exhausted_round_threshold=8, current_round=5)
        assert count == 1
        assert reg.entries[cid].get("exhausted") is not True


class TestUnconfirmedGracePeriod:
    """F14/F17/F22 composed: grace period + reopen on evidence."""

    def test_unconfirmed_in_grace_period_counted(self):
        """UNCONFIRMED within grace period should count as contested."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=1)
        reg.resolve(cid, "UNCONFIRMED", round_idx=5)
        # Round 6: only 1 round since UNCONFIRMED, within grace period of 2
        assert reg.contested_count(current_round=6, grace_period=2) == 1

    def test_unconfirmed_after_grace_excluded(self):
        """UNCONFIRMED past grace period with no new evidence excluded."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=1)
        reg.resolve(cid, "UNCONFIRMED", round_idx=5)
        # Round 10: 5 rounds since UNCONFIRMED, well past grace
        assert reg.contested_count(current_round=10, grace_period=2) == 0

    def test_unconfirmed_reopened_on_new_evidence(self):
        """UNCONFIRMED with new evidence after grace should reopen."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=1)
        reg.resolve(cid, "UNCONFIRMED", round_idx=5)
        # New evidence arrives at round 8
        reg.add_verdict(cid, "Codex", "CHALLENGE", round_idx=8)
        # Round 10: past grace, but new evidence exists
        count = reg.contested_count(current_round=10, grace_period=2)
        assert reg.entries[cid]["status"] == "OPEN"  # Reopened
