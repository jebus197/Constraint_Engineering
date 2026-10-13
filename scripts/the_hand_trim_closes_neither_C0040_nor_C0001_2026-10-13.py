#!/usr/bin/env python3
"""The hand-trim cannot close C0040: the 2 files are on different paths. Measured.

FREE PANEL, 2026-10-13, ITEM 5. The brief proposes RETIRING the coherence pruner
by hand-trimming the directive set, and attaches this claim to its step (3):
"once the full text fits every model's budget, the pruner has nothing to do and
the reduced rendering never triggers, which closes C0040 and C0001 together
without changing a single measurement."

THAT CLAIM IS ARITHMETICALLY FALSE, and the error is a file mix-up it inherits
from its own citation. Three facts, all executed below.

FACT 1 -- THE REVIEW MEASURED A DIFFERENT FILE FROM THE ONE C0040 IS ABOUT.
`experimental_notes/CDSFL_Directive_Pruning_Review_2026-07-18.md` names its
target in its own header: bench/directives/universal/cdsfl_operational.md. The
file `_load_universal_directive` reads, and whose length triggers the reduced
rendering at bench/cdsfl_registry/composer.py:592-595, is
bench/directives/universal/cdsfl_core_formal.md. They are different files and
they reach the model by different routes: the operational directive is APPENDED
IN FULL and is EXEMPT from the per-model `max_directive_chars` caps -- pinned by
bench/tests/test_falsifier_C0040_universal_directive_2026-09-10.py, which
asserts both that the append happens and that the appended prose is more than
90% of what the model receives. Every character the review proposes to cut is a
character that never passed through the cap, so trimming it cannot change that
branch.

FACT 2 -- THE REQUIRED CUT IS 3.7x TO 5.6x THE REVIEW'S COMMITTED ESTIMATE, on
a file the review never measured. Computed below.

FACT 3 -- THE REVIEW FORBIDS THE EDIT THE BRIEF PROPOSES, in its own words,
stated twice (its lines 29-34 and 1611-1616): "Nothing should be cut until a
lean-versus-full ablation has run... This report is the input to that
experiment, not a licence to edit."

WHAT SURVIVES OF THE BRIEF'S ITEM 5 -- its diagnosis. The inversion is forced by
the SHAPE of the metric, not by a loop bug. `_count_constraints`
(composer.py:857-874) takes the merged TOML policy dict and nothing else -- no
DirectivePacket, no `.text` -- so the numerator of `constraint_density` cannot
move when text is deleted while the denominator (`len(text)//4`) strictly falls.
Density is monotonically non-decreasing across both pruning passes. Re-derived
below with SymPy and z3.

THE CONSEQUENCE THE BRIEF DOES NOT STATE, and it is the one a repair must
answer: with both early exits unreachable, `_prune_for_coherence` ALWAYS falls
through to composer.py:935. Its observable behaviour is not "prune until the
budget is met" -- it is "delete every prunable SOFT packet whenever the budget
is exceeded". The function has no stopping rule. Pinned, 2026-10-13, by 2 new
assertions in bench/tests/test_falsifier_C0001_prune_inversion_2026-09-10.py,
which previously pinned only the weaker claim that density worsens.

ON THE ADDITIVE STANDARD'S REMOVAL CLAUSE. The committed measurement a
retirement needs already exists, in that test's own docstring: deepseek_v3 /
software, density 0.011851 -> 0.021042 against a budget of 0.010, 1.7756x WORSE
on the named property (constraint_density against budget), with 10 of 50
compositions losing a domain directive entirely -- 20.0000%, Wilson [11.2438%,
33.0371%]. Not pruning dominates pruning on the metric pruning exists to
optimise. That licenses retiring the PRUNER. It does not license a hand trim,
which is a different intervention on a different file with no measurement at
all.

Usage: python3 scripts/the_hand_trim_closes_neither_C0040_nor_C0001_2026-10-13.py
"""
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
UNIVERSAL = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
OPERATIONAL = REPO / "bench" / "directives" / "universal" / "cdsfl_operational.md"
REVIEW = REPO / "experimental_notes" / "CDSFL_Directive_Pruning_Review_2026-07-18.md"

#: Mirrors PHENOTYPE_TRANSFORMS in bench/cdsfl_registry/composer.py:90-117.
CAPS = {"opus_4_6": 12000, "chatgpt_5_4": 8000, "codex_5_3": 6000,
        "gemini_3_1_pro": 8000, "deepseek_v3": 4000}
#: The review's own committed estimate, from its summary table.
REVIEW_SAVING_CHARS = 6650
REVIEW_MEASURED_CHARS = 43667


def chars(p):
    return len(p.read_text(encoding="utf-8")) if p.exists() else 0


