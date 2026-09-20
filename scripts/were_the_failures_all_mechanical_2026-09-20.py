#!/usr/bin/env python3
"""Have this project's failures been PURELY MECHANICAL, as the standing directive says?

THE CLAIM UNDER TEST. `.claude/CLAUDE.md` states: "If convergence ever seems out
of reach, the cause is MECHANICAL, not the model ... The maths model has never
been shown wrong. The faults have always been implementation." The founder
restated it on 2026-09-20: "Every failure we have had so far has always and
invariably been purely mechanical in nature. Until now the maths model has stood
every test we have thrown at it." He added, correctly, that this does not mean
the model cannot be falsified or meaningfully revised.

WHY IT MATTERS. The directive is load-bearing: it tells every session to hunt
the mechanics first and not to argue the model is wrong. If it is right, it
saves enormous wasted effort. If it is over-stated, it biases every future
investigation away from a class of defect that does occur.

THE MEASUREMENT. This counts the corrections the APPENDIX ITSELF records, and
classifies each as MECHANICAL (code, pipeline, harness, parsing) or MODEL (the
mathematics as written in the appendix was wrong). The appendix is the model's
own statement of itself, so an error in it is an error in the model as stated --
distinct from an error in the code that implements it.

Run:  python3 scripts/were_the_failures_all_mechanical_2026-09-20.py
"""
from __future__ import annotations

import argparse
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPENDIX = ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


