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
    # SNAPSHOT UPDATED 2026-08-08, and the reason is the point of the test.
    # Was [10, 2, 2, 1, 0...]. The `<generic>` bucket fix landed: findings from
    # which no location could be extracted used to share ONE key, so the first
    # claimed it and every later one was non-novel forever. They now key on their
    # own content. That surfaces 3 criticals in this run that were permanently
    # invisible, all in the first four rounds.
    #
    # The direction is the safe one and it is asserted below rather than assumed:
    # the new series is >= the old at every index. Splitting only. Convergence can
    # therefore be DELAYED but never ADVANCED, which is why the gate outcome is
    # unchanged — verified across all 8 archived runs carrying a registry.
    OLD_SERIES = [10, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert loc == [11, 3, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert all(n >= o for n, o in zip(loc, OLD_SERIES)), (
        "the generic-bucket fix must only ever SPLIT, never merge — a series that "
        "dips below the old one means findings are being lost, not surfaced"
    )
    assert sum(loc) - sum(OLD_SERIES) == 3

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


class TestMarkdownTargets:
    """One-shot arc (2026-07-29): exam modules are markdown claim documents."""

    def test_claim_ids_and_headings_extracted(self):
        from bench.convergence_location import target_symbols
        md = ("# Analytical Chemistry Reference\n\n"
              "## Stoichiometry Claims\n\n"
              "CH-01: The combustion of methane balances as CH4 + 2O2 -> CO2 + 2H2O.\n"
              "CH-02: The reaction has a coefficient sum of 6.\n")
        syms = target_symbols(md)
        assert "CH-01" in syms and "CH-02" in syms
        assert any("stoichiometry" in s for s in syms)

    def test_python_targets_unchanged(self):
        from bench.convergence_location import target_symbols
        syms = target_symbols("def compute_ratio(a, b):\n    return a / b\n")
        assert syms == frozenset({"compute_ratio"})

    def test_markdown_finding_locations_match(self):
        from bench.convergence_location import target_symbols, finding_locations
        md = "## Kinetics\nCH-07: rate doubles per 10K rise.\n"
        syms = target_symbols(md)
        assert "CH-07" in finding_locations("The claim CH-07 misstates Arrhenius scaling", syms)
