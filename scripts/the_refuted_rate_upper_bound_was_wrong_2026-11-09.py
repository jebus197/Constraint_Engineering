#!/usr/bin/env python3
"""The refuted-finding rate's Wilson UPPER bound was wrong in 6 live places.

THE CLAIM UNDER TEST, quoted identically by 5 live files: "2 of 319 findings
the shadow saw were refuted, 0.006270, Wilson [0.001720, 0.022696]". The
Clopper-Pearson interval stated beside it in 1 of those files,
[0.000760, 0.022463], is CORRECT, which is why this is a transcription error
rather than a method error -- whoever wrote it had working tools.

WHY IT HAD TO BE PRODUCED RATHER THAN CORRECTED IN PROSE. The original figure
existed ONLY as prose: in 4 documents and as a string literal inside
`scripts/which_of_his_instructions_were_carried_out_2026-11-02.py`. No script
computed it. Replacing one unproduced number with another unproduced number
would leave `measured-rate-travels-with-its-script` violated in exactly the
same way, so the corrected value ships with the code that derives it.

HOW THE ERROR WAS RULED OUT AS SOMETHING ELSE, because a figure can answer a
different question and this project has been caught by that:
  * 5 constructions at 95% -- Wilson, Clopper-Pearson, Agresti-Coull, Jeffreys
    and the normal approximation -- and none yields 0.022696.
  * Denominators 317 through 321, in case the count or total was misquoted.
  * z = 1.96 rounded, and Wilson with a continuity correction.
  * Solving for the z that WOULD reproduce it gives 1.969919299, a two-sided
    level of 95.115238%, which nobody selects.
The stated LOWER bound 0.001720 IS correct, being 0.001721035570 truncated, so
only the upper is affected.

THE ERROR DIRECTION IS CONSERVATIVE. 0.022696 is WIDER than the true 0.022568,
so it overstates uncertainty. Nothing downstream was made over-confident, and
the entry it supports -- that at this rate the 2 measures are arithmetically
indistinguishable -- is unaffected and if anything understated.

WHAT IS DELIBERATELY NOT CHANGED. 12 files under `bench/logs/` carry the
original value inside harvested seat output and archived run artefacts. Those
are verbatim records of what a model produced on a date; editing them would
falsify the record, and the repository's own count/interval guard skips
harvested seat files for the same reason.

Exit 0 iff every live file states the correct value and 4 routes agree.
"""
from __future__ import annotations

import math
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")

K, N = 2, 319
WRONG = "0.022696"
#: The live surfaces. Archived seat output under bench/logs/ is NOT here.
LIVE = (
    "resources/RECOVERY.md",
    "scripts/which_of_his_instructions_were_carried_out_2026-11-02.py",
    "experimental_notes/Rerun_Converged_And_A_Prediction_Failed_2026-11-02.md",
    "experimental_notes/CDSFL_MASTER_TASK_LIST.md",
    "experimental_notes/data/morning_report_decisions.json",
)


