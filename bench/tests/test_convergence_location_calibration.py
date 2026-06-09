"""Calibration / safety tests for code-location novelty keying.

These are the GATE to trusting the location key as a convergence trigger (T8). They test the
LocationNoveltyTracker against synthetic ground-truth streams — NOT against Exp 42's desired
answer — to establish: (1) re-finds collapse (the bug it fixes); (2) ongoing genuine discovery
blocks convergence (no false convergence); (3) the KNOWN LIMITATION (a second distinct defect
in an already-flagged function is missed by location-only keying) is surfaced explicitly.

The diminishing-returns assumption (discovery decays, is not bursty-with-gaps) is shared by
ALL quiescence criteria — gamma, the raw count, and this. A genuine defect after a K-round
quiet gap is missed by all three; that is a property of the model, mitigated by the severity
veto + A4 unresolved-critical block + adequate K + run length, not a regression of this key.
"""
from __future__ import annotations

from dataclasses import dataclass

from bench.convergence_location import LocationNoveltyTracker

SYMS = frozenset({"func_alpha", "func_beta", "func_gamma", "func_delta", "func_epsilon"})


@dataclass
class F:
    severity: float
    description: str


def crit(loc: str, extra: str = "") -> F:
    return F(0.9, f"`{loc}` mishandles the situation packet {extra}".strip())


# ---------------------------------------------------------------------------
# 1. SEEDED: re-finds collapse (the actual Exp-42 bug, in miniature)
# ---------------------------------------------------------------------------

def test_rewordered_refinds_collapse_and_converge():
    """4 distinct defect-locations found rounds 0-1, then RE-FOUND with different wording
    rounds 2-8. Each location counts new exactly once; the re-finds add zero; converges."""
    t = LocationNoveltyTracker(symbols=SYMS, consecutive_required=3, earliest_round=2)
    locs = ["func_alpha", "func_beta", "func_gamma", "func_delta"]
    # rounds 0-1: introduce all four
    t.add_round(0, [crit("func_alpha"), crit("func_beta")])
    t.add_round(1, [crit("func_gamma"), crit("func_delta")])
    # rounds 2-8: re-finds, each round re-states the same four with fresh wording
    for r in range(2, 9):
        t.add_round(r, [crit(l, extra=f"variant phrasing round {r} number {i}")
                        for i, l in enumerate(locs)])
    assert t.new_per_round == [2, 2, 0, 0, 0, 0, 0, 0, 0]
    assert t.converged_round == 4  # 3 consecutive zeros: rounds 2,3,4
    assert t.converged()


def test_model_id_style_churn_would_not_collapse():
    """Contrast: if the SAME re-finds had unique ids (model-id keying), each would count new.
    We emulate by giving each re-find a UNIQUE location -> never converges (sanity that the
    tracker DOES react to genuinely-distinct locations)."""
    t = LocationNoveltyTracker(symbols=frozenset({f"func_{i}" for i in range(30)}),
                               consecutive_required=3, earliest_round=2)
    for r in range(10):
        t.add_round(r, [F(0.9, f"`func_{r}` is broken")])  # a NEW location every round
    assert t.converged_round is None  # genuine new location each round -> never converges


# ---------------------------------------------------------------------------
# 2. NULL / safety: ongoing genuine discovery blocks convergence
# ---------------------------------------------------------------------------

def test_ongoing_new_locations_block_convergence():
    syms = frozenset({f"func_{i}" for i in range(20)})
    t = LocationNoveltyTracker(symbols=syms, consecutive_required=3, earliest_round=2)
    # new location every round through round 6, then quiet
    for r in range(7):
        t.add_round(r, [F(0.9, f"`func_{r}` mishandles X")])
    assert t.converged_round is None  # still discovering at round 6
    for r in range(7, 11):
        t.add_round(r, [F(0.9, "`func_0` again (re-find)")])  # only re-finds now
    assert t.converged_round == 9  # 3 zeros: rounds 7,8,9


def test_subcritical_late_findings_do_not_block():
    """A clean critical run must not be held open by sub-critical footnotes."""
    t = LocationNoveltyTracker(symbols=SYMS, consecutive_required=3, earliest_round=2)
    t.add_round(0, [crit("func_alpha")])
    for r in range(1, 6):
        t.add_round(r, [F(0.3, f"`func_beta` minor style nit round {r}")])  # sub-critical
    assert t.converged_round == 3  # criticals quiet from round 1; footnotes ignored


# ---------------------------------------------------------------------------
# 3. KNOWN LIMITATION (surfaced, not hidden): 2nd distinct defect in a flagged function
# ---------------------------------------------------------------------------

def test_known_limitation_second_defect_same_function_is_missed():
    """LOCATION-ONLY keying treats any later critical naming an already-flagged function as a
    re-find — so a genuinely DISTINCT second defect in that same function is NOT counted as new.
    This is the documented limitation requiring a calibrated semantic splitter (future work).
    The test PINS the current behaviour so the gap is visible, not silent."""
    t = LocationNoveltyTracker(symbols=SYMS, consecutive_required=2, earliest_round=2)
    t.add_round(0, [F(0.9, "`func_alpha` truncates HARD directives (defect 1)")])
    t.add_round(1, [F(0.9, "`func_beta` ok")])
    # A genuinely different defect in func_alpha at round 4:
    new = t.add_round(4, [F(0.95, "`func_alpha` ALSO drops nested policy constraints (defect 2)")])
    assert new == 0, "location-only keying misses a 2nd distinct defect in a flagged function"
    # This is WHY live-gating promotion is conditional on adding the semantic splitter +
    # null/seeded calibration. Documented in Convergence_Consolidation_Plan_2026-06-08.md.
