#!/usr/bin/env python3
"""I31: was the drift detector wired on a true premise, and can it fire? Read-only.

The founder's ruling on I31 was conditional: "if it depends on some element of
how our current mathematical model functions, defer it". Commit 90873cb wired
`ImmuneMemory.update_drift` into `run_experiment` on the stated ground that the
value it reads, `pi_mem`, "appears nowhere in docs/MATHEMATICAL_APPENDIX.md".
This script tests that premise and the detector's reachability by execution:

  1. PREMISE. Occurrences of the ASCII spelling `pi_mem` and the Greek `π_mem`
     in the appendix, and the lines defining pi_mem, the CUSUM statistics and
     the drift threshold.
  2. SAME MATHEMATICS. SymPy: the return expression of `ImmuneMemory.pi_mem`,
     read by AST, minus the appendix's formula simplifies to 0. Numeric: the
     code's CUSUM, driven through `update_drift` over seeded random sequences,
     against the appendix recursion in exact fractions.
  3. CAN IT FIRE. z3: with observed rates and predictions in [0, 1], fewer than
     3 updates in the same direction cannot exceed the threshold of 2.0.
  4. WHAT PRODUCTION DOES. The production sequence on a copy of
     bench/state/immune_memory.json (1 update per class per run), whether
     `save`/`load` keep the CUSUM state, and `immune_memory_enabled` in the 3
     experiment 56 arms.

Writes nothing in the repository. Runs everything by default; `--help` is inert.
"""
from __future__ import annotations

import argparse
import ast
import glob
import json
import random
import re
import shutil
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"


def premise() -> None:
    text = APPENDIX.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"appendix occurrences: 'pi_mem' {text.count('pi_mem')}, 'π_mem' {text.count('π_mem')}")
    for pat, label in ((r"\*\*π_mem\(k\) =", "pi_mem defined"), (r"\*\*S_pos\(t\) =", "S_pos defined"),
                       (r"\*\*S_neg\(t\) =", "S_neg defined"), (r"drift threshold \(default", "threshold stated")):
        hit = next((i + 1 for i, line in enumerate(lines) if re.search(pat, line)), None)
        print(f"  {label}: line {hit}")


def same_mathematics() -> None:
    import logging
    import sympy as sp
    logging.disable(logging.WARNING)   # the replay trips the detector on purpose
    sys.path.insert(0, str(REPO))
    from bench.dm._memory import ImmuneMemory
    src = (REPO / "bench" / "dm" / "_memory.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "pi_mem")
    # The return that reads the record; the other one is the no-data prior.
    ret = next(n for n in ast.walk(fn) if isinstance(n, ast.Return) and "rec.confirmed" in ast.unparse(n))
    code = ast.unparse(ret.value).replace("rec.confirmed", "c").replace("rec.rejected", "r") \
        .replace("self.ALPHA_0", "a0").replace("self.BETA_0", "b0")
    c, r, a0, b0 = sp.symbols("c r a0 b0", nonnegative=True)
    appendix = (c + a0) / (c + r + a0 + b0)
    diff = sp.simplify(sp.sympify(code, locals={"c": c, "r": r, "a0": a0, "b0": b0}) - appendix)
    print(f"SymPy: code pi_mem {code!r} minus appendix formula = {diff}; "
          f"ALPHA_0 = {ImmuneMemory.ALPHA_0}, BETA_0 = {ImmuneMemory.BETA_0}, appendix says 0.5 and 0.5")

    rng = random.Random(20260917)
    worst = Fraction(0)
    for _ in range(200):
        mem = ImmuneMemory(decay_rate=0.1, drift_threshold=2.0)
        p = Fraction(mem.pi_mem(7)).limit_denominator(10**12)
        s_pos = s_neg = Fraction(0)
        for _ in range(rng.randint(1, 12)):
            x = Fraction(rng.randint(0, 1000), 1000)
            mem.update_drift(7, float(x))
            s_pos, s_neg = max(Fraction(0), s_pos + x - p), min(Fraction(0), s_neg + x - p)
            ds = mem._drift[7]
            worst = max(worst, abs(Fraction(ds.cusum_pos) - s_pos), abs(Fraction(ds.cusum_neg) - s_neg))
    print(f"numeric: code CUSUM against the appendix recursion over 200 seeded sequences, "
          f"largest difference {float(worst):.3e}")


def can_it_fire() -> None:
    import z3
    thr = z3.RealVal(2)
    for n in (1, 2, 3):
        xs = [z3.Real(f"x{i}") for i in range(n)]
        ps = [z3.Real(f"p{i}") for i in range(n)]
        s = z3.Solver()
        for x, p in zip(xs, ps):
            s.add(x >= 0, x <= 1, p >= 0, p <= 1)
        s.add(z3.Or(z3.Sum([x - p for x, p in zip(xs, ps)]) > thr, z3.Sum([x - p for x, p in zip(xs, ps)]) < -thr))
        print(f"z3: {n} same-direction update(s) from 0 can exceed |2.0|: {s.check() == z3.sat}")


def production() -> None:
    import logging
    logging.disable(logging.WARNING)
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    from bench.dm._memory import ImmuneMemory
    import reference_runner_v3 as R
    tmp = Path(tempfile.mkdtemp(prefix="i31_probe_"))
    try:
        path = tmp / "immune_memory.json"
        shutil.copyfile(REPO / "bench" / "state" / "immune_memory.json", path)
        base = ImmuneMemory.load(str(path))
        cases = [(0, 50), (50, 0), (1, 0), (0, 1), (1000, 0), (0, 1000)]
        worst, fired, trials = 0.0, 0, 0
        for fc in sorted(base._records) + [99]:
            for c, r in cases:
                mem = ImmuneMemory.load(str(path))
                mem.record_experiment(exp_id="probe", flaw_counts={fc: (c, r)})
                fired += int(mem.update_drift(fc, c / (c + r)))
                ds = mem._drift[fc]
                worst = max(worst, ds.cusum_pos, abs(ds.cusum_neg))
                trials += 1
        print(f"production sequence: {trials} cases, {fired} fired, worst |CUSUM| {worst:.6f}, "
              f"threshold {base.drift_threshold}")
        mem = ImmuneMemory.load(str(path))
        mem.update_drift(1, 1.0)
        out = tmp / "roundtrip.json"
        mem.save(str(out))
        keys = [k for k in json.loads(out.read_text()) if "drift" in k.lower() or "cusum" in k.lower()]
        print(f"keys save() writes about drift: {keys}; drift state after reload: "
              f"{dict(ImmuneMemory.load(str(out))._drift)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in sorted(glob.glob(str(REPO / "bench" / "exp56_configs" / "*.json"))):
        cfg = R.RunnerConfig.from_dict(json.loads(Path(f).read_text(encoding="utf-8")))
        print(f"{Path(f).name}: immune_memory_enabled={cfg.immune_memory_enabled}")


def main() -> int:
    argparse.ArgumentParser(description="Test I31's wiring premise and whether the drift detector "
                                        "can fire. Read-only.").parse_args()
    premise()
    same_mathematics()
    can_it_fire()
    production()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
