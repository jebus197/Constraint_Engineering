#!/usr/bin/env python3
"""The live fix-admission gate is ONE CONSTANT, and an unmeasured input decides it.

THE CLAIM, IN FOUR PARTS, EACH ASSERTED BELOW SO THIS FILE IS ITS OWN FALSIFIER.
Run it: `python3 scripts/gate_collapses_to_one_constant_2026-09-20.py`.
It exits 0 iff every part holds and raises AssertionError naming the part that fails.

PART 1 -- THE PARAMETERS ARE FROZEN.
  `check_sk_threshold_corrected` reads q, R_old, nu_b, nu_f from
  `entry["model_params"]` (reference_runner_v3.py:11921). `model_params` has NO
  WRITER anywhere in the repository -- the only two occurrences are `.get()`
  reads in reference_runner.py:3156 and reference_runner_v3.py:11921. So on every
  real run the gate is called at exactly
      q = 0.5, R_old = RK0_PI_BASE = 0.5, nu_b = 0.05, nu_f = 0.20
  and the ONLY varying argument is `sk`.

PART 2 -- SO THE GATE IS A SCALAR THRESHOLD.
  Sweeping sk across [0,1] at those frozen values produces exactly ONE verdict
  flip. The five-parameter, three-phase apparatus decides precisely one thing:
      ADMIT iff sk >= 0.504931170970423  ( = -7/2 + sqrt(23161)/38, exact )
  That number is the whole operational content of the risk model today.

PART 3 -- ITS LOCATION IS GOVERNED BY AN UNMEASURED CONSTANT.
  nu_b = 0.05 is the introduction rate b. It carries no measurement. The three
  figures the panel has for b are not the same quantity and span a wide range,
  and the threshold is steeply sensitive to which is used:
      nu_b = 0.0154  (cc2 F7, Wilson UPPER on 0 of 246 paired) -> admit sk >= 0.4350
      nu_b = 0.05    (SHIPPED, no provenance)                  -> admit sk >= 0.5049
      nu_b = 0.2089  (cc2 F7 lint channel, Wilson LOWER)       -> admit sk >= 0.8830
      nu_b = 0.3077  (cc2 F7 lint channel, point estimate)     -> ADMITS NOTHING

PART 4 -- THE GATE CLOSES COMPLETELY AT nu_b > 1/4, EXACTLY.
  Solving compute_rk(1/2, 1/2, sk=1, nu_b, 1/5) = 1/2 for nu_b gives the exact
  rational 1/4 (SymPy). Above it, not even a perfect fix (sk = 1) is admitted.
  So the answer to "does naming the introduction rate change a decision?" is YES,
  and the decision is fix admission: the range of defensible b spans
  "admit sk >= 0.435" to "admit nothing at all".

WHAT THIS DOES NOT CLAIM. It does not claim 0.05 is the wrong value; nobody knows
the right one. It claims the value decides, and is unmeasured. That is the finding.

TWO TOOLS PER CLAIM: SymPy for the exact roots, and bisection on the LIVE
`check_sk_threshold_corrected` function (no shared code with SymPy) for each one.
"""
from __future__ import annotations

import subprocess
import sys

import sympy as sp

sys.path.insert(0, ".")
from bench import reference_runner_v3 as rr  # noqa: E402

FAILED = False


def live_threshold(nu_b, nu_f=0.20, q=0.5, R=0.5):
    """Smallest sk the LIVE gate admits; None if it admits nothing."""
    if not rr.check_sk_threshold_corrected(1.0, nu_b, nu_f, q, R)[0]:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        if rr.check_sk_threshold_corrected(m, nu_b, nu_f, q, R)[0]:
            hi = m
        else:
            lo = m
    return hi


def part1_parameters_are_frozen():
    """AST, not grep: find any real WRITE to model_params in production code."""
    import ast
    import pathlib
    writes, reads = [], []
    for f in sorted(pathlib.Path(".").rglob("*.py")):
        s = str(f)
        if "/tests/" in s or s.startswith("scripts/gate_collapses"):
            continue
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            # entry["model_params"] = ... / entry["model_params"][k] = ...
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in tgts:
                    for sub in ast.walk(t):
                        if (isinstance(sub, ast.Subscript)
                                and isinstance(sub.slice, ast.Constant)
                                and sub.slice.value == "model_params"):
                            writes.append(f"{s}:{node.lineno}")
            # {"model_params": ...} dict literal in production code
            if isinstance(node, ast.Dict):
                for k in node.keys:
                    if isinstance(k, ast.Constant) and k.value == "model_params":
                        writes.append(f"{s}:{node.lineno} (dict literal)")
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "get" and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == "model_params"):
                reads.append(f"{s}:{node.lineno}")
    print(f"[part 1] AST over production .py (tests excluded): "
          f"{len(writes)} writes, {len(reads)} reads")
    for r in reads:
        print("          READ ", r)
    for w in writes:
        print("          WRITE", w)
    assert len(writes) == 0, (
        f"FALSIFIED part 1: model_params now HAS a writer in production code: "
        f"{writes}. The parameters are no longer frozen and parts 2-4 do not "
        f"describe the live gate.")
    assert len(reads) >= 1, "FALSIFIED part 1: nothing reads model_params at all"
    assert rr.RK0_PI_BASE == 0.5, "FALSIFIED part 1: RK0_PI_BASE moved"