#: Each entry: (label, classification, the appendix's own words, anchor).
#: Every one is quoted from docs/MATHEMATICAL_APPENDIX.md, line numbers as read
#: on 2026-09-20.
RECORD = [
    ("Ising boundedness constraint", "MODEL",
     "the March 2026 constraint was wrong and is withdrawn ... That justification "
     "is false", "L38"),
    ("Ising bound, complement error", "MODEL",
     "Writing (1 - q_i) where q_i belongs crosses over at exactly q = 1/2 ... "
     "above 1/2 it under-constrains", "L46"),
    ("Mobius inverse sign", "MODEL",
     "this line read (pi_k-R_k)/(pi_k(R_k-1)), which is the NEGATIVE of the "
     "inverse and returns C = -3/4 ... named first by the proposed revision 1.1",
     "L169"),
    ("Stage 2->3 called a generalisation", "MODEL",
     "the previous text called all 5 strict generalisations ... this one is not a "
     "generalisation", "L165-L169"),
    ("G_n corroboration reduction row", "MODEL",
     "previously read 'K=1, d=1, uniform p -> C(n)' with no further condition, "
     "which is false whenever a human stream is present ... twice found incomplete",
     "L736-L740"),
    ("G_n numerical illustration table", "MODEL",
     "the previous table was spliced from 2 inconsistent computations", "L757"),
    ("Runner gate C4 polarity", "MODEL",
     "As written ... is backwards relative to 7.1 and the live estimator ... a "
     "converging run failing the convergence condition", "L1024-L1032"),
    ("Suppression weights in q_eff (Error 1)", "MODEL",
     "caused a 113x overestimate of residual risk ... Root cause: conflation of "
     "'finding weight in convergence metric' with 'finding weight in Bayesian "
     "update'", "L1882"),
    ("Predecessor-product order dependence (Error 2)", "MODEL",
     "produced different weights depending on the order findings were processed",
     "L1884"),
    ("kappa overflow (Error 3)", "MODEL",
     "caused the metric to leave [0, 1] ... Root cause: insufficient SymPy "
     "verification of boundary conditions", "L1886"),
    ("sigma placement in the three-phase extension", "MODEL",
     "both falsified the original sigma placement and corrected it", "L2075"),
    ("S_sync formula inverted", "MODEL",
     "original formula (1 - delta)(1 - O_A) was inverted with respect to Delta",
     "L1065"),
    ("Multi-verifier negative weights", "MODEL",
     "original Dimensional and Numerical negative weights were computed as "
     "ln(FNR/TPR) instead of the correct ln(FNR/TNR)", "L1177"),
    ("Attention yield claim", "MODEL",
     "tau_defer replaces the falsified attention yield claim from Rounds 2-6",
     "L487"),
    # For contrast, defects that ARE mechanical and are recorded elsewhere.
    ("Panel seats had no file-reading tools", "MECHANICAL",
     "harness: the tool specification offered no read_file", "round 1, 2026-09-20"),
    ("Empty-content retry missing in the paid-seat loop", "MECHANICAL",
     "harness: ge returned 0 characters", "round 3, 2026-09-20"),
    ("Forced-synthesis temperature hardcoded", "MECHANICAL",
     "harness: kimi returned 0 characters after 25 tool calls", "round 3, 2026-09-20"),
    ("model_params has 0 writers", "MECHANICAL",
     "wiring: the parameters the model needs are never supplied", "cc2, round 3"),
    ("Sandbox profile poisonable", "MECHANICAL",
     "harness: confinement escape via a cached profile", "2026-09-20"),
]


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)

    text = APPENDIX.read_text(errors="ignore") if APPENDIX.is_file() else ""

    print("WERE THE FAILURES PURELY MECHANICAL? THE APPENDIX'S OWN RECORD")
    print("=" * 70)
    model = [r for r in RECORD if r[1] == "MODEL"]
    mech = [r for r in RECORD if r[1] == "MECHANICAL"]
    n = len(RECORD)
    for label, kind, quote, anchor in RECORD:
        print(f"  [{kind:10s}] {label}  ({anchor})")
    print()
    k = len(model)
    lo, hi = wilson(k, n)
    print(f"  corrections classified MODEL      : {k} of {n} = {k/n:.4%}")
    print(f"      Wilson [{lo:.4%}, {hi:.4%}]")
    lo2, hi2 = wilson(len(mech), n)
    print(f"  corrections classified MECHANICAL : {len(mech)} of {n} = {len(mech)/n:.4%}")
    print(f"      Wilson [{lo2:.4%}, {hi2:.4%}]")
    try:
        from statsmodels.stats.proportion import proportion_confint
        a, b = proportion_confint(k, n, method="wilson")
        print(f"  cross-check, statsmodels agrees   : "
              f"{abs(a-lo) < 1e-12 and abs(b-hi) < 1e-12}")
    except ImportError:
        print("  cross-check: statsmodels unavailable")

    print()
    print("  SANITY: are these quotes really in the appendix?")
    found = sum(1 for _l, kind, q, _a in RECORD
                if kind == "MODEL" and q.split(" ...")[0][:40] in text)
    print(f"      {found} of {k} MODEL quotes located verbatim in the file")

    print()
    print("-" * 70)
    print("WHAT THE RECORD SUPPORTS, stated exactly.")
    print()
    print("  SUPPORTED: the CORE recursion has stood. C(n) -> F_n -> R_n -> the")
    print("  recursive collapse -> the three-phase form: every reduction in that")
    print("  chain is verified, and no panel round has refuted the core update")
    print("  R_k(i) = R_k(i-1)(1-q)/(1-q R_k(i-1)).")
    print()
    print("  NOT SUPPORTED: 'the maths model has never been shown wrong'. The")
    print("  appendix records at least", k, "mathematical corrections to itself,")
    print("  including a boundedness constraint that was FALSE and carried for 6")
    print("  months, an inverse with the wrong SIGN, a suppression weight in the")
    print("  wrong place that overestimated residual risk 113-fold, and a")
    print("  convergence condition with INVERTED POLARITY that failed a run the")
    print("  same document calls converging.")
    print()
    print("  THE DISTINCTION THAT RESCUES THE DIRECTIVE'S INTENT: every one of")
    print("  those was found by falsification and corrected, which is the method")
    print("  working, not failing. And 1 of them -- the inverse sign error -- was")
    print("  'named first by the proposed revision 1.1', the very package under")
    print("  review. That is evidence the revision earned its place, independent")
    print("  of whether its larger machinery is adopted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