def wilson_four_routes(k: int, n: int) -> dict:
    """Wilson on 4 implementations, with z obtained 2 different ways.

    HONEST ABOUT ITS OWN INDEPENDENCE. statsmodels and the written-out numpy
    form are 1 formulation computed twice, which this project's independence
    rule of 2026-10-31 calls the WEAKER cross-check. The genuine independence
    here is in z: scipy's normal quantile against mpmath's and SymPy's inverse
    error function. Overstating this is the error withdrawn on 2026-11-09.
    """
    import mpmath
    import numpy as np
    import sympy as sp
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    mpmath.mp.dps = 40
    out = {}

    out["statsmodels"] = tuple(float(x) for x in
                               proportion_confint(k, n, alpha=0.05,
                                                  method="wilson"))
    z = float(stats.norm.ppf(0.975))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * float(np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    out["written-out + numpy"] = (c - h, c + h)

    zm = mpmath.sqrt(2) * mpmath.erfinv(mpmath.mpf("0.95"))
    pm = mpmath.mpf(k) / n
    dm = 1 + zm ** 2 / n
    cm = (pm + zm ** 2 / (2 * n)) / dm
    hm = zm * mpmath.sqrt(pm * (1 - pm) / n + zm ** 2 / (4 * n ** 2)) / dm
    out["mpmath 40 dps"] = (float(cm - hm), float(cm + hm))

    zs = sp.sqrt(2) * sp.erfinv(sp.Rational(95, 100))
    ps = sp.Rational(k, n)
    ds = 1 + zs ** 2 / n
    cs = (ps + zs ** 2 / (2 * n)) / ds
    hs = zs * sp.sqrt(ps * (1 - ps) / n + zs ** 2 / (4 * n ** 2)) / ds
    out["sympy erfinv"] = (float(cs - hs), float(cs + hs))
    return out


def clopper_pearson(k: int, n: int) -> tuple:
    """The interval stated beside it, which was already correct."""
    from statsmodels.stats.proportion import proportion_confint
    return tuple(float(x) for x in
                 proportion_confint(k, n, alpha=0.05, method="beta"))


def ruled_out(k: int, n: int, target: float) -> list:
    """Every construction and denominator checked against the stated value."""
    from scipy import optimize, stats
    from statsmodels.stats.proportion import proportion_confint
    rows = []
    for meth in ("wilson", "beta", "agresti_coull", "jeffreys", "normal"):
        hi = float(proportion_confint(k, n, alpha=0.05, method=meth)[1])
        rows.append((f"{meth} at {k}/{n}", hi, abs(hi - target) < 5e-7))
    for nn in (317, 318, 320, 321):
        hi = float(proportion_confint(k, nn, alpha=0.05, method="wilson")[1])
        rows.append((f"wilson at {k}/{nn}", hi, abs(hi - target) < 5e-7))

    def hi_at(z):
        p = k / n
        d = 1 + z * z / n
        return (p + z * z / (2 * n)) / d + z * math.sqrt(
            p * (1 - p) / n + z * z / (4 * n * n)) / d

    rows.append(("wilson at z = 1.96", hi_at(1.96),
                 abs(hi_at(1.96) - target) < 5e-7))
    z_fit = optimize.brentq(lambda z: hi_at(z) - target, 1.5, 2.5)
    level = 100 * (2 * stats.norm.cdf(z_fit) - 1)
    rows.append((f"implied z = {z_fit:.9f} -> level {level:.6f}%",
                 target, True))
    return rows


def live_state() -> list:
    out = []
    for rel in LIVE:
        p = REPO / rel
        txt = p.read_text(errors="replace") if p.is_file() else ""
        out.append((rel, p.is_file(), txt.count(WRONG)))
    return out


def archived_count() -> int:
    r = subprocess.run(["grep", "-rl", WRONG, "bench/logs"],
                       capture_output=True, text=True, cwd=str(REPO))
    return len([x for x in r.stdout.split() if x.strip()])


def main() -> int:
    routes = wilson_four_routes(K, N)
    his = [v[1] for v in routes.values()]
    los = [v[0] for v in routes.values()]
    correct_hi, correct_lo = his[0], los[0]
    spread = max(his) - min(his)
    cp = clopper_pearson(K, N)

    print("=" * 78)
    print("THE REFUTED-FINDING RATE'S WILSON UPPER BOUND WAS WRONG")
    print("=" * 78)
    print(f"\n  claim: {K} of {N} = {K/N:.6f}")
    print("\n  WILSON UPPER, 4 implementations:")
    for name, (lo, hi) in routes.items():
        print(f"    {name:22s} {hi:.12f}")
    print(f"    max spread across routes: {spread:.3e}")
    print(f"\n  stated in the record : {WRONG}")
    print(f"  correct              : {correct_hi:.6f}")
    print(f"  the stated value is high by {float(WRONG) - correct_hi:.6f}")
    print(f"\n  WILSON LOWER {correct_lo:.12f} -- the stated 0.001720 is this")
    print("  truncated, so only the upper bound was affected.")
    print(f"  CLOPPER-PEARSON [{cp[0]:.6f}, {cp[1]:.6f}] -- stated correctly")
    print("  in the record already, which is why this is transcription and")
    print("  not method.")

    print("\n  WHAT THE STATED VALUE IS NOT:")
    for label, value, match in ruled_out(K, N, float(WRONG)):
        print(f"    {label:48s} {value:.9f} {'MATCH' if match else ''}")

    print(f"\n  LIVE SURFACES, which must all now read {correct_hi:.6f}:")
    bad = []
    for rel, exists, n_wrong in live_state():
        tag = "MISSING" if not exists else ("STILL WRONG" if n_wrong else "ok")
        if not exists or n_wrong:
            bad.append(rel)
        print(f"    {tag:11s} {rel}")

    arch = archived_count()
    print(f"\n  ARCHIVED FILES UNDER bench/logs/ STILL CARRYING {WRONG}: {arch}")
    print("    Left deliberately. These are harvested seat output and run")
    print("    artefacts: verbatim records of what a model produced on a")
    print("    date. Editing them would falsify the record, and the")
    print("    repository's count/interval guard skips harvested seat files")
    print("    for the same reason.")

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS AND WHAT IT DOES NOT")
    print("  SUPPORTS: the stated upper bound was wrong by 0.000128 in 6")
    print("    places across 5 live files, and the corrected value is")
    print("    reproduced here by 4 implementations agreeing to machine")
    print("    precision.")
    print("  DOES NOT SUPPORT: that any conclusion drawn from the figure")
    print("    changes. The error is CONSERVATIVE -- the stated interval was")
    print("    too WIDE -- so the entry's claim that the 2 severity measures")
    print("    are arithmetically indistinguishable at this rate is")
    print("    unaffected, and was if anything understated.")
    print("  HONEST LIMIT ON THE CROSS-CHECK: 2 of the 4 routes are 1")
    print("    formulation computed twice, which this project's independence")
    print("    rule calls the weaker kind. The real independence is in how z")
    print("    is obtained -- a normal quantile against an inverse error")
    print("    function.")
    print("=" * 78)

    if spread > 1e-12:
        print(f"\nFAIL: the 4 routes disagree by {spread:.3e}")
        return 1
    if bad:
        print(f"\nFAIL: {len(bad)} live surface(s) not corrected: {bad}")
        return 1
    print("\nVERDICT: 6 corrections applied, 4 routes agree, archive untouched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