def part2_scalar_threshold():
    vals = [rr.check_sk_threshold_corrected(i / 2000, 0.05, 0.20, 0.5, 0.5)[0]
            for i in range(2001)]
    flips = sum(1 for a, b in zip(vals, vals[1:]) if a != b)
    t_live = live_threshold(0.05)
    s = sp.Symbol("s")
    R = q = sp.Rational(1, 2)
    nb, nf = sp.Rational(5, 100), sp.Rational(1, 5)
    R_det = R * (1 - q) / (1 - q * R)
    ne = 1 - (1 - nb) * (1 - (1 - s) * nf)
    Rk = (s * R_det + (1 - s) * R) * (1 - ne) + ne
    exact = [r for r in sp.solve(sp.Eq(Rk, R), s) if r.is_real and 0 <= r <= 1]
    print(f"[part 2] verdict flips across sk in [0,1]: {flips} (1 == pure threshold)")
    print(f"[part 2] live bisection threshold : {t_live!r}")
    print(f"[part 2] sympy exact root         : {exact[0]} = {float(exact[0])!r}")
    assert flips == 1, f"FALSIFIED part 2: {flips} flips, the gate is not a threshold"
    assert abs(t_live - float(exact[0])) < 1e-9, (
        "FALSIFIED part 2: bisection and SymPy disagree on the threshold")


def part3_sensitivity():
    table = [(0.0154, "cc2 F7 Wilson UPPER, 0 of 246 paired"),
             (0.0500, "SHIPPED DEFAULT, no provenance"),
             (0.2089, "cc2 F7 lint channel, Wilson LOWER"),
             (0.3077, "cc2 F7 lint channel, point estimate")]
    print("[part 3]  nu_b      source                                   admit-threshold")
    got = {}
    for nb, lab in table:
        t = live_threshold(nb)
        got[nb] = t
        print(f"          {nb:.4f}  {lab:<40s} "
              f"{'ADMITS NOTHING' if t is None else f'sk >= {t:.6f}'}")
    assert got[0.0154] is not None and got[0.05] is not None
    assert got[0.0154] < got[0.05] < got[0.2089], (
        "FALSIFIED part 3: the threshold is not monotone increasing in nu_b")
    assert got[0.3077] is None, (
        "FALSIFIED part 3: the gate still admits something at the lint-channel "
        "point estimate; the sensitivity claim overstates the effect")


def part4_gate_closes_at_quarter():
    s, nb = sp.symbols("s nu_b")
    R = q = sp.Rational(1, 2)
    nf = sp.Rational(1, 5)
    R_det = R * (1 - q) / (1 - q * R)
    ne = 1 - (1 - nb) * (1 - (1 - s) * nf)
    Rk = (s * R_det + (1 - s) * R) * (1 - ne) + ne
    roots = sp.solve(sp.Eq(Rk.subs(s, 1), R), nb)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        if rr.check_sk_threshold_corrected(1.0, m, 0.20, 0.5, 0.5)[0]:
            lo = m
        else:
            hi = m
    print(f"[part 4] sympy exact closing nu_b : {roots}")
    print(f"[part 4] live bisection closing   : {lo!r}")
    assert sp.Rational(1, 4) in roots, (
        f"FALSIFIED part 4: exact closing nu_b is {roots}, not 1/4")
    assert abs(lo - 0.25) < 1e-9, (
        "FALSIFIED part 4: the live gate does not close at nu_b = 1/4")


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    for fn in (part1_parameters_are_frozen, part2_scalar_threshold,
               part3_sensitivity, part4_gate_closes_at_quarter):
        fn()
    print("\nALL FOUR PARTS HOLD. The live risk model decides exactly one "
          "number, and an unmeasured constant decides where it sits.")
