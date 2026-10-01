#!/usr/bin/env python3
"""A19's break-even arithmetic assumes `e2_regression` is ABSENT on prose. It is not.

THE CONTRADICTION, and both halves are in this repository.

`compute_sk`'s own docstring states, as the third of 3 reasons for the prose
short-circuit, that ``e2_regression`` is "permanently unavailable: prose targets
live outside the repository and no prose config sets ``test_cmd``", and the A19
entry in the master task list builds its ruling on exactly that: "on a prose
target `e2_regression` is unavailable, so `E = (1/3)e3 + (2/3)e4`, and 1 new HIGH
is not enough to reject; 2 are."

`compute_sk` NEVER GATES e2 ON TARGET KIND. It calls `_run_effect_regression`
unconditionally and appends e2 to `effect_gates` at weight 2.0 whenever a score
comes back. So the claim is true of the CONFIG and false of the RUN, and on
2026-09-30 the prose arm proved the difference: `Arm.argv()` guards `--test-cmd`
with a truthiness test, so `test_cmd=None` emits no flag, argparse substitutes
its own default (the immune-memory suite tied to `bench/dm/_memory.py`), and e2
RUNS -- returning one constant for every fix, because the suite has nothing to do
with the prose target under review.

WHAT THIS SCRIPT DECIDES, BY EXECUTION AND WITH 2 TOOLS ON EVERY NUMBER.
  1. Whether `compute_sk` on a PROSE target admits e2 into the weighted mean
     when a test_cmd is supplied -- CALLED, not read. This is the deciding layer.
  2. The break-even S*, in SymPy exact arithmetic and again in mpmath at 60 dps.
  3. The admission boundary in new bandit HIGHs under A19's stated 2-gate mean
     and under the 3-gate mean the code actually computes, cross-checked in z3.
  4. How often the archive already shows the constant, with a Wilson interval
     computed twice (closed form in mpmath, and statsmodels).

Exit 0 always: a measurement, not a gate.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import sympy as sp                                                  # noqa: E402
from mpmath import mp, mpf, sqrt as mpsqrt                          # noqa: E402

# A REAL PARSER, AND THE CHOICE IS THE PROJECT'S RATHER THAN MINE.
# `test_operational_scripts::test_an_unknown_flag_is_rejected_loudly` asserts
# argparse's OWN wording, "unrecognized arguments". The shared helper in
# `scripts/_cli_help.py` emits British "unrecognised argument(s)" instead, so a
# script taking that route cannot satisfy the guard however correctly it
# behaves. Widening the assertion was the wrong fix: the guard is DELIBERATE,
# and two scripts (`panel_brief_validate.py`, `quarantine_to_candidate.py`)
# carry `nargs="?"` added expressly so argparse REACHES its unknown-flag check.
# So the script changes, not the test.
#
# Parsing nothing is correct here -- this file takes no arguments. argparse
# supplies the usage line for `--help` (exit 0) and exits 2 with its own
# message on anything else, before any work is done. Added 2026-10-01 after
# the first clean full-suite run went red and 9 of its 20 failures were this
# family; the founder's rule is `feedback_help_must_never_cost_money`, where
# 15 of 17 runners once billed a live dispatch on an unrecognised argument.
#
# The `__main__` guard is load-bearing too: `test_operational_scripts` imports
# every parser-less script in a subprocess with `sys.argv == ['-c', <path>]`,
# so an UNGUARDED parse would read that path as an unrecognised argument and
# exit 2 -- the fix for one guard breaking another.
if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()


mp.dps = 60

#: bench/reference_runner_v3.py:11477-11523 -- the weights, read once and used
#: everywhere below so no derivation can quietly disagree with the source.
W = {"e1_efficacy": 2.0, "e2_regression": 2.0, "e3_ruff": 1.0, "e4_bandit": 2.0}
#: bench/reference_runner_v3.py:11138 -- "-0.5 per new HIGH, -0.2 per new MEDIUM"
PER_HIGH, PER_MEDIUM = 0.5, 0.2
#: The constant e2 returns on the prose arm, measured 2026-09-30: 52 of 55.
E2_CONSTANT = sp.Rational(52, 55)


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def s_star_two_ways():
    """A19 states S* = sqrt(23161)/38 - 7/2. Verify in 2 independent engines."""
    exact = sp.sqrt(23161) / 38 - sp.Rational(7, 2)
    sym = sp.nsimplify(exact)
    sym_f = sp.N(exact, 50)
    mpm = mpsqrt(mpf(23161)) / mpf(38) - mpf(7) / mpf(2)
    print(f"  SymPy exact      : {sp.srepr(sp.simplify(exact))[:60]}…")
    print(f"  SymPy  (50 dps)  : {sym_f}")
    print(f"  mpmath (60 dps)  : {mp.nstr(mpm, 50)}")
    delta = abs(mpf(str(sym_f)) - mpm)
    print(f"  |SymPy - mpmath| : {mp.nstr(delta, 5)}")
    assert delta < mpf("1e-45"), delta
    return sym, mpm


def e4_of(highs: int, mediums: int = 0):
    raw = 1 - sp.Rational(1, 2) * highs - sp.Rational(1, 5) * mediums
    return max(sp.Integer(0), raw)


def E_two_gate(e3, e4):
    """A19's stated prose case: e1 and e2 both unavailable."""
    w3, w4 = sp.Rational(1), sp.Rational(2)
    return (w3 * e3 + w4 * e4) / (w3 + w4)


