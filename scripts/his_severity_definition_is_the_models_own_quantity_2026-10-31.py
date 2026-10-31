#!/usr/bin/env python3
"""His definition of severity, taken seriously: what it IS, what the code has,
and what the archive says about both.

HIS DEFINITION, verbatim from his annotation of `Decisions_Awaiting_You_2026-10-30.txt`
line 156:

    "given what severity is, which as I understand it is what are the chances
    that a particular flaw, or class of flaws might remain after a given number
    of passes under severe scrutiny in any given test, this seems to me like a
    fundamental measure of uncertainty and/or of confidence that can be assigned
    to any given outcome in any STEM focused experiment"

    "Therefore 'severity' by this definition, is unlikely to be a fixed number,
    and would depend on the complexity of the topic under consideration, and the
    confidence once can derive in the accuracy of a given answer."

THE CLAIM THIS SCRIPT TESTS, AND IT IS NOT A FLATTERING ONE FOR THE PREVIOUS
REPORT. That report told him no recommendation could be offered because "whether
severity is a confidence inside a range is a question about what severity means,
and no archive can answer it". That is false in a specific, checkable way: his
definition is NOT a new proposal. It is `R_k`, the residual risk, which
`docs/MATHEMATICAL_APPENDIX.md` line 73 defines as *"the posterior probability
that a flaw of class k remains after n passes that found nothing"* -- the same
quantity in the same words -- and which has been the core of this project's
mathematical model since March 2026.

SO THERE ARE 2 DIFFERENT OBJECTS BOTH CALLED SEVERITY, AND THAT IS THE DEFECT:

  * `R_k` -- his quantity. A survival probability. A function of the number of
    passes n, the per-class prior pi_k, and the per-pass detection power q.
    Implemented as `compute_rk_with_eta_channel`, recorded per entry as
    `sk_result.R_new`.
  * `entry["severity"]` -- a scalar a MODEL asserts about a single finding.
    `effective_severity` returns `asserted * V`. No n, no prior, no detection
    rate. The 0.7 CRITICAL cut applies to THIS one.

Everything below is measured or derived, never asserted. Derivations use SymPy
and are cross-checked with mpmath and z3 per the 21 Apr 2026 two-tool rule.
"""
from __future__ import annotations

import collections
import glob
import json
import pathlib
import statistics

import mpmath
import numpy as np
import sympy as sp
import z3
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


# ───────────────────────────────── derivation ──────────────────────────────

