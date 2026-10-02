# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'green_board_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 219fe7c64e4ed998973d29d5d3da1ab73992040c9f35f2f7f1bc1d19f82ab424
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""compute_rk tracks the DETECTION BRANCH, and that is a decision, pinned.

THE MODEL QUESTION, settled 2026-09-29 (panel, green-board item 4) under the
founder's framing: accuracy in MEASURING an already-expended run, and
PREDICTIVE accuracy before one. They are answers to two different questions:

  branch (shipped):   A(R) = sigma*B_minus + (1-sigma)*R,
                      B_minus = R(1-q)/(1-qR)   -- the Bayes posterior after
                      a pass that FOUND NOTHING. The runner is a measurement
                      instrument: it updates as realised rounds land, and a
                      converged run's final rounds are observed quiet rounds.
                      Conditioning on what actually happened is measurement.
  expectation (Astra): M(R) = R(1-q*sigma)     -- the branch-weighted average
                      BEFORE the outcome is known. The honest quantity for a
                      decision, because the decision precedes the outcome.
                      It is the explorer's prospective mode, already shipped
                      with its own floor and break-even.

DERIVED, NOT ASSERTED (SymPy, re-run below numerically against the live
function; Wolfram concurs on the identity):

  * A - M = R^2*q*sigma*(1-q)/(1-qR) >= 0 on the unit cube: the branch form
    NEVER flatters. Switching the runner to M lowers every archived R_k
    (measured blast radius: 386/386 triples move, median 0.0438) -- the
    direction that licenses earlier convergence. A measurement channel must
    not be moved in the flattering direction by a modelling preference.
  * Law of total probability: (1-qR)*B_minus + qR*(1-sigma)*1 = M exactly.
    M is the coherent average of the branch posteriors -- correct BEFORE the
    round. After a quiet round, the observed-branch posterior is B_minus,
    and averaging over a branch you already observed under-states risk.

THE RULING PINNED HERE: the runner KEEPS the branch (measurement); the
expectation LIVES in the explorer (prediction), where both modes are already
selectable. No report field is added: a field no channel reads is the
"addition that nothing reaches" this project has confirmed 11 times.

These tests import the REAL compute_rk. A silent switch to the expectation
-- the mutation this file exists to catch -- fails every class below.
"""
from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bench.reference_runner_v3 import compute_rk  # noqa: E402

GRID = [i / 10 for i in range(11)]


def _expectation(R, q, s):
    return R * (1.0 - q * s)


class TestTheBranchIsWhatShips:
    def test_the_briefs_own_discriminating_point(self):
        """R=1/2, q=4/5, sigma=1: branch 1/6, expectation 1/10. The shipped
        value IS the negative-branch posterior, exactly."""
        got = compute_rk(0.5, 0.8, 1.0, nu_b=0.0, nu_f=0.0)
        assert got == pytest.approx(1 / 6, abs=1e-12)
        assert abs(got - 0.1) > 0.06, (
            "compute_rk now returns the branch-weighted expectation; that "
            "silently lowers every archived R_k (386/386 measured) and "
            "loosens every threshold read downstream. This is a founder-level "
            "model decision, not a refactor.")

    def test_the_gap_identity_holds_on_the_live_function(self):
        """A - M = R^2*q*s*(1-q)/(1-qR), SymPy-derived, executed here against
        the real implementation with re-injection off."""
        for R in GRID:
            for q in GRID:
                for s in GRID:
                    if q * R == 1.0:
                        continue
                    a = compute_rk(R, q, s, nu_b=0.0, nu_f=0.0)
                    gap = R * R * q * s * (1 - q) / (1 - q * R)
                    assert a - _expectation(R, q, s) == pytest.approx(
                        gap, abs=1e-9), (R, q, s)

    def test_the_branch_never_flatters(self):
        """A >= M everywhere, with re-injection ON at the shipped defaults:
        phase 3 is increasing in its input, so the ordering survives it.
        The conservative direction is the fail-safe direction for a gate."""
        for R in GRID:
            for q in GRID:
                for s in GRID:
                    if q * R == 1.0:
                        continue
                    a = compute_rk(R, q, s)
                    nu_eff = 1.0 - (1.0 - 0.05) * (1.0 - (1.0 - s) * 0.20)
                    m3 = _expectation(R, q, s) * (1.0 - nu_eff) + nu_eff
                    assert a >= m3 - 1e-12, (R, q, s, a, m3)

    def test_law_of_total_probability_closes(self):
        """The expectation is the coherent branch average -- so the two forms
        are two QUESTIONS, not a right and a wrong formula. Pinned so the
        next panel starts from the derivation, not from scratch."""
        for R in GRID:
            for q in GRID:
                for s in GRID:
                    if q * R == 1.0:
                        continue
                    b_minus = R * (1 - q) / (1 - q * R)
                    lhs = (1 - q * R) * b_minus + q * R * (1 - s)
                    assert lhs == pytest.approx(_expectation(R, q, s),
                                                abs=1e-12)


class TestTheEquilibriumSeparatesTheQuestions:
    """At nu > 0 the two recursions settle at DIFFERENT floors. The archive's
    R_k series must settle at the trajectory floor; landing on the
    expectation floor is the same silent switch seen from equilibrium."""

    def test_iterated_compute_rk_reaches_the_trajectory_floor(self):
        nu, q, s = 0.1, 0.4, 0.5
        R = 0.9
        for _ in range(4000):
            R = compute_rk(R, q, s, nu_b=nu, nu_f=0.0)
        traj = nu / (q * (s + nu * (1 - s)))          # 0.4545...
        expc = nu / (q * s + nu * (1 - q * s))        # 0.3571...
        assert R == pytest.approx(traj, abs=1e-9)
        assert abs(R - expc) > 0.09, (
            "the iterated runner recursion has moved to the expectation's "
            "equilibrium -- the measurement channel changed meaning")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
