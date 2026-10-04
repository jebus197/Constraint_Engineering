#!/usr/bin/env python3
"""Why the EXHAUSTED release valve cannot fire in an 8-round run.

The valve in `_update_finding_statuses` (bench/reference_runner_v3.py:3930-3938)
frees a stuck critical finding from the A4 blocker when THREE locks all open:

    status in EXHAUSTED_VALVE_STATUSES  and  severity >= 0.7
    and  age >= cfg.exhausted_round_threshold  and  has_reviews

where  age = round_idx - last_status_change_round.

`exhausted_round_threshold` defaults to 8 (line 1607). In a run of R rounds the
round index is 0-based, so round_idx <= R-1, and last_status_change_round >= 0.
The maximum reachable age is therefore R-1, not R.

This script proves the lock is UNSATISFIABLE for R = 8 two independent ways
(z3 unsat proof, NumPy exhaustive enumeration), derives the general condition
with SymPy, and states the smallest threshold change that makes the valve
reachable. It asserts the two tools agree, so a disagreement is a failure here
rather than a silent choice between them.
"""
import pathlib as _pathlib
import sys as _sys

import numpy as np
import sympy as sp
import z3

_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

# A `--help` MUST NEVER COST ANYTHING. This script parses no arguments, so
# without this line `--help` ran the whole measurement and printed no usage --
# caught by bench/tests/test_help_is_answered_2026-09-11.py as "exit 0 but no
# usage line, the flag was ignored". The helper returns immediately on an empty
# argv, so a plain run reaches exactly the code it reached before, and an
# unrecognised flag exits 2 rather than being silently ignored.
# GUARDED BY `__main__`, and the reason is a real failure (2026-10-03).
# `bench/tests/test_operational_scripts.py::test_help_builds_and_lists_every_advertised_flag`
# import-probes every parser-less script in a subprocess started with
# `python3 -c ...`, where `sys.argv` is ['-c', '<this path>']. A module-level
# `answer_help` therefore sees the script's own path as an unrecognised argument
# and exits 2, so the script "no longer imports" as far as that guard is
# concerned. The project's convention is to call it from main() --
# scripts/a19_flag_admits_harmful_fixes_2026-09-22.py:81 does exactly that.
if __name__ == "__main__":
    answer_help(__doc__, __file__)

R = 8                      # --rounds 8, as run 1b was launched
THRESHOLD = 8              # RunnerConfig.exhausted_round_threshold default

print(f"run length R = {R} rounds (round_idx in 0..{R-1}); threshold = {THRESHOLD}")
print()

# ---- Arm 1: z3. Is there ANY legal (round_idx, lscr) with age >= THRESHOLD? ----
ri, lscr = z3.Ints("round_idx last_status_change_round")
s = z3.Solver()
s.add(ri >= 0, ri <= R - 1)          # 0-based round index
s.add(lscr >= 0, lscr <= R - 1)      # a status change happens in some round
s.add(lscr <= ri)                    # ...never in the future
s.add(ri - lscr >= THRESHOLD)        # the valve's age lock
z3_result = s.check()
z3_reachable = (z3_result == z3.sat)
print(f"  z3            : {z3_result}  -> age lock "
      f"{'REACHABLE' if z3_reachable else 'UNREACHABLE'}")

# ---- Arm 2: NumPy. Enumerate every legal pair and take the max age. ----
grid_ri, grid_lscr = np.meshgrid(np.arange(R), np.arange(R), indexing="ij")
legal = grid_lscr <= grid_ri
ages = (grid_ri - grid_lscr)[legal]
max_age = int(ages.max())
np_reachable = bool((ages >= THRESHOLD).any())
print(f"  NumPy         : {legal.sum()} legal (round_idx, lscr) pairs, "
      f"max age = {max_age}  -> age lock "
      f"{'REACHABLE' if np_reachable else 'UNREACHABLE'}")

assert z3_reachable == np_reachable, (
    f"z3 and NumPy disagree on reachability: {z3_reachable} vs {np_reachable}")
print(f"  AGREEMENT     : both tools say "
      f"{'REACHABLE' if z3_reachable else 'UNREACHABLE'}")
print()

# ---- The general condition, symbolically ----
Rs, Ts = sp.symbols("R T", integer=True, positive=True)
# max age = R - 1; the valve is reachable iff R - 1 >= T
condition = sp.Ge(Rs - 1, Ts)
print(f"  SymPy         : max_age = R - 1; valve reachable iff  {condition}")
print(f"                  i.e. threshold T <= R - 1, "
      f"equivalently R >= T + 1")
sym_reachable = bool(condition.subs({Rs: R, Ts: THRESHOLD}))
assert sym_reachable == z3_reachable, "SymPy disagrees with z3"
print(f"                  at R={R}, T={THRESHOLD}: {sym_reachable} "
      f"(agrees with z3 and NumPy)")
print()

# ---- What would make it reachable, and by how little ----
largest_usable_T = R - 1
smallest_usable_R = THRESHOLD + 1
print("  THE SHORTFALL IS EXACTLY 1 ROUND:")
print(f"    keep R={R}  -> threshold must be <= {largest_usable_T}")
print(f"    keep T={THRESHOLD}  -> run must be >= {smallest_usable_R} rounds")
print()

# ---- How many rounds a finding would actually have to survive ----
print("  REACHABILITY BY THRESHOLD, at R = 8 "
      "(a finding first seen in round 0, never changing status):")
for T in range(5, 11):
    ok = (R - 1) >= T
    print(f"    T = {T:2d}  -> {'reachable' if ok else 'UNREACHABLE'}"
          f"   (needs age {T}, max available {R-1})")