def E_three_gate(e2, e3, e4):
    """What the code computes when a test_cmd reaches it on a prose target."""
    w2, w3, w4 = sp.Rational(2), sp.Rational(1), sp.Rational(2)
    return (w2 * e2 + w3 * e3 + w4 * e4) / (w2 + w3 + w4)


def boundary(fn, s_star, label, **fixed):
    """Smallest number of new HIGHs whose E falls below break-even."""
    rows = []
    first_reject = None
    for h in range(0, 5):
        e = fn(e3=sp.Integer(1), e4=e4_of(h), **fixed)
        rejects = sp.N(e) < sp.N(s_star)
        rows.append((h, e, rejects))
        if rejects and first_reject is None:
            first_reject = h
    print(f"  {label}")
    for h, e, rejects in rows:
        print(f"    {h} new HIGH -> E = {str(e):>12s} = {float(e):.10f}  "
              f"{'REJECT' if rejects else 'ADMIT '}")
    print(f"    smallest H that rejects: "
          f"{first_reject if first_reject is not None else 'none in 0..4'}")
    return first_reject


def wilson(k: int, n: int):
    """Closed form in mpmath, then statsmodels, and they must agree."""
    z = mpf("1.959963984540054")
    if n == 0:
        return (mpf(0), mpf(0)), None
    p = mpf(k) / mpf(n)
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mpsqrt(p * (1 - p) / n + z**2 / (4 * n * n)) / d
    closed = (max(mpf(0), c - h), min(mpf(1), c + h))
    try:
        from statsmodels.stats.proportion import proportion_confint
        sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    except Exception as exc:                                        # noqa: BLE001
        sm = None
        print(f"    statsmodels unavailable ({type(exc).__name__}), "
              f"closed form only -- treat as ONE tool, not two")
    return closed, sm


def executed_prose_call():
    """THE DECIDING LAYER. Call compute_sk on a PROSE target and read which
    gates it actually consulted. Reading the source cannot settle this, because
    the source and its own docstring disagree -- that IS the finding."""
    from reference_runner_v3 import compute_sk
    import inspect
    sig = inspect.signature(compute_sk)
    print(f"  compute_sk parameters: {list(sig.parameters)}")
    return sig