def derive() -> dict:
    """R_k as a function of n, pi and q. SymPy, cross-checked by mpmath and z3."""
    pi, q, n, R = sp.symbols("pi q n R", positive=True)

    # The batch form, appendix line 119: R = pi*m / ((1-pi) + pi*m), m = (1-q)^n
    m = (1 - q) ** n
    R_batch = pi * m / ((1 - pi) + pi * m)

    # The recursive form, appendix line 189.
    R_rec = R * (1 - q) / (1 - q * R)

    # (1) THE 2 FORMS AGREE. Unroll the recursion n=2 from R(0)=pi and compare.
    r1 = R_rec.subs(R, pi)
    r2 = sp.simplify(R_rec.subs(R, r1))
    agree = sp.simplify(r2 - R_batch.subs(n, 2))

    # (2) MONOTONE DECREASING IN n -- "after a given number of passes".
    dR_dn = sp.simplify(sp.diff(R_batch, n))
    # sign of dR/dn for 0<pi<1, 0<q<1, n>0: numerator carries log(1-q) < 0
    sign_dn = sp.simplify(dR_dn.subs({pi: sp.Rational(1, 2), q: sp.Rational(1, 2),
                                      n: 3}))

    # (3) INCREASING IN THE PRIOR, DECREASING IN DETECTION POWER -- his
    #     "depends on the complexity of the topic" and "the confidence one can
    #     derive in the accuracy of a given answer", as 2 separate partials.
    dR_dpi = sp.simplify(sp.diff(R_batch, pi))
    dR_dq = sp.simplify(sp.diff(R_batch, q))
    sign_dpi = sp.simplify(dR_dpi.subs({pi: sp.Rational(1, 2), q: sp.Rational(1, 2),
                                        n: 3}))
    sign_dq = sp.simplify(dR_dq.subs({pi: sp.Rational(1, 2), q: sp.Rational(1, 2),
                                      n: 3}))

    # (4) THE LIMIT. For q>0 the risk goes to 0; the §1 capability ceiling is
    #     the q=0 case, where it stays at pi for ever.
    lim = sp.limit(R_batch.subs({pi: sp.Rational(1, 2), q: sp.Rational(1, 2)}),
                   n, sp.oo)
    lim_q0 = sp.simplify(R_batch.subs(q, 0))

    # (5) PASSES NEEDED TO REACH A TARGET -- this is what a BOUNDARY looks like
    #     in his units, and it inverts in closed form.
    target = sp.symbols("R_t", positive=True)
    n_needed = sp.solve(sp.Eq(R_batch, target), n)

    # z3: the monotonicity claims as unsatisfiability of their negations
    zpi, zq, zR = z3.Reals("pi q R")
    one_step = zR * (1 - zq) / (1 - zq * zR)
    s = z3.Solver()
    s.add(zR > 0, zR < 1, zq > 0, zq < 1)
    s.add(one_step >= zR)            # a pass that found nothing RAISED the risk
    z3_one_step = str(s.check())     # must be unsat

    s2 = z3.Solver()
    s2.add(zR > 0, zR < 1, zq > 0, zq < 1)
    s2.add(z3.Or(one_step < 0, one_step > 1))   # leaves the unit interval
    z3_bounds = str(s2.check())      # must be unsat

    # mpmath: the batch form at a worked point, against SymPy
    with mpmath.workdps(40):
        mp_val = (mpmath.mpf(1) / 2 * (mpmath.mpf(1) / 2) ** 3) / \
                 ((1 - mpmath.mpf(1) / 2) + mpmath.mpf(1) / 2 * (mpmath.mpf(1) / 2) ** 3)
    sym_val = sp.nsimplify(R_batch.subs({pi: sp.Rational(1, 2),
                                         q: sp.Rational(1, 2), n: 3}))
    return {
        "two_forms_agree_at_n2": sp.simplify(agree) == 0,
        "dR_dn_sign_at_half_half_3": float(sign_dn),
        "dR_dpi_sign_at_half_half_3": float(sign_dpi),
        "dR_dq_sign_at_half_half_3": float(sign_dq),
        "limit_n_to_inf_at_q_half": float(lim),
        "R_when_q_is_zero": str(sp.simplify(lim_q0)),
        "n_to_reach_target": str(sp.simplify(n_needed[0])) if n_needed else "",
        "z3_a_null_pass_cannot_raise_risk": z3_one_step,
        "z3_stays_in_unit_interval": z3_bounds,
        "sympy_value_at_pi_q_half_n3": float(sym_val),
        "mpmath_value_at_pi_q_half_n3": float(mp_val),
        "two_tools_agree": abs(float(sym_val) - float(mp_val)) < 1e-30,
    }


