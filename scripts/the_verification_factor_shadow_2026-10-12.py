#!/usr/bin/env python3
"""What would section 7.7's VERIFICATION FACTOR do to the severity gate?

HIS RULING, 2026-10-12: *"Severity was supposed to be calculated in accordance
with our existing maths model. If the models are asked to compute anything it
should surely be computed from our maths model and from what this already says
about severity surely, then they must provide a proof to demonstrate that they
have computed severity correctly, then the other machinery of the schema should
apply a working falsifier/use tools to check that this number makes sense and
checks out. This does not qualify as a 'vote'. Indeed it is the very opposite of
a vote."*

THE SPECIFICATION HE IS POINTING AT EXISTS. docs/MATHEMATICAL_APPENDIX.md 7.7:

    Sev(f) = W(class) . confidence . V(verification)
    W(HARD) = 1.0  W(SOFT) = 0.5
    V(True) = 1.0  V(None) = 0.5  V(False) = 0.0

AND TWO OF ITS THREE INPUTS WERE NEVER COLLECTED. Measured over 3,298 archived
entries: `confidence` appears on 0 of them, and no field carries a HARD/SOFT
constraint class (`flaw_class` is an integer class identifier, the k of section
4's s_k, not the W of 7.7). So the product cannot be computed from the archive,
and `bench/reference_runner_v3.py:6682` instead reads
`severity=float(entry.get("severity") or 0.0)` straight from the model's own
output. The 2026-09-06 argument for removing the severity test -- that severity
is a model-assigned number and there are no votes in CDSFL -- was SOUND ABOUT
THE IMPLEMENTATION AND WRONG ABOUT THE SPECIFICATION.

THE ONE FACTOR THE HARNESS CAN APPLY TODAY, WITH NO SCHEMA CHANGE, IS V. It is
the falsifier's own verdict, which the harness computes itself -- so applying it
is exactly the step he describes as "the other machinery of the schema should
apply a working falsifier". It is also the factor that makes the formula the
opposite of a vote: V(False) = 0 annihilates the product, so a disproved finding
scores zero no matter how confident the model was.

THIS SCRIPT SHADOWS THAT. It takes the model-asserted severity as a stand-in for
the uncollected W . confidence, multiplies by V from the recorded verdict, and
reports what changes -- above all at the 0.7 cut the gate actually uses.

Usage: python3 scripts/the_verification_factor_shadow_2026-10-12.py
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
CUT = 0.7

#: Section 7.7's V, read off the harness's OWN falsifier verdict.
V_TRUE = {"CONFIRMED"}
V_FALSE = {"REFUTED"}


def v_factor(verdict: str) -> float:
    v = (verdict or "").strip().upper()
    if v in V_TRUE:
        return 1.0
    if v in V_FALSE:
        return 0.0
    return 0.5          # V(None): not assessed


def entries():
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if isinstance(e, dict) and isinstance(e.get("severity"), (int, float)):
                yield cid, e


def main() -> int:
    answer_help(__doc__, __file__)
    import numpy as np
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats

    asserted, shadow, byv = [], [], collections.Counter()
    for _cid, e in entries():
        a = float(e["severity"])
        v = v_factor(e.get("falsifier_verdict"))
        asserted.append(a)
        shadow.append(a * v)
        byv[v] += 1

    n = len(asserted)
    if n < 10:
        print(f"only {n} entries; measurement void.")
        return 3
    a = np.array(asserted)
    s = np.array(shadow)

    print(f"archived entries with a severity: {n}")
    print(f"  V(True)=1.0  (CONFIRMED) : {byv[1.0]}")
    print(f"  V(None)=0.5  (unassessed): {byv[0.5]}")
    print(f"  V(False)=0.0 (REFUTED)   : {byv[0.0]}")

    print(f"\nseverity, asserted vs section-7.7 shadow:")
    print(f"  mean   {a.mean():.4f}  ->  {s.mean():.4f}")
    print(f"  median {np.median(a):.4f}  ->  {np.median(s):.4f}")

    ka, ks = int((a >= CUT).sum()), int((s >= CUT).sum())
    for label, k in (("asserted", ka), ("7.7 shadow", ks)):
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        print(f"  at or above the {CUT} cut, {label:<11}: {k:5d}/{n} = "
              f"{k/n:7.4%}  Wilson [{lo:.4%}, {hi:.4%}]")

    moved = int(((a >= CUT) & (s < CUT)).sum())
    lo, hi = proportion_confint(moved, n, alpha=0.05, method="wilson")
    lo2 = stats.beta.ppf(0.025, moved, n - moved + 1) if moved else 0.0
    hi2 = stats.beta.ppf(0.975, moved + 1, n - moved) if moved < n else 1.0
    print(f"\n  entries that CROSS the cut downward: {moved}/{n} = {moved/n:.4%}")
    print(f"    Wilson 95%          [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"    Clopper-Pearson 95% [{lo2:.4%}, {hi2:.4%}]  (scipy.beta)")
    print("  Those are findings the gate currently treats as CRITICAL and which")
    print("  section 7.7 would not, because no tool has verified them.")

    # The appendix's KEY PROPERTY, as a straight count.
    bad = sum(1 for _c, e in entries()
              if v_factor(e.get("falsifier_verdict")) == 0.0
              and float(e["severity"]) != 0.0)
    tot = byv[0.0]
    if tot:
        lo3, hi3 = proportion_confint(bad, tot, alpha=0.05, method="wilson")
        print(f"\n  the appendix's KEY PROPERTY (disproved -> severity 0) is "
              f"violated on {bad} of {tot} = {bad/tot:.4%}")
        print(f"    Wilson 95% [{lo3:.4%}, {hi3:.4%}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
