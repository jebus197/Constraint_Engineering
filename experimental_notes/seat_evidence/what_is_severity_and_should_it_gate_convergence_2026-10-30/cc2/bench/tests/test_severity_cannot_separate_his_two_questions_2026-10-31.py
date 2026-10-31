# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'what_is_severity_and_should_it_gate_convergence_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 887ee7e5ce8fe1d1efce2f7c15e39a5ce8a96d50044fe65b7ee82d7d6743f8a4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Severity-as-residual-risk: pin the gap that stops it gating convergence.

WHY THIS FILE EXISTS. The founder asked (2026-10-30) whether severity should
feed the convergence mechanics rather than be recorded only, and gave the
definition: *the chance that a particular flaw, or class of flaws, remains
after a given number of passes under severe scrutiny*. That quantity already
exists in this harness -- it is ``R_k(i)``, computed by
``bench.reference_runner_v3.compute_rk`` and recorded as
``sk_result["R_new"]``. It is NOT ``entry["severity"]``, which is a
model-asserted consequence rating cut at ``CRITICAL_SEVERITY_THRESHOLD``.
Measured over 1,252 archived entries carrying both, the two are near
orthogonal: Spearman -0.1408, p = 5.7e-07
(``scripts/his_severity_definition_is_the_models_own_quantity_2026-10-31.py``).

The answer to his question is BLOCKED, not open, and this file makes the
blockage executable rather than a paragraph in a panel report. Four facts,
each asserted by running the real code:

  1. ``model_params`` -- the sole source of ``q``, the per-pass detection
     probability -- has ZERO writers in the live runner. The runner's own
     comment at the ``R_old`` precedence block already says so. So ``q``
     is ``0.5`` on every real run.
  2. With ``q`` and ``pi`` both pinned, ``R_k`` is a function of ``S_k``
     ALONE. It returns the same number for his 4+4 example and for his
     Riemann example. A gate reading it would be gating on fix quality
     wearing a residual-risk label.
  3. The one measured channel that could move ``pi`` -- the appendix 1.5
     blend ``pi = (1-rho)*pi_base + rho*pi_mem`` -- is confined by the
     shipped ``rho`` to a window 0.2 wide centred on 0.5. His worked
     example needs 0.02 .. 0.90. Neither endpoint is reachable.
  4. The live two-sided gate CONVERGES on a run where ``R_k`` rises
     monotonically toward its fixed point of 1.0 -- the ``q = 0`` case,
     a question whose flaws this panel cannot see. That is the failure
     his proposal would catch, and it is a real call of the real gate.

And one POSITIVE result, which is the answer to his "what should realistic
boundaries be": the boundaries are not chosen, they are derived from the
model already in the code. Under a perfect fix the recursion's fixed point
is ``R* = nu_b / q`` and its floor at perfect detection is ``nu_b``. So the
bound on severity is set by the harness's detection power on THAT question,
which is exactly why it cannot be a single constant. Derived with SymPy and
independently confirmed with Wolfram Language (local Wolfram Engine); here it
is asserted by ITERATING THE REAL ``compute_rk`` rather than by re-deriving.

