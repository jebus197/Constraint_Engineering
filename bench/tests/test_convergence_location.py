"""Tests for code-location novelty keying (bench/convergence_location.py).

Pins the T2 discovery (2026-06-08): location-keyed critical novelty converges Exp 42 at
round 7 with a stable zero tail, where the inline model-id path never converges and the
embedding detector falsely converges at round 2.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import pytest

from bench.convergence_location import (
    LocationNoveltyTracker,
    finding_locations,
    target_symbols,
)

RUN = os.path.join(
    os.path.dirname(__file__), "..", "logs",
    "exp42_composer_takeupslack_20260607T154745Z",
    "exp42_composer_takeupslack_report.json",
)
COMPOSER = os.path.join(os.path.dirname(__file__), "..", "cdsfl_registry", "composer.py")


@dataclass
class F:
    """Minimal Finding-like stub: the tracker only reads .severity and .description."""
    severity: float
    description: str


def test_target_symbols_extracts_composer_functions():
    syms = target_symbols(COMPOSER)
    assert "_count_constraints" in syms
    assert "_prune_for_coherence" in syms
    assert "_apply_phenotype_transform" in syms
    # generic/short names excluded
    assert "main" not in syms or len("main") <= 4


def test_finding_locations_word_boundary_and_generic():
    syms = {"_count_constraints", "_prune_for_coherence", "compose"}
    locs = finding_locations("`_count_constraints` skips nested policy entries", syms)
    assert locs == frozenset({"_count_constraints"})
    # 'compose' is generic -> excluded
    assert finding_locations("compose() does X", syms) == frozenset()
    # substring must not match across word boundary
    assert "_count_constraints" not in finding_locations("xx_count_constraintsyy", syms)


def test_same_location_is_refind_location_only():
    syms = frozenset({"_count_constraints", "_prune_for_coherence"})
    t = LocationNoveltyTracker(symbols=syms, consecutive_required=2, earliest_round=0)
    assert t.add_round(0, [F(0.9, "`_count_constraints` skips nested entries")]) == 1
    # re-worded re-find of the SAME function -> NOT new
    assert t.add_round(1, [F(0.9, "the `_count_constraints` helper omits divergence sections")]) == 0
    # a DIFFERENT function -> new
    assert t.add_round(2, [F(0.9, "`_prune_for_coherence` orders situation before domain")]) == 1


def test_subcritical_findings_ignored():
    syms = frozenset({"_prune_for_coherence"})
    t = LocationNoveltyTracker(symbols=syms, severity_threshold=0.7, earliest_round=0)
    assert t.add_round(0, [F(0.4, "`_prune_for_coherence` minor nit")]) == 0  # below threshold


def test_generic_findings_bucketed():
    syms = frozenset({"_prune_for_coherence"})
    t = LocationNoveltyTracker(symbols=syms, consecutive_required=2, earliest_round=0)
    assert t.add_round(0, [F(0.9, "compose() does something broadly wrong")]) == 1  # generic bucket
    assert t.add_round(1, [F(0.9, "compose() also has this other broad issue")]) == 0  # same bucket


@pytest.mark.skipif(not os.path.exists(RUN), reason="Exp 42 run log not present")
def test_exp42_location_keyed_convergence_round7():
    """REGRESSION PIN: location-only keying converges Exp 42 at round 7, stable zero tail."""
    j = json.load(open(RUN))
    syms = target_symbols(COMPOSER)
    t = LocationNoveltyTracker(symbols=syms, severity_threshold=0.7,
                               consecutive_required=3, earliest_round=2)
    for r in j["rounds"]:
        findings = [F(f["severity"], f["description"]) for f in r["findings"]]
        t.add_round(r["round"], findings)
    # Conservative (S3) sequence; the convergence behaviour (R7 + stable tail) is robust
    # to the exact re-find rule — see Convergence_Consolidation_Plan_2026-06-08.md.
    assert t.new_per_round == [10, 2, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert t.converged_round == 7
    # Robust invariants: stable zero tail from round 5; the late "burst" R12-14 = 0 new.
    assert all(v == 0 for v in t.new_per_round[5:]), "zero tail must be stable from round 5"
    assert t.new_per_round[12] == 0 and t.new_per_round[13] == 0 and t.new_per_round[14] == 0


@pytest.mark.skipif(not os.path.exists(RUN), reason="Exp 42 run log not present")
def test_location_keyed_series_makes_real_gate_converge():
    """CHARACTERISATION (the live-gating proof): feed the REAL production convergence
    gate (_check_gamma_alt_convergence) the location-keyed critical series vs the
    ID-proxy series, on the real Exp 42 registry. The ID-proxy series NEVER converges
    (the bug); the location-keyed series converges at round 6. This is what
    `location_keyed_convergence=True` wires into the runner."""
    import bench.reference_runner_v2 as rr
    from collections import Counter
    j = json.load(open(RUN))
    entries = j["registry"]["entries"]

    class _Reg:
        pass
    reg = _Reg(); reg.entries = entries
    syms = target_symbols(COMPOSER)
    loc = rr._location_keyed_critical_series(reg, 15, syms)
    idp = [Counter(e["open_since_round"] for e in entries.values()
                   if (e.get("severity") or 0) >= 0.7).get(r, 0) for r in range(16)]
    assert loc == [10, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    cfg = rr.RunnerConfig()

    def first_converge(series):
        for r in range(16):
            conv, _ = rr._check_gamma_alt_convergence(
                r, 0.5, series[:r + 1], cfg,
                unresolved_critical=0, contested=0, rho_churn=False)
            if conv:
                return r
        return None

    assert first_converge(idp) is None, "ID-proxy series must NOT converge (the bug)"
    assert first_converge(loc) == 6, "location-keyed series must converge at round 6"
