# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_severity_gates_convergence_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 47ab4145c9345a969325c934d51a7c82ff3d90cd173a4ea5a78f03bb7d56a597
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Boundary constraints any future R_k convergence conjunct must respect.

JOINT ROUND `joint_severity_gates_convergence_2026-10-31`. Both blind seats
agreed the founder's severity definition is R_k (appendix §1.1 / Stage 5,
`compute_rk`), that it should eventually become a FOURTH conjunct beside the
two-sided gate's (a) gamma_critical >= theta, (b) K zero-new-critical rounds,
(c) A4/not-contested — and that it cannot be wired until `entry["model_params"]`
has a writer. The blind round's pinning test was written only into a seat
sandbox and was destroyed with it (the 2026-09-10 failure mode); this file is
the delivered replacement, narrowed to what the JOINT round settled.

What the joint round settled BY EXECUTION — the seats' one live disagreement,
which model sets the bound:

  * The SECOND seat derived bounds from the appendix §1 batch posterior
    R = pi*m/((1-pi)+pi*m), m = (1-q)^n, and its inversion n(R_t). That model
    has no re-injection and can emit targets like 3.19e-10.
  * The FIRST seat derived bounds from the shipped recursion, whose output is
    floored at nu_b (z3: `Rk < nb` is UNSAT over the full valid input box) and
    whose s=1 attractor is nu_b/q (SymPy fixed points {1, nb/q}; Wolfram
    Language agrees; iteration of the real function agrees).

  RESOLUTION: the gate will read `sk_result["R_new"]`, which `compute_rk`
  produces. A bound must therefore be stated in RECURSION coordinates: any
  threshold theta < nu_b is unsatisfiable by the quantity the gate reads, and
  any batch-inversion target below nu_b is unreachable. The batch form remains
  correct for what it answers (risk after n clean passes, no fix applied); it
  is the wrong coordinate system for a bound on R_new.

Producers: SymPy/z3/mpmath/NumPy runs recorded in the joint-round reply of
2026-10-31; Wolfram Language (local Wolfram Engine) as second falsifier for
the fixed points {1, nb/q} and the worked contrast {3.1888e-10, 0.868694}.
"""
import ast
import inspect
import math

import pytest

from bench.reference_runner_v3 import (
    RunnerConfig,
    _check_gamma_alt_convergence,
    compute_rk,
)
import bench.reference_runner_v3 as _runner_module

NU_B, NU_F = 0.05, 0.20   # the model_params fallbacks the runner actually uses


def _batch_posterior(pi: float, q: float, n: int) -> float:
    """Appendix §1 batch form — the coordinate system the bound must NOT use."""
    m = (1.0 - q) ** n
    return pi * m / ((1.0 - pi) + pi * m)


class TestTheFloorIsNuB:
    def test_no_single_update_goes_below_nu_b(self):
        # z3 proved `Rk < nb` UNSAT over R,q,s in [0,1], nb+nf <= 1, q*R < 1
        # (joint round, 2026-10-31). This executes the same claim against the
        # real function on a dense grid, so the pin survives without z3.
        grid = [i / 20 for i in range(21)]
        floor = min(
            compute_rk(R, q, s, NU_B, NU_F)
            for R in grid for q in grid for s in grid
        )
        assert floor >= NU_B - 1e-12, (
            f"compute_rk produced {floor!r} < nu_b={NU_B}; the floor theorem "
            f"is broken and every bound derived from it must be re-derived")

    def test_a_bound_below_nu_b_is_unsatisfiable(self):
        # The operational consequence: a convergence conjunct `R_new <= theta`
        # with theta < nu_b can never pass. 3.19e-10 is the second seat's own
        # batch-inversion output for (pi=0.02, q=0.95, n=6).
        batch_target = _batch_posterior(0.02, 0.95, 6)
        assert batch_target < NU_B, "the demonstration case moved"
        grid = [i / 20 for i in range(21)]
        reachable = min(
            compute_rk(R, q, 1.0, NU_B, NU_F) for R in grid for q in grid
        )
        assert reachable > batch_target, (
            "the shipped recursion reached a batch-coordinate target; the "
            "two models no longer disagree below nu_b and the coordinate "
            "warning in this file's docstring is stale")


class TestTheAttractorIsNuBOverQ:
    @pytest.mark.parametrize("q", [0.95, 0.5, 0.3])
    def test_s1_iteration_converges_to_nb_over_q(self, q):
        for start in (0.999, 0.001):
            r = start
            for _ in range(4000):
                r = compute_rk(r, q, 1.0, NU_B, NU_F)
            assert r == pytest.approx(NU_B / q, abs=1e-6), (
                f"attractor at q={q} moved from nu_b/q={NU_B / q:.6f} to "
                f"{r:.6f}; any pre-registered gate bound expressed as a "
                f"multiple of nu_b/q is now wrong")

    def test_q_at_or_below_nu_b_saturates(self):
        # nu_b/q >= 1 when q <= nu_b: no number of passes reduces risk. This
        # is the formal signature of a question beyond the ensemble, and a
        # gate bound must treat it as NEVER-CONVERGE, not as a high threshold.
        r = 0.5
        for _ in range(4000):
            r = compute_rk(r, NU_B, 1.0, NU_B, NU_F)
        assert r > 0.99

    def test_one_is_absorbing(self):
        for q in (0.05, 0.5, 0.95):
            for s in (0.0, 0.5, 1.0):
                assert compute_rk(1.0, q, s, NU_B, NU_F) == 1.0


class TestThePreconditionsAreStillOpen:
    """These two pins turn RED when the wiring lands — deliberately, so the
    gate conjunct and its bound are added together, not discovered apart."""

    def test_model_params_still_has_no_writer(self):
        src = inspect.getsource(_runner_module)
        tree = ast.parse(src)
        writers = []
        for node in ast.walk(tree):
            # entry["model_params"] = ...  /  x.setdefault("model_params", ...)
            if isinstance(node, ast.Subscript) and \
                    isinstance(node.slice, ast.Constant) and \
                    node.slice.value == "model_params" and \
                    isinstance(node.ctx, (ast.Store, ast.Del)):
                writers.append(node.lineno)
            if isinstance(node, ast.Call) and \
                    isinstance(node.func, ast.Attribute) and \
                    node.func.attr == "setdefault" and node.args and \
                    isinstance(node.args[0], ast.Constant) and \
                    node.args[0].value == "model_params":
                writers.append(node.lineno)
        assert writers == [], (
            f"model_params gained writer(s) at line(s) {writers}: q and pi "
            f"can now vary per question. The R_k gate conjunct is now "
            f"implementable — update this file AND register the bound "
            f"(theta >= nu_b, expressed per-question as a multiple of "
            f"nu_b/q) BEFORE wiring the conjunct, per the joint round of "
            f"2026-10-31")

    def test_convergence_gate_signature_carries_no_risk_term(self):
        params = set(
            inspect.signature(_check_gamma_alt_convergence).parameters)
        rk_like = {p for p in params
                   if "r_new" in p.lower() or "r_old" in p.lower()
                   or "residual" in p.lower() or p.lower() in ("r", "rk", "r_k")}
        assert rk_like == set(), (
            f"the convergence gate grew risk parameter(s) {sorted(rk_like)}; "
            f"RECORDED-ONLY is no longer true and the bound registered with "
            f"it must satisfy theta >= nu_b={NU_B}")