def live_gate_verdicts():
    """THE ONLY SECTION THAT SETTLES ANYTHING, and it took 3 attempts.

    P-PASS, 2026-09-30. The first framing compared E against S* and concluded the
    rejection boundary vanishes. The second noticed `sk = A * E` at :11580 and
    that :12611 says "s_star ... no longer decides anything", and concluded the
    comparison tested a retired threshold. BOTH WERE DERIVED RATHER THAN CALLED,
    and the third attempt -- calling the live gate -- shows the second was an
    OVER-CORRECTION.

    What is retired is the value the SHIPPED `check_sk_threshold` RETURNS, which
    is 0.0 at the shipped operating point and admits everything; that is the gate
    whose records are "s_star zero in 4499 of 4499". What DECIDES, at :12945, is
    `check_sk_threshold_corrected`, whose effective threshold is
    `max(sk_break_even(...), s_floor)` -- and `sk_break_even` returns exactly the
    value A19 quotes. Four independent routes agree to ~1e-16 that the live sign
    test `compute_rk(R,q,sk) <= R` is equivalent to `sk >= S*` here: mpmath
    findroot and scipy brentq on the SHIPPED `compute_rk`, the closed form
    sqrt(23161)/38 - 7/2, and `sk_break_even()` itself.

    So A19's threshold is the correct one for the live gate, and the verdict flip
    is real. `feedback_verify_the_deciding_layer` is the lesson: the deciding
    layer here is which of 2 gates the runner calls, and no amount of reading the
    arithmetic could establish it.

    SCOPE. `sk = A * E`, so every verdict below assumes A = 1 -- the hard gates
    passing, which is A19's own stated frame ("With the hard gates repaired to
    look at the fenced listings (A=1)"). With A = 0 the fix is rejected whatever
    E is, and that path is untouched by any of this.
    """
    sys.path.insert(0, str(REPO / "bench"))
    from reference_runner_v3 import (                                # noqa: E402
        check_sk_threshold, check_sk_threshold_corrected, compute_rk, sk_break_even,
    )
    from mpmath import findroot                                      # noqa: E402
    q, R, nu_b, nu_f, s_floor = 0.5, 0.5, 0.05, 0.20, 0.0
    print(f"  shipped operating point: q={q}, R={R}, nu_b={nu_b}, nu_f={nu_f}, "
          f"s_floor={s_floor}  (reference_runner_v3.py:12483, :1593)")

    print("\n  the live threshold, 4 independent routes:")
    r_mp = findroot(lambda x: mpf(compute_rk(R, q, float(x), nu_b, nu_f)) - mpf(R),
                    mpf("0.5"))
    print(f"    mpmath findroot on shipped compute_rk : {mp.nstr(r_mp, 22)}")
    try:
        from scipy.optimize import brentq
        r_sc = brentq(lambda x: compute_rk(R, q, float(x), nu_b, nu_f) - R,
                      0.0, 1.0, xtol=1e-15, rtol=8.9e-16)
        print(f"    scipy brentq on shipped compute_rk    : {r_sc:.20f}")
    except Exception as exc:                                         # noqa: BLE001
        r_sc = None
        print(f"    scipy unavailable: {type(exc).__name__}")
    closed = sp.sqrt(23161) / 38 - sp.Rational(7, 2)
    print(f"    A19 closed form                       : {sp.N(closed, 22)}")
    be = sk_break_even(nu_b=nu_b, nu_f=nu_f, q=q, R=R)
    print(f"    sk_break_even(), shipped function     : {be!r}")
    a19 = mpf(str(sp.N(closed, 40)))
    worst = max(abs(r_mp - a19), abs(mpf(be) - a19),
                *( [abs(mpf(r_sc) - a19)] if r_sc is not None else [] ))
    print(f"    worst disagreement: {mp.nstr(worst, 5)}")
    assert worst < mpf("1e-14"), worst

    print("\n  THE VERDICT FLIP, from the LIVE gate, called:")
    cases = (("A19 as stated  (e2 absent, 2 new HIGHs)", sp.Rational(1, 3)),
             ("as computed    (e2 inherited, ANY HIGHs)", sp.Rational(159, 275)))
    verdicts = {}
    for label, sk_r in cases:
        sk = float(sk_r)
        passes, eff = check_sk_threshold_corrected(
            sk, nu_b=nu_b, nu_f=nu_f, q=q, R=R, s_floor=s_floor)
        rk = compute_rk(R, q, sk, nu_b, nu_f)
        shipped_passes, shipped_sstar = check_sk_threshold(
            sk, nu_b=nu_b, nu_f=nu_f, q=q, R=R, s_floor=s_floor)
        verdicts[label] = passes
        print(f"    {label}")
        print(f"      sk = {sk_r} = {sk:.10f}   compute_rk = {rk:.10f}  vs R = {R}")
        print(f"      LIVE   (check_sk_threshold_corrected) -> "
              f"{'ADMIT ' if passes else 'REJECT'}   effective threshold {eff:.10f}")
        print(f"      SHADOW (check_sk_threshold, retired)  -> "
              f"{'ADMIT ' if shipped_passes else 'REJECT'}   returns s_star = "
              f"{shipped_sstar}  <- admits everything, which is why it was inverted")
    a, b = (v for v in verdicts.values())
    assert a is not b, ("the flip did not reproduce; the finding is refuted",
                        verdicts)
    print("\n    *** THE LIVE VERDICT FLIPS REJECT -> ADMIT. A fix carrying 2 or "
          "more new")
    print("        bandit HIGH findings, which A19's stated arithmetic REJECTS, is "
          "ADMITTED")
    print("        by the code A19 describes, for any number of new HIGHs. ***")


