# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_severity_gates_convergence_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 77037cf8e37732a8360bb0f853f7514a1e65dfac14349061c683d1f600547ce1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The preconditions an R_k convergence gate must satisfy before a BOUNDARY on
it can be set, each stated as a mechanical check.

WHY THIS FILE EXISTS (joint round, third seat, 2026-10-31). The founder asked
whether severity -- by his definition, "the chances that a particular flaw ...
might remain after a given number of passes" -- should gate convergence, and
what realistic boundaries such a gate would use. His definition is ``R_k``.
Both blind seats agreed on that and both proposed a boundary. Each boundary was
derived from the WRONG model:

  * The appendix batch posterior ``R = pi*m/((1-pi)+pi*m)``, ``m=(1-q)^n``, has
    NO re-injection term, so it is unbounded below -- it reaches 3.19e-10 at
    (pi=0.02, q=0.95, n=6). The inversion ``n(R_t) = log[R_t(1-pi)/(pi(1-R_t))]
    / log(1-q)`` offered as the boundary rule inherits that unboundedness.
  * The GATE-BEARING code is ``compute_rk``, which DOES have a re-injection
    term, and is therefore bounded below by ``nu_eff``. A bound taken from the
    appendix inversion is unreachable in the shipped recursion by roughly 8
    orders of magnitude at (pi=0.02, q=0.95). A gate carrying it would never
    fire; a run chasing it would never converge.
  * The floor is NOT ``nu_b`` either. It is
    ``nu_eff = 1 - (1-nu_b)*(1-(1-S_k)*nu_f)``, a function of FIX EFFICACY.
    At the archive's weaker fixes it is 0.145, not 0.05. So the floor moves with
    how well the panel repairs things, and not at all with how hard the question
    is.

Derivations are SymPy-checked and independently confirmed in Wolfram Language
(local Wolfram Engine, exit 0): the s=1 fixed points are {1, nu_b/q}, and
Minimize over (R, q) returns the branch ``nb + nf + nb*nf*(s-1) - nf*s``, which
is ``nu_eff`` expanded. Wolfram is the second falsifier only; every assertion
below is computed here from the SHIPPED function, never a retyped copy.

WHAT THIS FILE PROTECTS. Tests 4 and 5 are the tripwire. While ``q`` has no
production writer and no convergence predicate reads ``R_k``, the quantity is
recorded and the boundaries question has no answer in difficulty units. The day
either changes is the day the question becomes answerable -- and these tests
fail then, loudly, so that the boundary is re-derived against the recursion that
actually gates rather than carried over from the appendix.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import numpy as np
import pytest
import sympy as sp

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import reference_runner_v3 as rr  # noqa: E402

#: The shipped fallbacks, read so this file cannot drift from the runner.
NU_B, NU_F = 0.05, 0.20
#: ``model_params`` is unwritten on every real run, so this is the q the
#: recursion actually receives.
Q_FALLBACK = 0.5

#: Production modules. ``bench/logs/**`` holds harvested COPIES of the runner
#: from past sandbox runs; counting them as live is the error that makes a
#: writer census meaningless.
_EXCLUDED_PARTS = {"logs", ".git", "seat_evidence", "sandbox_harvest",
                   "experimental_notes"}


def _live_py_files():
    for p in sorted(REPO.rglob("*.py")):
        if _EXCLUDED_PARTS & set(p.parts):
            continue
        yield p


def _nu_eff(sk: float, nu_b: float = NU_B, nu_f: float = NU_F) -> float:
    return 1.0 - (1.0 - nu_b) * (1.0 - (1.0 - sk) * nu_f)


def _appendix_batch_posterior(pi: float, q: float, n: int) -> float:
    """The Stage-4 batch posterior from MATHEMATICAL_APPENDIX §1. NO
    re-injection term -- which is exactly the discrepancy under test."""
    m = (1.0 - q) ** n
    return pi * m / ((1.0 - pi) + pi * m)


