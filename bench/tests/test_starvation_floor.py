"""A pipeline that passes NOTHING must raise its own alarm.

THE DEFECT THIS PINS, measured 2026-08-18.

`regulatory_t_v2` is the autoimmune brake — it exists to notice when the immune
pipeline is destroying good findings. It carried an explicit carve-out:

    if removal_rate > max_rejection_rate:
        if rejected == 0:
            checks_fired.append("depletion_high_duplicate_rate")
            # NOTE: intentionally NOT appending to `reasons`

The reasoning was sound as far as it went. A high duplicate rate IS ordinary
depletion rather than autoimmunity, and the comment says so. What it lacked was a
FLOOR: `rejected == 0` is also true when the pipeline removes EVERY finding, so
total starvation reported as health.

OBSERVED, and this is why the floor exists. From round 1 onward, in every modern
run, `filtered_findings` is empty and the rejection rate is exactly 1.0 — exp44
in 11 of 12 rounds, exp47 in 8 of 8, and likewise exp45, exp46, exp48, exp49.
Root cause dated to 12 April 2026, commit "Phase 2: Embedding similarity shared
backend": under embeddings, UNRELATED findings on this corpus score a minimum of
0.418 against a duplicate threshold of 0.50. The pipeline printed "0/N survived"
every round for five months and this monitor reported healthy every time.

THE DISTINCTION THE FIX PRESERVES. A high duplicate rate can be benign — that
judgement was correct and is kept. Nothing surviving cannot be benign, whatever
reason is offered, so the duplicate/rejected split is not consulted in that case.

This is the project's signature failure shape once more: every failure rendering
as a confident success, in the very component built to notice failure.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from bench.immune_agents import regulatory_t_v2  # noqa: E402


def _verdicts(n: int, duplicated: int, rejected: int) -> dict:
    return {
        f"F{i:03d}": ("DUPLICATE" if i < duplicated
                      else "REJECTED" if i < duplicated + rejected
                      else "CONFIRMED")
        for i in range(n)
    }


def _run(n: int, duplicated: int, rejected: int):
    """Returns (autoimmune_flag, reason). The function returns a 3-tuple, not an
    object — an earlier draft of this test read attributes off the tuple and saw
    None for everything, which looked exactly like the fix not working."""
    flag, reason, _result = regulatory_t_v2(_verdicts(n, duplicated, rejected), [])
    return flag, reason


class TestStarvationRaisesTheAlarm:

    def test_the_archived_pattern_now_fires(self):
        """100% duplicates, nothing survives — the shape every modern run records."""
        flag, reason = _run(10, 10, 0)
        assert flag is True
        assert "STARVATION" in reason

    def test_total_removal_fires_even_when_mixed(self):
        """The duplicate/rejected split must not be consulted when the total is
        everything — otherwise the carve-out simply moves."""
        flag, reason = _run(10, 6, 4)
        assert flag is True

    @pytest.mark.parametrize("n,dup", [(10, 10), (7, 7), (20, 20)])
    def test_it_fires_at_any_size_above_the_minimum(self, n, dup):
        flag, _ = _run(n, dup, 0)
        assert flag is True


class TestLegitimateDepletionStaysQuiet:
    """The fix must not turn the brake into a nuisance. The original judgement —
    that a high duplicate rate is depletion, not autoimmunity — was right."""

    def test_high_duplicate_rate_with_survivors_does_not_fire(self):
        flag, _ = _run(10, 8, 0)
        assert flag is False

    def test_a_healthy_round_does_not_fire(self):
        flag, _ = _run(10, 3, 0)
        assert flag is False

    def test_a_single_survivor_is_enough_to_be_depletion(self):
        """The floor is 'nothing survived', not 'almost nothing survived'. One
        survivor means the discriminator is still discriminating."""
        flag, _ = _run(10, 9, 0)
        assert flag is False
