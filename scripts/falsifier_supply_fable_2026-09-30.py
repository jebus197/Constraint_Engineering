#!/usr/bin/env python3
# PROVENANCE: written by panel seat fable inside its own sandbox during the
# falsifier-root-cause design review of 2026-09-30, NOT by the orchestrating
# session. Rescued verbatim to scripts/ on 2026-09-30T10:47:16+01:00 because
# .gitignore:48 `bench/logs/**` excluded the harvest that held it, leaving the
# evidence behind this review's published figures unversioned and one reboot
# from unrecoverable. Body is byte-identical to the seat's output below this
# header; the seat's original sha256 is 2a9696713be9be159730340684393f3d01dd1e3939af0c0b3cb241644a174879
# (recorded in scripts/seat_evidence_manifest_2026-09-30.json). It is EVIDENCE,
# not an applied fix: no seat proposal is adopted by this rescue.
"""Falsifiers for the fable seat's findings, design review 2026-09-30.

Five executed checks, each named for the finding it decides:

  CHK-1  fixture falsifier contract: the STRUCTURAL template, bound to a copy
         of its pristine document and decided by the runner's REAL decider
         (reverify_falsifier), returns CONFIRMED; after the correct_fix it
         returns REFUTED.
  CHK-2  compute_sk on the same prose target: score_prose_listings=False
         -> NO_SCORE; True -> a scored tristate. Executed, not read.
  CHK-3  resolve_via_routing with the real decider: a weak rung supplying no
         falsifier does NOT resolve; a strong rung supplying the fixture
         template DOES.
  CHK-4  the arm-4 test_cmd inheritance defect: Arm.argv() with test_cmd=None
         omits --test-cmd, and run_simulated_experiment's argparse default is
         the immune-memory suite -- so "excluded" is actually "inherited".
  CHK-5  n* = (a/theta)^(1/gamma) at the March fit and arm 1's best fit,
         mpmath vs sympy; the brief's Wilson intervals, statsmodels vs
         closed-form mpmath; the Fisher exact, scipy vs hypergeometric tail.

Exit 0 with all checks printed PASS, else AssertionError at the failing check.
Spends nothing; dispatches no model; writes only to tempdirs.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("CE_ROOT",
                                   pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))

from bench.tests.fixtures.stem.stem_fixtures import STRUCTURAL          # noqa: E402
from bench.falsifier_verify import reverify_falsifier                    # noqa: E402
from bench.routing import resolve_via_routing                            # noqa: E402
from bench.reference_runner_v3 import compute_sk, _capture_baseline      # noqa: E402

BASELINE = _capture_baseline(STRUCTURAL.document, str(STRUCTURAL.doc_path))


def chk1_fixture_contract(tmp: pathlib.Path) -> None:
    fx = STRUCTURAL
    pristine = tmp / fx.doc_name
    shutil.copyfile(fx.doc_path, pristine)
    v_pristine = reverify_falsifier(fx.falsifier(pristine), repo_root=str(ROOT))
    fixed = tmp / ("fixed_" + fx.doc_name)
    fixed.write_text(fx.apply(fx.correct_fix), encoding="utf-8")
    v_fixed = reverify_falsifier(fx.falsifier(fixed), repo_root=str(ROOT))
    print(f"CHK-1 pristine={v_pristine} fixed={v_fixed}")
    assert v_pristine == "CONFIRMED", v_pristine
    assert v_fixed == "REFUTED", v_fixed
    print("CHK-1 PASS: prose claim decided by runnable code, both directions")


def chk2_sk_flag(tmp: pathlib.Path) -> None:
    """The flag's real semantics are ONE-SIDED (veto, never admit).

    First run of this check asserted flag-on must leave NO_SCORE -- wrong:
    reference_runner_v3.py:11624 deliberately returns NO_SCORE for a CLEAN
    prose fix even with gates run (a clean static sweep is not evidence a
    prose fix is correct). The behavioural difference the flag makes is on a
    HARMFUL fix: flag off -> unscored; flag on -> REJECTED (a conviction).
    """
    fx = STRUCTURAL

    def sk_for(patches, flag):
        fix_text = "\n".join(
            f"<<<< SEARCH {fx.doc_path}\n{p.old}\n==== REPLACE\n{p.new}\n>>>>\n"
            for p in patches)
        return compute_sk(fix_text, fx.document, str(fx.doc_path),
                          baseline=BASELINE, score_prose_listings=flag)

    c_off = sk_for(fx.correct_fix, False)
    c_on = sk_for(fx.correct_fix, True)
    h_off = sk_for(fx.harmful_fix, False)
    h_on = sk_for(fx.harmful_fix, True)
    print(f"CHK-2 correct: off={c_off.tristate} on={c_on.tristate} "
          f"(computed_sk={c_on.gate_details.get('_prose_one_sided', {}).get('computed_sk')})")
    print(f"CHK-2 harmful: off={h_off.tristate} on={h_on.tristate} "
          f"detail={str(h_on.gate_details.get('_prose_one_sided', {}).get('detail',''))[:80]!r}")
    assert c_off.tristate == "NO_SCORE" and "e3_ruff" not in c_off.gate_details
    assert c_on.tristate == "NO_SCORE" and "_prose_one_sided" in c_on.gate_details
    assert h_off.tristate == "NO_SCORE"
    assert h_on.tristate == "REJECTED", h_on.tristate
    print("CHK-2 PASS: flag is veto-only -- convicts harm, never admits; "
          "closure on prose still runs ONLY through falsifiers")


def chk3_routing_supplies(tmp: pathlib.Path) -> None:
    fx = STRUCTURAL
    pristine = tmp / ("r_" + fx.doc_name)
    shutil.copyfile(fx.doc_path, pristine)
    finding = {"finding_id": "C-SM-08", "severity": 0.85,
               "description": "SM-08 linear-in-thickness scaling is false",
               "source_model": "DeepSeek"}

    def resolve_fn(model, f):
        return "" if model == "Gemini" else fx.falsifier(pristine)

    def reverify_fn(code):
        return reverify_falsifier(code, repo_root=str(ROOT))

    r = resolve_via_routing(finding, ["Gemini", "Codex"], resolve_fn,
                            reverify_fn, max_rungs=2)
    print(f"CHK-3 verdict={r.verdict} resolved={r.resolved} "
          f"model={r.model_used} rungs={r.rungs_tried}")
    assert r.resolved and r.verdict == "CONFIRMED" and r.model_used == "Codex"
    r2 = resolve_via_routing(finding, ["Gemini"], lambda m, f: "",
                             reverify_fn, max_rungs=2)
    assert not r2.resolved and r2.verdict == "ERROR"
    print("CHK-3 PASS: supply is a property of the ladder, not the finding")


def chk4_arm4_inheritance() -> None:
    """FALSIFIER (fails iff the defect is present): arm 4's argv, run through
    the launcher's own argparse defaults, must NOT hand the runner the
    immune-memory suite. Pre-fix (2026-09-30) this raised AssertionError with
    parsed test_cmd == the immune default -- the defect demonstrated. Post-fix
    (argv always emits --test-cmd, empty string for an excluded gate) it
    parses to "" and compute_sk records e2_regression unavailable.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "commissioning_arms", ROOT / "bench/tools/commissioning_arms_2026-09-21.py")
    arms_mod = importlib.util.module_from_spec(spec)
    sys.modules["commissioning_arms"] = arms_mod   # dataclasses resolves __module__
    spec.loader.exec_module(arms_mod)
    arm4 = next(a for a in arms_mod.ARMS if a.key == "arm4")
    argv = arm4.argv()
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--target"); ap.add_argument("--seats")
    ap.add_argument("--rounds"); ap.add_argument("--name")
    default_cmd = ("python3 -m pytest bench/tests/test_immune_memory_consumption.py "
                   "bench/tests/test_immune_memory_evaluation.py -q")
    ap.add_argument("--test-cmd", dest="test_cmd", default=default_cmd)
    got = ap.parse_args(argv)
    real = (ROOT / "bench/tools/run_simulated_experiment.py").read_text(encoding="utf-8")
    frag = real[real.index('dest="test_cmd"'):real.index('dest="test_cmd"') + 400]
    assert "test_immune_memory_consumption.py" in frag and \
           "test_immune_memory_evaluation.py -q" in frag, "launcher default drifted"
    print(f"CHK-4 arm4 argv --test-cmd present: {'--test-cmd' in argv}; "
          f"parsed test_cmd = {got.test_cmd!r}")
    assert got.test_cmd != default_cmd, \
        "FALSIFIED: arm4 inherits the immune-memory suite as its e2 gate"
    assert got.test_cmd == "", got.test_cmd
    # And the runner treats "" as gate-unavailable:
    from bench.reference_runner_v3 import _run_effect_regression
    score, detail = _run_effect_regression("x = 1\n", "dummy.py", "")
    assert score is None, (score, detail)
    print(f"CHK-4 PASS: gate genuinely excluded (e2 unavailable: {detail!r})")