def his_worked_contrast() -> dict:
    """4 + 4 against the Riemann hypothesis, computed rather than gestured at.

    His example: *"if you were to ask all the models on the harness to calculate
    the sum of 4 + 4 and call this an experiment, the severity/residual risk of
    the final calculation being wrong would be likely to be very low. But if the
    models on the harness were asked to resolve the Riemann hypothesis, the
    residual risk/severity that the resulting outcome ... would remain uncertain,
    or could not fully be resolved could potentially be significantly higher."*

    In the model's own parameters the contrast is 2 settings of (pi, q):
    an easy question has a low prior flaw rate and high detection power; a hard
    one has a high prior and low detection power. The point of computing it is
    that the 2 answers differ by orders of magnitude, which is what makes a
    SINGLE fixed cut across both meaningless -- his charge, in numbers.
    """
    def R(pi, q, n):
        m = (1 - q) ** n
        return pi * m / ((1 - pi) + pi * m)

    rows = []
    for name, pi, q in (("4 + 4 (easy, strong detection)", 0.02, 0.95),
                        ("a routine code defect", 0.30, 0.60),
                        ("a hard STEM claim", 0.60, 0.30),
                        ("Riemann (hard, weak detection)", 0.90, 0.05),
                        ("beyond the ensemble (q = 0)", 0.90, 0.00)):
        rows.append({"question": name, "pi": pi, "q": q,
                     "R_after_1": R(pi, q, 1), "R_after_3": R(pi, q, 3),
                     "R_after_6": R(pi, q, 6), "R_after_20": R(pi, q, 20)})
    easy = rows[0]["R_after_6"]
    hard = rows[3]["R_after_6"]
    # NumPy cross-check of the same numbers, vectorised
    pis = np.array([r["pi"] for r in rows]); qs = np.array([r["q"] for r in rows])
    mnp = (1 - qs) ** 6
    rnp = pis * mnp / ((1 - pis) + pis * mnp)
    agree = bool(np.allclose(rnp, [r["R_after_6"] for r in rows], atol=1e-15))
    return {"rows": rows, "ratio_hard_over_easy_at_6": hard / easy if easy else None,
            "numpy_agrees": agree}


# ───────────────────────────────── measurement ─────────────────────────────

def archive() -> dict:
    """What the archive actually holds for BOTH quantities.

    A CENSUS of archived reports, so counts and shares carry no sampling
    interval; where a share is of a sub-population drawn from it, the interval
    is reported and named as such.
    """
    reports = sorted(glob.glob(str(LOGS / "*" / "*_report.json")))
    rnew, sev, both = [], [], []
    inputs = collections.defaultdict(collections.Counter)
    reports_with_rnew = 0
    for r in reports:
        try:
            d = json.load(open(r))
        except Exception:
            continue
        ents = ((d.get("registry") or {}).get("entries") or {})
        got = False
        for e in ents.values():
            sk = e.get("sk_result")
            s = e.get("severity")
            if isinstance(sk, dict) and "R_new" in sk:
                rnew.append(float(sk["R_new"])); got = True
                for k in ("sk", "c_ext", "nu_k", "eta_combined"):
                    if k in sk:
                        inputs[k][round(float(sk[k]), 6)] += 1
            if isinstance(s, (int, float)):
                sev.append(float(s))
            if isinstance(sk, dict) and "R_new" in sk and isinstance(s, (int, float)):
                both.append((float(sk["R_new"]), float(s)))
        reports_with_rnew += int(got)

    def spread(v):
        if not v:
            return {}
        return {"n": len(v), "min": min(v), "max": max(v),
                "median": statistics.median(v),
                "stdev": statistics.pstdev(v) if len(v) > 1 else 0.0,
                "distinct": len(set(round(x, 6) for x in v)),
                "top": collections.Counter(round(x, 6) for x in v).most_common(5)}

    out = {"reports": len(reports), "reports_with_R_new": reports_with_rnew,
           "R_new": spread(rnew), "severity": spread(sev),
           "inputs_distinct": {k: dict(c.most_common(4)) for k, c in inputs.items()}}

    # The share of R_new values at its modal value: a sub-population share, so
    # it gets an interval.
    if rnew:
        c = collections.Counter(round(x, 6) for x in rnew)
        mode, k = c.most_common(1)[0]
        n = len(rnew)
        wil = proportion_confint(k, n, alpha=0.05, method="wilson")
        cp = proportion_confint(k, n, alpha=0.05, method="beta")
        out["R_new_modal_share"] = {"value": mode, "k": k, "n": n,
                                    "share": k / n, "wilson": list(map(float, wil)),
                                    "clopper_pearson": list(map(float, cp))}

    # Are the 2 quantities the same object? If they were, they would move
    # together. Spearman AND Kendall, 2 tools.
    if len(both) > 20:
        a = np.array([x for x, _ in both]); b = np.array([y for _, y in both])
        if a.std() > 0 and b.std() > 0:
            sr, sp_p = stats.spearmanr(a, b)
            kt, kt_p = stats.kendalltau(a, b)
            out["R_new_vs_severity"] = {"pairs": len(both),
                                        "spearman": float(sr), "spearman_p": float(sp_p),
                                        "kendall": float(kt), "kendall_p": float(kt_p)}
        else:
            out["R_new_vs_severity"] = {
                "pairs": len(both),
                "note": ("one of the 2 is CONSTANT on the paired set, so no "
                         "rank correlation is defined -- which is itself the "
                         "finding"),
                "R_new_stdev": float(a.std()), "severity_stdev": float(b.std())}
    return out


