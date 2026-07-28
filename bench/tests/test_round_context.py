"""Tests for round-context helpers (Items 1D.1, 1D.2, 1D.4).

Covers:
  - ``build_prior_fix_summary`` — enumerates confirmed fixes from prior rounds
  - ``build_consolidation_preamble`` — final-phase prompt preamble
  - ``build_windowed_context`` — long-run context windowing
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from bench.dm._round_context import (
    build_prior_fix_summary,
    build_consolidation_preamble,
    build_windowed_context,
)


# ─────────────────────────────────────────────────────────────────────────────
# build_prior_fix_summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPriorFixSummary:
    def test_empty_registry_returns_empty_string(self):
        reg = SimpleNamespace(entries={})
        assert build_prior_fix_summary(reg, round_idx=5) == ""

    def test_round_0_returns_empty_string(self):
        reg = SimpleNamespace(entries={
            "C0001": {"status": "CONFIRMED", "round_closed": 0, "description": "x"},
        })
        assert build_prior_fix_summary(reg, round_idx=0) == ""

    def test_lists_confirmed_entries_from_prior_rounds(self):
        reg = SimpleNamespace(entries={
            "C0001": {
                "status": "CONFIRMED", "round_closed": 1,
                "description": "First fix", "severity": 0.8,
            },
            "C0002": {
                "status": "CONFIRMED", "round_closed": 2,
                "description": "Second fix", "severity": 0.9,
            },
        })
        out = build_prior_fix_summary(reg, round_idx=3)
        assert "PRIOR FIXES APPLIED (2" in out
        assert "C0001" in out
        assert "C0002" in out
        assert "First fix" in out

    def test_sorts_by_severity_descending(self):
        reg = SimpleNamespace(entries={
            "C0001": {
                "status": "CONFIRMED", "round_closed": 1,
                "description": "low-sev fix", "severity": 0.3,
            },
            "C0002": {
                "status": "CONFIRMED", "round_closed": 1,
                "description": "high-sev fix", "severity": 0.95,
            },
        })
        out = build_prior_fix_summary(reg, round_idx=3)
        # C0002 (higher severity) should appear before C0001
        assert out.index("C0002") < out.index("C0001")

    def test_filters_out_non_confirmed_status(self):
        reg = SimpleNamespace(entries={
            "C0001": {"status": "OPEN", "round_closed": 1, "description": "open"},
            "C0002": {"status": "CONFIRMED", "round_closed": 1, "description": "confirmed"},
            "C0003": {"status": "REJECTED", "round_closed": 1, "description": "rejected"},
        })
        out = build_prior_fix_summary(reg, round_idx=3)
        assert "C0001" not in out
        assert "C0002" in out
        assert "C0003" not in out

    def test_filters_out_future_and_current_round_closures(self):
        reg = SimpleNamespace(entries={
            "C0001": {"status": "CONFIRMED", "round_closed": 0, "description": "past"},
            "C0002": {"status": "CONFIRMED", "round_closed": 3, "description": "current"},
            "C0003": {"status": "CONFIRMED", "round_closed": 5, "description": "future"},
        })
        # round_idx=3 → only C0001 (round_closed=0 < 3) qualifies
        out = build_prior_fix_summary(reg, round_idx=3)
        assert "C0001" in out
        assert "C0002" not in out
        assert "C0003" not in out

    def test_respects_max_entries(self):
        entries = {
            f"C{i:04d}": {
                "status": "CONFIRMED", "round_closed": 1,
                "description": f"Fix {i}", "severity": 0.5,
            }
            for i in range(30)
        }
        reg = SimpleNamespace(entries=entries)
        out = build_prior_fix_summary(reg, round_idx=3, max_entries=10)
        assert "and 20 more" in out


# ─────────────────────────────────────────────────────────────────────────────
# build_consolidation_preamble
# ─────────────────────────────────────────────────────────────────────────────

class TestConsolidationPreamble:
    def test_early_rounds_no_preamble(self):
        assert build_consolidation_preamble(
            round_idx=2, max_rounds=10, consolidation_rounds=3,
        ) == ""

    def test_consolidation_window_fires(self):
        # max_rounds=10, consolidation_rounds=3 → window = rounds 7, 8, 9
        out = build_consolidation_preamble(
            round_idx=7, max_rounds=10, consolidation_rounds=3,
        )
        assert "CONSOLIDATION MODE" in out
        assert "round 1/3" in out

    def test_last_round_shows_position(self):
        out = build_consolidation_preamble(
            round_idx=9, max_rounds=10, consolidation_rounds=3,
        )
        assert "round 3/3" in out

    def test_disabled_when_consolidation_rounds_zero(self):
        assert build_consolidation_preamble(
            round_idx=9, max_rounds=10, consolidation_rounds=0,
        ) == ""

    def test_preamble_mentions_convergence(self):
        out = build_consolidation_preamble(
            round_idx=8, max_rounds=10, consolidation_rounds=3,
        )
        assert "CONVERGENCE" in out
        assert "CLOSING OPEN CHALLENGES" in out


# ─────────────────────────────────────────────────────────────────────────────
# build_windowed_context
# ─────────────────────────────────────────────────────────────────────────────

class TestWindowedContext:
    def _make_summary(self, r: int, findings: int, novel: int):
        return {
            "round": r, "findings_count": findings,
            "novel_this_round": novel, "open_crit_high": 5,
            "gamma": 0.3, "rho": 0.5,
        }

    def test_empty_history_returns_empty(self):
        assert build_windowed_context([], round_idx=3) == ""

    def test_short_history_all_recent(self):
        summaries = [
            self._make_summary(0, 10, 10),
            self._make_summary(1, 8, 6),
        ]
        out = build_windowed_context(
            summaries, round_idx=2, window_full_rounds=2,
        )
        assert "Round 0" in out
        assert "Round 1" in out
        assert "summarised" not in out

    def test_long_history_compresses_older(self):
        summaries = [
            self._make_summary(r, 10, 10 - r) for r in range(10)
        ]
        out = build_windowed_context(
            summaries, round_idx=10, window_full_rounds=2,
        )
        # Older rounds (0..7) summarised; recent rounds (8..9) full
        assert "summarised" in out
        assert "Rounds 0..7" in out
        assert "Round 8" in out
        assert "Round 9" in out

    def test_truncates_to_max_chars(self):
        summaries = [
            self._make_summary(r, 1000, 500) for r in range(50)
        ]
        out = build_windowed_context(
            summaries, round_idx=50, window_full_rounds=2, max_chars=500,
        )
        assert len(out) <= 520  # max_chars + small overhead
        assert "truncated" in out or len(out) <= 500
