"""The rung ladder's promotion RULE, not the ladder, is what fails.

P-PASS of bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py,
2026-10-08, and of 2 claims CC1 made in the panel brief.

ATTACK 1, AND THE FINDING STRENGTHENS. The measurement assumed a CONSTANT
per-rung success probability, which contradicts the design it tests -- the
founder's rungs get harder as a model climbs. With a declining profile a strong
model is kept out of the top rung 0.5930 of the time against 0.4095 under the
constant assumption, so promote-on-one-success excludes good models MORE than
reported, not less.

ATTACK 2, AND CC1's FIRST PROBE WAS WRONG. The brief claims resolution depth is
already recorded, so difficulty needs no classifier. A first probe looked for
`rungs_tried` as a TOP-LEVEL key on a registry entry and found 0 of them,
apparently making the claim an unwired addition. It is not: `rungs_tried` is
nested inside each `routing_history` record. Measured over 305 such records:
rungs_tried takes 0 on 59, 1 on 103 and 2 on 143, and the ladder had more than 1
rung available on 246 of 305, 80.6557%, Wilson [75.8527%, 84.6962%]. The claim
stands and the probe was unrepresentative.

AND A CONSEQUENCE NOBODY HAD ARGUED. Because the cap is 2, `rungs_tried` cannot
exceed 2, so the recorded difficulty signal is TRUNCATED BY THE CAP. Removing the
cap does not only improve coverage -- it unlocks a finer difficulty label, which
is precisely what the founder's promotion ladder needs as its input. That is a
new argument for his no-cap ruling.
"""
from __future__ import annotations

import glob
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