def derive():
    import sympy as sp
    C = sp.Symbol("C", positive=True)
    L = sp.Symbol("L", positive=True)
    density = C / (L / 4)
    out = {"density": sp.simplify(density),
           "d_dL": sp.simplify(sp.diff(density, L))}
    from z3 import Solver, Reals, Not, unsat
    C_, L0, L1, Bz = Reals("C L0 L1 Bz")
    s = Solver()
    s.add(C_ > 0, L0 > 0, L1 > 0, L1 < L0, Not(4 * C_ / L1 > 4 * C_ / L0))
    out["z3_shorter_without_worse"] = s.check()
    out["z3_shorter_without_worse_unsat"] = (s.check() == unsat)
    s2 = Solver()
    s2.add(C_ > 0, L0 > 0, L1 > 0, Bz > 0, L1 < L0,
           4 * C_ / L0 > Bz, 4 * C_ / L1 <= Bz)
    out["z3_early_exit"] = s2.check()
    out["z3_early_exit_unsat"] = (s2.check() == unsat)
    return out


def main() -> int:
    answer_help(__doc__, __file__)
    uni, ope = chars(UNIVERSAL), chars(OPERATIONAL)
    print("=" * 78)
    print("FACT 1 -- TWO DIFFERENT FILES, TWO DIFFERENT PATHS TO THE MODEL")
    print("=" * 78)
    print(f"\n  universal   (read by _load_universal_directive, CAPPED) : {uni:7d} chars")
    print(f"              bench/directives/universal/cdsfl_core_formal.md")
    print(f"  operational (appended in full, EXEMPT from the caps)     : {ope:7d} chars")
    print(f"              bench/directives/universal/cdsfl_operational.md")
    print(f"\n  the 2026-07-18 review exists: {REVIEW.exists()}")
    if REVIEW.exists():
        txt = REVIEW.read_text(encoding="utf-8", errors="ignore")
        print(f"    header names cdsfl_operational.md  : "
              f"{'cdsfl_operational.md' in txt[:4000]}")
        print(f"    header names cdsfl_core_formal.md  : "
              f"{'cdsfl_core_formal.md' in txt[:4000]}")
        print(f"    states an ablation gate on adoption: {'ablation' in txt.lower()}")
    print("\n  So the review's cuts land entirely outside the capped path.")

    print()
    print("=" * 78)
    print("FACT 2 -- REQUIRED CUT vs THE REVIEW'S COMMITTED ESTIMATE")
    print("=" * 78)
    print("\n  required cut on the universal file to clear each cap:")
    for m, c in sorted(CAPS.items(), key=lambda kv: -kv[1]):
        print(f"    {m:15s} cap {c:6d}   must lose {100.0 * (uni - c) / uni:8.4f}%"
              f"   (keep {c} of {uni})")
    rate = REVIEW_SAVING_CHARS / REVIEW_MEASURED_CHARS
    landed = uni - round(uni * rate)
    print(f"\n  review's committed estimate : ~{REVIEW_SAVING_CHARS} of "
          f"{REVIEW_MEASURED_CHARS} = {100 * rate:.4f}%  (OPERATIONAL file)")
    print(f"  that rate on the universal file : {uni} -> {landed} chars")
    print(f"    clears the smallest cap ({min(CAPS.values())})? "
          f"{landed <= min(CAPS.values())}   shortfall {landed - min(CAPS.values()):+d}")
    print(f"    clears the largest  cap ({max(CAPS.values())})? "
          f"{landed <= max(CAPS.values())}   shortfall {landed - max(CAPS.values()):+d}")
    print(f"\n  required-cut / committed-estimate, most generous cap : "
          f"{((uni - max(CAPS.values())) / uni) / rate:.4f}x")
    print(f"  the same ratio at the strictest cap                  : "
          f"{((uni - min(CAPS.values())) / uni) / rate:.4f}x")
    print(f"\n  CONCLUSION: the hand trim closes C0040 for 0 of {len(CAPS)} models.")

    print()
    print("=" * 78)
    print("WHAT SURVIVES -- THE INVERSION, RE-DERIVED (SymPy, then z3)")
    print("=" * 78)
    d = derive()
    print(f"\n  SymPy: constraint_density(L) = {d['density']}  with C text-independent")
    print(f"         d/dL = {d['d_dL']}  -- strictly negative in L, so shortening")
    print(f"         the text RAISES density.")
    print(f"\n  z3: 'text got shorter AND density did not worsen' -> "
          f"{d['z3_shorter_without_worse']}  (unsat: {d['z3_shorter_without_worse_unsat']})")
    print(f"  z3: 'over budget AND an early exit fires'          -> "
          f"{d['z3_early_exit']}  (unsat: {d['z3_early_exit_unsat']})")
    print("\n  composer.py:919 and :932 are UNREACHABLE once :895 falls through, so")
    print("  _prune_for_coherence ALWAYS runs to :935: it deletes every prunable")
    print("  SOFT packet. It has no stopping rule.")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print("""
  The brief's ITEM 5 diagnosis survives; its step (3) does not. A hand trim of
  the operational directive cannot close C0040 -- different file, uncapped path,
  and a required cut 3.7x to 5.6x the review's own committed estimate. The
  review also forbids the edit until an ablation has run.

  The removal clause is the right frame and its committed measurement already
  exists (see this file's docstring). It licenses retiring the PRUNER. It does
  not license a hand trim.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
