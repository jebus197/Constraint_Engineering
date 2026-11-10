#!/usr/bin/env python3
"""`_verify_dimensional_analysis` applies the rule for a SUM to every equation,
so it falsely REJECTS any correct claim built from a product or a quotient.

HOW THIS WAS FOUND, and the order matters. Pointing the per-domain tool sets at
the project's own STEM corpus showed 2 of 5 definitive verdicts were rejections
of CORRECT claims, both from chemistry. The first reading was "the tools are
wrong 2 of 5 times". A DISCRIMINATION CONTROL -- does the tool vary with its
input at all -- gave the real diagnosis instead, which is a specific and fixable
predicate error rather than a rate.

THE PREDICATE, read from `bench/immune_agents.py` rather than inferred. When the
claim contains `=` and at least 2 quantities parse:

    if all(d == lhs_dim for d in rhs_dims):  -> DIM_CONSISTENT -> CONFIRMED
    else:                                    -> DIM_INCONSISTENT -> REJECTED

That requires EVERY extracted quantity to share the FIRST one's dimension. It is
the rule for dimensional HOMOGENEITY, which governs the terms of a SUM. It is
not the rule for an equation in general: `v = 10 m / 2 s = 5 m/s` is correct
physics whose quantities have 3 different dimensions by construction.

MEASURED CONSEQUENCE. Every correct claim built from a product or a quotient is
REJECTED, and that is most of physics, chemistry and engineering:

    speed is 10 m / 2 s = 5 m/s                      REJECTED, and correct
    E = m c^2, 1 kg and 299792458 m/s -> 8.98755e16 J REJECTED, and correct
    a 4.905 m free fall takes 1.0 s at g = 9.81 m/s^2 REJECTED, and correct
    5 m plus 3 m equals 8 m                           CONFIRMED, and correct
    5 m plus 3 s equals 8 m                           UNCERTAIN, and WRONG way

The one shape it gets right is the one it models: a sum of like quantities.

AND IT CONTAMINATES AN AGREEMENT, WHICH IS WHY THE CONTROL MATTERED. On the
corpus, SM-08 is a FALSE claim that this tool REJECTED, counted as agreement.
But the tool rejects mixed-dimension claims whatever their truth, so that
agreement is the base rate rather than a judgement. Of the 3 agreements in that
measurement only 2 -- `statsmodels` on ST-01 and `stoichiometric_balance` on
CM-10, both CONFIRMED -- are discriminating.

WHY IT MATTERS BEYOND ONE TOOL. `dimensional_analysis` is in the PRIMARY tool
list for physics, chemistry, engineering and cross_domain, and physics,
chemistry and engineering are the K/L/M specialist cells promoted from shadow to
LIVE on 2026-07-27. Constraint S5 required their tool coverage be validated
first; that validation was superseded rather than performed, and 0 files under
`scripts/` or `bench/tests/` match `specialist.*accuracy`.

WHAT IS NOT CLAIMED. No fix is proposed here. A correct check needs the
expression's STRUCTURE -- which quantities are summed and which multiplied --
and `pint` can do that given a parsed expression rather than a bag of
quantities. That is a build on a live specialist tool and it is not undertaken
from a measurement alone.

Run: python3 scripts/the_dimensional_check_tests_homogeneity_not_correctness_2026-11-10.py
Exit 0 while the defect reproduces, 1 if the predicate has been repaired --
because a producer that still reports a fixed defect is the stale figure this
project keeps catching.
"""
from __future__ import annotations

import pathlib
import sys


def _find_repo() -> pathlib.Path:
    for start in (pathlib.Path(__file__).resolve().parent,
                  pathlib.Path.cwd().resolve()):
        for cand in (start, *start.parents):
            if (cand / "bench" / "immune_agents.py").is_file():
                return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()