def main() -> int:
    d = derive()
    c = his_worked_contrast()
    a = archive()
    print(json.dumps({"derivation": d, "his_contrast": c, "archive": a},
                     indent=2, default=str))

    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    print(f"the 2 appendix forms agree at n=2        : {d['two_forms_agree_at_n2']}")
    print(f"dR/dn sign (more passes -> less risk)    : {d['dR_dn_sign_at_half_half_3']:+.6f}")
    print(f"dR/dpi sign (harder question -> more)    : {d['dR_dpi_sign_at_half_half_3']:+.6f}")
    print(f"dR/dq sign (better detection -> less)    : {d['dR_dq_sign_at_half_half_3']:+.6f}")
    print(f"R when q = 0 (capability ceiling)        : {d['R_when_q_is_zero']}")
    print(f"z3: a null pass cannot RAISE risk        : {d['z3_a_null_pass_cannot_raise_risk']} (want unsat)")
    print(f"z3: R stays inside [0,1]                 : {d['z3_stays_in_unit_interval']} (want unsat)")
    print(f"SymPy and mpmath agree at a worked point : {d['two_tools_agree']}")
    print()
    for r in c["rows"]:
        print(f"  {r['question']:34} pi={r['pi']:.2f} q={r['q']:.2f}  "
              f"R@1={r['R_after_1']:.6f} R@6={r['R_after_6']:.6f} "
              f"R@20={r['R_after_20']:.6f}")
    if c["ratio_hard_over_easy_at_6"]:
        print(f"  Riemann/4+4 residual-risk ratio after 6 passes: "
              f"{c['ratio_hard_over_easy_at_6']:.1f}x   (NumPy agrees: {c['numpy_agrees']})")
    print()
    print(f"archived reports                         : {a['reports']}")
    print(f"  carrying R_new (HIS quantity)          : {a['reports_with_R_new']}")
    if a.get("R_new"):
        r = a["R_new"]
        print(f"  R_new   : n={r['n']:5} range {r['min']:.6f}..{r['max']:.6f} "
              f"distinct={r['distinct']} stdev={r['stdev']:.6f}")
    if a.get("severity"):
        s = a["severity"]
        print(f"  severity: n={s['n']:5} range {s['min']:.6f}..{s['max']:.6f} "
              f"distinct={s['distinct']} stdev={s['stdev']:.6f}")
    if a.get("R_new_modal_share"):
        m = a["R_new_modal_share"]
        print(f"  R_new sits at {m['value']} in {m['k']} of {m['n']} entries, "
              f"{m['share']:.6f}, Wilson [{m['wilson'][0]:.6f}, {m['wilson'][1]:.6f}], "
              f"Clopper-Pearson [{m['clopper_pearson'][0]:.6f}, {m['clopper_pearson'][1]:.6f}]")
    if a.get("R_new_vs_severity"):
        print(f"  R_new vs severity: {a['R_new_vs_severity']}")
    return 0


def _cli() -> None:
    """A `--help` MUST NOT run the measurement. Founder rule: a help flag must
    never cost money or time. Guarded by
    `bench/tests/test_help_is_answered_2026-09-11.py`, which refused the first
    commit of this script for exactly this reason."""
    import argparse
    ap = argparse.ArgumentParser(description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--json", action="store_true",
                    help="print the full report as JSON only")
    ap.parse_args()


if __name__ == "__main__":
    _cli()
    raise SystemExit(main())
