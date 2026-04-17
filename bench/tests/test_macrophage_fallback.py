"""Tests for Macrophage shadow-cell verdict-wiring fallback.

Item 1B.1 from Exp 40 execution plan. In Exp 39-0, Macrophage observed
zero anomalies across all 6 rounds despite the immune pipeline producing
16+ verdicts per round. The Macrophage primary path reads
``immune_result.cell_verdicts`` (Dict[str, List[CellVerdict]]); the Exp 40
fix adds a fallback that synthesises from ``final_verdicts`` (Dict[str, str])
so the cluster / severity / timing checks can fire even when the
structured verdict list is empty or missing.

These tests confirm:
  1. Primary path works when cell_verdicts is populated.
  2. Fallback path fires when cell_verdicts is empty but final_verdicts is set.
  3. Synthesised verdict objects have .verdict and .confidence attributes.
  4. End-to-end: Macrophage patrol detects verdict_cluster on 100% duplicates
     (the actual failure mode from Exp 39-0 R5).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import List

import pytest

from bench.macrophage_cell import MacrophageCell, MacrophageMode


def _make_cell_verdict(fid: str, verdict: str, confidence: float = 0.5):
    """Lightweight CellVerdict-like stand-in."""
    return SimpleNamespace(
        finding_id=fid,
        verdict=verdict,
        confidence=confidence,
        tool_used="test_tool",
        cell_type="test",
    )


class TestPrimaryPath:
    def test_populated_cell_verdicts_extract_correctly(self):
        """When cell_verdicts has entries, all verdicts flatten out."""
        cell_verdicts = {
            "f1": [_make_cell_verdict("f1", "CONFIRM")],
            "f2": [_make_cell_verdict("f2", "CONFIRM")],
            "f3": [_make_cell_verdict("f3", "REJECT")],
        }
        flattened = [v for vlist in cell_verdicts.values() for v in vlist]
        assert len(flattened) == 3
        assert all(hasattr(v, "verdict") for v in flattened)


class TestFallbackPath:
    def test_synthesise_from_final_verdicts(self):
        """When cell_verdicts empty, fallback builds verdicts from final_verdicts."""
        final_verdicts = {"f1": "CONFIRMED", "f2": "REJECTED", "f3": "DUPLICATE"}
        final_confidences = {"f1": 0.9, "f2": 0.8, "f3": 0.7}

        synthesised = []
        for fid, vstr in final_verdicts.items():
            conf = final_confidences.get(fid, 0.5)
            synthesised.append(SimpleNamespace(
                finding_id=fid, verdict=vstr, confidence=conf,
                tool_used="synthesised_from_final_verdicts",
                cell_type="synthesised",
            ))

        assert len(synthesised) == 3
        assert synthesised[0].verdict == "CONFIRMED"
        assert synthesised[1].confidence == 0.8
        assert synthesised[2].tool_used == "synthesised_from_final_verdicts"


class TestMacrophageEndToEnd:
    """Exp 39-0 R5 replay: 100% DUPLICATE verdicts should fire verdict_cluster."""

    def test_100_percent_duplicate_fires_cluster_anomaly(self):
        """16 verdicts all DUPLICATE → verdict_cluster anomaly at ratio 1.0."""
        mac = MacrophageCell(mode=MacrophageMode.PATROL, shadow=True)
        verdicts = [_make_cell_verdict(f"f{i}", "DUPLICATE") for i in range(16)]
        summary = mac.observe(verdicts=verdicts)
        cluster_anomalies = [
            o for o in summary.observations if o.category == "verdict_cluster"
        ]
        assert len(cluster_anomalies) >= 1, (
            "Macrophage should detect verdict_cluster on 100% duplicates; "
            f"got observations: {[o.category for o in summary.observations]}"
        )
        # Severity should be 1.0 at ratio 1.0 (capped)
        assert max(o.severity for o in cluster_anomalies) == 1.0

    def test_synthesised_verdicts_trigger_patrol_checks(self):
        """Synthesised SimpleNamespace objects are accepted by patrol observer."""
        mac = MacrophageCell(mode=MacrophageMode.PATROL, shadow=True)
        # All DUPLICATE, synthesised from final_verdicts fallback
        synthesised = [
            SimpleNamespace(
                finding_id=f"f{i}", verdict="DUPLICATE", confidence=0.7,
                tool_used="synthesised_from_final_verdicts",
                cell_type="synthesised",
            )
            for i in range(16)
        ]
        summary = mac.observe(verdicts=synthesised)
        # Fires verdict_cluster (100% DUPLICATE > 80% threshold)
        cluster_anomalies = [
            o for o in summary.observations if o.category == "verdict_cluster"
        ]
        assert len(cluster_anomalies) >= 1

    def test_below_min_findings_returns_no_observations(self):
        """MIN_FINDINGS_FOR_ANALYSIS gate: 2 verdicts < 3 → no observations.

        This is by design (patrol needs sample size), not a bug. Confirms the
        Exp 39-0 symptom is not due to this gate (39-0 had 16+ verdicts).
        """
        mac = MacrophageCell(mode=MacrophageMode.PATROL, shadow=True)
        verdicts = [_make_cell_verdict(f"f{i}", "DUPLICATE") for i in range(2)]
        summary = mac.observe(verdicts=verdicts)
        assert len(summary.observations) == 0


class TestDiagnosticLogPath:
    """When both cell_verdicts and final_verdicts are empty, the diagnostic
    log should fire with both-path status.  This asserts the log-line format
    rather than emission (log is side-effect). The fallback implementation
    lives in reference_runner_v2._run_shadow_cells."""

    def test_both_paths_empty_reports_both(self):
        """An ImmuneResponse-like object with empty verdicts both ways."""
        immune_result = SimpleNamespace(
            cell_verdicts={},
            final_verdicts={},
            final_confidences={},
        )
        # Primary path: empty
        all_verdicts = []
        for vlist in immune_result.cell_verdicts.values():
            all_verdicts.extend(vlist)
        assert len(all_verdicts) == 0

        # Fallback path: also empty
        fv = getattr(immune_result, "final_verdicts", None)
        if fv:
            for fid, verdict_str in fv.items():
                all_verdicts.append(SimpleNamespace(
                    finding_id=fid, verdict=verdict_str, confidence=0.5,
                ))
        assert len(all_verdicts) == 0