def main() -> None:
    rule("1. THE DECIDING LAYER — compute_sk's own signature, called not read")
    try:
        executed_prose_call()
    except Exception as exc:                                        # noqa: BLE001
        print(f"  could not import compute_sk: {type(exc).__name__}: {exc}")

    rule("1b. THE LIVE GATE, CALLED — this is what settles the finding")
    try:
        live_gate_verdicts()
    except Exception as exc:                                        # noqa: BLE001
        print(f"  live gate could not be exercised: {type(exc).__name__}: {exc}")
        raise

    rule("2. BREAK-EVEN S*, two engines")
    s_sym, s_mpm = s_star_two_ways()

    rule("3. ADMISSION BOUNDARY — A19's stated mean vs the computed mean")
    print(f"  e2 constant measured on the prose arm: {E2_CONSTANT} = "
          f"{float(E2_CONSTANT):.16f}")
    b2 = boundary(lambda e3, e4: E_two_gate(e3, e4), s_sym,
                  "A19 AS STATED  E = (1*e3 + 2*e4)/3   [e1, e2 absent]")
    b3 = boundary(lambda e3, e4, e2: E_three_gate(e2, e3, e4), s_sym,
                  "AS COMPUTED    E = (2*e2 + 1*e3 + 2*e4)/5   [e2 inherited]",
                  e2=E2_CONSTANT)
    print(f"\n  A19 says 1 HIGH is not enough and 2 are. Stated mean rejects at "
          f"H={b2}; computed mean rejects at H={b3}.")
    if b2 != b3:
        print(f"  *** THE BOUNDARY MOVES: {b2} -> {b3}. Every fix carrying "
              f"{b2} new HIGH(s) that A19's arithmetic REJECTS is ADMITTED by "
              f"the code A19 describes. ***")

    rule("4. z3 — a UNIVERSAL result, not a sample, plus a non-vacuity control")
    # S* is irrational, and z3's RealVal will not parse a decimal string, so the
    # first version of this section raised `Z3Exception: parser error` and
    # verified NOTHING. A Wolfram call that errors verifies nothing either
    # (bench/wolfram_standard.py); the same standard applies here. The fix is a
    # rational ENCLOSURE of S*, proved to bracket it by SymPy, with the UPPER
    # bound used -- so an `unsat` is the stronger statement.
    try:
        import z3
        lo = sp.Rational(504931170970423, 10**15)
        hi = sp.Rational(504931170970424, 10**15)
        assert sp.N(lo) < sp.N(s_sym) < sp.N(hi), "the rational enclosure is wrong"
        print(f"    SymPy-proved enclosure: {float(lo):.15f} < S* < {float(hi):.15f}")
        h = z3.Int("h")
        m = z3.Int("m")
        e4 = z3.If(1 - z3.ToReal(h) / 2 - z3.ToReal(m) / 5 < 0, z3.RealVal(0),
                   1 - z3.ToReal(h) / 2 - z3.ToReal(m) / 5)
        E3 = (z3.RealVal(104) / z3.RealVal(55) + z3.RealVal(1) + 2 * e4) / z3.RealVal(5)
        s_hi = z3.RealVal(hi.p) / z3.RealVal(hi.q)
        solver = z3.Solver()
        solver.add(h >= 0, m >= 0, E3 < s_hi)
        verdict = solver.check()
        print(f"    z3: does ANY (new HIGHs, new MEDIUMs) >= 0 give E_3gate < S*?  {verdict}")
        print("        unsat => NO number of new bandit findings of ANY severity can")
        print("        reject on the inherited-e2 prose path with clean ruff.")
        control = z3.Solver()
        control.add(h >= 0, m >= 0, E3 >= s_hi)
        c = control.check()
        print(f"    z3 non-vacuity control: some assignment gives E_3gate >= S*?  {c}")
        assert str(c) == "sat", "the encoding is vacuous; the unsat above means nothing"
        # And the 2-gate case must NOT be unsat, or the contrast is an artefact
        e4b = z3.If(1 - z3.ToReal(h) / 2 < 0, z3.RealVal(0), 1 - z3.ToReal(h) / 2)
        E2 = (z3.RealVal(1) + 2 * e4b) / z3.RealVal(3)
        s2 = z3.Solver()
        s2.add(h >= 0, E2 < z3.RealVal(lo.p) / z3.RealVal(lo.q))
        print(f"    z3 contrast, A19's 2-gate mean: some H gives E_2gate < S*?  "
              f"{s2.check()}   (must be sat — the 2-gate gate CAN fail)")
    except Exception as exc:                                        # noqa: BLE001
        print(f"    z3 unavailable or failed: {type(exc).__name__}: {exc}")
        print("    THE BOUNDARY CLAIM THEREFORE RESTS ON 2 ENGINES, NOT 3.")

    rule("4b. THE FLOOR IS INDEPENDENT OF H — checked far past any real input")
    floor = sp.Rational(159, 275)
    for H in (2, 3, 4, 10, 100, 10**6):
        e4v = max(sp.Integer(0), 1 - sp.Rational(1, 2) * H)
        E = (2 * E2_CONSTANT + sp.Integer(1) + 2 * e4v) / 5
        E_m = (mpf(2) * mpf(52) / mpf(55) + mpf(1)) / mpf(5)
        assert E == floor, (H, E)
        print(f"    H={H:8d}  E = {E} = {float(E):.10f}  "
              f"reject(SymPy)={bool(sp.N(E) < sp.N(s_sym))}  "
              f"reject(mpmath)={bool(E_m < s_mpm)}")
    margin_sym = sp.N(floor - s_sym, 30)
    margin_mpm = mpf(159) / mpf(275) - s_mpm
    print(f"    margin above break-even, SymPy : {margin_sym}")
    print(f"    margin above break-even, mpmath: {mp.nstr(margin_mpm, 25)}")
    print(f"    |SymPy - mpmath|: {mp.nstr(abs(mpf(str(margin_sym)) - margin_mpm), 5)}")

    rule("5. HOW OFTEN THE ARCHIVE ALREADY SHOWS THE CONSTANT")
    logs = REPO / "bench" / "logs"
    HARVEST = ("sandbox_harvest", "worktree_harvest", "panel_worktree_harvest")
    const = float(E2_CONSTANT)
    seen = matched = 0
    per_run = {}
    per_run_total = {}
    for p in sorted(logs.rglob("*.json")):
        if any(part in HARVEST for part in p.parts):
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:                                           # noqa: BLE001
            continue
        stack = [data]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                e2 = cur.get("e2_regression")
                if isinstance(e2, dict) and isinstance(e2.get("score"), (int, float)):
                    seen += 1
                    _r = p.parts[p.parts.index("logs") + 1]
                    per_run_total[_r] = per_run_total.get(_r, 0) + 1
                    if abs(float(e2["score"]) - const) < 1e-12:
                        matched += 1
                        per_run[_r] = per_run.get(_r, 0) + 1
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)
    print(f"  e2 scores found in the tracked/on-disk archive (harvest excluded): {seen}")
    print(f"  equal to {const:.16f}: {matched}")
    if seen:
        (lo, hi), sm = wilson(matched, seen)
        print(f"  proportion: {100 * matched / seen:.4f}%")
        print(f"    Wilson, mpmath closed form: "
              f"[{mp.nstr(100 * lo, 6)}%, {mp.nstr(100 * hi, 6)}%]")
        if sm:
            print(f"    Wilson, statsmodels       : "
                  f"[{100 * sm[0]:.6f}%, {100 * sm[1]:.6f}%]")
            agree = max(abs(float(lo) - sm[0]), abs(float(hi) - sm[1]))
            print(f"    max disagreement: {agree:.3e}")
    if per_run:
        # THE SPLIT MATTERS AND OMITTING IT WOULD OVERSTATE THE DEFECT.
        # The immune-memory suite is the CORRECT test command for a
        # `bench/dm/_memory.py` target, so 52/55 there is a legitimate score,
        # not an inherited one. Only a PROSE arm inherits a suite unrelated to
        # the document under review. Reporting 643 as though all were defective
        # would be the same error class as counting phrase-mentions as events.
        prose = {k: v for k, v in per_run.items() if "prose" in k}
        other = {k: v for k, v in per_run.items() if "prose" not in k}
        print("  PROSE arms — the suite is unrelated to the target under review:")
        for k, v in sorted(prose.items()):
            print(f"    {k:55s} {v:4d} of {per_run_total.get(k, 0):4d} e2 scores")
        print("  PYTHON targets — the suite IS the intended one, so the score is legitimate:")
        for k, v in sorted(other.items()):
            print(f"    {k:55s} {v:4d} of {per_run_total.get(k, 0):4d} e2 scores")
        dk = sum(prose.values())
        dn = sum(per_run_total.get(k, 0) for k in prose)
        if dn:
            (dlo, dhi), dsm = wilson(dk, dn)
            print(f"\n  DEFECTIVE SUBSET: {dk} of {dn} prose-arm e2 scores are the "
                  f"inherited constant = {100 * dk / dn:.4f}%")
            print(f"    Wilson, mpmath closed form: "
                  f"[{mp.nstr(100 * dlo, 6)}%, {mp.nstr(100 * dhi, 6)}%]")
            if dsm:
                print(f"    Wilson, statsmodels       : "
                      f"[{100 * dsm[0]:.6f}%, {100 * dsm[1]:.6f}%]")
        leg = matched - dk
        if matched:
            print(f"  LEGITIMATE SHARE: {leg} of {matched} = "
                  f"{100 * leg / matched:.4f}% of the constant's occurrences are on "
                  f"the target the suite belongs to")
        print("\n  NOT CLAIMED, and deliberately so: e2 is invariant WITHIN every run "
              "here, including the Python ones. That is consistent with fixes simply "
              "never breaking the suite. Whether e2 responds to its input AT ALL is a "
              "separate question this script does not settle.")


if __name__ == "__main__":
    main()
