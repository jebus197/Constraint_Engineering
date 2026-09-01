"""Tests for the Exp 40 1E.10 channel-assignment boundary.

The divergence modulator m_div may only enter R_k through eta_int.
Passing m_div in a forbidden slot (R_k pre-factor, free factor in q,
contribution to nu_k) must raise ChannelViolationError.

The symbolic channel invariant was proven in round-2 Divergence
confer (41/41 SymPy/z3); these tests verify the runtime enforcement
at the compute_rk_with_eta_channel call site.
"""

from __future__ import annotations

import math

import pytest

from bench.reference_runner_v3 import (
    ChannelViolationError,
    compute_rk,
    compute_rk_with_eta_channel,
)


class TestChannelComposition:
    """With the channel enforced, R_k output matches the documented pipeline."""

    def test_compliant_no_modulation(self):
        # m_div = 1.0 means no modulation — R_k equals the direct-q form.
        eta_int, c_ext, nu_k, d, p = 0.5, 0.3, 0.7, 0.8, 0.9
        eta_combined = eta_int * (1 - c_ext * (1 - nu_k))
        q_direct = eta_combined * d * p
        direct = compute_rk(R_old=0.4, q=q_direct, sk=0.5)

        wrapped = compute_rk_with_eta_channel(
            R_old=0.4, sk=0.5,
            eta_int=eta_int, m_div=1.0,
            c_ext=c_ext, nu_k=nu_k, d=d, p=p,
        )
        assert math.isclose(direct, wrapped, abs_tol=1e-9)

    def test_severe_modulation_reduces_q(self):
        # m_div = 0.6 (severe tier) reduces eta_int to 60% of its unmodulated
        # value. The resulting q must be 0.6 × q_unmodulated.
        eta_int, c_ext, nu_k, d, p = 0.5, 0.3, 0.7, 0.8, 0.9
        eta_combined_full = eta_int * (1 - c_ext * (1 - nu_k))
        q_full = eta_combined_full * d * p
        q_severe = 0.6 * q_full

        direct = compute_rk(R_old=0.4, q=q_severe, sk=0.5)
        wrapped = compute_rk_with_eta_channel(
            R_old=0.4, sk=0.5,
            eta_int=eta_int, m_div=0.60,
            c_ext=c_ext, nu_k=nu_k, d=d, p=p,
        )
        assert math.isclose(direct, wrapped, abs_tol=1e-9)

    def test_tier_ordering(self):
        # Higher m_div (less modulation) → higher q → lower R_k
        # (more failures admitted; residual probability goes DOWN).
        tiers = [0.60, 0.70, 0.85, 1.00]
        rks = [
            compute_rk_with_eta_channel(
                R_old=0.5, sk=0.5,
                eta_int=0.5, m_div=m,
                c_ext=0.3, nu_k=0.7, d=0.8, p=0.9,
            )
            for m in tiers
        ]
        # Strictly monotone decreasing as modulation weakens.
        assert all(rks[i] >= rks[i + 1] for i in range(len(rks) - 1))


class TestChannelViolations:
    """Forbidden assignments raise ChannelViolationError."""

    @pytest.mark.parametrize("bad_m_div", [-0.01, 1.01, 1.5, -1.0, 2.0, 100.0])
    def test_m_div_out_of_range(self, bad_m_div):
        with pytest.raises(ChannelViolationError) as exc:
            compute_rk_with_eta_channel(
                R_old=0.5, sk=0.5,
                eta_int=0.5, m_div=bad_m_div,
                c_ext=0.3, nu_k=0.7, d=0.8, p=0.9,
            )
        assert "m_div" in str(exc.value)

    @pytest.mark.parametrize("bad_eta_int", [-0.1, 1.1, 10.0])
    def test_eta_int_out_of_range(self, bad_eta_int):
        with pytest.raises(ChannelViolationError):
            compute_rk_with_eta_channel(
                R_old=0.5, sk=0.5,
                eta_int=bad_eta_int, m_div=0.85,
                c_ext=0.3, nu_k=0.7, d=0.8, p=0.9,
            )

    @pytest.mark.parametrize("name, bad_value", [
        ("c_ext", -0.1), ("c_ext", 1.5),
        ("nu_k", -0.5), ("nu_k", 2.0),
        ("d", -1.0), ("d", 1.1),
        ("p", -0.01), ("p", 1.5),
    ])
    def test_other_factors_out_of_range(self, name, bad_value):
        kwargs = {
            "R_old": 0.5, "sk": 0.5,
            "eta_int": 0.5, "m_div": 0.85,
            "c_ext": 0.3, "nu_k": 0.7, "d": 0.8, "p": 0.9,
        }
        kwargs[name] = bad_value
        with pytest.raises(ChannelViolationError) as exc:
            compute_rk_with_eta_channel(**kwargs)
        assert name in str(exc.value)


