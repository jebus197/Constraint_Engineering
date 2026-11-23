#!/usr/bin/env python3
"""How many commit boards does it cost to LAND 1 batch, with an interval.

DESTINATION `scripts/`. Written 2026-11-22 while a board held the tree.

WHY. The pinned cost figures give the MEAN DURATION of a board (1876.858696 s
= 31.28 min over 92 boards) and the REFUSAL RATE (44 of 92 = 0.478261). Neither
is the number a plan needs. A plan needs the cost of LANDING a batch, which is
the duration times the EXPECTED NUMBER OF BOARDS, and that number was pinned
nowhere.

EVERY FIGURE ON 2 ROUTES, per the 21 April 2026 rule.
"""
from __future__ import annotations
import pathlib
import sys

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp
import sympy as sp

#: ★ ANSWER `--help` BEFORE MEASURING ANYTHING. Added 2026-11-23 because the
#: board refused the batch on
#: `test_help_is_answered_2026-09-11.py::test_every_measurement_script_is_covered`
#: with "exit 0 but no usage line -- the flag was ignored": this script has no
#: parser, so `--help` silently ran the whole measurement instead of describing
#: it. `answer_help` is the helper for a PARSERLESS script -- its
#: `takes_no_arguments` defaults True, which is correct here and is exactly
#: why it must NOT be used on a script that takes real arguments (that mistake
#: is recorded in `scripts/the_board_progress_census_2026-11-22.py`).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
try:
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
except ImportError:                                          # noqa: BLE001
    pass

mp.mp.dps = 40
REFUSED, BOARDS = 44, 92

print("=" * 74)
print("HOW MANY BOARDS DOES IT COST TO LAND 1 BATCH?")
print("=" * 74)

p = REFUSED / BOARDS
w_lo, w_hi = proportion_confint(REFUSED, BOARDS, method="wilson")
# route 2 for Wilson: closed form in mpmath
z = mp.mpf(str(stats.norm.ppf(0.975)))
n, k = mp.mpf(BOARDS), mp.mpf(REFUSED)
ph = k / n
den = 1 + z**2 / n
ctr = (ph + z**2 / (2 * n)) / den
hw = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2))
print(f"\n  refusal rate              : {REFUSED} of {BOARDS} = {p:.6f}")
print(f"  Wilson statsmodels        : [{w_lo:.6f}, {w_hi:.6f}]")
print(f"  Wilson mpmath closed form : [{float(ctr-hw):.6f}, {float(ctr+hw):.6f}]"
      f"   max abs diff {max(abs(float(ctr-hw)-w_lo), abs(float(ctr+hw)-w_hi)):.3e}")
cp_lo, cp_hi = proportion_confint(REFUSED, BOARDS, method="beta")
print(f"  Clopper-Pearson beta      : [{cp_lo:.6f}, {cp_hi:.6f}]")

# ---- Expected boards per landed batch, geometric: E = 1/(1-p) ----
q = sp.Symbol("q", positive=True)
E_sym = sp.simplify(sp.summation(sp.Symbol("i") * 0, (sp.Symbol("i"), 1, 1)) + 1 / (1 - q))
E_closed = float(E_sym.subs(q, sp.Rational(REFUSED, BOARDS)))
rng = np.random.default_rng(20261122)
draws = rng.geometric(1 - p, size=400_000)          # trials until first success
E_mc = float(draws.mean())
print(f"\n  EXPECTED BOARDS PER LANDED BATCH (independent-refusal model)")
print(f"    SymPy closed form 1/(1-p) : {E_closed:.6f}")
print(f"    NumPy 400,000 draws       : {E_mc:.6f}"
      f"   abs diff {abs(E_closed-E_mc):.6f}")
print(f"    propagated from Wilson    : [{1/(1-w_lo):.6f}, {1/(1-w_hi):.6f}]")

MEAN_BOARD_S = 1876.858696
print(f"\n  COST IN WALL-CLOCK, at the pinned mean board of {MEAN_BOARD_S:.1f} s")
print(f"    point estimate            : {E_closed*MEAN_BOARD_S/60:.1f} min per landed batch")
print(f"    interval                  : [{MEAN_BOARD_S/(1-w_lo)/60:.1f}, "
      f"{MEAN_BOARD_S/(1-w_hi)/60:.1f}] min")

print(f"\n  THE LIMIT, AND IT CUTS AGAINST THE MODEL.")
print(f"    Boards are NOT independent: a refusal is diagnosed and fixed before")
print(f"    the next board, so long refusal runs do not occur. The geometric")
print(f"    model therefore OVERSTATES the tail. This session: batch 2 took 2")
print(f"    boards (refuse, fix, pass), which the point estimate {E_closed:.2f}")
print(f"    matches -- but 1 observation cannot validate a tail.")
print(f"    Treat {E_closed:.2f} as a PLANNING MULTIPLIER, not a distribution.")
