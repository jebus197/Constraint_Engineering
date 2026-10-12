#!/usr/bin/env python3
"""Does the harness compute severity the way the mathematical appendix specifies?

HIS QUESTION, 2026-10-12, VERBATIM: *"What was the original specification for the
severity gate? Severity was supposed to be calculated in accordance with our
existing maths model. If the models are asked to compute anything it should
surely be computed from our maths model and from what this already says about
severity surely, then they must provide a proof to demonstrate that they have
computed severity correctly, then the other machinery of the schema should apply
a working falsifier/use tools to check that this number makes sense and checks
out. This does not qualify as a 'vote'. Indeed it is the very opposite of a
vote."*

THE SPECIFICATION EXISTS AND HE IS RIGHT ABOUT IT. docs/MATHEMATICAL_APPENDIX.md
section 7.7, Per-Finding Severity:

    Sev(f) = W(class) . confidence . V(verification)

    W(HARD) = 1.0   W(SOFT) = 0.5
    V(True) = 1.0   V(None) = 0.5   V(False) = 0.0

TWO OF THE THREE FACTORS ARE THE HARNESS'S TO DETERMINE, NOT THE MODEL'S. The
constraint class is a HARD/SOFT classification the schema already governs, and
the verification factor is the falsifier outcome the harness itself computes.
Only `confidence` is the model's to assert. The appendix states the consequence
as the section's KEY PROPERTY: "Disproved findings always receive zero severity,
regardless of confidence. A model that is very confident about something wrong
gets zero credit." A verification result VETOES the model's number. That is
structurally the opposite of a vote, exactly as he says.

WHAT THE IMPLEMENTATION DOES INSTEAD. bench/reference_runner_v3.py:6682 reads
`severity=float(entry.get("severity") or 0.0)` from the model's own parsed
output. The product W . confidence . V is computed NOWHERE in live code. So the
number the gate has always used is a single float the model asserts, and the
2026-09-06 argument for removing the severity test -- that severity is a
model-assigned number and there are no votes in CDSFL -- was SOUND ABOUT THE
IMPLEMENTATION AND WRONG ABOUT THE SPECIFICATION. The remedy the argument
licensed was removal; the remedy the specification licenses is to compute it.

THE DECISIVE TEST, AND IT IS THE APPENDIX'S OWN. If the implementation followed
section 7.7, every finding whose falsifier DISPROVED it would carry severity
exactly 0.0, because V(False) = 0 annihilates the product. This script counts
them.

Usage: python3 scripts/severity_was_never_computed_from_the_model_2026-10-12.py
"""
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: Falsifier verdicts that mean THE CLAIM WAS COMPUTATIONALLY DISPROVED, which
#: is the appendix's V(False) case. REFUTED is the runner's own word for it.
DISPROVED = {"REFUTED"}
#: Verdicts meaning computationally VERIFIED -- the appendix's V(True).
VERIFIED = {"CONFIRMED"}


def entries():
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if isinstance(e, dict):
                yield fp, cid, e


def main() -> int:
    answer_help(__doc__, __file__)
    tally = collections.Counter()
    disproved_nonzero, verified_sev, n = [], [], 0
    for _fp, cid, e in entries():
        sev = e.get("severity")
        if not isinstance(sev, (int, float)):
            continue
        n += 1
        verdict = str(e.get("falsifier_verdict") or "").strip().upper()
        tally[verdict or "(none)"] += 1
        if verdict in DISPROVED:
            if float(sev) != 0.0:
                disproved_nonzero.append((cid, float(sev)))
        if verdict in VERIFIED:
            verified_sev.append(float(sev))

    if not n:
        print("no archived entries carry a numeric severity; measurement void.")
        return 3

    print(f"archived entries with a numeric severity: {n}")
    print("\nby falsifier verdict:")
    for v, c in tally.most_common(8):
        print(f"  {v:<22}{c:>6}")

    disproved_total = sum(c for v, c in tally.items() if v in DISPROVED)
    print(f"\nTHE APPENDIX'S KEY PROPERTY (section 7.7): a DISPROVED finding must")
    print(f"carry severity exactly 0.0, because V(False) = 0 annihilates the product.")
    print(f"  disproved (REFUTED) findings          : {disproved_total}")
    print(f"  of those carrying NON-ZERO severity   : {len(disproved_nonzero)}")
    if disproved_total:
        from statsmodels.stats.proportion import proportion_confint
        from scipy import stats
        k = len(disproved_nonzero)
        lo, hi = proportion_confint(k, disproved_total, alpha=0.05, method="wilson")
        lo2 = stats.beta.ppf(0.025, k, disproved_total - k + 1) if k else 0.0
        hi2 = (stats.beta.ppf(0.975, k + 1, disproved_total - k)
               if k < disproved_total else 1.0)
        print(f"  violation rate                        : "
              f"{k/disproved_total:.4%}")
        print(f"    Wilson 95%          [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"    Clopper-Pearson 95% [{lo2:.4%}, {hi2:.4%}]  (scipy.beta)")
        _shown = disproved_nonzero[:6]
        for cid, sev in _shown:
            print(f"      {cid}  severity={sev}")
        if len(disproved_nonzero) > len(_shown):
            print(f"      ... and {len(disproved_nonzero) - len(_shown)} more "
                  f"(of {len(disproved_nonzero)} in total)")

    # SECOND, INDEPENDENT CHECK. Under section 7.7 severity is a product of
    # W in {0.5, 1.0} and V in {0.0, 0.5, 1.0} with confidence in [0, 1], so a
    # VERIFIED HARD finding has severity == confidence and a VERIFIED SOFT one
    # has severity == confidence/2. Nothing constrains the archive's values to
    # any such grid -- but if the implementation computed the product, the
    # DISPROVED set would be identically zero. That is the test above; this is
    # the corroborating spread.
    if verified_sev:
        import numpy as np
        a = np.array(verified_sev)
        print(f"\nverified (CONFIRMED) findings: {len(a)}  "
              f"severity min {a.min():.4f} max {a.max():.4f} "
              f"mean {a.mean():.4f}")

    if disproved_nonzero:
        print("\nVERDICT: the implementation does NOT compute severity as the")
        print("  appendix specifies. Disproved findings carry non-zero severity,")
        print("  which section 7.7 forbids by construction. The gate has always")
        print("  read a model-asserted float, and the specification it was")
        print("  supposed to implement was never implemented.")
        return 0
    print("\nVERDICT: no disproved finding carries non-zero severity; the")
    print("  implementation is consistent with section 7.7 on this property.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