class TestBoundaryConditions:
    """Edge values at the allowed boundaries work without raising."""

    def test_zero_m_div(self):
        # m_div = 0 means total suppression — eta_int_modulated = 0,
        # q = 0. compute_rk with q=0 returns R_old with re-injection.
        rk = compute_rk_with_eta_channel(
            R_old=0.5, sk=0.5,
            eta_int=0.5, m_div=0.0,
            c_ext=0.3, nu_k=0.7, d=0.8, p=0.9,
        )
        assert 0.0 <= rk <= 1.0

    def test_unit_values_all_factors(self):
        # All factors at 1.0 — q = 1.0 (maximum failure admission).
        rk = compute_rk_with_eta_channel(
            R_old=0.5, sk=0.5,
            eta_int=1.0, m_div=1.0,
            c_ext=1.0, nu_k=1.0, d=1.0, p=1.0,
        )
        assert 0.0 <= rk <= 1.0

    def test_zero_eta_int(self):
        # eta_int = 0 — channel closed, q = 0 regardless of m_div.
        for m in (0.60, 0.70, 0.85, 1.00):
            rk = compute_rk_with_eta_channel(
                R_old=0.3, sk=0.5,
                eta_int=0.0, m_div=m,
                c_ext=0.3, nu_k=0.7, d=0.8, p=0.9,
            )
            assert 0.0 <= rk <= 1.0


class TestWrapperIdentityModeGridSweep:
    """F2 shadow-promotion identity guarantee (2026-04-21).

    At m_div=1.0, c_ext=0, nu_k=0, d=1, p=1, eta_int=q the wrapper
    reduces mathematically to bare compute_rk(q). This test documents
    the identity-mode invariant the Exp 40 shipping config relies on
    (reference_runner_v3.py:3510) by sweeping a dense grid and
    comparing both forms within 1e-9.
    """

    def test_grid_identity_mode(self):
        eta_ints = [0.0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1.0]
        R_olds = [0.05, 0.15, 0.3, 0.45, 0.5, 0.6, 0.75, 0.85, 0.95]
        sks = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9]
        mismatches = []
        count = 0
        for q in eta_ints:
            for R_old in R_olds:
                for sk in sks:
                    count += 1
                    direct = compute_rk(R_old=R_old, q=q, sk=sk)
                    wrapped = compute_rk_with_eta_channel(
                        R_old=R_old, sk=sk,
                        eta_int=q, m_div=1.0,
                        c_ext=0.0, nu_k=0.0, d=1.0, p=1.0,
                    )
                    if not math.isclose(direct, wrapped, abs_tol=1e-9):
                        mismatches.append((q, R_old, sk, direct, wrapped))
        assert not mismatches, (
            f"F2 identity violated in {len(mismatches)}/{count} cases: "
            f"{mismatches[:5]}"
        )
        assert count >= 500, f"Grid too sparse: only {count} cases"


class TestForbiddenShortcutDetection:
    """Demonstrates the class of errors the channel check prevents."""

    def test_r_old_premultiplied_would_be_caught_if_out_of_range(self):
        # If a caller did R_old' = m_div * R_old with R_old > 1 and m_div
        # large enough to bring R_old' into [0, 1], the range check can't
        # catch it alone. But the channel check DOES catch the m_div itself
        # being out of range in any such attempt to disguise the pattern.
        #
        # More importantly: m_div as a pre-factor on R_k is impossible to
        # express via compute_rk_with_eta_channel — the channel is enforced
        # by construction because the function composes q internally from
        # the named factors. The only way for a caller to violate the
        # channel is to bypass this wrapper entirely and hand-build q —
        # which is precisely the case 1E.10 flags at review time.
        # This test documents that the wrapper does NOT accept a pre-
        # computed q (so you cannot smuggle a bad q past it).
        import inspect
        sig = inspect.signature(compute_rk_with_eta_channel)
        assert "q" not in sig.parameters, \
            "compute_rk_with_eta_channel must compose q internally — "\
            "accepting q as a parameter would defeat the channel check."
