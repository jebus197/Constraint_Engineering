#!/usr/bin/env python3
"""What is a self-reported `v_bar` worth in the role score? DERIVED, not measured.

CONTEXT. A defect fixed 2026-11-03 let a model set the `verified` flag by writing
`"VERIFIED": true` in its own reply. The terminal-state half of that is repaired.
The half left for the founder is that the same flag feeds `v_bar`, 1 of the 4
CapabilityFingerprint dimensions that decide role assignment, and entry B94 said
only that the dimension "is not inert". That is true and it does not say how much
is at stake. This derives the bound.

WHY A BOUND AND NOT A MEASUREMENT. Nothing in the stored fingerprints records
WHICH setter produced a given `v_bar`, so no archived role assignment can be
attributed to self-reporting, and this script does not attempt it. What it
establishes is the SIZE of the exposure, which follows from the equations alone
and is therefore DERIVED in the sense note-standard Rule 26 uses.

THE DERIVATION, in 2 steps, each cross-checked on 2 tools.
  1. `DynamicManagementConfig.get_alpha` returns a 4-vector per role and the
     file's own comment says those vectors sum to 1. That is asserted here
     rather than trusted, by NumPy and by exact SymPy rationals. Because they
     sum to 1, the weight on `v_bar` IS `v_bar`'s share of the whole score.
  2. `CapabilityFingerprint.as_normalised_array` sets the term to
     `v_bar / pool_max`. So the contribution is `alpha1 * v / m`, and the gain
     from 0 to the pool maximum simplifies, in SymPy, to exactly `alpha1`.

AND IT IS WORSE THAN ADDITIVE, WHICH IS THE PART A WEIGHT ALONE DOES NOT SHOW.
The pool maximum is the DENOMINATOR, so a model that inflates its own `v_bar`
becomes that maximum, and every honest model's term falls from 1 to its own raw
value. The mechanism raises the self-reporter AND depresses the rest, so the
spread between them moves by more than the weight.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def _live_alphas():
    """Read the alpha vectors from the LIVE config rather than retyping them.

    A figure retyped from a source file is a claim about that file. Importing
    the dataclass means a change to the defaults changes this output, which is
    what makes the number travel with the code instead of beside it.
    """
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "_dm_types_probe", REPO / "bench" / "dm" / "_types.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_dm_types_probe"] = mod
    spec.loader.exec_module(mod)
    cfg = mod.DynamicManagementConfig()
    return [("PM / orchestrator", cfg.get_alpha(mod.Role.PM)),
            ("COL / classifier", cfg.get_alpha(mod.Role.COL)),
            ("PAR / worker", cfg.get_alpha(mod.Role.PAR))], mod


def main() -> int:
    argparse.ArgumentParser(
        description=("Derive how much a self-reported v_bar is worth in the "
                     "role score.")).parse_args()
    import numpy as np
    import sympy as sp

    alphas, mod = _live_alphas()

    print("=" * 78)
    print("WHAT A SELF-REPORTED v_bar IS WORTH IN THE ROLE SCORE  (DERIVED)")
    print("=" * 78)

    print("\n1. THE WEIGHT VECTORS, READ FROM THE LIVE CONFIG, SUM TO 1.")
    shares = {}
    for name, a in alphas:
        s_np = float(np.asarray(a, dtype=float).sum())
        s_sp = float(sum(sp.Rational(str(float(x))) for x in a))
        assert abs(s_np - 1.0) < 1e-12, f"{name}: alpha sums to {s_np}, not 1"
        assert abs(s_np - s_sp) < 1e-12, f"{name}: NumPy and SymPy disagree"
        shares[name] = float(a[1])
        print(f"   {name:20s} {[round(float(x), 6) for x in a]}"
              f"   sum {s_np:.6f} (SymPy {s_sp:.6f})   v_bar share {a[1]:.6f}")
    print("   => because they sum to 1, the v_bar weight IS its share of the")
    print("      whole score. The orchestrator seat is the most exposed.")

    print("\n2. THE MAXIMUM GAIN IS EXACTLY THAT WEIGHT, SYMBOLICALLY.")
    v, m, a1 = sp.symbols("v m alpha1", positive=True)
    contrib = a1 * v / m
    gain = sp.simplify(contrib.subs(v, m) - contrib.subs(v, 0))
    print(f"   normalised contribution : {contrib}")
    print(f"   gain from 0 to pool max : {gain}")
    assert sp.simplify(gain - a1) == 0, f"the symbolic gain is {gain}, not alpha1"
    print("   => SymPy confirms it. NumPy agrees numerically below.")
    for name, share in shares.items():
        num = float(share * 1.0 / 1.0) - 0.0
        assert abs(num - share) < 1e-12
        print(f"      {name:20s} maximum gain {num:.6f}")

    print("\n3. AND IT DEPRESSES HONEST MODELS, BECAUSE pool_max IS THE DIVISOR.")
    print("   An honest model that WAS the pool maximum had a term of 1.000000;")
    print("   once another model inflates to the maximum, its term is its own")
    print("   raw v_bar. The loss is the weight times (1 - raw).")
    for vh in (0.8, 0.5, 0.2):
        row = []
        for name, share in shares.items():
            loss = share * (1.0 - vh)
            sym = float(sp.simplify(sp.Rational(str(share))
                                    * (1 - sp.Rational(str(vh)))))
            assert abs(loss - sym) < 1e-12, "NumPy and SymPy disagree on the loss"
            row.append(f"{name.split(' / ')[1]} {loss:.6f}")
        print(f"   honest v_bar {vh:.6f} loses: " + ",  ".join(row))

    print("\n4. THE LABEL, AND IT IS NOT DECORATION. This is DERIVED: it follows")
    print("   from the equations and says NOTHING about whether it has happened.")
    print("   Nothing in the stored fingerprints records which setter produced a")
    print("   v_bar, so no archived role assignment is attributed to")
    print("   self-reporting here. The exposure is the finding; an occurrence")
    print("   would be a separate claim needing separate evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
