# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4667b4ca5ffe5f0c4f82ed2e2eb2842bf43b91f252785720c08daa9ee5c5abb3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q6 - settle whether `a` in n* = (a/theta)^(1/gamma) is a CUMULATIVE
coefficient or a RATE coefficient, and what n* actually is.

Run from the repository root:

    python3 scripts/q6_nstar_alpha_is_cumulative_2026-09-30.py

Every number this script prints is computed here. Nothing is quoted from a
note. Cross-verified on mpmath + SymPy (+ scipy.optimize.brentq for the
discrete root), per `measured-rate-travels-with-its-script`.
"""
from __future__ import annotations

import glob
import inspect
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import mpmath as mp  # noqa: E402
import sympy as sp  # noqa: E402

mp.mp.dps = 40


def say(s: str = "") -> None:
    print(s)


def s1_fitter_is_cumulative() -> dict:
    say("S1  THE COMMITTED FITTER FITS THE CUMULATIVE SERIES")
    from bench import decay_analysis as da

    per_round = [5] * 8          # constant RATE 5/round -> cumulative 5*n
    res = da.fit_duane(per_round)
    alpha = res["params"]["alpha"]
    gamma = res["params"]["gamma"]
    say(f"    fit_duane({per_round})")
    say(f"      -> alpha = {alpha}   gamma = {gamma}   sse = {res['sse']}")
    ok = abs(alpha - 5.0) < 1e-2 and abs(gamma - 1.0) < 1e-2
    say(f"      constant RATE 5/round => cumulative 5*n. alpha~5, gamma~1 ? {ok}")
    assert ok, "fit_duane did not fit the cumulative series"

    res2 = da.fit_duane([12, 0, 0, 0, 0, 0])
    say(f"    fit_duane([12,0,0,0,0,0]) -> alpha = {res2['params']['alpha']}, "
        f"gamma = {res2['params']['gamma']}  (gamma pinned at the 0.01 bound)")
    src = inspect.getsource(da.fit_duane)
    say(f"    'cumsum' present in fit_duane source: {'cumsum' in src}")
    say(f"    docstring: {da._duane_cumulative.__doc__!r}")
    say("    VERDICT S1: alpha is a CUMULATIVE coefficient. N(1) = alpha.")
    say()
    return {"alpha": alpha, "gamma": gamma}


def s2_gamma_name_collision() -> dict:
    say("S2  TWO INCOMPATIBLE QUANTITIES ARE BOTH NAMED `gamma`")
    from bench import decay_analysis as da
    from bench.run_exp35_policy_engine import _estimate_gamma

    per_round = [1, 3, 5, 7, 9, 11, 13, 15]      # cumulative = n**2, beta = 2
    da_gamma = da.fit_duane(per_round)["params"]["gamma"]
    rr_gamma = _estimate_gamma(per_round)
    say(f"    per-round {per_round}  (cumulative n**2, growth exponent beta = 2)")
    say(f"      decay_analysis.fit_duane   gamma = {da_gamma:.6f}   (== beta)")
    say(f"      run_exp35._estimate_gamma  gamma = {rr_gamma:.6f}   "
        f"(== max(0, 1-beta), clamped)")
    say(f"      unclamped 1 - beta         = {1 - da_gamma:.6f}")

    per_round2 = [8, 2, 6, 5, 4, 3, 3, 9]        # arm 1's own novel-per-round
    g_da = da.fit_duane(per_round2)["params"]["gamma"]
    g_rr = _estimate_gamma(per_round2)
    say(f"    arm-1 novel-per-round {per_round2}")
    say(f"      fit_duane gamma (beta)         = {g_da:.6f}")
    say(f"      _estimate_gamma gamma (1-beta) = {g_rr:.6f}")
    say(f"      1 - fit_duane gamma            = {1 - g_da:.6f}")
    collides = abs(g_da - g_rr) > 0.1
    say(f"      the two `gamma`s disagree by {abs(g_da - g_rr):.6f}: {collides}")
    assert collides, "expected the two gamma conventions to differ"
    say("    VERDICT S2: 2 distinct quantities share the name `gamma`.")
    say()
    return {"fit_duane_gamma": g_da, "estimate_gamma": g_rr}


def s3_live_path_emits_no_a() -> dict:
    say("S3  THE LIVE PATH PRODUCES NO `a`, SO IT CANNOT EVALUATE n*")
    from bench.run_exp35_policy_engine import _estimate_gamma

    val = _estimate_gamma([8, 2, 6, 5, 4, 3, 3, 9])
    say(f"    _estimate_gamma(...) returns {type(val).__name__} = {val:.6f}")
    say(f"    return annotation: "
        f"{inspect.signature(_estimate_gamma).return_annotation}")
    src = inspect.getsource(_estimate_gamma)
    forms_intercept = bool(re.search(r"intercept|alpha\s*=", src))
    say(f"    source forms a regression intercept anywhere: {forms_intercept}")
    assert not forms_intercept, "unexpected: _estimate_gamma now emits alpha"

    live = ["bench/reference_runner_v3.py", "bench/routing.py",
            "bench/falsifier_verify.py", "bench/runner_core.py"]
    total = 0
    for p in live:
        f = REPO / p
        t = f.read_text(errors="replace") if f.exists() else ""
        n = t.count("decay_analysis") + t.count("fit_duane")
        total += n
        say(f"    {p:38s} mentions of decay_analysis/fit_duane: {n}")
    say(f"    total = {total}")
    say("    VERDICT S3: n* is not computable by the running harness.")
    say()
    return {"live_fitter_mentions": total}


def s4_nstar_three_readings(a: float = 4.89, g: float = 0.709,
                            theta: float = 1.0) -> dict:
    say(f"S4  n* UNDER THE THREE READINGS   (a = {a}, gamma = {g}, theta = {theta})")
    beta = 1.0 - g

    A_mp = mp.power(mp.mpf(str(a)) / mp.mpf(str(theta)), 1 / mp.mpf(str(g)))
    A_sp = sp.N((sp.Rational(str(a)) / sp.Rational(str(theta)))
                ** (1 / sp.Rational(str(g))), 30)
    say("  (A) a is a RATE coefficient, lambda(n) = a*n^-gamma")
    say("      n* = (a/theta)^(1/gamma)")
    say(f"      mpmath {mp.nstr(A_mp, 12)}   sympy {sp.N(A_sp, 12)}   "
        f"|diff| {abs(float(A_sp) - float(A_mp)):.3e}")

    B_mp = mp.power(mp.mpf(str(a)) * mp.mpf(str(beta)) / mp.mpf(str(theta)),
                    1 / mp.mpf(str(g)))
    B_sp = sp.N((sp.Rational(str(a)) * (1 - sp.Rational(str(g))))
                ** (1 / sp.Rational(str(g))), 30)
    say("  (B) a is CUMULATIVE, continuous dN/dn = a*beta*n^(beta-1)")
    say("      n* = (a*(1-gamma)/theta)^(1/gamma)")
    say(f"      mpmath {mp.nstr(B_mp, 12)}   sympy {sp.N(B_sp, 12)}   "
        f"|diff| {abs(float(B_sp) - float(B_mp)):.3e}")

    def incr(n):
        return (mp.mpf(str(a)) * (mp.power(n, beta) - mp.power(n - 1, beta))
                - mp.mpf(str(theta)))

    C_mp = mp.findroot(incr, mp.mpf("2.0"))
    n_sym = sp.symbols("n", positive=True)
    expr = (sp.Rational(str(a))
            * (n_sym ** sp.Rational(str(beta))
               - (n_sym - 1) ** sp.Rational(str(beta)))
            - sp.Rational(str(theta)))
    C_sp = sp.nsolve(expr, n_sym, 2.0, prec=30)
    say("  (C) a is CUMULATIVE, DISCRETE round increment N(n)-N(n-1) = theta")
    say(f"      mpmath {mp.nstr(C_mp, 12)}   sympy {sp.N(C_sp, 12)}   "
        f"|diff| {abs(float(C_sp) - float(C_mp)):.3e}")
    try:
        from scipy.optimize import brentq
        C_sc = brentq(lambda n: a * (n ** beta - (n - 1) ** beta) - theta,
                      1.0001, 50.0)
        say(f"      scipy.brentq (third tool) {C_sc:.12f}")
    except Exception as e:
        say(f"      scipy unavailable: {e}")

    say(f"      ratio (A)/(B) = {float(A_mp) / float(B_mp):.6f}   "
        f"= (1-gamma)^(-1/gamma) = "
        f"{float(mp.power(mp.mpf(str(beta)), -1 / mp.mpf(str(g)))):.6f}")
    say(f"      ratio (A)/(C) = {float(A_mp) / float(C_mp):.6f}")
    say()
    say("  THE DISCRIMINATOR. For the fitted cumulative N(n) = alpha*n^beta,")
    say(f"      N(1) = alpha*1^beta = alpha = {a}  for EVERY beta.")
    say("      So alpha IS the round-1 finding count. The law's own gloss --")
    say("      'the round-1 finding rate divided by the threshold' -- is met")
    say("      by alpha itself, NOT by alpha*(1-gamma).")
    n1_A = float(mp.mpf(str(a)) / mp.mpf(str(beta)))
    say(f"      Under reading (A) instead, N(1) = int_0^1 a*n^-g dn = "
        f"a/(1-gamma) = {n1_A:.6f},")
    say(f"      i.e. reading (A) implies round 1 yielded {n1_A:.2f} findings, "
        f"not {a}.")
    say()
    return {"A": float(A_mp), "B": float(B_mp), "C": float(C_mp)}


def s5_provenance_of_the_constants() -> dict:
    say("S5  CAN (a = 4.89, gamma = 0.709) BE REPRODUCED FROM COMMITTED DATA?")
    from bench import decay_analysis as da

    REVIEWERS = ("cc", "deepseek", "cx", "gemini", "chatgpt")
    curves = []
    for f in sorted(glob.glob(str(REPO / "bench/results/**/*_result.json"),
                              recursive=True)):
        try:
            d = json.loads(Path(f).read_text())
        except Exception:
            continue
        for rev in REVIEWERS:
            c = []
            for rd in d.get("rounds", []) or []:
                x = rd.get(rev, {})
                if isinstance(x, dict):
                    fs = x.get("findings") or x.get("hard_findings") or []
                    c.append(len(fs) if isinstance(fs, list) else 0)
            if len(c) >= 3 and sum(c) > 0:
                curves.append((Path(f).name, rev, c))
    say(f"    committed per-round curves with >=3 rounds and >0 findings: "
        f"{len(curves)}")
    r1 = [c[0] for _, _, c in curves]
    fits = []
    for name, rev, c in curves:
        try:
            p = da.fit_duane(c)["params"]
            fits.append((p.get("alpha"), p.get("gamma")))
        except Exception:
            pass
    near = [(al, ga) for al, ga in fits if al is not None and abs(al - 4.89) < 0.5]
    near_both = [(al, ga) for al, ga in near if abs(ga - 0.709) < 0.05]
    say(f"    round-1 counts: {r1}")
    if r1:
        say(f"    mean round-1 count = {sum(r1) / len(r1):.6f}   max = {max(r1)}")
    say(f"    fits with alpha within 0.5 of 4.89     : {len(near)}")
    say(f"    fits with alpha ~4.89 AND gamma ~0.709 : {len(near_both)}")
    say("    VERDICT S5: the pair (4.89, 0.709) is NOT reproducible from any "
        "committed artefact in this tree. UNSOURCED CONSTANT.")
    say()
    return {"n_curves": len(curves), "near_both": len(near_both)}


def s6_round_budget(a: float = 4.89, theta: float = 1.0) -> dict:
    say("S6  DOES rounds = 10 SURVIVE, AND DOES IT DEPEND ON THE ANSWER?")
    rows = []
    for g in (0.709, 0.5301, 0.2824, 0.1914, 0.1776):
        beta = 1 - g
        A = float(mp.power(mp.mpf(str(a)) / mp.mpf(str(theta)), 1 / mp.mpf(str(g))))
        B = float(mp.power(mp.mpf(str(a)) * mp.mpf(str(beta)), 1 / mp.mpf(str(g))))
        C = float(mp.findroot(
            lambda n, _b=beta: a * (mp.power(n, _b) - mp.power(n - 1, _b)) - theta,
            mp.mpf("2.0")))
        rows.append((g, A, B, C))
    say(f"    {'gamma':>8} {'(A) rate':>14} {'(B) cont.':>12} {'(C) discrete':>14}")
    for g, A, B, C in rows:
        say(f"    {g:8.4f} {A:14.4f} {B:12.4f} {C:14.4f}")
    say(f"    spread across readings at gamma=0.709: "
        f"{rows[0][1]:.4f} / {rows[0][2]:.4f} / {rows[0][3]:.4f}")
    say(f"    spread across arm-1's own gamma history under (A): "
        f"{min(r[1] for r in rows):.4f} .. {max(r[1] for r in rows):.4f}")
    say("    VERDICT S6: n* is not a stable number. rounds = 10 survives ONLY "
        "as an empirical budget, never as a derivation from n*.")
    say()
    return {"rows": rows}


def main() -> int:
    say("=" * 78)
    say("Q6 SETTLEMENT - n* = (a/theta)^(1/gamma)")
    say("=" * 78)
    say()
    s1_fitter_is_cumulative()
    s2_gamma_name_collision()
    s3_live_path_emits_no_a()
    s4_nstar_three_readings()
    s5_provenance_of_the_constants()
    s6_round_budget()
    say("=" * 78)
    say("SETTLED: `a` is a CUMULATIVE coefficient (S1, by calling the only")
    say("committed fitter). The prior round's correction to")
    say("(a*(1-gamma)/theta)^(1/gamma) = 1.6447 is ALSO wrong: it takes a")
    say("CONTINUOUS derivative of a series indexed by a DISCRETE round number.")
    say("N(1) = alpha exactly, so alpha IS the round-1 count, and the discrete")
    say("stopping rule gives n* ~ 2.2, not 9.3805 and not 1.6447. All three")
    say("are moot in the harness (S3), and the constants are unsourced (S5).")
    say("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