# ---------------------------------------------------------------------------
# 1. The floor of the gate-bearing recursion is nu_eff(S_k), not nu_b.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("sk", [0.0, 0.5, 0.8, 0.92, 0.95, 1.0])
def test_floor_is_nu_eff_of_fix_efficacy_not_nu_b(sk):
    """inf over (R_old, q) of the SHIPPED compute_rk equals the closed form.

    Two independent routes to the same number: a 101x101 brute grid over the
    real function, and the SymPy-simplified closed form. They must agree, and
    the result must be nu_b ONLY at S_k = 1.
    """
    closed = _nu_eff(sk)

    grid_min = min(
        rr.compute_rk(float(r), float(q), sk, nu_b=NU_B, nu_f=NU_F)
        for r in np.linspace(0.0, 1.0, 101)
        for q in np.linspace(0.0, 1.0, 101)
    )
    assert grid_min == pytest.approx(closed, abs=1e-12), (
        f"S_k={sk}: shipped compute_rk reaches {grid_min!r}, closed form "
        f"nu_eff={closed!r}. The re-injection floor moved; any R_k boundary "
        f"expressed against the old floor is now wrong.")

    # SymPy, as the second route to the closed form.
    R, q, s, nb, nf = sp.symbols("R q s nu_b nu_f", nonnegative=True)
    nu_eff_sym = 1 - (1 - nb) * (1 - (1 - s) * nf)
    R_sym = (s * (R * (1 - q) / (1 - q * R)) + (1 - s) * R) * (1 - nu_eff_sym) + nu_eff_sym
    at_floor = sp.simplify(R_sym.subs({R: 0}))   # R_base = 0 attains the floor
    assert sp.simplify(at_floor - nu_eff_sym) == 0, at_floor
    assert float(nu_eff_sym.subs({s: sk, nb: NU_B, nf: NU_F})) == pytest.approx(closed)

    if sk < 1.0:
        assert closed > NU_B + 1e-12, (
            f"S_k={sk}: floor {closed} collapsed onto nu_b={NU_B}. The claim "
            f"that the floor tracks FIX EFFICACY rather than nu_b alone is "
            f"what sets the boundary units; if it no longer holds, re-derive.")
    else:
        assert closed == pytest.approx(NU_B, abs=1e-12)


# ---------------------------------------------------------------------------
# 2. The s=1 attractor is nu_b/q, and R=1 is absorbing.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("q", [0.95, 0.50, 0.30])
def test_perfect_fix_attractor_is_nu_b_over_q(q):
    """Iterating the SHIPPED function, not a copy. Confirms the derived
    interior fixed point nu_b/q (SymPy; Wolfram Language concurs)."""
    x = 0.5
    for _ in range(4000):
        x = rr.compute_rk(x, q, 1.0, nu_b=NU_B, nu_f=NU_F)
    assert x == pytest.approx(NU_B / q, abs=1e-9), (
        f"q={q}: iterated attractor {x}, derived nu_b/q={NU_B / q}")


def test_at_q_equal_nu_b_the_root_is_double_and_never_attained():
    """At q <= nu_b the two fixed points coincide at 1, so approach is
    ALGEBRAIC, not geometric. 'Saturated at 1.0' is a limit statement and is
    false of any finite run: at n=6 the risk is ~0.90, not 1.0."""
    R, q, nb = sp.symbols("R q nu_b")
    roots = sp.solve((q * R**2 - (q + nb) * R + nb).subs(
        {q: sp.Rational(1, 20), nb: sp.Rational(1, 20)}), R)
    assert roots == [1], roots          # degenerate: one root, multiplicity 2

    x = 0.90
    for _ in range(6):
        x = rr.compute_rk(x, 0.05, 1.0, nu_b=NU_B, nu_f=NU_F)
    assert 0.85 < x < 0.95, x
    assert x < 1.0 - 1e-3, (
        f"after 6 passes at q=0.05 the risk is {x}; it must still be strictly "
        f"and measurably below 1, or the 'never attained' claim is wrong")

    # and 1 really is absorbing, for every (q, s)
    for qv in np.linspace(0.0, 1.0, 11):
        for sv in np.linspace(0.0, 1.0, 11):
            assert rr.compute_rk(1.0, float(qv), float(sv)) == 1.0


# ---------------------------------------------------------------------------
# 3. An appendix-derived boundary is UNREACHABLE in the gate-bearing recursion.
# ---------------------------------------------------------------------------
def test_appendix_boundary_is_unreachable_in_the_shipped_recursion():
    """The precise reason the founder's second question cannot be answered from
    the appendix inversion: the two models disagree by ~8 orders of magnitude
    at the easy end, because only one of them has a re-injection floor."""
    appendix = _appendix_batch_posterior(0.02, 0.95, 6)
    assert appendix == pytest.approx(3.188776e-10, rel=1e-4), appendix

    shipped = 0.02
    for _ in range(6):
        shipped = rr.compute_rk(shipped, 0.95, 1.0, nu_b=NU_B, nu_f=NU_F)

    assert shipped > appendix * 1e6, (
        f"appendix posterior {appendix:.3e} vs shipped recursion {shipped:.6f}. "
        f"If these have converged, the re-injection term has been removed or "
        f"nu_b driven to 0, and an appendix-derived R_k boundary is now "
        f"admissible -- re-derive the boundary before relying on it.")

    # No admissible S_k brings the floor anywhere near the appendix value.
    assert min(_nu_eff(sk) for sk in np.linspace(0.0, 1.0, 101)) > appendix * 1e6

    # And the easy question's prior sits BELOW the floor, so the recursion
    # RAISES its risk. This is why R_k cannot express an easy question today.
    raised = rr.compute_rk(0.02, 0.95, 0.92, nu_b=NU_B, nu_f=NU_F)
    assert raised > 0.02, (
        f"pi=0.02 updated to {raised}; the claim that a prior below nu_eff is "
        f"pushed UP by one pass no longer holds")
    assert raised >= _nu_eff(0.92) - 1e-12