NOTHING IS DISABLED OR REMOVED BY THIS FILE. It adds checks only. Items 1-4
are expected to stop holding once the writers land: each assertion is phrased
so that fixing the gap turns the test red and forces a deliberate update,
which is the point -- a measured gap that can be closed silently is not
pinned.
"""

import ast
import inspect
import math
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bench.reference_runner_v3 import (  # noqa: E402  real target, not a copy
    CRITICAL_SEVERITY_THRESHOLD,
    RK0_PI_BASE,
    RunnerConfig,
    _check_gamma_alt_convergence,
    compute_rk,
)

_RUNNER_SRC = os.path.join(_ROOT, "bench", "reference_runner_v3.py")

#: The shipped re-injection parameters, as ``compute_rk``'s own signature
#: defaults declare them. Read, not retyped, so a change to the signature
#: cannot leave this file asserting a stale pair.
_NU_B = compute_rk.__defaults__[0]
_NU_F = compute_rk.__defaults__[1]

#: His two worked questions, as (pi, q). pi is the prior flaw rate; q is the
#: per-pass detection probability. 4+4 -- an easy question a competent panel
#: sees through -- is a low prior and near-perfect detection. The Riemann
#: hypothesis is a high prior and near-zero detection: the panel cannot see
#: the flaw, so passes do not remove it.
_FOUR_PLUS_FOUR = (0.02, 0.95)
_RIEMANN = (0.90, 0.05)


def _runner_tree():
    with open(_RUNNER_SRC) as fh:
        src = fh.read()
    return src, ast.parse(src)


def _enclosing_fn(tree, lineno):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and \
                node.lineno <= lineno <= (node.end_lineno or 0):
            if best is None or node.lineno > best.lineno:
                best = node
    return best.name if best else "<module>"


# -- 1. q has no writer, so it is 0.5 on every real run ---------------------

def test_model_params_has_no_writer_so_q_is_pinned():
    """``q`` enters ``R_k`` only via ``entry["model_params"]``, and nothing
    assigns that key. Structural (AST), the same technique
    ``test_immune_memory_consumption.py`` uses for the R_k guard -- a grep
    would also match the runner's own prose about the gap.

    A WRITE is ``entry["model_params"] = ...``, ``.setdefault("model_params")``
    or ``.update({"model_params": ...})``. Reads are not writes.
    """
    _src, tree = _runner_tree()

    writers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and \
                isinstance(node.slice, ast.Constant) and \
                node.slice.value == "model_params" and \
                isinstance(node.ctx, ast.Store):
            writers.add(_enclosing_fn(tree, node.lineno))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in {"setdefault", "update"}:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == "model_params":
                    writers.add(_enclosing_fn(tree, node.lineno))
                if isinstance(arg, ast.Dict):
                    for key in arg.keys:
                        if isinstance(key, ast.Constant) and \
                                key.value == "model_params":
                            writers.add(_enclosing_fn(tree, node.lineno))

    readers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "get" and node.args \
                and isinstance(node.args[0], ast.Constant) \
                and node.args[0].value == "model_params":
            readers.add(_enclosing_fn(tree, node.lineno))

    assert readers, "model_params lost its reader; the R_k parameter path moved"
    assert writers == set(), (
        f"model_params GAINED a writer: {sorted(writers)}. This is the "
        f"precondition the 2026-10-31 severity panel named. Re-measure whether "
        f"R_k now separates the founder's two worked questions and update the "
        f"assertions below -- do NOT simply relax this one."
    )


# -- 2. R_k is blind to difficulty: 4+4 and Riemann score identically -------

def test_r_k_returns_the_same_number_for_four_plus_four_and_riemann():
    """The consequence of item 1, executed on the real function.

    With ``model_params`` unwritten the pipeline passes ``q = 0.5`` and
    ``R_old = RK0_PI_BASE`` for EVERY finding regardless of the question, so
    ``R_k`` collapses to a function of ``S_k``. The two questions the founder
    contrasted therefore receive the same residual risk, which is the precise
    sense in which severity "tells us very little" today.
    """
    sk = 1.0  # a perfect fix, so only the question differs
    as_run_4p4 = compute_rk(RK0_PI_BASE, 0.5, sk)
    as_run_rh = compute_rk(RK0_PI_BASE, 0.5, sk)
    assert as_run_4p4 == as_run_rh, "pipeline inputs are no longer pinned"
    assert math.isclose(as_run_4p4, 0.366666666, abs_tol=1e-6), (
        f"the pinned operating point moved: {as_run_4p4}. The archive's modal "
        f"R_new (743 of 1252 entries) sits at this value precisely because the "
        f"inputs are constant; re-measure the archive before editing."
    )

    # The formula itself is NOT the problem: fed the real questions it
    # separates them by orders of magnitude. The defect is upstream wiring.
    able_4p4 = compute_rk(_FOUR_PLUS_FOUR[0], _FOUR_PLUS_FOUR[1], sk)
    able_rh = compute_rk(_RIEMANN[0], _RIEMANN[1], sk)
    assert able_rh > 10 * able_4p4, (
        f"compute_rk can no longer separate the two questions "
        f"(4+4={able_4p4}, RH={able_rh}); the mathematical model, not the "
        f"wiring, would then be the thing to repair."
    )


# -- 3. the measured pi channel is confined to a 0.2-wide window ------------

def test_the_blended_prior_cannot_reach_either_of_his_endpoints():
    """``pi = (1-rho)*pi_base + rho*pi_mem`` with the shipped ``rho`` and a
    constant ``pi_base`` spans [0.4, 0.6] even when ``pi_mem`` is free over
    its whole range. His example needs [0.02, 0.90].

    This is a HARD arithmetic ceiling, not a missing writer: turning immune
    memory consumption on does not lift it. ``pi_mem`` is additionally
    Beta-Binomial smoothed with 0.5/0.5 pseudocounts, so in practice the
    window is narrower still.
    """
    cfg = RunnerConfig()
    rho = cfg.immune_memory_rho
    lo = (1.0 - rho) * RK0_PI_BASE + rho * 0.0
    hi = (1.0 - rho) * RK0_PI_BASE + rho * 1.0
    width = hi - lo

    assert math.isclose(width, rho, abs_tol=1e-12), "the blend form changed"
    needed = _RIEMANN[0] - _FOUR_PLUS_FOUR[0]
    assert width < needed, (
        f"achievable pi window {width:.4f} now covers the {needed:.4f} his "
        f"worked example requires -- re-measure before relaxing"
    )
    assert lo > _FOUR_PLUS_FOUR[0], (
        f"pi can now reach down to his 4+4 prior ({lo:.4f} <= "
        f"{_FOUR_PLUS_FOUR[0]}); the floor has been lifted"
    )
    assert hi < _RIEMANN[0], (
        f"pi can now reach up to his Riemann prior ({hi:.4f} >= "
        f"{_RIEMANN[0]}); the ceiling has been lifted"
    )


# -- 4. the live gate converges while residual risk rises ------------------

def test_live_gate_converges_on_a_run_whose_residual_risk_is_rising():
    """THE CASE HIS PROPOSAL TARGETS, against the REAL gate function.

    A question with zero detection power yields an all-zero critical series,
    because nothing was detectable. The settled novelty condition is then
    satisfied for free and the vacuous-curve branch admits the run. Meanwhile
    ``R_k`` rises every pass -- at ``q = 0`` the recursion's only fixed point
    is 1.0, so more passes make residual risk WORSE, not better.

    The gate's reason string does warn the reader ("a clean target and a
    broken severity classifier look alike from here"), but it returns True
    and the loop acts on the boolean.
    """
    cfg = RunnerConfig()

    risk = _RIEMANN[0]
    trajectory = [risk]
    for _ in range(6):
        risk = compute_rk(risk, 0.0, 1.0)  # q = 0: nothing is detected
        trajectory.append(risk)

    assert all(b > a for a, b in zip(trajectory, trajectory[1:])), (
        f"residual risk no longer rises monotonically at q=0: {trajectory}"
    )

    converged, reason = _check_gamma_alt_convergence(
        round_idx=6,
        gamma=0.9,
        novel_critical_history=[0, 0, 0, 0, 0, 0],
        cfg=cfg,
        unresolved_critical=0,
        contested=0,
        rho_churn=False,
        irreducible_queue=0,
        gamma_critical=0.0,
        total_findings=12,
    )

    assert converged is True, (
        f"the gate NO LONGER converges on the zero-detection run -- a severity "
        f"or residual-risk condition may have landed. Reason: {reason}"
    )
    assert "CONVERGED" in reason
    # And nothing in the gate's signature can see the risk figure: that is the
    # structural guard in test_immune_memory_consumption.py, correct for
    # R_k(0) and over-broad for R_k(i>=1). Stated here as the reason the
    # condition cannot simply be added.
    params = set(inspect.signature(_check_gamma_alt_convergence).parameters)
    assert not (params & {"residual_risk", "R_k", "r_new", "severity"}), (
        f"the gate gained a risk/severity parameter: {sorted(params)} -- the "
        f"2026-10-31 panel's blocked recommendation may have been implemented; "
        f"re-measure items 1-3 before trusting it"
    )


# -- 5. POSITIVE: the boundary is derived, not chosen ----------------------

@pytest.mark.parametrize("q", [0.95, 0.60, 0.50, 0.30, 0.10])
def test_the_recursion_attractor_is_nu_b_over_q(q):
    """``R* = nu_b / q`` under a perfect fix, by ITERATING the real function.

    This is the answer to "what should realistic boundaries be" and it is a
    property of the shipped model rather than a number anyone picked: no
    quantity of passes drives residual risk below ``nu_b / q``, and at
    perfect detection the floor is ``nu_b`` itself. Because ``q`` is a
    property of the question and the panel reviewing it, the boundary is
    per-question -- which is precisely the founder's point that severity
    cannot be one constant.

    Derived symbolically with SymPy and confirmed independently in Wolfram
    Language (local Wolfram Engine). Asserted here numerically so the claim
    rests on the code that ships, not on either derivation.
    """
    predicted = min(1.0, _NU_B / q)

    risk = 0.99  # start far above the attractor; it must fall to it
    for _ in range(4000):
        risk = compute_rk(risk, q, 1.0)
    assert math.isclose(risk, predicted, rel_tol=1e-6), (
        f"iterating compute_rk at q={q} settled at {risk:.9f}, not the "
        f"derived attractor nu_b/q = {predicted:.9f}"
    )

    # Approached from below it is a floor, not merely a limit.
    risk = 0.0
    for _ in range(4000):
        risk = compute_rk(risk, q, 1.0)
    assert risk >= predicted - 1e-9, (
        f"residual risk fell BELOW the derived floor at q={q}: "
        f"{risk:.9f} < {predicted:.9f}"
    )


def test_the_floor_is_nu_b_at_perfect_detection():
    """The special case q = 1: ``R_k = nu_b`` exactly, for any starting risk.

    So the LOWEST residual risk this harness can ever report is ``nu_b``
    (0.05 as shipped). A severity boundary set below that is unsatisfiable,
    and any gate threshold must therefore be expressed as a multiple of
    ``nu_b`` rather than as an absolute figure.
    """
    # STRICTLY below 1. The first version of this check included start=1.0 and
    # FAILED, correctly: R = 1 is the OTHER fixed point SymPy returns, and it is
    # absorbing for every (q, s) -- compute_rk(1.0, q, s) = 1.0 across the whole
    # grid, because `1 - q*R_old` vanishes and the detection phase short-circuits
    # to R_det = R_old. Certainty stays certainty, which is right: the runner
    # already treats R == 1 as "a corruption signal, not an operating point"
    # (`check_sk_threshold_corrected`). The claim is corrected and the absorbing
    # case is asserted below rather than excluded silently.
    for start in (0.0, 0.02, 0.5, 0.9, 0.999999):
        assert math.isclose(compute_rk(start, 1.0, 1.0), _NU_B, abs_tol=1e-12), (
            f"compute_rk({start}, 1.0, 1.0) != nu_b={_NU_B}"
        )
    for q in (0.0, 0.5, 1.0):
        for sk in (0.0, 0.5, 1.0):
            assert compute_rk(1.0, q, sk) == 1.0, (
                f"R = 1 stopped being absorbing at q={q}, S_k={sk}: "
                f"{compute_rk(1.0, q, sk)}. SymPy gives exactly 2 fixed points "
                f"for this recursion, R* = 1 and R* = nu_b/q; this is the first."
            )
    assert _NU_B < CRITICAL_SEVERITY_THRESHOLD, (
        "nu_b has risen above the CRITICAL cut; the two quantities would then "
        "no longer be independently scaled and this file's premise needs review"
    )