@pytest.fixture(scope="module")
def M():
    spec = importlib.util.spec_from_file_location(
        "promo",
        REPO / "bench" / "the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["promo"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def history():
    """Every routing_history record in the archive."""
    out = []
    for f in sorted(glob.glob(str(REPO / "bench" / "logs" / "**" / "*report*.json"),
                              recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        reg = d.get("registry")
        if not isinstance(reg, dict):
            continue
        entries = (reg.get("entries")
                   if isinstance(reg.get("entries"), dict) else reg)
        if not isinstance(entries, dict):
            continue
        for e in entries.values():
            if not isinstance(e, dict):
                continue
            for h in (e.get("routing_history") or []):
                if isinstance(h, dict):
                    out.append(h)
    return out


class TestOneSuccessPromotionExcludesGoodModels:
    def test_a_strong_model_is_kept_out_a_large_share_of_the_time(self, M):
        d = M.claim_single_success_promotion_is_asymmetric(5)
        assert d[0.90]["P_stuck_below_top"] > 0.35, d[0.90]
        assert d[0.90]["mpmath_agrees"] and d[0.90]["scipy_agrees"]

    def test_the_rule_is_asymmetric_not_merely_noisy(self, M):
        """It must exclude good models MORE than it admits bad ones."""
        d = M.claim_single_success_promotion_is_asymmetric(5)
        assert d[0.90]["P_stuck_below_top"] > d[0.10]["P_reaches_top_rung"] * 1000

    def test_declining_rungs_make_it_worse_not_better(self):
        """MUTATION of the measurement's own assumption.

        If a declining profile IMPROVED the outcome, the constant-p figure would
        be the conservative one and the attack would be empty.
        """
        import numpy as np
        const = 0.90 ** 5
        declining = float(np.prod([0.95, 0.90, 0.85, 0.80, 0.70]))
        assert declining < const, (declining, const)
        assert (1 - declining) > 0.55

    def test_the_obvious_bound_gate_overcorrects(self, M):
        """CC1's own proposed repair is worse on the same axis."""
        d = M.claim_a_bound_gate_fixes_the_asymmetry(5, 10, 0.50)
        assert d["successes_needed_per_rung"] == 9, d
        assert d[0.90]["P_reaches_top_rung"] < 0.30, (
            "if the bound gate did NOT overcorrect, CC1's repair would stand and "
            "there would be nothing for the panel to derive")


class TestTheAbsorbingRungContradictsBidirectionality:
    def test_good_models_are_permanently_capped_by_luck(self, M):
        d = M.claim_the_absorbing_rung_contradicts_bidirectionality(trials=4000)
        assert d["rate"] > 0.30, d
        assert abs(d["rate"] - d["closed_form_check"]) < 0.03, d


class TestDepthIsRecordedAndTruncatedByTheCap:
    def test_rungs_tried_is_nested_not_top_level(self, history):
        """The probe that returned 0 was looking in the wrong place."""
        assert history, "no routing_history records found in the archive"
        assert any("rungs_tried" in h for h in history), (
            "rungs_tried is absent from routing_history too, so the brief's "
            "difficulty claim really is unwired and must be withdrawn")

    def test_recorded_depth_actually_varies(self, history):
        vals = {h.get("rungs_tried") for h in history if "rungs_tried" in h}
        assert len(vals) >= 2, (
            f"depth takes only {vals}, so it cannot label difficulty at all")

    def test_most_records_had_more_than_one_rung_available(self, history):
        n = len(history)
        multi = sum(1 for h in history
                    if isinstance(h.get("rungs_available"), int)
                    and h["rungs_available"] > 1)
        lo, hi = wilson(multi, n)
        assert multi / n > 0.5, (multi, n, lo, hi)

    def test_depth_is_truncated_by_the_cap(self, history):
        """The new argument for removing the cap: it caps the difficulty signal.

        rungs_tried cannot exceed the cap, so while the cap is 2 the label has at
        most 3 levels. This test fails once the cap is lifted and deeper values
        appear -- which is the outcome wanted, and the test should then be updated
        to assert the richer range rather than deleted.
        """
        tried = [h["rungs_tried"] for h in history
                 if isinstance(h.get("rungs_tried"), int)]
        assert tried
        assert max(tried) <= 2, (
            f"depth now reaches {max(tried)}, so the cap has been lifted; update "
            "this assertion to the new range rather than removing it")


class TestDepthIsCensoredAndTheCheckMustExecute:
    """The difficulty check now CALLS route. It used to scan field names.

    CONDEMNED BY THE cc2 SEAT, 2026-10-08: *"The artefact's claim 4 validates this
    by AST-scanning FIELD NAMES -- it never executes `route`, so it would report
    `records_resolution_depth: True` whatever the values are."* That is
    `execute-do-not-grep`, committed by CC1 in a script used to brief a panel.

    AND THE SEAT'S SUBSTANTIVE FINDING, confirmed by execution against the real
    `route`: `rungs_tried` is RIGHT-CENSORED. A finding of true depth 4 reports 2
    under `max_rungs=2`, and a finding genuinely resolved at rung 2 also reports 2.
    The 2 are indistinguishable, so depth orders difficulty only where the ladder
    ran to exhaustion. Under a cap it is a LOWER BOUND.

    This matters for the founder's rung ladder, which needs difficulty as its
    input: the cap must lift before recorded depth can supply it.
    """

    def test_the_check_calls_route_rather_than_reading_it(self):
        src = (REPO / "bench"
               / "the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py").read_text()
        body = src[src.index("def claim_difficulty_can_be_measured_not_judged"):
                   src.index("def main()")]
        assert "RT.route(" in body, (
            "the difficulty claim no longer executes route, so it has reverted to "
            "asserting that a field name exists")
        assert "ast.walk" not in body, (
            "an AST scan is back in the difficulty claim; a field name present is "
            "not a value recorded")

    def test_a_capped_depth_is_indistinguishable_from_an_honest_one(self, M):
        d = M.claim_difficulty_can_be_measured_not_judged()
        assert d["reported_under_cap_2"] == d["a_genuine_rung_2_resolution_reports"]
        assert d["censored_and_honest_are_indistinguishable"] is True, d

    def test_exhaustion_recovers_the_true_depth(self, M):
        d = M.claim_difficulty_can_be_measured_not_judged()
        assert d["reported_under_exhaustion"] == d["true_depth"], d
        assert d["resolved_under_exhaustion"] is True
        assert d["depth_is_a_label_only_under_exhaustion"] is True, (
            "if a capped run also recovered the true depth, the censoring would "
            "not matter and the cap would not block the rung ladder")