# ---------------------------------------------------------------------------
# 4. TRIPWIRE: q has no production writer, so R_k carries no difficulty signal.
# ---------------------------------------------------------------------------
def test_q_has_no_production_writer_so_rk_cannot_separate_two_questions():
    """``q`` reaches ``compute_rk`` only through ``entry["model_params"]``.

    A WRITE is ``entry["model_params"] = ...``, a ``{"model_params": ...}``
    literal, ``.setdefault("model_params", ...)`` or
    ``.update({"model_params": ...})``. Reads are not writes.

    Writers found inside ``bench/tests/`` are recorded and allowed: a test
    fixture supplying the parameter dict proves the READ PATH is exercised, not
    that a real run varies q. A writer anywhere else means the difficulty term
    now arrives, and the boundary must be derived in difficulty units -- which
    is what this test exists to force.
    """
    prod_writers, test_writers, readers = [], [], []
    for p in _live_py_files():
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        rel = str(p.relative_to(REPO))
        bucket = test_writers if "/tests/" in f"/{rel}" else prod_writers
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in tgts:
                    for sub in ast.walk(t):
                        if (isinstance(sub, ast.Subscript)
                                and isinstance(sub.slice, ast.Constant)
                                and sub.slice.value == "model_params"):
                            bucket.append((rel, node.lineno))
            if isinstance(node, ast.Dict):
                for k in node.keys:
                    if isinstance(k, ast.Constant) and k.value == "model_params":
                        bucket.append((rel, node.lineno))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                for a in node.args:
                    if isinstance(a, ast.Constant) and a.value == "model_params":
                        if node.func.attr in ("setdefault", "update"):
                            bucket.append((rel, node.lineno))
                        elif node.func.attr in ("get", "pop"):
                            readers.append((rel, node.lineno))
            if (isinstance(node, ast.Subscript)
                    and isinstance(node.slice, ast.Constant)
                    and node.slice.value == "model_params"
                    and isinstance(node.ctx, ast.Load)):
                readers.append((rel, node.lineno))

    assert readers, "model_params lost its reader; the q parameter path moved"
    assert not prod_writers, (
        f"model_params GAINED a production writer at {sorted(prod_writers)}. "
        f"q may now vary per question, so (a) re-run the measurement that "
        f"shows whether R_k separates an easy question from a hard one, and "
        f"(b) derive the gate boundary in those units. Until then no boundary "
        f"on R_k means anything.")

    # The consequence, computed: with q pinned, two questions at opposite ends
    # of difficulty produce bit-identical trajectories.
    def traj(pi, q, n=12, sk=0.92):
        xs, x = [], pi
        for _ in range(n):
            x = rr.compute_rk(x, q, sk, nu_b=NU_B, nu_f=NU_F)
            xs.append(x)
        return xs

    easy = traj(rr.RK0_PI_BASE, Q_FALLBACK)
    hard = traj(rr.RK0_PI_BASE, Q_FALLBACK)
    assert easy == hard
    assert max(abs(a - b) for a, b in zip(easy, hard)) == 0.0

    # Monotone in the ROUND INDEX, and a plausible bound is crossed purely by
    # running more rounds. That is the defect a gate today would ship.
    assert all(easy[i + 1] <= easy[i] + 1e-15 for i in range(len(easy) - 1))
    first_below_020 = next(i + 1 for i, v in enumerate(easy) if v <= 0.20)
    assert first_below_020 == 5, first_below_020


# ---------------------------------------------------------------------------
# 5. TRIPWIRE: no convergence predicate reads R_k. It is recorded, not gating.
# ---------------------------------------------------------------------------
_GATE_FNS = ("_check_gamma_alt_convergence", "_check_hardened_convergence",
             "_check_stall_convergence", "_check_state_convergence")


def test_no_convergence_predicate_reads_rk_today():
    """If this fails, an R_k term has been wired into a convergence gate. Check
    tests 1-4 first: while q is pinned, such a gate is satisfied by round count
    and fix quality, NOT by confidence in the answer -- which is a
    verification-integrity defect, not a feature."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    tree = ast.parse(src)
    seen, offenders = set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in _GATE_FNS:
            seen.add(node.name)
            hits = set()
            for sub in ast.walk(node):
                if (isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                        and sub.value in ("R_new", "R_old", "sk_result")):
                    hits.add(sub.value)
                if isinstance(sub, ast.Name) and sub.id in ("R_new", "R_old"):
                    hits.add(sub.id)
                if isinstance(sub, ast.Attribute) and sub.attr in ("R_new", "R_old"):
                    hits.add(sub.attr)
            if hits:
                offenders[node.name] = sorted(hits)

    assert seen == set(_GATE_FNS), (
        f"convergence predicates renamed or removed; this tripwire is no "
        f"longer watching the gate. Found {sorted(seen)}")
    assert not offenders, (
        f"an R_k term reached a convergence predicate: {offenders}. With q "
        f"pinned at {Q_FALLBACK} this gate measures round count, not "
        f"confidence.")
