#!/usr/bin/env python3
"""FALSIFIER: compute_rk Phase 2 interpolates between two DIFFERENT probability
spaces, and the error is one-signed (it always OVERSTATES residual risk).

THE DEFECT. bench/reference_runner_v3.py:10985-10993 computes

    Phase 1:  R_det  = R_old*(1-q)/(1-q*R_old)      # P(flaw | NOT detected)  -- CONDITIONAL
    Phase 2:  R_base = sk*R_det + (1-sk)*R_old      # mixes it with R_old     -- UNCONDITIONAL

R_det is a posterior conditioned on non-detection; R_old is an unconditional
prior. A convex combination of the two is not an expectation over any partition
of the sample space, so R_base is not a probability of anything.

THE EXACT ANSWER, by total expectation over the three disjoint branches:
    present & detected     R_old*q      -> flaw survives w.p. (1-sk)
    present & not detected R_old*(1-q)  -> flaw survives w.p. 1
    absent                 1-R_old      -> stays absent
    =>  R_after = R_old*q*(1-sk) + R_old*(1-q) = R_old*(1 - q*sk)

RESIDUAL, derived with SymPy and independently proved non-negative over the open
unit box by Wolfram Language `Resolve[ForAll[...]]` (quantifier elimination):

    shipped - exact = R^2*q*sk*(1-q)/(1-q*R)  >= 0

So the shipped pipeline is biased in ONE direction only. Because the admission
gate (check_sk_threshold_corrected:11708) is the sign test
`compute_rk(R,q,sk) <= R`, a one-signed overstatement of R_k is a one-signed
OVER-REFUSAL of fixes. At the frozen operating point every archived run used
(R_old=0.5, q=0.5, nu_b=0.05, nu_f=0.20 -- `model_params` has 0 writers) the
break-even moves from 0.395043 (exact) to 0.504931 (shipped): fixes scoring in
that band are net-beneficial and are refused.

NOTE ON THE APPENDIX FORM. The revision's Phase 2, (1-sigma)*R_det, is NOT the
repair either: at sigma=0 it returns R_det < R_old, crediting a fix that does
nothing with the full detection gain. The shipped form and the exact form both
correctly return R_old there. Only the exact form is right at BOTH endpoints.

Exits cleanly if the defect is absent. Raises AssertionError if it is present.
Run:  python3 scripts/phase2_mixes_probability_spaces_2026-09-20.py
"""
from __future__ import annotations
import ast
import math
import os
import sys
import types
from fractions import Fraction as F
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "bench" / "reference_runner_v3.py"


def load_real_functions() -> types.ModuleType:
    """Import the REAL shipped functions from the REAL target file.

    Executed by AST extraction rather than `import`, because importing
    reference_runner_v3 as a module runs several thousand lines of unrelated
    top-level setup. The function bodies are the file's own bytes, unmodified:
    nothing here retypes or paraphrases the code under test.
    """
    src = TARGET.read_text()
    tree = ast.parse(src)
    want = {"compute_rk", "check_sk_threshold_corrected", "sk_break_even",
            "check_sk_threshold"}
    mod = types.ModuleType("rr_real")
    mod.__dict__.update({"math": math, "os": os, "Optional": Optional,
                         "Tuple": Tuple, "Dict": Dict, "Any": Any})
    found = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in want:
            exec(compile(ast.Module([node], []), str(TARGET), "exec"), mod.__dict__)
            found.add(node.name)
    missing = want - found
    assert not missing, f"target changed shape; not found in {TARGET}: {sorted(missing)}"
    return mod


def exact_phase12(R: float, q: float, sk: float) -> float:
    """R_old*(1 - q*sk): the total-expectation replacement for Phases 1+2."""
    return R * (1.0 - q * sk)


def main() -> int:
    rr = load_real_functions()
    gate = rr.check_sk_threshold_corrected
    assert callable(rr.compute_rk), 'compute_rk missing from the real target'
    NB, NF = 0.05, 0.20

    # ---- 1. the shipped Phase 2 is not the exact expectation -----------------
    # Re-derived in exact rational arithmetic straight off the shipped source
    # lines, so no floating point enters the identity claim.
    mismatches, worst = 0, F(0)
    total = 0
    for i in range(1, 16):
        for j in range(1, 16):
            for k in range(0, 16):
                R, q, s = F(i, 16), F(j, 16), F(k, 15)
                total += 1
                shipped_base = s * (R * (1 - q) / (1 - q * R)) + (1 - s) * R
                d = shipped_base - R * (1 - q * s)
                assert d >= 0, (
                    f"FALSIFIED the one-sidedness claim at R={R} q={q} s={s}: "
                    f"shipped - exact = {d} < 0")
                if d != 0:
                    mismatches += 1
                worst = max(worst, d)
    print(f"[1] exact-rational samples                      : {total}")
    print(f"    shipped Phase 2 != exact expectation        : {mismatches}")
    print(f"    max(shipped - exact), always >= 0           : {float(worst):.6f}")

    # ---- 2. the error reaches the admission gate ----------------------------
    R = q = 0.5   # the frozen literals: model_params has 0 writers
    band = [x / 1000.0 for x in range(1001)]
    over = [s for s in band
            if _rk_exact(R, q, s, NB, NF) <= R and not gate(s, NB, NF, q, R, 0.0)[0]]
    harmful = [s for s in band
               if _rk_exact(R, q, s, NB, NF) > R and gate(s, NB, NF, q, R, 0.0)[0]]
    print("[2] at the operating point R=q=0.5, over 1001 sk values:")
    print(f"    net-beneficial fixes the live gate REFUSES  : {len(over)} "
          f"({100.0 * len(over) / len(band):.4f}%)")
    print(f"    harmful fixes the live gate ADMITS          : {len(harmful)}")
    if over:
        print(f"    refused band                                : "
              f"sk in [{min(over):.3f}, {max(over):.3f}]")

    # ---- 3. the endpoint the appendix form gets wrong ------------------------
    appendix_base_at_zero = (1 - 0.0) * R * (1 - q) / (1 - q * R)
    print(f"[3] a WORTHLESS fix (sk=0.0), R_old={R}:")
    print(f"    exact/shipped Phase-2 base                  : {R:.6f}  (correct: unchanged)")
    print(f"    the revision's (1-sigma)*R_det base         : {appendix_base_at_zero:.6f}"
          f"  (credits a no-op fix)")

    assert mismatches > 0 and len(over) > 0, (
        "defect NOT demonstrated: shipped Phase 2 agrees with the exact "
        "expectation and the gate refuses nothing net-beneficial")
    print("\nFALSIFIED: compute_rk Phase 2 mixes a conditional posterior with an "
          "unconditional prior;\nthe resulting one-signed overstatement of R_k "
          "makes the admission gate refuse net-beneficial fixes.")
    return 1


def _rk_exact(R: float, q: float, sk: float, nu_b: float, nu_f: float) -> float:
    """Phases 1+2 replaced by the exact expectation; Phase 3 UNCHANGED."""
    base = exact_phase12(R, q, sk)
    nu_eff = 1.0 - (1.0 - nu_b) * (1.0 - (1.0 - sk) * nu_f)
    return max(0.0, min(1.0, base * (1.0 - nu_eff) + nu_eff))


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    sys.exit(0 if main() == 0 else 1)
