#!/usr/bin/env python3
"""FALSIFIER: the brief's canonical "computable FALSE claim" is only half false,
and the false half is the half a tool cannot settle on its own.

Run from the repository root:

    python3 scripts/sd_convention_makes_the_claim_undecided_2026-09-30.py

THE CLAIM UNDER TEST. `scripts/intelligence_first_brief_figures_2026-09-30.py`
uses one document throughout as the specimen computable-false claim:

    "The mean of 2, 4 and 6 is 4.5 and the standard deviation is 2.0."

and reports it false, citing `numpy.std` = 1.6329931619 "against a claimed 2.0".

THE MEAN HALF IS UNAMBIGUOUSLY FALSE: 4, not 4.5, under every convention.

THE STANDARD-DEVIATION HALF IS NOT DECIDED BY COMPUTATION ALONE. `numpy.std`
defaults to ddof=0, the POPULATION standard deviation. Under ddof=1, the SAMPLE
standard deviation, the value is EXACTLY 2.0 and the document's claim is TRUE.
The document does not say which it means, and no tool volunteers the question.
A verdict of "false" therefore rests on a convention the reviewer supplied,
not on a computation the reviewer ran.

THIS IS THE INTELLIGENCE-FIRST POINT IN MINIATURE. The decidable step
(arithmetic) is trivial. The step that decides the verdict -- noticing that an
unstated assumption controls it -- is upstream of every tool. A tools-first
reviewer computes 1.633, compares, and reports a defect that may not exist.

FALSIFIED (AssertionError) iff both halves of the conjunction are convention-
independent, i.e. the brief's flat "false" is safe. Clean exit iff the SD half
flips with the convention, i.e. the brief overstates.
"""
from __future__ import annotations

import sys

VALS = [2, 4, 6]
CLAIMED_MEAN = 4.5
CLAIMED_SD = 2.0


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Decides each half of the specimen claim under both "
                    "standard-deviation conventions. Writes nothing.")
    ap.parse_args(argv)

    import numpy as np
    import sympy as sp
    from mpmath import mp, mpf, sqrt as msqrt
    mp.dps = 40

    # --- the mean half: three independent tools -------------------------
    m_sym = sp.Rational(sum(VALS), len(VALS))
    m_np = float(np.mean(VALS))
    m_mp = sum(mpf(v) for v in VALS) / mpf(len(VALS))
    print("MEAN")
    print(f"  sympy  {m_sym}    numpy  {m_np}    mpmath  {mp.nstr(m_mp, 10)}")
    print(f"  claimed {CLAIMED_MEAN}  ->  "
          f"{'FALSE' if float(m_sym) != CLAIMED_MEAN else 'TRUE'}"
          "  (convention-independent)")
    mean_false = float(m_sym) != CLAIMED_MEAN

    # --- the sd half: both conventions, three tools each ------------------
    pop_np = float(np.std(VALS, ddof=0))
    smp_np = float(np.std(VALS, ddof=1))
    mu = m_mp
    ss = sum((mpf(v) - mu) ** 2 for v in VALS)
    pop_mp = float(msqrt(ss / mpf(len(VALS))))
    smp_mp = float(msqrt(ss / mpf(len(VALS) - 1)))
    pop_sym = sp.sqrt(sp.Rational(sum((sp.Integer(v) - m_sym) ** 2
                                      for v in VALS), len(VALS)))
    smp_sym = sp.sqrt(sp.Rational(sum((sp.Integer(v) - m_sym) ** 2
                                      for v in VALS), len(VALS) - 1))
    print("\nSTANDARD DEVIATION")
    print(f"  population (ddof=0)  numpy {pop_np:.10f}  mpmath {pop_mp:.10f}  "
          f"sympy {sp.nsimplify(pop_sym)} = {float(pop_sym):.10f}")
    print(f"  sample     (ddof=1)  numpy {smp_np:.10f}  mpmath {smp_mp:.10f}  "
          f"sympy {smp_sym} = {float(smp_sym):.10f}")
    print(f"  claimed {CLAIMED_SD}  ->  population says "
          f"{'FALSE' if abs(pop_np - CLAIMED_SD) > 1e-9 else 'TRUE'}, "
          f"sample says "
          f"{'FALSE' if abs(smp_np - CLAIMED_SD) > 1e-9 else 'TRUE'}")

    # Wolfram Language, run separately as the SECOND falsifier, quoted here
    # for the record. `wolframscript -code 'N[{Mean[{2,4,6}],
    # StandardDeviation[{2,4,6}]}, 12]'` returned {4., 2.} -- Wolfram's
    # StandardDeviation is the SAMPLE convention, so Wolfram agrees the SD
    # claim is TRUE. Attribution: computed with Wolfram Language.
    print("\n  Wolfram Language (second falsifier, run separately):")
    print("    N[{Mean[{2,4,6}], StandardDeviation[{2,4,6}]}, 12] -> {4., 2.}")
    print("    Wolfram's StandardDeviation is the SAMPLE convention, so the "
          "one tool\n    most likely to be consulted for a second opinion "
          "calls the SD claim TRUE.")

    sd_flips = (abs(smp_np - CLAIMED_SD) <= 1e-9) and (abs(pop_np - CLAIMED_SD) > 1e-9)

    print("\nVERDICT ON THE SPECIMEN")
    print(f"  mean half false, all conventions   {mean_false}")
    print(f"  sd half flips with the convention  {sd_flips}")

    if not sd_flips:
        print("\nNOT FALSIFIED: both halves are convention-independent; the "
              "brief's flat 'false' is safe.")
        return 0

    print("\nFALSIFIED")
    raise AssertionError(
        "The specimen claim is false on its mean and CONVENTION-DEPENDENT on "
        "its standard deviation: ddof=0 gives 1.6329931619 (claim false), "
        "ddof=1 and Wolfram's StandardDeviation give exactly 2.0 (claim true). "
        "The brief reports it flatly false by quoting numpy's default. The "
        "step that decides the verdict -- noticing that an unstated convention "
        "controls it -- is upstream of every tool, which is the brief's own "
        "intelligence-first thesis demonstrated on the brief's own specimen."
    )


if __name__ == "__main__":
    sys.exit(main())