#: (claim, is the claim TRUE, what shape it is)
CASES = (
    ("speed is 10 m / 2 s = 5 m/s", True, "quotient"),
    ("E = m c^2 with m = 1 kg and c = 299792458 m/s gives 8.98755e16 J",
     True, "product"),
    ("a free-fall drop of 4.905 m takes 1.0 s at g = 9.81 m/s^2",
     True, "quotient under a root"),
    ("5 m plus 3 m equals 8 m", True, "sum of like quantities"),
    ("5 m plus 3 s equals 8 m", False, "sum of unlike quantities"),
    ("speed is 10 m / 2 s = 5 kg", False, "quotient, wrong result"),
)

FOR = ("CONFIRMED", "VERIFIED", "SUPPORTED")
AGAINST = ("REJECTED", "REFUTED", "CONTRADICTED")


def main(argv=None) -> int:
    #: A `--help` MUST NEVER COST MINUTES -- his standing rule, and the
    #: project enforces it. This producer had no argparse at all, so `--help`
    #: was ignored and the whole measurement ran (5.65s on 2026-11-10).
    #: The description is taken from the module docstring so the usage text
    #: cannot drift from the file.
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0] if __doc__ else "")
    _ap.parse_args(argv)
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    import immune_agents as ia

    print("=" * 78)
    print("THE DIMENSIONAL CHECK TESTS HOMOGENEITY, NOT CORRECTNESS")
    print("=" * 78)

    rows = []
    for claim, truth, shape in CASES:
        v = ia._verify_dimensional_analysis(claim)
        verdict = getattr(v, "verdict", None)
        says = (True if verdict in FOR
                else False if verdict in AGAINST else None)
        correct = None if says is None else (says == truth)
        rows.append((shape, truth, verdict, correct, claim))
        flag = ("abstains" if correct is None
                else "AGREES" if correct else "*** WRONG ***")
        print(f"\n  {shape:24s} truth={str(truth):5s} -> "
              f"{str(verdict):10s} {flag}")
        print(f"    {claim[:84]}")

    definitive = [r for r in rows if r[3] is not None]
    wrong = [r for r in definitive if not r[3]]
    sums = [r for r in rows if "sum" in r[0]]
    prods = [r for r in rows if r[0] in ("product", "quotient",
                                         "quotient under a root",
                                         "quotient, wrong result")]
    prod_true_wrong = [r for r in prods if r[1] and r[3] is False]

    print(f"\n  definitive verdicts : {len(definitive)} of {len(rows)}")
    print(f"  wrong               : {len(wrong)}")
    print(f"  TRUE product/quotient claims it REJECTS: "
          f"{len(prod_true_wrong)} of {len([r for r in prods if r[1]])}")

    #: THE PREDICATE ITSELF, so the finding does not rest on behaviour alone.
    src = (REPO / "bench" / "immune_agents.py").read_text()
    homogeneity = "all(d == lhs_dim for d in rhs_dims)" in src
    print(f"\n  the homogeneity predicate is in the source: {homogeneity}")
    if homogeneity:
        print("    `if all(d == lhs_dim for d in rhs_dims)` -> CONSISTENT,")
        print("    else INCONSISTENT. That is the rule for the terms of a SUM,")
        print("    applied to every claim containing '='.")

    print("\n  AND IT CONTAMINATES AN AGREEMENT: a FALSE product/quotient claim")
    print("  is also rejected, so counting that as a correct verdict reports")
    print("  the base rate rather than a judgement. Discrimination, not")
    print("  accuracy, is the question for a tool that mostly refuses.")

    reproduces = homogeneity and bool(prod_true_wrong)
    print("\n" + "=" * 78)
    if reproduces:
        print("  DEFECT REPRODUCES — correct product and quotient claims are")
        print("  rejected, and the predicate that does it is in the source.")
    else:
        print("  DEFECT DOES NOT REPRODUCE — the predicate appears repaired.")
        print("  Retire this producer rather than leaving it to report a")
        print("  figure that is no longer true.")
    print("=" * 78)
    return 0 if reproduces else 1


if __name__ == "__main__":
    raise SystemExit(main())