def chk5_numbers() -> None:
    import mpmath as mp
    import sympy as sp
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint

    mp.mp.dps = 30
    # The brief quotes 9.3805 and 19.9645. The first reproduces; the second
    # does NOT: from its own stated inputs the value is 19.9681 (rel. err.
    # 1.8e-4 in the brief). Asserted at the RECOMPUTED values; the brief's
    # figure is reported as a (non-material) transcription defect.
    cases = [(4.89, 1.0, 0.709, "9.3805"),
             (4.89, 1.0, 0.5301, "19.9681")]
    for a, th, g, want in cases:
        v_mp = mp.power(a / th, 1 / mp.mpf(g))
        v_sp = float(sp.N(sp.Rational(str(a)) ** (1 / sp.Rational(str(g))), 12))
        assert abs(float(v_mp) - v_sp) < 1e-6, (v_mp, v_sp)
        assert f"{float(v_mp):.4f}" == want, (v_mp, want)
        print(f"CHK-5 n*({a},{th},{g}) = {float(v_mp):.4f}  [mpmath==sympy]")
    print("CHK-5 NOTE: brief's 19.9645 for gamma=0.5301 does not reproduce; "
          "correct value 19.9681")

    def wilson(k, n):
        z = mp.mpf(st.norm.ppf(0.975))
        p = mp.mpf(k) / n
        den = 1 + z**2 / n
        ctr = (p + z**2 / (2 * n)) / den
        hw = (z / den) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
        return float(ctr - hw), float(ctr + hw)

    for k, n, lo_want, hi_want in [(46, 50, 81.1618, 96.8450),
                                   (7, 13, 29.1438, 76.7939),
                                   (5, 29, 7.5979, 34.5484)]:
        lo, hi = wilson(k, n)
        lo2, hi2 = proportion_confint(k, n, method="wilson")
        assert abs(lo - lo2) < 1e-9 and abs(hi - hi2) < 1e-9
        assert f"{lo*100:.4f}" == f"{lo_want:.4f}" and f"{hi*100:.4f}" == f"{hi_want:.4f}", \
            (k, n, lo * 100, hi * 100)
        print(f"CHK-5 Wilson {k}/{n} = [{lo*100:.4f}%, {hi*100:.4f}%]  "
              f"[closed-form==statsmodels]")

    p_sci = st.fisher_exact([[0, 12], [46, 4]], alternative="two-sided")[1]
    N, K, n = 62, 46, 12
    def pmf(x):
        return (mp.binomial(K, x) * mp.binomial(N - K, n - x)) / mp.binomial(N, n)
    p0 = pmf(0)
    p_exact = float(sum(pmf(x) for x in range(0, min(K, n) + 1)
                        if pmf(x) <= p0 * (1 + mp.mpf('1e-12'))))
    assert abs(p_sci - p_exact) / p_sci < 1e-6, (p_sci, p_exact)
    print(f"CHK-5 Fisher exact p = {p_sci:.6e}  [scipy==mpmath hypergeom] "
          f"(brief said 8.425329e-10: "
          f"{'match' if abs(p_sci - 8.425329e-10) / p_sci < 1e-4 else 'MISMATCH'})")


def main() -> None:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="fable_falsifier_"))
    try:
        chk1_fixture_contract(tmp)
        chk2_sk_flag(tmp)
        chk3_routing_supplies(tmp)
        chk4_arm4_inheritance()
        chk5_numbers()
        print("ALL CHECKS PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
